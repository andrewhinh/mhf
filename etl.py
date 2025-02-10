import json
import multiprocessing
import os
import random
import tempfile
from pathlib import Path

import cv2
import modal
import numpy as np
import requests
from gimpformats.gimpXcfDocument import GimpDocument
from PIL import Image
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map

from utils import (
    ARTIFACTS_PATH,
    DEFAULT_USER_PROMPT,
    MINUTES,
    NAME,
    PRETRAINED_VOLUME,
    PYTHON_VERSION,
    VOLUME_CONFIG,
)

# -----------------------------------------------------------------------------

# Modal
if modal.is_local():
    DATA_VOL_PATH = str(ARTIFACTS_PATH / "data")
else:
    DATA_VOL_PATH = f"/{PRETRAINED_VOLUME}/data"
os.makedirs(DATA_VOL_PATH, exist_ok=True)

IMAGE = (
    modal.Image.debian_slim(python_version=PYTHON_VERSION)
    .apt_install("ffmpeg", "libsm6", "libxext6")
    .pip_install(
        "gimpformats>=2024",
        "modal>=0.73.24",
        "opencv-python>=4.11.0.86",
        "requests>=2.32.3",
        "tqdm>=4.67.1",
    )
)
TIMEOUT = 24 * 60 * MINUTES

APP_NAME = f"{NAME}-etl"
app = modal.App(name=APP_NAME)

# -----------------------------------------------------------------------------

# helpers

random.seed(42)

ORIGINAL_JSON = Path(f"{DATA_VOL_PATH}/original.json")

TRAIN_SZ, VAL_SZ, TEST_SZ = 0.8, 0.1, 0.1

SFT_TRAIN_JSON = Path(f"{DATA_VOL_PATH}/sft_train.json")
SFT_VAL_JSON = Path(f"{DATA_VOL_PATH}/sft_val.json")
SFT_TEST_JSON = Path(f"{DATA_VOL_PATH}/sft_test.json")


def clean_ux(image):
    """
    Function designed to clean the UX from a US image from Girona.

    :param image: Image with the UX.
    :return: a clean image without UX.
    """
    new_image = image.copy()
    new_image[:50, ...] = 0
    new_image[:150, -100:] = 0
    new_image[:, :40] = 0

    return new_image


def get_points(image):
    """
    Function designed to take an image with manually drawn points and return
    the set of coordinates for their centroid.

    :param image: RGB image with the point annotations.
    :return:  numpy aray with the centroids (points x coordinates).
    """
    # We us OpenCV to binarize the image and detect the points.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray[gray > 0] = 255

    # We use OpenCV to compute the centroids of the annotated points.
    _, _, _, centroids = cv2.connectedComponentsWithStats(gray)

    # We ignore the background centroid (first and largest one).
    return centroids[1:]


def makeDict(names, points):
    """
    Given two lists of layers and another list with the lists of points in each layer at every position,
    create a dictionary with layer names as keys
    and the lists of points as values
    """
    return {names[i]: points[i] for i in range(len(names))}


def load_xcf(path):
    """
    Given the name of a xcf file, this functions reads it using GimpDocument,
    extract a list of images along with a list of layer names and returns them
    as two lists.
    :param path: Path to the image.
    :return: list of the layer names and their data (images).
    """

    # List data on groups followed by the direct children of a gimp xcf
    # document.
    project = GimpDocument(path)
    layers = project.layers
    # CAUTION: We are including the image. It's important if we only want the
    # coordinates of the annotatons, as we will need to ignore it!
    names, data = zip(
        *[(layer.name, layer.image) for layer in layers if not layer.isGroup]
    )
    labels = list(names)[:-1]
    annotations = list(data)[:-1]
    points = [get_points(np.array(x)) for x in annotations]
    image = clean_ux(np.array(data[-1])[..., 0])

    return image, labels, points


def process_xcf(url: str, i: int):
    xcf_data = requests.get(url).content
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xcf").name
    with open(tmp_file, "wb") as f:
        f.write(xcf_data)
    image, labels, points = load_xcf(tmp_file)
    names_to_points = makeDict(labels, points)
    pil_image = Image.fromarray(image)
    img_path = Path(f"{DATA_VOL_PATH}/{i}.png")
    pil_image.save(img_path)
    return names_to_points, i


@app.function(
    image=IMAGE,
    timeout=TIMEOUT,
)
def load_json(sample: dict):
    return json.loads(requests.get(sample["url"]).text)


def write_sft_json(json_path: Path, xcfs: list):
    with open(json_path, "w") as f:
        json.dump(
            [
                {
                    "conversations": [
                        {
                            "from": "human",
                            "value": f"<image>{DEFAULT_USER_PROMPT}",
                        },
                        {
                            "from": "gpt",
                            "value": json.dumps(
                                xcf[0],
                                default=lambda x: x.tolist()
                                if isinstance(x, np.ndarray)
                                else x,
                            ),
                        },
                    ],
                    "images": [f"{DATA_VOL_PATH}/{xcf[1]}.png"],
                }
                for xcf in xcfs
            ],
            f,
            indent=4,
        )


# -----------------------------------------------------------------------------


def main(sft: bool, dpo: bool):
    if not sft and not dpo:
        raise ValueError("Must specify at least one of `sft` or `dpo`")

    if sft:
        with open(ORIGINAL_JSON, "r") as f:
            data = json.load(f)

        if modal.is_local():
            json_data = list(
                tqdm(
                    thread_map(
                        load_json.local,
                        data,
                        max_workers=multiprocessing.cpu_count(),
                    )
                )
            )
        else:
            json_data = load_json.map(data)

        urls = [
            sample["files"][0]["download_url"]
            for sample in json_data
            if sample["files"][0]["mimetype"] == "image/x-xcf"
        ]

        n_unique = len(urls)
        xcfs = list(
            tqdm(
                thread_map(
                    process_xcf,
                    urls,
                    range(n_unique),
                    max_workers=multiprocessing.cpu_count(),
                )
            )
        )

        n_train = int(TRAIN_SZ * n_unique)
        n_val = int(VAL_SZ * n_unique)
        random.shuffle(xcfs)
        train, val, test = (
            xcfs[:n_train],
            xcfs[n_train : n_train + n_val],
            xcfs[n_train + n_val :],
        )
        for json_path, xcfs in zip(
            [SFT_TRAIN_JSON, SFT_VAL_JSON, SFT_TEST_JSON], [train, val, test]
        ):
            write_sft_json(json_path, xcfs)

    if dpo:
        pass


@app.function(
    image=IMAGE,
    volumes=VOLUME_CONFIG,
    timeout=TIMEOUT,
)
def run(sft: bool, dpo: bool):
    main(sft, dpo)


@app.local_entrypoint()
def local(sft: bool = False, dpo: bool = False):
    run.remote(sft, dpo)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--sft", action="store_true")
    parser.add_argument("--dpo", action="store_true")
    args = parser.parse_args()
    main(args.sft, args.dpo)
