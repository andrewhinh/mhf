import json
import time
from difflib import get_close_matches
from uuid import uuid4

import modal
import torch
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile
from PIL import ImageFile
from utils import (
    APP_NAME,
    DEFAULT_IMG_PATHS,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_USER_PROMPT,
    GPU_IMAGE,
    JSON_STRUCTURE,
    MINUTES,
    PROCESSOR,
    SECRETS,
    SFT_QUANT_MODEL,
    SUBSTRUCTURE_INFO,
    VOLUME_CONFIG,
    Colors,
    validate_image_file,
)
from vllm import LLM, SamplingParams
from vllm.sampling_params import GuidedDecodingParams

# -----------------------------------------------------------------------------

# vlm config

MODEL = SFT_QUANT_MODEL
QUANTIZATION = "awq_marlin"
KV_CACHE_DTYPE = None  # "fp8_e5m2"
LIMIT_MM_PER_PROMPT = {"image": 1}
ENFORCE_EAGER = False
MAX_NUM_SEQS = 1
MIN_PIXELS = 28 * 28
MAX_PIXELS = 1280 * 28 * 28
TEMPERATURE = 0.0
TOP_P = 0.001
REPEATION_PENALTY = 1.05
STOP_TOKEN_IDS = []
MAX_MODEL_LEN = 32768
MAX_TOKENS = 4096

MAX_FILE_SIZE_MB = 5
MAX_DIMENSIONS = (4096, 4096)

# -----------------------------------------------------------------------------

# Modal

TIMEOUT = 24 * 60 * MINUTES
SCALEDOWN_WINDOW = 5 * MINUTES
ALLOW_CONCURRENT_INPUTS = 1

if modal.is_local():
    GPU_COUNT = torch.cuda.device_count()
else:
    GPU_COUNT = 1

GPU_TYPE = "l4"
GPU_CONFIG = f"{GPU_TYPE}:{GPU_COUNT}"

app = modal.App(name=f"{APP_NAME}-api")

# -----------------------------------------------------------------------------

# main


def get_app():  # noqa: C901
    ## setup
    f_app = FastAPI()
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    llm = LLM(
        model=MODEL,
        tokenizer=PROCESSOR,
        limit_mm_per_prompt=LIMIT_MM_PER_PROMPT,
        enforce_eager=ENFORCE_EAGER,
        max_num_seqs=MAX_NUM_SEQS,
        tensor_parallel_size=GPU_COUNT,
        trust_remote_code=True,
        max_model_len=MAX_MODEL_LEN,
        mm_processor_kwargs={
            "min_pixels": MIN_PIXELS,
            "max_pixels": MAX_PIXELS,
        },
        **{
            k: v
            for k, v in [
                ("quantization", QUANTIZATION),
                ("kv_cache_dtype", KV_CACHE_DTYPE),
            ]
            if v is not None
        },
    )

    sampling_params = SamplingParams(
        temperature=TEMPERATURE,
        top_p=TOP_P,
        repetition_penalty=REPEATION_PENALTY,
        stop_token_ids=STOP_TOKEN_IDS,
        max_tokens=MAX_TOKENS,
        guided_decoding=GuidedDecodingParams(json=JSON_STRUCTURE),
    )

    @f_app.post("/")
    async def main(image_file: UploadFile) -> dict[str, list[list[int]]]:
        start = time.monotonic_ns()
        request_id = uuid4()
        print(f"Generating response to request {request_id}")

        response = validate_image_file(image_file)
        if "error" in response.keys():
            msg = response["error"]
            print(msg)
            raise HTTPException(status_code=400, detail=msg)

        ## send to model
        base64_img = list(response.values())[0]
        image_url = f"data:image/jpeg;base64,{base64_img}"
        dict_outputs = {}
        for substructure, info in SUBSTRUCTURE_INFO.items():
            conversation = [
                {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": DEFAULT_USER_PROMPT.format(
                                substructure=substructure,
                                min=info["min"],
                                max=info["max"],
                            ),
                        },
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ]
            outputs = llm.chat(conversation, sampling_params)
            outputs = [out.outputs[0].text.strip() for out in outputs][0]
            try:
                new_outputs = json.loads(outputs)
            except Exception:
                msg = f"Failed to parse output: {outputs}"
                print(msg)
                raise HTTPException(status_code=500, detail=msg)
            name = new_outputs["name"]
            closest = name
            if name not in SUBSTRUCTURE_INFO.keys():
                closest = get_close_matches(
                    name,
                    SUBSTRUCTURE_INFO.keys(),
                    n=len(SUBSTRUCTURE_INFO.keys()),
                    cutoff=0,
                )[0]
                print(f"Pred name: {name}, closest name: {closest}")
            dict_outputs[closest] = [[p["x"], p["y"]] for p in new_outputs["points"]]

        ## print response
        print(
            Colors.BOLD,
            Colors.GREEN,
            f"Response: {dict_outputs}",
            Colors.END,
            sep="",
        )
        print(
            f"request {request_id} completed in {round((time.monotonic_ns() - start) / 1e9, 2)} seconds"
        )

        return dict_outputs

    return f_app


@app.function(
    image=GPU_IMAGE,
    gpu=GPU_CONFIG,
    volumes=VOLUME_CONFIG,
    secrets=SECRETS,
    timeout=TIMEOUT,
    scaledown_window=SCALEDOWN_WINDOW,
)
@modal.concurrent(max_inputs=ALLOW_CONCURRENT_INPUTS)
@modal.asgi_app()
def modal_get():
    return get_app()


# -----------------------------------------------------------------------------


# testing


@app.local_entrypoint()
def main():
    import requests

    response = requests.post(
        f"{modal_get.web_url}",
        files={"image_file": open(DEFAULT_IMG_PATHS[0], "rb")},
    )
    assert response.ok, response.status_code


if __name__ == "__main__":
    uvicorn.run(get_app(), reload=True)
