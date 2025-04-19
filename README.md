# mhf

MHF Automated Labelling

An automated ultrasound substructure localization system utilizing a fine-tuned Qwen2.5-VL-3B-Instruct that reduces Hausdorff distance by 57.65% and Euclidean distance by 31.72% compared to the base model. ETL, evaluation, and model quantization/training alongside an API and website completed and served for under $2.

## helpful links

- [Web app](https://bit.ly/mhf-winter-2025)
- [Huggingface models](https://huggingface.co/andrewhinh)
- [Weights and Biases runs](https://wandb.ai/andrewhinh/mhf?nw=nwuserandrewhinh)

## setup

Run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --all-extras --dev
uv pip install git+https://github.com/seungwoos/AutoAWQ.git@add-qwen2_5_vl --no-deps --no-build-isolation
uv run pre-commit install
git clone https://github.com/Len-Stevens/Python-Antivirus.git
modal setup
modal config set-environment dev
echo "alias modal='uv run modal'" >> ~/.bashrc
echo "export PYTHONPATH=.:$PYTHONPATH" >> ~/.bashrc
echo "export TOKENIZERS_PARALLELISM=false" >> ~/.bashrc
echo "export HF_HUB_ENABLE_HF_TRANSFER=1" >> ~/.bashrc
source ~/.bashrc
```

Create a `.env` (+ `.env.dev`):

```bash
HF_TOKEN=
WANDB_API_KEY=
WANDB_PROJECT=
WANDB_ENTITY=
API_URL=
```

## repo structure

```bash
.
├── artifacts           # data + runs.
├── src                 # src.
│   ├── api.py          # api.
│   ├── app.py          # website.
│   ├── eda.ipynb       # eda.
│   ├── etl.py          # etl.
│   ├── eval.py         # eval.
│   ├── load_test.py    # load testing.
│   ├── locustfile.py   # locust user defn.
│   ├── quantize.py     # quantize.
│   └── utils.py        # utils.
```

## usage

Test the API:

```bash
modal run src/api.py
```

Serve the API:

```bash
uv run src/api.py
```

or

```bash
modal serve src/api.py
```

Deploy the API:

```bash
modal deploy --env=main src/api.py
```

Test the latency and throughput of the API:

```bash
modal run src/load_test.py
```

Serve the website:

```bash
uv run src/app.py
```

or

```bash
modal serve src/app.py
```

Deploy the website:

```bash
modal deploy --env=main src/app.py
```

## training

Download data:

```bash
uv run src/etl.py --sft
```

or

```bash
modal run src/etl.py --sft
```

Eval base model:

```bash
uv run src/eval.py --base
```

or

```bash
modal run src/eval.py --base
```

Quantize base model:

```bash
uv run src/quantize.py --base
```

or

```bash
modal run src/quantize.py --base
```

Eval quantized base model:

```bash
uv run src/eval.py --base --quant
```

or

```bash
modal run src/eval.py --base --quant
```

Run SFT:

```bash
modal run src/train.py --sft
```

Eval SFT model:

```bash
uv run src/eval.py --sft
```

or

```bash
modal run src/eval.py --sft
```

Quantize the SFT model:

```bash
uv run src/quantize.py --sft
```

or

```bash
modal run src/quantize.py --sft
```

Eval quantized SFT model:

```bash
uv run src/eval.py --sft --quant
```

or

```bash
modal run src/eval.py --sft --quant
```

## future plans

Run trained VLM on train data and construct new dataset with only relabelled incorrect examples:

```bash
uv run src/etl.py --dpo
```

or

```bash
modal run src/etl.py --dpo
```

Run DPO:

```bash
modal run src/train.py --dpo
```

Eval DPO model:

```bash
uv run src/eval.py --dpo
```

or

```bash
modal run src/eval.py --dpo
```

Quantize the DPO model:

```bash
uv run src/quantize.py --dpo
```

or

```bash
modal run src/quantize.py --dpo
```

Eval quantized DPO model:

```bash
uv run src/eval.py --dpo --quant
```

or

```bash
modal run src/eval.py --dpo --quant
```

## results

### All substructures

Baseline prompt with EDA info:

```bash
train:
  label_metrics:
    precision: 1.0
    recall: 1.0
    f1: 1.0
  point_metrics:
    calota:
      hausdorff_distance: 22965.67
      euclidean_distance: 62339.63
      tp: 6
      fp: 392
      fn: 327
      precision: 0.015
      recall: 0.018
      f1: 0.016
      auc_roc: 1.0
      auc_pr: 1.0
    linia mitja:
      hausdorff_distance: 22100.31
      euclidean_distance: 25520.88
      tp: 2
      fp: 390
      fn: 164
      precision: 0.005
      recall: 0.012
      f1: 0.007
      auc_roc: 1.0
      auc_pr: 1.0
    cavum:
      hausdorff_distance: 18862.54
      euclidean_distance: 49474.65
      tp: 4
      fp: 394
      fn: 329
      precision: 0.01
      recall: 0.012
      f1: 0.011
      auc_roc: 1.0
      auc_pr: 1.0
    cerebel:
      hausdorff_distance: 20464.17
      euclidean_distance: 61998.21
      tp: 25
      fp: 431
      fn: 636
      precision: 0.055
      recall: 0.038
      f1: 0.045
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 17418.43
      euclidean_distance: 29991.32
      tp: 10
      fp: 384
      fn: 244
      precision: 0.025
      recall: 0.039
      f1: 0.031
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 24028.31
      euclidean_distance: 51882.73
      tp: 0
      fp: 392
      fn: 249
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    astes anteriors:
      hausdorff_distance: 22219.08
      euclidean_distance: 24442.36
      tp: 0
      fp: 393
      fn: 164
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
val:
  label_metrics:
    precision: 1.0
    recall: 0.99
    f1: 0.99
  point_metrics:
    calota:
      hausdorff_distance: 2745.82
      euclidean_distance: 7391.43
      tp: 2
      fp: 46
      fn: 40
      precision: 0.042
      recall: 0.048
      f1: 0.044
      auc_roc: 1.0
      auc_pr: 1.0
    linia mitja:
      hausdorff_distance: 2689.81
      euclidean_distance: 3357.93
      tp: 0
      fp: 49
      fn: 20
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cavum:
      hausdorff_distance: 2207.66
      euclidean_distance: 5920.44
      tp: 0
      fp: 49
      fn: 40
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cerebel:
      hausdorff_distance: 2365.12
      euclidean_distance: 8707.97
      tp: 2
      fp: 49
      fn: 78
      precision: 0.039
      recall: 0.025
      f1: 0.031
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 2112.69
      euclidean_distance: 4249.38
      tp: 1
      fp: 48
      fn: 31
      precision: 0.02
      recall: 0.031
      f1: 0.025
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 2762.54
      euclidean_distance: 5973.73
      tp: 0
      fp: 48
      fn: 30
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    astes anteriors:
      hausdorff_distance: 2633.82
      euclidean_distance: 3006.68
      tp: 0
      fp: 48
      fn: 20
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
test:
  label_metrics:
    precision: 1.0
    recall: 1.0
    f1: 1.0
  point_metrics:
    calota:
      hausdorff_distance: 3351.69
      euclidean_distance: 7946.43
      tp: 1
      fp: 62
      fn: 43
      precision: 0.016
      recall: 0.023
      f1: 0.019
      auc_roc: 1.0
      auc_pr: 1.0
    linia mitja:
      hausdorff_distance: 3166.11
      euclidean_distance: 3712.88
      tp: 0
      fp: 61
      fn: 22
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cavum:
      hausdorff_distance: 2798.88
      euclidean_distance: 6982.81
      tp: 0
      fp: 64
      fn: 44
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cerebel:
      hausdorff_distance: 2915.65
      euclidean_distance: 9029.97
      tp: 1
      fp: 69
      fn: 87
      precision: 0.014
      recall: 0.011
      f1: 0.013
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 2358.98
      euclidean_distance: 4207.55
      tp: 2
      fp: 60
      fn: 31
      precision: 0.032
      recall: 0.061
      f1: 0.042
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 3201.25
      euclidean_distance: 7328.32
      tp: 0
      fp: 61
      fn: 33
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    astes anteriors:
      hausdorff_distance: 3244.97
      euclidean_distance: 3708.49
      tp: 0
      fp: 62
      fn: 22
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
```

Baseline prompt with EDA info (7B):

```bash
train:
  label_metrics:
    precision: 1.0
    recall: 1.0
    f1: 1.0
  point_metrics:
    astes anteriors:
      hausdorff_distance: 16071.07
      euclidean_distance: 26622.66
      tp: 6
      fp: 214
      fn: 158
      precision: 0.027
      recall: 0.037
      f1: 0.031
      auc_roc: 1.0
      auc_pr: 1.0
    cavum:
      hausdorff_distance: 13117.6
      euclidean_distance: 41645.36
      tp: 10
      fp: 336
      fn: 323
      precision: 0.029
      recall: 0.03
      f1: 0.029
      auc_roc: 1.0
      auc_pr: 1.0
    calota:
      hausdorff_distance: 25103.81
      euclidean_distance: 66878.54
      tp: 13
      fp: 319
      fn: 320
      precision: 0.039
      recall: 0.039
      f1: 0.039
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 11874.31
      euclidean_distance: 28102.76
      tp: 17
      fp: 275
      fn: 237
      precision: 0.058
      recall: 0.067
      f1: 0.062
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 17494.8
      euclidean_distance: 49032.12
      tp: 0
      fp: 250
      fn: 249
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    linia mitja:
      hausdorff_distance: 17016.54
      euclidean_distance: 32535.82
      tp: 1
      fp: 165
      fn: 165
      precision: 0.006
      recall: 0.006
      f1: 0.006
      auc_roc: 1.0
      auc_pr: 1.0
    cerebel:
      hausdorff_distance: 19344.85
      euclidean_distance: 83555.97
      tp: 34
      fp: 478
      fn: 627
      precision: 0.066
      recall: 0.051
      f1: 0.058
      auc_roc: 1.0
      auc_pr: 1.0
val:
  label_metrics:
    precision: 1.0
    recall: 0.99
    f1: 0.99
  point_metrics:
    astes anteriors:
      hausdorff_distance: 2336.19
      euclidean_distance: 3529.08
      tp: 0
      fp: 31
      fn: 20
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cavum:
      hausdorff_distance: 1646.56
      euclidean_distance: 4821.2
      tp: 0
      fp: 45
      fn: 40
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    calota:
      hausdorff_distance: 2722.35
      euclidean_distance: 7275.52
      tp: 0
      fp: 40
      fn: 40
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    talems:
      hausdorff_distance: 1887.86
      euclidean_distance: 4361.25
      tp: 2
      fp: 36
      fn: 30
      precision: 0.053
      recall: 0.062
      f1: 0.057
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 2262.52
      euclidean_distance: 6152.66
      tp: 0
      fp: 31
      fn: 30
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    linia mitja:
      hausdorff_distance: 2527.07
      euclidean_distance: 4688.1
      tp: 0
      fp: 22
      fn: 20
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cerebel:
      hausdorff_distance: 2838.5
      euclidean_distance: 11192.18
      tp: 1
      fp: 84
      fn: 79
      precision: 0.012
      recall: 0.013
      f1: 0.012
      auc_roc: 1.0
      auc_pr: 1.0
test:
  label_metrics:
    precision: 1.0
    recall: 0.99
    f1: 0.99
  point_metrics:
    astes anteriors:
      hausdorff_distance: 2096.78
      euclidean_distance: 3590.14
      tp: 0
      fp: 30
      fn: 22
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cavum:
      hausdorff_distance: 1929.17
      euclidean_distance: 6501.95
      tp: 0
      fp: 45
      fn: 44
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    calota:
      hausdorff_distance: 3341.31
      euclidean_distance: 8846.23
      tp: 1
      fp: 43
      fn: 45
      precision: 0.023
      recall: 0.022
      f1: 0.022
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 1996.23
      euclidean_distance: 4963.39
      tp: 3
      fp: 35
      fn: 30
      precision: 0.079
      recall: 0.091
      f1: 0.085
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 2396.6
      euclidean_distance: 6781.42
      tp: 1
      fp: 32
      fn: 32
      precision: 0.03
      recall: 0.03
      f1: 0.03
      auc_roc: 1.0
      auc_pr: 1.0
    linia mitja:
      hausdorff_distance: 2625.77
      euclidean_distance: 5004.67
      tp: 0
      fp: 23
      fn: 22
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cerebel:
      hausdorff_distance: 3202.71
      euclidean_distance: 15544.2
      tp: 0
      fp: 66
      fn: 88
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
```

Baseline prompt with EDA info, quantized:

```bash
train:
  label_metrics:
    precision: 1.0
    recall: 0.95
    f1: 0.97
  point_metrics:
    cavum:
      hausdorff_distance: 18779.22
      euclidean_distance: 48492.51
      tp: 4
      fp: 312
      fn: 329
      precision: 0.013
      recall: 0.012
      f1: 0.012
      auc_roc: 1.0
      auc_pr: 1.0
    calota:
      hausdorff_distance: 23339.68
      euclidean_distance: 54512.15
      tp: 11
      fp: 319
      fn: 322
      precision: 0.033
      recall: 0.033
      f1: 0.033
      auc_roc: 1.0
      auc_pr: 1.0
    cerebel:
      hausdorff_distance: 18925.81
      euclidean_distance: 43038.32
      tp: 19
      fp: 257
      fn: 594
      precision: 0.069
      recall: 0.031
      f1: 0.043
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 22076.6
      euclidean_distance: 52506.46
      tp: 0
      fp: 280
      fn: 234
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    talems:
      hausdorff_distance: 16500.37
      euclidean_distance: 32975.16
      tp: 2
      fp: 274
      fn: 233
      precision: 0.007
      recall: 0.009
      f1: 0.008
      auc_roc: 1.0
      auc_pr: 1.0
    astes anteriors:
      hausdorff_distance: 20481.47
      euclidean_distance: 21988.55
      tp: 2
      fp: 271
      fn: 150
      precision: 0.007
      recall: 0.013
      f1: 0.009
      auc_roc: 1.0
      auc_pr: 1.0
    linia mitja:
      hausdorff_distance: 20745.85
      euclidean_distance: 23486.82
      tp: 4
      fp: 272
      fn: 150
      precision: 0.014
      recall: 0.026
      f1: 0.019
      auc_roc: 1.0
      auc_pr: 1.0
val:
  label_metrics:
    precision: 1.0
    recall: 0.92
    f1: 0.96
  point_metrics:
    cavum:
      hausdorff_distance: 1835.9
      euclidean_distance: 4906.27
      tp: 0
      fp: 35
      fn: 40
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    calota:
      hausdorff_distance: 2561.06
      euclidean_distance: 5338.61
      tp: 1
      fp: 36
      fn: 39
      precision: 0.027
      recall: 0.025
      f1: 0.026
      auc_roc: 1.0
      auc_pr: 1.0
    cerebel:
      hausdorff_distance: 2010.75
      euclidean_distance: 4558.72
      tp: 0
      fp: 34
      fn: 72
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    silvio:
      hausdorff_distance: 2238.71
      euclidean_distance: 5679.35
      tp: 0
      fp: 34
      fn: 27
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    talems:
      hausdorff_distance: 1779.12
      euclidean_distance: 3350.6
      tp: 1
      fp: 33
      fn: 28
      precision: 0.029
      recall: 0.034
      f1: 0.032
      auc_roc: 1.0
      auc_pr: 1.0
    astes anteriors:
      hausdorff_distance: 2065.22
      euclidean_distance: 2526.78
      tp: 0
      fp: 34
      fn: 18
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    linia mitja:
      hausdorff_distance: 2025.39
      euclidean_distance: 2521.95
      tp: 0
      fp: 34
      fn: 18
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
test:
  label_metrics:
    precision: 1.0
    recall: 0.94
    f1: 0.97
  point_metrics:
    cavum:
      hausdorff_distance: 2693.98
      euclidean_distance: 7984.58
      tp: 0
      fp: 44
      fn: 44
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    calota:
      hausdorff_distance: 3510.88
      euclidean_distance: 8306.04
      tp: 0
      fp: 46
      fn: 46
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cerebel:
      hausdorff_distance: 2549.62
      euclidean_distance: 7361.08
      tp: 2
      fp: 38
      fn: 78
      precision: 0.05
      recall: 0.025
      f1: 0.033
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 3170.36
      euclidean_distance: 7801.17
      tp: 0
      fp: 40
      fn: 30
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    talems:
      hausdorff_distance: 2337.37
      euclidean_distance: 5179.98
      tp: 0
      fp: 40
      fn: 30
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    astes anteriors:
      hausdorff_distance: 2929.98
      euclidean_distance: 3392.89
      tp: 0
      fp: 40
      fn: 20
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    linia mitja:
      hausdorff_distance: 2832.44
      euclidean_distance: 3502.27
      tp: 1
      fp: 39
      fn: 19
      precision: 0.025
      recall: 0.05
      f1: 0.033
      auc_roc: 1.0
      auc_pr: 1.0
```

SFT:

- [Unrefined run](https://wandb.ai/andrewhinh/mhf/runs/5v83pidh?nw=nwuserandrewhinh)
- [Refined run](https://wandb.ai/andrewhinh/mhf/runs/4wmqs9hc?nw=nwuserandrewhinh)

Baseline prompt with EDA info, SFT:

```bash
train:
  label_metrics:
    precision: 1.0
    recall: 0.99
    f1: 1.0
  point_metrics:
    cerebel:
      hausdorff_distance: 18408.22
      euclidean_distance: 129879.73
      tp: 4
      fp: 660
      fn: 657
      precision: 0.006
      recall: 0.006
      f1: 0.006
      auc_roc: 1.0
      auc_pr: 1.0
    linia mitja:
      hausdorff_distance: 13456.71
      euclidean_distance: 25636.71
      tp: 0
      fp: 164
      fn: 164
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cavum:
      hausdorff_distance: 9540.57
      euclidean_distance: 35175.12
      tp: 6
      fp: 318
      fn: 323
      precision: 0.019
      recall: 0.018
      f1: 0.018
      auc_roc: 1.0
      auc_pr: 1.0
    calota:
      hausdorff_distance: 12606.27
      euclidean_distance: 30002.15
      tp: 20
      fp: 312
      fn: 313
      precision: 0.06
      recall: 0.06
      f1: 0.06
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 8410.47
      euclidean_distance: 23053.61
      tp: 8
      fp: 241
      fn: 246
      precision: 0.032
      recall: 0.031
      f1: 0.032
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 9195.4
      euclidean_distance: 24373.25
      tp: 13
      fp: 233
      fn: 233
      precision: 0.053
      recall: 0.053
      f1: 0.053
      auc_roc: 1.0
      auc_pr: 1.0
    astes anteriors:
      hausdorff_distance: 13184.08
      euclidean_distance: 23849.96
      tp: 1
      fp: 161
      fn: 161
      precision: 0.006
      recall: 0.006
      f1: 0.006
      auc_roc: 1.0
      auc_pr: 1.0
val:
  label_metrics:
    precision: 1.0
    recall: 0.99
    f1: 0.99
  point_metrics:
    cerebel:
      hausdorff_distance: 2234.61
      euclidean_distance: 15170.35
      tp: 1
      fp: 79
      fn: 79
      precision: 0.013
      recall: 0.013
      f1: 0.013
      auc_roc: 1.0
      auc_pr: 1.0
    linia mitja:
      hausdorff_distance: 1530.28
      euclidean_distance: 2874.74
      tp: 0
      fp: 20
      fn: 20
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cavum:
      hausdorff_distance: 1200.13
      euclidean_distance: 4376.51
      tp: 0
      fp: 40
      fn: 40
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    calota:
      hausdorff_distance: 1341.79
      euclidean_distance: 3364.83
      tp: 3
      fp: 37
      fn: 37
      precision: 0.075
      recall: 0.075
      f1: 0.075
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 1053.77
      euclidean_distance: 2482.67
      tp: 3
      fp: 27
      fn: 29
      precision: 0.1
      recall: 0.094
      f1: 0.097
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 1126.25
      euclidean_distance: 3010.33
      tp: 0
      fp: 30
      fn: 30
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    astes anteriors:
      hausdorff_distance: 1425.34
      euclidean_distance: 2531.93
      tp: 0
      fp: 20
      fn: 20
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
test:
  label_metrics:
    precision: 1.0
    recall: 1.0
    f1: 1.0
  point_metrics:
    cerebel:
      hausdorff_distance: 2375.49
      euclidean_distance: 16930.09
      tp: 0
      fp: 88
      fn: 88
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    linia mitja:
      hausdorff_distance: 1736.73
      euclidean_distance: 3379.4
      tp: 0
      fp: 22
      fn: 22
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cavum:
      hausdorff_distance: 1312.6
      euclidean_distance: 4892.99
      tp: 0
      fp: 44
      fn: 44
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    calota:
      hausdorff_distance: 1669.7
      euclidean_distance: 3981.02
      tp: 1
      fp: 43
      fn: 45
      precision: 0.023
      recall: 0.022
      f1: 0.022
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 1018.82
      euclidean_distance: 2723.72
      tp: 4
      fp: 29
      fn: 29
      precision: 0.121
      recall: 0.121
      f1: 0.121
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 1354.83
      euclidean_distance: 3668.67
      tp: 3
      fp: 30
      fn: 30
      precision: 0.091
      recall: 0.091
      f1: 0.091
      auc_roc: 1.0
      auc_pr: 1.0
    astes anteriors:
      hausdorff_distance: 1861.37
      euclidean_distance: 3438.65
      tp: 0
      fp: 22
      fn: 22
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
```

Baseline prompt with EDA info, SFT + quantized:

```bash
train:
  label_metrics:
    precision: 1.0
    recall: 0.9
    f1: 0.95
  point_metrics:
    silvio:
      hausdorff_distance: 7053.68
      euclidean_distance: 18423.57
      tp: 14
      fp: 193
      fn: 193
      precision: 0.068
      recall: 0.068
      f1: 0.068
      auc_roc: 1.0
      auc_pr: 1.0
    astes anteriors:
      hausdorff_distance: 11987.38
      euclidean_distance: 21158.84
      tp: 3
      fp: 136
      fn: 133
      precision: 0.022
      recall: 0.022
      f1: 0.022
      auc_roc: 1.0
      auc_pr: 1.0
    calota:
      hausdorff_distance: 15510.83
      euclidean_distance: 41979.94
      tp: 9
      fp: 323
      fn: 324
      precision: 0.027
      recall: 0.027
      f1: 0.027
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 11511.76
      euclidean_distance: 33140.62
      tp: 0
      fp: 249
      fn: 254
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cavum:
      hausdorff_distance: 9469.12
      euclidean_distance: 35015.07
      tp: 2
      fp: 274
      fn: 274
      precision: 0.007
      recall: 0.007
      f1: 0.007
      auc_roc: 1.0
      auc_pr: 1.0
    linia mitja:
      hausdorff_distance: 12319.31
      euclidean_distance: 23669.79
      tp: 2
      fp: 137
      fn: 136
      precision: 0.014
      recall: 0.014
      f1: 0.014
      auc_roc: 1.0
      auc_pr: 1.0
    cerebel:
      hausdorff_distance: 19282.45
      euclidean_distance: 129890.2
      tp: 7
      fp: 651
      fn: 654
      precision: 0.011
      recall: 0.011
      f1: 0.011
      auc_roc: 1.0
      auc_pr: 1.0
val:
  label_metrics:
    precision: 1.0
    recall: 0.93
    f1: 0.96
  point_metrics:
    silvio:
      hausdorff_distance: 879.15
      euclidean_distance: 2338.88
      tp: 1
      fp: 26
      fn: 26
      precision: 0.037
      recall: 0.037
      f1: 0.037
      auc_roc: 1.0
      auc_pr: 1.0
    astes anteriors:
      hausdorff_distance: 1311.95
      euclidean_distance: 2287.9
      tp: 1
      fp: 18
      fn: 17
      precision: 0.053
      recall: 0.056
      f1: 0.054
      auc_roc: 1.0
      auc_pr: 1.0
    calota:
      hausdorff_distance: 1791.23
      euclidean_distance: 4599.44
      tp: 0
      fp: 40
      fn: 40
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    talems:
      hausdorff_distance: 1460.74
      euclidean_distance: 3855.8
      tp: 0
      fp: 30
      fn: 32
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cavum:
      hausdorff_distance: 1135.22
      euclidean_distance: 4009.79
      tp: 2
      fp: 34
      fn: 34
      precision: 0.056
      recall: 0.056
      f1: 0.056
      auc_roc: 1.0
      auc_pr: 1.0
    linia mitja:
      hausdorff_distance: 1473.04
      euclidean_distance: 2790.85
      tp: 1
      fp: 17
      fn: 17
      precision: 0.056
      recall: 0.056
      f1: 0.056
      auc_roc: 1.0
      auc_pr: 1.0
    cerebel:
      hausdorff_distance: 2250.26
      euclidean_distance: 14709.06
      tp: 0
      fp: 80
      fn: 80
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
test:
  label_metrics:
    precision: 1.0
    recall: 0.95
    f1: 0.97
  point_metrics:
    silvio:
      hausdorff_distance: 1164.87
      euclidean_distance: 3046.16
      tp: 0
      fp: 30
      fn: 30
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    astes anteriors:
      hausdorff_distance: 1713.24
      euclidean_distance: 3081.66
      tp: 0
      fp: 22
      fn: 20
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    calota:
      hausdorff_distance: 2003.69
      euclidean_distance: 5521.22
      tp: 2
      fp: 42
      fn: 44
      precision: 0.045
      recall: 0.043
      f1: 0.044
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 1386.22
      euclidean_distance: 4089.02
      tp: 0
      fp: 33
      fn: 33
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cavum:
      hausdorff_distance: 1329.19
      euclidean_distance: 4994.83
      tp: 0
      fp: 40
      fn: 40
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    linia mitja:
      hausdorff_distance: 1757.64
      euclidean_distance: 3401.69
      tp: 1
      fp: 19
      fn: 19
      precision: 0.05
      recall: 0.05
      f1: 0.05
      auc_roc: 1.0
      auc_pr: 1.0
    cerebel:
      hausdorff_distance: 2499.23
      euclidean_distance: 16871.43
      tp: 1
      fp: 87
      fn: 87
      precision: 0.011
      recall: 0.011
      f1: 0.011
      auc_roc: 1.0
      auc_pr: 1.0
```

### Per-substructure

Baseline prompt with EDA info:

```bash
train:
  label_metrics:
    precision: 0.14
    recall: 1.0
    f1: 0.25
  point_metrics:
    calota:
      hausdorff_distance: 19085.66
      euclidean_distance: 50284.24
      tp: 5
      fp: 325
      fn: 328
      precision: 0.015
      recall: 0.015
      f1: 0.015
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 14020.37
      euclidean_distance: 29034.9
      tp: 14
      fp: 231
      fn: 240
      precision: 0.057
      recall: 0.055
      f1: 0.056
      auc_roc: 1.0
      auc_pr: 1.0
    cerebel:
      hausdorff_distance: 14943.57
      euclidean_distance: 62782.64
      tp: 8
      fp: 485
      fn: 653
      precision: 0.016
      recall: 0.012
      f1: 0.014
      auc_roc: 1.0
      auc_pr: 1.0
    cavum:
      hausdorff_distance: 13808.74
      euclidean_distance: 39841.72
      tp: 9
      fp: 320
      fn: 324
      precision: 0.027
      recall: 0.027
      f1: 0.027
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 12293.15
      euclidean_distance: 14670.65
      tp: 3
      fp: 116
      fn: 246
      precision: 0.025
      recall: 0.012
      f1: 0.016
      auc_roc: 1.0
      auc_pr: 1.0
    astes anteriors:
      hausdorff_distance: 13644.83
      euclidean_distance: 20839.5
      tp: 0
      fp: 142
      fn: 164
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    linia mitja:
      hausdorff_distance: 12980.76
      euclidean_distance: 13981.56
      tp: 1
      fp: 113
      fn: 165
      precision: 0.009
      recall: 0.006
      f1: 0.007
      auc_roc: 1.0
      auc_pr: 1.0
valid:
  label_metrics:
    precision: 0.14
    recall: 1.0
    f1: 0.25
  point_metrics:
    calota:
      hausdorff_distance: 2290.72
      euclidean_distance: 6356.82
      tp: 0
      fp: 40
      fn: 40
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    talems:
      hausdorff_distance: 1628.3
      euclidean_distance: 3565.96
      tp: 3
      fp: 27
      fn: 29
      precision: 0.1
      recall: 0.094
      f1: 0.097
      auc_roc: 1.0
      auc_pr: 1.0
    cerebel:
      hausdorff_distance: 1925.53
      euclidean_distance: 8099.18
      tp: 0
      fp: 60
      fn: 80
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cavum:
      hausdorff_distance: 1554.05
      euclidean_distance: 4709.51
      tp: 2
      fp: 37
      fn: 38
      precision: 0.051
      recall: 0.05
      f1: 0.051
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 1473.76
      euclidean_distance: 1910.49
      tp: 0
      fp: 15
      fn: 30
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    astes anteriors:
      hausdorff_distance: 1521.79
      euclidean_distance: 2391.73
      tp: 0
      fp: 17
      fn: 20
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    linia mitja:
      hausdorff_distance: 1566.4
      euclidean_distance: 1863.16
      tp: 0
      fp: 14
      fn: 20
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
test:
  label_metrics:
    precision: 0.14
    recall: 1.0
    f1: 0.25
  point_metrics:
    calota:
      hausdorff_distance: 2804.17
      euclidean_distance: 6890.46
      tp: 0
      fp: 43
      fn: 46
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    talems:
      hausdorff_distance: 1956.31
      euclidean_distance: 4671.32
      tp: 0
      fp: 33
      fn: 33
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cerebel:
      hausdorff_distance: 2080.79
      euclidean_distance: 8519.39
      tp: 3
      fp: 59
      fn: 85
      precision: 0.048
      recall: 0.034
      f1: 0.04
      auc_roc: 1.0
      auc_pr: 1.0
    cavum:
      hausdorff_distance: 1964.23
      euclidean_distance: 5789.37
      tp: 0
      fp: 44
      fn: 44
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    silvio:
      hausdorff_distance: 2248.34
      euclidean_distance: 3192.05
      tp: 0
      fp: 18
      fn: 33
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    astes anteriors:
      hausdorff_distance: 1927.33
      euclidean_distance: 2922.35
      tp: 0
      fp: 19
      fn: 22
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    linia mitja:
      hausdorff_distance: 1808.33
      euclidean_distance: 1480.5
      tp: 1
      fp: 11
      fn: 21
      precision: 0.083
      recall: 0.045
      f1: 0.059
      auc_roc: 1.0
      auc_pr: 1.0
```

Baseline prompt with EDA info, quantized (not done for sake of time):

SFT:

- [Unrefined run](https://wandb.ai/andrewhinh/mhf/runs/7pqnqxm3?nw=nwuserandrewhinh)
- [Refined run](https://wandb.ai/andrewhinh/mhf/runs/48vtndx7?nw=nwuserandrewhinh)
- [Encoder & multimodal projector freeze + refined run, overfit](https://wandb.ai/andrewhinh/mhf/runs/elyvg3c5?nw=nwuserandrewhinh)
- [Encoder & multimodal projector freeze + refined run, reduced steps](https://wandb.ai/andrewhinh/mhf/runs/1bdq8vjn?nw=nwuserandrewhinh)

Baseline prompt with EDA info, SFT:

```bash
train:
  label_metrics:
    precision: 1.0
    recall: 1.0
    f1: 1.0
  point_metrics:
    astes anteriors:
      hausdorff_distance: 13442.13
      euclidean_distance: 25200.04
      tp: 9
      fp: 157
      fn: 157
      precision: 0.054
      recall: 0.054
      f1: 0.054
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 6828.12
      euclidean_distance: 18191.55
      tp: 16
      fp: 233
      fn: 238
      precision: 0.064
      recall: 0.063
      f1: 0.064
      auc_roc: 1.0
      auc_pr: 1.0
    cerebel:
      hausdorff_distance: 11367.55
      euclidean_distance: 80824.98
      tp: 44
      fp: 618
      fn: 617
      precision: 0.066
      recall: 0.067
      f1: 0.067
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 5657.49
      euclidean_distance: 14967.74
      tp: 15
      fp: 234
      fn: 234
      precision: 0.06
      recall: 0.06
      f1: 0.06
      auc_roc: 1.0
      auc_pr: 1.0
    linia mitja:
      hausdorff_distance: 11988.14
      euclidean_distance: 23008.51
      tp: 7
      fp: 159
      fn: 159
      precision: 0.042
      recall: 0.042
      f1: 0.042
      auc_roc: 1.0
      auc_pr: 1.0
    cavum:
      hausdorff_distance: 6814.21
      euclidean_distance: 25042.06
      tp: 29
      fp: 303
      fn: 304
      precision: 0.087
      recall: 0.087
      f1: 0.087
      auc_roc: 1.0
      auc_pr: 1.0
    calota:
      hausdorff_distance: 7935.77
      euclidean_distance: 22012.61
      tp: 40
      fp: 292
      fn: 293
      precision: 0.12
      recall: 0.12
      f1: 0.12
      auc_roc: 1.0
      auc_pr: 1.0
valid:
  label_metrics:
    precision: 1.0
    recall: 1.0
    f1: 1.0
  point_metrics:
    astes anteriors:
      hausdorff_distance: 1685.3
      euclidean_distance: 3147.94
      tp: 2
      fp: 18
      fn: 18
      precision: 0.1
      recall: 0.1
      f1: 0.1
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 942.51
      euclidean_distance: 2426.7
      tp: 0
      fp: 30
      fn: 31
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cerebel:
      hausdorff_distance: 1466.09
      euclidean_distance: 9761.79
      tp: 4
      fp: 74
      fn: 76
      precision: 0.051
      recall: 0.05
      f1: 0.051
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 612.9
      euclidean_distance: 1596.7
      tp: 1
      fp: 29
      fn: 29
      precision: 0.033
      recall: 0.033
      f1: 0.033
      auc_roc: 1.0
      auc_pr: 1.0
    linia mitja:
      hausdorff_distance: 1511.37
      euclidean_distance: 2889.64
      tp: 2
      fp: 18
      fn: 18
      precision: 0.1
      recall: 0.1
      f1: 0.1
      auc_roc: 1.0
      auc_pr: 1.0
    cavum:
      hausdorff_distance: 809.04
      euclidean_distance: 2982.56
      tp: 2
      fp: 38
      fn: 38
      precision: 0.05
      recall: 0.05
      f1: 0.05
      auc_roc: 1.0
      auc_pr: 1.0
    calota:
      hausdorff_distance: 933.09
      euclidean_distance: 2581.95
      tp: 1
      fp: 39
      fn: 39
      precision: 0.025
      recall: 0.025
      f1: 0.025
      auc_roc: 1.0
      auc_pr: 1.0
test:
  label_metrics:
    precision: 0.97
    recall: 1.0
    f1: 0.99
  point_metrics:
    astes anteriors:
      hausdorff_distance: 1814.5
      euclidean_distance: 3361.41
      tp: 1
      fp: 19
      fn: 19
      precision: 0.05
      recall: 0.05
      f1: 0.05
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 868.33
      euclidean_distance: 2239.31
      tp: 1
      fp: 32
      fn: 33
      precision: 0.03
      recall: 0.029
      f1: 0.03
      auc_roc: 1.0
      auc_pr: 1.0
    cerebel:
      hausdorff_distance: 1604.43
      euclidean_distance: 11405.61
      tp: 6
      fp: 82
      fn: 82
      precision: 0.068
      recall: 0.068
      f1: 0.068
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 881.5
      euclidean_distance: 2338.94
      tp: 0
      fp: 33
      fn: 33
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    linia mitja:
      hausdorff_distance: 1606.16
      euclidean_distance: 3070.56
      tp: 0
      fp: 22
      fn: 22
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    cavum:
      hausdorff_distance: 1007.69
      euclidean_distance: 3773.48
      tp: 6
      fp: 38
      fn: 38
      precision: 0.136
      recall: 0.136
      f1: 0.136
      auc_roc: 1.0
      auc_pr: 1.0
    calota:
      hausdorff_distance: 1184.72
      euclidean_distance: 3325.27
      tp: 1
      fp: 39
      fn: 41
      precision: 0.025
      recall: 0.024
      f1: 0.024
      auc_roc: 1.0
      auc_pr: 1.0
```

Baseline prompt with EDA info, SFT + quantized:

```bash
train:
  label_metrics:
    precision: 1.0
    recall: 1.0
    f1: 1.0
  point_metrics:
    cavum:
      hausdorff_distance: 6816.03
      euclidean_distance: 24970.97
      tp: 28
      fp: 304
      fn: 305
      precision: 0.084
      recall: 0.084
      f1: 0.084
      auc_roc: 1.0
      auc_pr: 1.0
    calota:
      hausdorff_distance: 8098.78
      euclidean_distance: 21969.76
      tp: 39
      fp: 293
      fn: 294
      precision: 0.117
      recall: 0.117
      f1: 0.117
      auc_roc: 1.0
      auc_pr: 1.0
    cerebel:
      hausdorff_distance: 11562.0
      euclidean_distance: 83331.97
      tp: 34
      fp: 630
      fn: 627
      precision: 0.051
      recall: 0.051
      f1: 0.051
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 5722.61
      euclidean_distance: 15116.69
      tp: 18
      fp: 231
      fn: 231
      precision: 0.072
      recall: 0.072
      f1: 0.072
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 7173.47
      euclidean_distance: 19349.33
      tp: 10
      fp: 239
      fn: 244
      precision: 0.04
      recall: 0.039
      f1: 0.04
      auc_roc: 1.0
      auc_pr: 1.0
    linia mitja:
      hausdorff_distance: 10763.36
      euclidean_distance: 20659.55
      tp: 10
      fp: 156
      fn: 156
      precision: 0.06
      recall: 0.06
      f1: 0.06
      auc_roc: 1.0
      auc_pr: 1.0
    astes anteriors:
      hausdorff_distance: 13394.19
      euclidean_distance: 24826.65
      tp: 8
      fp: 158
      fn: 158
      precision: 0.048
      recall: 0.048
      f1: 0.048
      auc_roc: 1.0
      auc_pr: 1.0
valid:
  label_metrics:
    precision: 1.0
    recall: 1.0
    f1: 1.0
  point_metrics:
    cavum:
      hausdorff_distance: 806.02
      euclidean_distance: 2975.86
      tp: 2
      fp: 38
      fn: 38
      precision: 0.05
      recall: 0.05
      f1: 0.05
      auc_roc: 1.0
      auc_pr: 1.0
    calota:
      hausdorff_distance: 1007.47
      euclidean_distance: 2807.56
      tp: 1
      fp: 39
      fn: 39
      precision: 0.025
      recall: 0.025
      f1: 0.025
      auc_roc: 1.0
      auc_pr: 1.0
    cerebel:
      hausdorff_distance: 1428.26
      euclidean_distance: 9848.4
      tp: 5
      fp: 73
      fn: 75
      precision: 0.064
      recall: 0.062
      f1: 0.063
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 641.22
      euclidean_distance: 1686.31
      tp: 3
      fp: 27
      fn: 27
      precision: 0.1
      recall: 0.1
      f1: 0.1
      auc_roc: 1.0
      auc_pr: 1.0
    talems:
      hausdorff_distance: 933.73
      euclidean_distance: 2417.55
      tp: 0
      fp: 30
      fn: 31
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    linia mitja:
      hausdorff_distance: 1528.42
      euclidean_distance: 2926.34
      tp: 1
      fp: 19
      fn: 19
      precision: 0.05
      recall: 0.05
      f1: 0.05
      auc_roc: 1.0
      auc_pr: 1.0
    astes anteriors:
      hausdorff_distance: 1670.9
      euclidean_distance: 3089.49
      tp: 1
      fp: 19
      fn: 19
      precision: 0.05
      recall: 0.05
      f1: 0.05
      auc_roc: 1.0
      auc_pr: 1.0
test:
  label_metrics:
    precision: 0.97
    recall: 1.0
    f1: 0.99
  point_metrics:
    cavum:
      hausdorff_distance: 1023.78
      euclidean_distance: 3826.73
      tp: 5
      fp: 39
      fn: 39
      precision: 0.114
      recall: 0.114
      f1: 0.114
      auc_roc: 1.0
      auc_pr: 1.0
    calota:
      hausdorff_distance: 1155.2
      euclidean_distance: 3299.2
      tp: 1
      fp: 39
      fn: 41
      precision: 0.025
      recall: 0.024
      f1: 0.024
      auc_roc: 1.0
      auc_pr: 1.0
    cerebel:
      hausdorff_distance: 1596.36
      euclidean_distance: 11241.99
      tp: 4
      fp: 84
      fn: 84
      precision: 0.045
      recall: 0.045
      f1: 0.045
      auc_roc: 1.0
      auc_pr: 1.0
    silvio:
      hausdorff_distance: 883.69
      euclidean_distance: 2348.0
      tp: 0
      fp: 33
      fn: 33
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    talems:
      hausdorff_distance: 1054.29
      euclidean_distance: 2742.11
      tp: 0
      fp: 33
      fn: 34
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    linia mitja:
      hausdorff_distance: 1344.63
      euclidean_distance: 2573.79
      tp: 0
      fp: 22
      fn: 22
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
    astes anteriors:
      hausdorff_distance: 1813.68
      euclidean_distance: 3359.78
      tp: 0
      fp: 20
      fn: 20
      precision: 0.0
      recall: 0.0
      f1: 0.0
      auc_roc: 0.0
      auc_pr: 0.0
```
