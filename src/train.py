"""Official qwen2_5-VL training scripts."""

import json
import os
from pathlib import Path

import modal

from utils import (
    APP_NAME,
    BASE_HF_MODEL,
    DATA_VOL_PATH,
    DPO_HF_MODEL,
    DPO_MERGED,
    DPO_MODEL,
    GPU_IMAGE,
    MINUTES,
    RUNS_VOL_PATH,
    SECRETS,
    SFT_HF_MODEL,
    SFT_MODEL,
    VOLUME_CONFIG,
    _exec_subprocess,
)

# -----------------------------------------------------------------------------

# Modal
TRAIN_REPO_PATH = Path("/LLaMA-Factory")
IMAGE = GPU_IMAGE.run_commands(
    [
        f"git clone --depth 1 https://github.com/hiyouga/LLaMA-Factory.git {TRAIN_REPO_PATH}",
        f"cd {TRAIN_REPO_PATH} && pip install -e '.[torch,metrics]'",
    ]
).env(
    {
        "FORCE_TORCHRUN": "1",
    }
)
TIMEOUT = 24 * 60 * MINUTES

GPU_TYPE = "h100"
GPU_COUNT = 2
GPU_SIZE = None  # options = None, "40GB", "80GB"
GPU_CONFIG = f"{GPU_TYPE}:{GPU_COUNT}"

app = modal.App(name=f"{APP_NAME}-train")


## dataset_info.json
SFT_DATA = "sft_train.json"
DPO_DATA = "dpo_train.json"
dataset_info = {
    "sft": {
        "file_name": str(TRAIN_REPO_PATH / "data" / SFT_DATA),
        "formatting": "sharegpt",
        "columns": {"messages": "conversations", "images": "images"},
    },
    "dpo": {
        "file_name": str(TRAIN_REPO_PATH / "data" / DPO_DATA),
        "formatting": "sharegpt",
        "ranking": True,
        "columns": {
            "messages": "conversations",
            "chosen": "chosen",
            "rejected": "rejected",
            "images": "images",
        },
    },
}
DS_PATH = TRAIN_REPO_PATH / "ds_config.json"
ds_config = {
    "train_batch_size": "auto",
    "train_micro_batch_size_per_gpu": "auto",
    "gradient_accumulation_steps": "auto",
    "gradient_clipping": "auto",
    "zero_allow_untested_optimizer": True,
    "fp16": {
        "enabled": "auto",
        "loss_scale": 0,
        "loss_scale_window": 1000,
        "initial_scale_power": 16,
        "hysteresis": 2,
        "min_loss_scale": 1,
    },
    "bf16": {"enabled": "auto"},
    "zero_optimization": {
        "stage": 0,
        "allgather_partitions": True,
        "allgather_bucket_size": 5e8,
        "overlap_comm": True,
        "reduce_scatter": True,
        "reduce_bucket_size": 5e8,
        "contiguous_gradients": True,
        "round_robin_gradients": True,
    },
}

# -----------------------------------------------------------------------------

# sft

SFT_YAML = "qwen2_5vl_full_sft_train.yaml"

sft_config = {
    ### model
    "model_name_or_path": BASE_HF_MODEL,
    "image_max_pixels": 262144,
    "video_max_pixels": 16384,
    "trust_remote_code": True,
    ### method
    "stage": "sft",
    "do_train": True,
    "finetuning_type": "full",
    "freeze_vision_tower": False,
    "freeze_multi_modal_projector": False,
    "train_mm_proj_only": False,
    "deepspeed": str(DS_PATH),
    ### dataset
    "dataset": "sft",
    "template": "qwen2_vl",
    "cutoff_len": 32768,
    "max_samples": 1000,
    "overwrite_cache": True,
    "preprocessing_num_workers": 16,  # 16 = max
    ### output
    "output_dir": str(RUNS_VOL_PATH / SFT_MODEL),
    "logging_steps": 10,
    "save_steps": 500,
    "plot_loss": True,
    "overwrite_output_dir": True,
    "include_effective_tokens_per_second": True,
    ### train
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 1,
    "learning_rate": 1.0e-6,
    "max_steps": 100,
    "lr_scheduler_type": "cosine",
    "warmup_ratio": 0.1,
    "bf16": True,
    "ddp_timeout": 180000000,
    "weight_decay": 3e2,
    ### eval
    "val_size": 0.1,
    "per_device_eval_batch_size": 4,
    "eval_strategy": "steps",
    "eval_steps": 10,
    "report_to": "wandb",
    "run_name": SFT_MODEL,
}

# -----------------------------------------------------------------------------

# dpo

DPO_YAML = "qwen2_5vl_lora_dpo_train.yaml"
DPO_MERGE_YAML = "qwen2_5vl_lora_dpo_merge.yaml"

dpo_train_config = {
    ### model
    "model_name_or_path": SFT_HF_MODEL,
    "image_max_pixels": 262144,
    "video_max_pixels": 16384,
    "trust_remote_code": True,
    ### method
    "stage": "dpo",
    "do_train": True,
    "finetuning_type": "lora",
    "lora_rank": 8,
    "lora_target": "all",
    "pref_beta": 0.1,
    "pref_loss": "sigmoid",  # choices: [sigmoid (dpo), orpo, simpo]
    ### dataset
    "dataset": "dpo",
    "template": "qwen2_vl",
    "cutoff_len": 32768,
    "max_samples": 1000,
    "overwrite_cache": True,
    "preprocessing_num_workers": 16,  # 16 = max
    ### output
    "output_dir": str(RUNS_VOL_PATH / DPO_MODEL),
    "logging_steps": 10,
    "save_steps": 500,
    "plot_loss": True,
    "overwrite_output_dir": True,
    "include_effective_tokens_per_second": True,
    ### train
    "per_device_train_batch_size": 1,
    "gradient_accumulation_steps": 8,
    "learning_rate": 5.0e-6,
    "num_train_epochs": 60.0,
    "lr_scheduler_type": "cosine",
    "warmup_ratio": 0.1,
    "bf16": True,
    "ddp_timeout": 180000000,
    ### eval
    "val_size": 0.1,
    "per_device_eval_batch_size": 1,
    "eval_strategy": "steps",
    "eval_steps": 10,
    "report_to": "wandb",
    "run_name": DPO_MODEL,
}

dpo_merge_config = {
    ### model
    "model_name_or_path": SFT_HF_MODEL,
    "adapter_name_or_path": str(RUNS_VOL_PATH / DPO_MODEL),
    "template": "qwen2_vl",
    "finetuning_type": "lora",
    "trust_remote_code": True,
    ### export
    "export_dir": str(RUNS_VOL_PATH / DPO_MERGED),
    "export_size": 2,
    "export_device": "cpu",
    "export_legacy_format": False,
}  ## Note: DO NOT use quantized model or quantization_bit when merging lora adapters

# -----------------------------------------------------------------------------

# helpers

with GPU_IMAGE.imports():
    import torch
    import yaml
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration


def push_to_hub(local_dir: str, model_path: str):
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        local_dir,
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2",
        device_map="auto",
    )
    processor = AutoProcessor.from_pretrained(local_dir)
    model.push_to_hub(model_path)
    processor.push_to_hub(model_path)


# -----------------------------------------------------------------------------

# main


def main(sft: bool, dpo: bool):
    if not sft and not dpo:
        raise ValueError("Must specify at least one of `sft` or `dpo`")

    with open(TRAIN_REPO_PATH / "data/dataset_info.json", "w") as f:
        json.dump(dataset_info, f, indent=4)

    with open(DS_PATH, "w") as f:
        json.dump(ds_config, f, indent=4)

    if sft:
        with open(TRAIN_REPO_PATH / SFT_YAML, "w") as f:
            yaml.dump(sft_config, f)
        os.chdir(TRAIN_REPO_PATH)
        _exec_subprocess(
            [
                "cp",
                str(DATA_VOL_PATH / SFT_DATA),
                f"data/{SFT_DATA}",
            ]
        )
        _exec_subprocess(
            [
                "llamafactory-cli",
                "train",
                SFT_YAML,
            ]
        )
        checkpoint_folder = str(
            max(
                list((RUNS_VOL_PATH / SFT_MODEL).glob("checkpoint-*")),
                key=lambda x: int(x.name.split("-")[-1]),
            )
        )
        push_to_hub(checkpoint_folder, SFT_HF_MODEL)
    if dpo:
        with open(TRAIN_REPO_PATH / DPO_YAML, "w") as f:
            yaml.dump(dpo_train_config, f)

        with open(TRAIN_REPO_PATH / DPO_MERGE_YAML, "w") as f:
            yaml.dump(dpo_merge_config, f)
        os.chdir(TRAIN_REPO_PATH)
        _exec_subprocess(
            [
                "cp",
                str(DATA_VOL_PATH / DPO_DATA),
                f"data/{DPO_DATA}",
            ]
        )
        _exec_subprocess(
            [
                "llamafactory-cli",
                "train",
                DPO_YAML,
            ]
        )
        _exec_subprocess(
            [
                "llamafactory-cli",
                "export",
                DPO_MERGE_YAML,
            ]
        )
        push_to_hub(str(RUNS_VOL_PATH / DPO_MERGED), DPO_HF_MODEL)


@app.function(
    image=IMAGE,
    gpu=GPU_CONFIG,
    volumes=VOLUME_CONFIG,
    secrets=SECRETS,
    timeout=TIMEOUT,
)
def run(sft: bool, dpo: bool):
    main(sft, dpo)


@app.local_entrypoint()
def local(sft: bool = False, dpo: bool = False):
    run.remote(sft, dpo)
