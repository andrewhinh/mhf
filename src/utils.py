import random
import subprocess
from pathlib import Path, PurePosixPath

import modal

random.seed(42)

APP_NAME = "mhf"
SPLITS = ["train", "valid", "test"]
PARENT_PATH = Path(__file__).parent.parent
ARTIFACTS_PATH = PARENT_PATH / "artifacts"

DEFAULT_IMG_PATH = ARTIFACTS_PATH / "data" / "0.png"
DEFAULT_IMG_URL = "https://ndownloader.figshare.com/files/46283905"
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."
DEFAULT_USER_PROMPT = """
Detect all substructures in the 2D ultrasound and return their locations in the form of xy-point-based outlines.
Here are the possible substructures and number of points that may be predicted for each substructure.
- calota, min=4, max=6
- cavum, min=4, max=5
- Córtex, min=2, max=2
- silvio, min=3, max=3
- astes anteriors, min=0, max=2
- talems, min=3, max=4
- linia mitja, min=2, max=2
- cerebel, min=6, max=8
Notes:
- the ultrasounds are of size 600 (width) x 800 (height), which indicates the limits of the x and y coordinates.
- multiple but not all substructures may not be present in the ultrasound.
"""

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

GPU_IMAGE = (
    modal.Image.from_registry(  # start from an official NVIDIA CUDA image
        TAG, add_python=PYTHON_VERSION
    )
    .apt_install("git", "ffmpeg", "libsm6", "libxext6")  # add system dependencies
    .pip_install(  # add Python dependencies
        "gimpformats>=2024",
        "hf-transfer>=0.1.9",
        "huggingface-hub>=0.28.1",
        "ipykernel>=6.29.5",
        "matplotlib>=3.10.0",
        "modal>=0.73.24",
        "more-itertools>=10.6.0",
        "opencv-python>=4.11.0.86",
        "python-dotenv>=1.0.1",
        "pyyaml>=6.0.2",
        "requests>=2.32.3",
        "scipy>=1.15.1",
        "tqdm>=4.67.1",
        "transformers @ git+https://github.com/huggingface/transformers.git",
        "vllm>=0.7.2",
        "ninja==1.11.1",  # required to build flash-attn
        "packaging==23.1",  # required to build flash-attn
        "wheel==0.41.2",  # required to build flash-attn
        "torch==2.5.1",  # required to build flash-attn,
    )
    .run_commands(  # add flash-attn
        "pip install flash-attn==2.7.2.post1 --no-build-isolation"
    )
    .env(
        {
            "TOKENIZERS_PARALLELISM": "false",
            "HUGGINGFACE_HUB_CACHE": f"/{PRETRAINED_VOLUME}",
            "HF_HUB_ENABLE_HF_TRANSFER": "1",
        }
    )
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
