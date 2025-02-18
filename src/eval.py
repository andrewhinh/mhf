import base64
import json
import os
from itertools import chain
from pathlib import Path

import modal
import numpy as np
import torch
import yaml
from huggingface_hub import login
from more_itertools import chunked
from pydantic import BaseModel
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import directed_hausdorff
from sklearn.metrics import auc, precision_recall_curve, roc_auc_score
from tqdm import tqdm
from vllm import LLM, SamplingParams
from vllm.sampling_params import GuidedDecodingParams

from utils import (
    APP_NAME,
    DATA_VOL_PATH,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_USER_PROMPT,
    GPU_IMAGE,
    MINUTES,
    SECRETS,
    SPLITS,
    VOLUME_CONFIG,
)

# -----------------------------------------------------------------------------

# vlm config
TOKENIZER = "Qwen/Qwen2.5-VL-3B-Instruct"
BASE_MODEL = "Qwen/Qwen2.5-VL-3B-Instruct"
# BASE_QUANT_MODEL = f"andrewhinh/{APP_NAME}-Qwen2.5-VL-3B-Instruct-AWQ"
# SFT_MODEL = f"andrewhinh/{APP_NAME}-qwen2.5-vl-3b-instruct-lora-sft-merged"
# SFT_QUANT_MODEL = f"andrewhinh/{APP_NAME}-qwen2.5-vl-3b-instruct-lora-sft-merged-awq"
# DPO_MODEL = f"andrewhinh/{APP_NAME}-qwen2.5-vl-3b-instruct-lora-dpo-merged"
# DPO_QUANT_MODEL = f"andrewhinh/{APP_NAME}-qwen2.5-vl-3b-instruct-lora-dpo-merged-awq"

KV_CACHE_DTYPE = None  # "fp8_e5m2"
ENFORCE_EAGER = False
MAX_NUM_SEQS = 32 if modal.is_local() else 128
MIN_PIXELS = 28 * 28
MAX_PIXELS = 1280 * 28 * 28
TEMPERATURE = 0.1
TOP_P = 0.001
REPEATION_PENALTY = 1.1
STOP_TOKEN_IDS = []
MAX_MODEL_LEN = 8192 if modal.is_local() else 32768
MAX_TOKENS = 4096


# -----------------------------------------------------------------------------


# output schema
class Point(BaseModel):
    x: float
    y: float


class Substructure(BaseModel):
    name: str
    points: list[Point]


class Substructures(BaseModel):
    substructures: list[Substructure]


JSON_STRUCTURE = Substructures.model_json_schema()


## container startup fn
def download_models():
    from huggingface_hub import snapshot_download

    login(token=os.getenv("HF_TOKEN"), new_session=False)

    for model in [
        TOKENIZER,
        BASE_MODEL,
        # BASE_QUANT_MODEL,
        # SFT_MODEL,
        # SFT_QUANT_MODEL,
        # DPO_MODEL,
        # DPO_QUANT_MODEL,
    ]:
        if not os.path.exists(model):
            snapshot_download(
                model,
                ignore_patterns=["*.pt", "*.bin"],
            )
        else:  # check if preprocessor_config.json was successfully copied; if not, do so
            if not os.path.exists(f"{model}/preprocessor_config.json"):
                tok_path = snapshot_download(
                    model,
                    ignore_patterns=["*.pt", "*.bin"],
                )
                os.rename(
                    f"{tok_path}/preprocessor_config.json",
                    f"{model}/preprocessor_config.json",
                )


# Modal
IMAGE = GPU_IMAGE.run_function(
    download_models,
    secrets=SECRETS,
    volumes=VOLUME_CONFIG,
)
TIMEOUT = 24 * 60 * MINUTES

if modal.is_local():
    GPU_COUNT = torch.cuda.device_count()
else:
    GPU_COUNT = 1

GPU_TYPE = "l40s"
GPU_SIZE = None  # options = None, "40GB", "80GB"
GPU_CONFIG = f"{GPU_TYPE}:{GPU_COUNT}"

app = modal.App(name=f"{APP_NAME}-eval")

# -----------------------------------------------------------------------------


# helpers
def point_level_metrics(gts, preds, threshold=20.0):
    """
    1) Uses Hungarian algorithm (linear_sum_assignment) to find a minimal-cost matching
       between ground-truth (gts) and predicted points (preds).
    2) If the distance of a matched pair > threshold, that match is considered invalid
       => effectively FP + FN instead of TP.
    3) Returns a dict with total TP, FP, FN, distances, plus a 'y_true_list' and 'score_list'
       for computing a global AUC-ROC/AUC-PR across all samples.
    """
    n, m = len(gts), len(preds)
    cost_matrix = np.zeros((n, m))
    # Hungarian assignment: each GT i is matched to exactly one Pred j if possible
    for i in range(n):
        for j in range(m):
            cost_matrix[i, j] = np.linalg.norm(np.array(gts[i]) - np.array(preds[j]))
    gt_indices, pred_indices = linear_sum_assignment(cost_matrix)
    matched_distances = cost_matrix[gt_indices, pred_indices]
    num_matched = len(gt_indices)

    # matched pair is a "true positive" if distance <= threshold,
    # otherwise it's effectively invalid => that GT is still unfilled, that Pred is spurious.
    tp = 0
    fp = 0
    fn = 0
    for dist in matched_distances:
        if dist <= threshold:
            tp += 1
        else:
            fp += 1
            fn += 1
    fp += m - num_matched  # unmatched predictions => FP
    fn += n - num_matched  # unmatched GT => FN

    # build y_true / score arrays for computing AUC per sample
    # - matched (distance <= threshold) => y_true=1; else 0
    # - score = -distance so smaller distance => higher "confidence"
    # For the unmatched predictions, we mark them as y_true=0, very negative score
    y_true_list = []
    score_list = []
    for dist in matched_distances:
        y_true_list.append(1 if dist <= threshold else 0)
        score_list.append(-dist)
    unmatched_fp = m - num_matched  # already added to fp
    for _ in range(unmatched_fp):
        y_true_list.append(0)
        score_list.append(-9999.0)

    hausdorff = 0.0
    euclid_sum = 0.0
    if num_matched > 0:
        hausdorff = max(
            directed_hausdorff(gts, preds)[0], directed_hausdorff(preds, gts)[0]
        )
        euclid_sum = float(np.sum(matched_distances))

    return {
        "hausdorff_distance": hausdorff,
        "euclidean_distance": euclid_sum,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        # For global AUC
        "y_true_list": y_true_list,
        "score_list": score_list,
    }


def label_and_point_metrics(
    gt_list, pred_list
):  # [{label: points for label in gt}, {label: points for label in pred}]
    """
    Processes a list of samples:
      gt_list[i] = {label: [[x0,y0], [x1,y1], ...], ...}
      pred_list[i] = {label: [[x0,y0], [x1,y1], ...], ...}

    Returns an array of sample-level dictionaries, each containing:
      - tp, fp, fn for label presence/absence (did we predict label X at all?)
      - "point_metrics": list of dictionaries with
         { label: str, tp, fp, fn, distances, y_true_list, score_list, ... }
         on a per-label basis (point-level).
    """
    all_metrics = []
    for gt_labels, pred_labels in zip(
        gt_list, pred_list
    ):  # {label: points for label in gt}, {label: points for label in pred}
        gt_ids, pred_ids = set(gt_labels.keys()), set(pred_labels.keys())
        matched_ids = gt_ids & pred_ids
        false_negative_labels = gt_ids - pred_ids
        false_positive_labels = pred_ids - gt_ids
        metrics = {
            "tp": len(matched_ids),
            "fp": len(false_positive_labels),
            "fn": len(false_negative_labels),
            "point_metrics": [],
        }
        for label in matched_ids:
            gt_points = gt_labels[label]  # [[x0, y0], [x1, y1], ...]
            pred_points = pred_labels[label]  # [[x0, y0], [x1, y1], ...]
            if len(gt_points) > 0 and len(pred_points) > 0:
                metrics["point_metrics"].append(
                    {
                        "label": label,
                        **point_level_metrics(gt_points, pred_points),
                    }
                )
        all_metrics.append(metrics)
    return all_metrics


def summarize(lbl_pt_metrics):
    """
    Aggregates:
      1) Label-level metrics from total label tp/fp/fn
      2) Point-level metrics from sum of point-level tp,fp,fn, distances
      3) *Global AUC* per label by combining all (y_true, score) across samples
    """
    # Label-level sums
    tp_labels = 0
    fp_labels = 0
    fn_labels = 0

    # Per-label aggregator for point-level metrics
    # label -> aggregated PointMetric
    label_metrics_map = {}
    label_ytrue_scores = {}  # label -> (list_of_y_true, list_of_scores)
    for metric in lbl_pt_metrics:
        tp_labels += metric["tp"]
        fp_labels += metric["fp"]
        fn_labels += metric["fn"]

        for pm_dict in metric["point_metrics"]:
            label = pm_dict["label"]
            if label not in label_metrics_map:
                label_metrics_map[label] = {
                    "hausdorff_distance": 0.0,
                    "euclidean_distance": 0.0,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0,
                }
                label_ytrue_scores[label] = ([], [])

            label_metrics_map[label]["hausdorff_distance"] += pm_dict[
                "hausdorff_distance"
            ]
            label_metrics_map[label]["euclidean_distance"] += pm_dict[
                "euclidean_distance"
            ]
            label_metrics_map[label]["tp"] += pm_dict["tp"]
            label_metrics_map[label]["fp"] += pm_dict["fp"]
            label_metrics_map[label]["fn"] += pm_dict["fn"]
            y_true_acc, score_acc = label_ytrue_scores[label]
            y_true_acc.extend(pm_dict["y_true_list"])
            score_acc.extend(pm_dict["score_list"])

    # label-level metrics from the aggregated counts
    label_precision = 0.0
    label_recall = 0.0
    label_f1 = 0.0

    if (tp_labels + fp_labels) > 0:
        label_precision = tp_labels / (tp_labels + fp_labels)
    if (tp_labels + fn_labels) > 0:
        label_recall = tp_labels / (tp_labels + fn_labels)
    if (label_precision + label_recall) > 0:
        label_f1 = 2 * label_precision * label_recall / (label_precision + label_recall)

    # point-level metrics from the aggregated counts
    point_metrics_dict = {}
    for label, agg_dict in label_metrics_map.items():
        # Recompute precision/recall/f1 from aggregated tp/fp/fn
        ttp = agg_dict["tp"]
        tfp = agg_dict["fp"]
        tfn = agg_dict["fn"]

        precision = 0.0
        recall = 0.0
        f1_val = 0.0
        if (ttp + tfp) > 0:
            precision = ttp / (ttp + tfp)
        if (ttp + tfn) > 0:
            recall = ttp / (ttp + tfn)
        if (precision + recall) > 0:
            f1_val = 2 * precision * recall / (precision + recall)

        y_true_list, score_list = label_ytrue_scores[label]
        auc_roc_val = 0.0
        auc_pr_val = 0.0
        # Check if there's at least 1 positive and 1 negative
        if 1 in y_true_list and 0 in y_true_list:
            try:
                auc_roc_val = roc_auc_score(y_true_list, score_list)
            except ValueError:
                auc_roc_val = 0.0
            try:
                precs, recs, _ = precision_recall_curve(y_true_list, score_list)
                auc_pr_val = auc(recs, precs)
            except ValueError:
                auc_pr_val = 0.0

        point_metrics_dict[label] = {
            "hausdorff_distance": round(agg_dict["hausdorff_distance"], 2),
            "euclidean_distance": round(agg_dict["euclidean_distance"], 2),
            "tp": ttp,
            "fp": tfp,
            "fn": tfn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1_val, 3),
            "auc_roc": round(auc_roc_val, 3),
            "auc_pr": round(auc_pr_val, 3),
        }

    return {
        "label_metrics": {
            "precision": round(label_precision, 2),
            "recall": round(label_recall, 2),
            "f1": round(label_f1, 2),
        },
        "point_metrics": point_metrics_dict,
    }


@app.function(
    image=IMAGE,
    gpu=GPU_CONFIG,
    volumes=VOLUME_CONFIG,
    secrets=SECRETS,
    timeout=TIMEOUT,
)
def run_model(img_paths: list[Path], model: str, quant: bool) -> list[dict]:
    conversations = []
    for img_path in img_paths:
        with open(img_path, "rb") as image_file:
            base64_img = base64.b64encode(image_file.read()).decode("utf-8")
        img_url = f"data:image/jpeg;base64,{base64_img}"
        conversations.append(
            [
                {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": DEFAULT_USER_PROMPT},
                        {"type": "image_url", "image_url": {"url": img_url}},
                    ],
                },
            ]
        )

    global quantization
    global llm
    global sampling_params
    # load pretrained vlm if not already loaded
    if "quantization" not in globals():
        quantization = "awq_marlin" if quant else None
    if "llm" not in globals():
        llm = LLM(
            model=model,
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
                    ("quantization", quantization),
                    ("kv_cache_dtype", KV_CACHE_DTYPE),
                ]
                if v is not None
            },
        )
    if "sampling_params" not in globals():
        sampling_params = SamplingParams(
            temperature=TEMPERATURE,
            top_p=TOP_P,
            repetition_penalty=REPEATION_PENALTY,
            stop_token_ids=STOP_TOKEN_IDS,
            max_tokens=MAX_TOKENS,
            guided_decoding=GuidedDecodingParams(json=JSON_STRUCTURE),
        )
    outputs = llm.chat(conversations, sampling_params, use_tqdm=True)
    preds = [out.outputs[0].text.strip() for out in outputs]
    for pred in preds:
        try:
            json.loads(pred)
        except Exception:
            print(pred)
    preds = [json.loads(pred)["substructures"] for pred in preds]
    return preds


# -----------------------------------------------------------------------------

# main


def main(base: bool, sft: bool, dpo: bool, quant: bool):
    if not base and not sft and not dpo:
        raise ValueError("Must specify at least one of `base`, `sft`, or `dpo`)")

    split_metrics = {}
    for split in SPLITS:
        with open(DATA_VOL_PATH / f"sft_{split}.json", "r") as f:
            read_ds = yaml.safe_load(f)
        img_paths = [sample["images"][0] for sample in read_ds]
        labels = [json.loads(sample["conversations"][1]["value"]) for sample in read_ds]

        ## run
        img_batches = list(chunked(img_paths, MAX_NUM_SEQS))
        model = (
            BASE_MODEL
            if base and not quant
            # else SFT_MODEL
            # if sft and not quant
            # else DPO_MODEL
            # if dpo and not quant
            # else BASE_QUANT_MODEL
            # if base and quant
            # else SFT_QUANT_MODEL
            # if sft and quant
            # else DPO_QUANT_MODEL
            # if dpo and quant
            else None
        )
        if modal.is_local():
            preds = list(
                tqdm(
                    chain.from_iterable(
                        run_model.local(batch, model, quant) for batch in img_batches
                    ),
                    desc=split,
                    total=len(img_batches),
                )
            )
        else:
            lst_preds = run_model.starmap(
                [(batch, model, quant) for batch in img_batches]
            )
            preds = [item for lst in lst_preds for item in lst]

        preds = [
            {
                substructure["name"]: [
                    [point["x"], point["y"]] for point in substructure["points"]
                ]
                for substructure in pred
            }
            for pred in preds
        ]

        split_metrics[split] = label_and_point_metrics(labels, preds)

    for split, metrics in split_metrics.items():
        print(summarize(metrics))


@app.function(
    image=IMAGE,
    gpu=GPU_CONFIG,
    volumes=VOLUME_CONFIG,
    secrets=SECRETS,
    timeout=TIMEOUT,
)
def run(base: bool, sft: bool, dpo: bool, quant: bool):
    main(base, sft, dpo, quant)


@app.local_entrypoint()
def local(
    base: bool = False, sft: bool = False, dpo: bool = False, quant: bool = False
):
    run.remote(base, sft, dpo, quant)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--base", action="store_true")
    parser.add_argument("--sft", action="store_true")
    parser.add_argument("--dpo", action="store_true")
    parser.add_argument("--quant", action="store_true")
    args = parser.parse_args()
    main(args.base, args.sft, args.dpo, args.quant)
