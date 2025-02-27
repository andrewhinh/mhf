import random
import subprocess
from pathlib import Path, PurePosixPath

import modal
from pydantic import BaseModel

random.seed(42)
APP_NAME = "mhf"

PARENT_PATH = Path(__file__).parent.parent
ARTIFACTS_PATH = PARENT_PATH / "artifacts"
SRC_PATH = PARENT_PATH / "src"

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
DEFAULT_IMG_PATH = ARTIFACTS_PATH / "data" / "0.png"
DEFAULT_IMG_URL = "https://ndownloader.figshare.com/files/46283905"
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
