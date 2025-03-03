import base64
import io
import random
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

import modal
from PIL import Image
from pydantic import BaseModel

random.seed(42)
APP_NAME = "mhf"

PARENT_PATH = Path(__file__).parent.parent
ARTIFACTS_PATH = PARENT_PATH / "artifacts"
SRC_PATH = PARENT_PATH / "src"

# display
RESIZE_DIMENSIONS = (800, 600)


# terminal


class Colors:
    """ANSI color codes"""

    GREEN = "\033[0;32m"
    BLUE = "\033[0;34m"
    GRAY = "\033[0;90m"
    BOLD = "\033[1m"
    END = "\033[0m"


# image validation
def validate_image_file(
    image_file,
) -> dict[str, str]:
    if image_file is not None:
        valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
        file_extension = Path(image_file.filename).suffix.lower()
        if file_extension not in valid_extensions:
            return {"error": "Invalid file type. Please upload an image."}
        with io.BytesIO(image_file.file.read()) as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")
        return validate_image_base64(image_base64)
    return {"error": "No image uploaded"}


def validate_image_base64(image_base64: str) -> dict[str, str]:
    # Verify MIME type and magic #
    img = Image.open(io.BytesIO(base64.b64decode(image_base64)))
    try:
        img.verify()
    except Exception as e:
        return {"error": e}

    # Limit img size
    MAX_FILE_SIZE_MB = 5
    MAX_DIMENSIONS = (4096, 4096)
    if len(image_base64) > MAX_FILE_SIZE_MB * 1024 * 1024:
        return {"error": f"File size exceeds {MAX_FILE_SIZE_MB}MB limit."}
    if img.size[0] > MAX_DIMENSIONS[0] or img.size[1] > MAX_DIMENSIONS[1]:
        return {
            "error": f"Image dimensions exceed {MAX_DIMENSIONS[0]}x{MAX_DIMENSIONS[1]} pixels limit."
        }

    # Run antivirus
    # write image_base64 to tmp file
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(base64.b64decode(image_base64))
        tmp_file_path = tmp_file.name

    try:
        result = subprocess.run(  # noqa: S603
            ["python", "main.py", str(tmp_file_path)],  # noqa: S607
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PARENT_PATH / "Python-Antivirus",
        )
        scan_result = result.stdout.strip().lower()
        if scan_result == "infected":
            return {"error": "Potential threat detected."}
    except Exception as e:
        return {"error": f"Error during antivirus scan: {e}"}

    return {"success": image_base64}


# model
HF_USERNAME = "andrewhinh"
PROCESSOR = "Qwen/Qwen2.5-VL-3B-Instruct"
BASE_HF_MODEL = "Qwen/Qwen2.5-VL-3B-Instruct"  # pretrained model or ckpt
BASE_QUANT_MODEL = f"{HF_USERNAME}/{APP_NAME}-{BASE_HF_MODEL.split('/')[1]}-AWQ"
SFT_MODEL = "qwen2.5-vl-3b-instruct-full-sft"
SFT_HF_MODEL = f"{HF_USERNAME}/{APP_NAME}-{SFT_MODEL}"  # pretrained model or ckpt
SFT_QUANT_MODEL = f"{SFT_HF_MODEL}-awq"
DPO_MODEL = "qwen2.5-vl-3b-instruct-lora-dpo"
DPO_MERGED = f"{DPO_MODEL}-merged"
DPO_HF_MODEL = f"{HF_USERNAME}/{APP_NAME}-{DPO_MERGED}"  # pretrained model or ckpt
DPO_QUANT_MODEL = f"{DPO_HF_MODEL}-awq"

# data
SPLITS = ["train", "valid", "test"]

# inference
DEFAULT_IMG_PATHS = [ARTIFACTS_PATH / "data" / f"{i}.png" for i in range(0, 4)]
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."
DEFAULT_USER_PROMPT = """
Detect the {substructure} substructure in the 2D ultrasound and return its location in the form of an xy-point-based outline.
For the {substructure}, the outline should have at least {min} points and at most {max} points.
Note that the ultrasounds are of size 800x600 which indicates the limits of the x and y coordinates.
Return a json object as follows:
```json
{{
    "name": "{{substructure}}",
    "points": [
        {{"x": float, "y": float}},
        ...
    ]
}}
```
"""
SUBSTRUCTURE_INFO = {
    "calota": {"min": 4, "max": 6},
    "cavum": {"min": 4, "max": 5},
    "silvio": {"min": 3, "max": 3},
    "astes anteriors": {"min": 2, "max": 2},
    "talems": {"min": 3, "max": 4},
    "linia mitja": {"min": 2, "max": 2},
    "cerebel": {"min": 6, "max": 8},
}


class Point(BaseModel):
    x: float
    y: float


class Substructure(BaseModel):
    name: str
    points: list[Point]


JSON_STRUCTURE = Substructure.model_json_schema()


# Modal
SECRETS = [modal.Secret.from_dotenv(path=PARENT_PATH, filename=".env")]

CUDA_VERSION = "12.4.0"
FLAVOR = "devel"
OS = "ubuntu22.04"
TAG = f"nvidia/cuda:{CUDA_VERSION}-{FLAVOR}-{OS}"
PYTHON_VERSION = "3.12"

DATA_VOLUME = f"{APP_NAME}-data"
PRETRAINED_VOLUME = f"{APP_NAME}-pretrained"
RUNS_VOLUME = f"{APP_NAME}-runs"
VOLUME_CONFIG: dict[str | PurePosixPath, modal.Volume] = {
    f"/{DATA_VOLUME}": modal.Volume.from_name(DATA_VOLUME, create_if_missing=True),
    f"/{PRETRAINED_VOLUME}": modal.Volume.from_name(
        PRETRAINED_VOLUME, create_if_missing=True
    ),
    f"/{RUNS_VOLUME}": modal.Volume.from_name(RUNS_VOLUME, create_if_missing=True),
}
if modal.is_local():
    DATA_VOL_PATH = ARTIFACTS_PATH / "data"
    RUNS_VOL_PATH = ARTIFACTS_PATH / "runs"
    DATA_VOL_PATH.mkdir(parents=True, exist_ok=True)
    RUNS_VOL_PATH.mkdir(parents=True, exist_ok=True)
else:
    DATA_VOL_PATH = Path(f"/{DATA_VOLUME}")
    RUNS_VOL_PATH = Path(f"/{RUNS_VOLUME}")

CPU = 20  # cores (Modal max)
MINUTES = 60  # seconds

TRAIN_REPO_PATH = Path("/LLaMA-Factory")
GPU_IMAGE = (
    modal.Image.from_registry(  # start from an official NVIDIA CUDA image
        TAG, add_python=PYTHON_VERSION
    )
    .apt_install("git", "ffmpeg", "libsm6", "libxext6")  # add system dependencies
    .pip_install(  # add Python dependencies
        "accelerate>=0.34.0,<=1.2.1",
        "datasets>=2.16.0,<=3.2.0",
        "deepspeed>=0.16.3",
        "fastapi>=0.115.8",
        "gimpformats>=2024",
        "hf-transfer>=0.1.9",
        "huggingface-hub>=0.28.1",
        "more-itertools>=10.6.0",
        "ninja>=1.11.1.3",  # required to build flash-attn
        "opencv-python>=4.11.0.86",
        "packaging>=24.2",  # required to build flash-attn
        "pyyaml>=6.0.2",
        "requests>=2.32.3",
        "scikit-learn>=1.6.1",
        "scipy>=1.15.1",
        "torch>=2.5.1",
        "tqdm>=4.67.1",
        "transformers @ git+https://github.com/huggingface/transformers.git@9985d06add07a4cc691dc54a7e34f54205c04d40",
        "vllm>=0.7.2",
        "wandb>=0.19.6",
        "wheel>=0.45.1",  # required to build flash-attn
    )
    .run_commands(
        "pip install git+https://github.com/seungwoos/AutoAWQ.git@add-qwen2_5_vl --no-deps"
    )
    .run_commands(  # add flash-attn
        "pip install flash-attn==2.7.4.post1 --no-build-isolation"
    )
    .run_commands(  # antivirus for file uploads
        [
            "git clone https://github.com/Len-Stevens/Python-Antivirus.git /Python-Antivirus"
        ]
    )
    .run_commands(
        [
            f"git clone --depth 1 https://github.com/hiyouga/LLaMA-Factory.git {TRAIN_REPO_PATH}",
            f"cd {TRAIN_REPO_PATH} && pip install -e '.[torch,metrics]'",
        ]
    )
    .env(
        {
            "TOKENIZERS_PARALLELISM": "false",
            "HUGGINGFACE_HUB_CACHE": f"/{PRETRAINED_VOLUME}",
            "HF_HUB_ENABLE_HF_TRANSFER": "1",
            "FORCE_TORCHRUN": "1",
        }
    )
    .add_local_python_source("utils")
)


## subprocess for Modal
def _exec_subprocess(cmd: list[str]):
    """Executes subprocess and prints log to terminal while subprocess is running."""
    process = subprocess.Popen(  # noqa: S603
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    with process.stdout as pipe:
        for line in iter(pipe.readline, b""):
            line_str = line.decode()
            print(f"{line_str}", end="")

    if exitcode := process.wait() != 0:
        raise subprocess.CalledProcessError(exitcode, "\n".join(cmd))
