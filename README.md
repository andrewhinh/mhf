# mhf

MHF Automated Labelling

## results

Baseline prompt with EDA info:

```bash
"train": {
  "label_metrics": {
    "precision": 1.0,
    "recall": 1.0,
    "f1": 1.0
  },
  "point_metrics": {
    "calota": {
      "hausdorff_distance": 22965.67,
      "euclidean_distance": 62339.63,
      "tp": 6,
      "fp": 392,
      "fn": 327,
      "precision": 0.015,
      "recall": 0.018,
      "f1": 0.016,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "linia mitja": {
      "hausdorff_distance": 22100.31,
      "euclidean_distance": 25520.88,
      "tp": 2,
      "fp": 390,
      "fn": 164,
      "precision": 0.005,
      "recall": 0.012,
      "f1": 0.007,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "cavum": {
      "hausdorff_distance": 18862.54,
      "euclidean_distance": 49474.65,
      "tp": 4,
      "fp": 394,
      "fn": 329,
      "precision": 0.01,
      "recall": 0.012,
      "f1": 0.011,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "cerebel": {
      "hausdorff_distance": 20464.17,
      "euclidean_distance": 61998.21,
      "tp": 25,
      "fp": 431,
      "fn": 636,
      "precision": 0.055,
      "recall": 0.038,
      "f1": 0.045,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "talems": {
      "hausdorff_distance": 17418.43,
      "euclidean_distance": 29991.32,
      "tp": 10,
      "fp": 384,
      "fn": 244,
      "precision": 0.025,
      "recall": 0.039,
      "f1": 0.031,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "silvio": {
      "hausdorff_distance": 24028.31,
      "euclidean_distance": 51882.73,
      "tp": 0,
      "fp": 392,
      "fn": 249,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "astes anteriors": {
      "hausdorff_distance": 22219.08,
      "euclidean_distance": 24442.36,
      "tp": 0,
      "fp": 393,
      "fn": 164,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    }
  }
},
"val": {
  "label_metrics": {
    "precision": 1.0,
    "recall": 0.99,
    "f1": 0.99
  },
  "point_metrics": {
    "calota": {
      "hausdorff_distance": 2745.82,
      "euclidean_distance": 7391.43,
      "tp": 2,
      "fp": 46,
      "fn": 40,
      "precision": 0.042,
      "recall": 0.048,
      "f1": 0.044,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "linia mitja": {
      "hausdorff_distance": 2689.81,
      "euclidean_distance": 3357.93,
      "tp": 0,
      "fp": 49,
      "fn": 20,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "cavum": {
      "hausdorff_distance": 2207.66,
      "euclidean_distance": 5920.44,
      "tp": 0,
      "fp": 49,
      "fn": 40,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "cerebel": {
      "hausdorff_distance": 2365.12,
      "euclidean_distance": 8707.97,
      "tp": 2,
      "fp": 49,
      "fn": 78,
      "precision": 0.039,
      "recall": 0.025,
      "f1": 0.031,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "talems": {
      "hausdorff_distance": 2112.69,
      "euclidean_distance": 4249.38,
      "tp": 1,
      "fp": 48,
      "fn": 31,
      "precision": 0.02,
      "recall": 0.031,
      "f1": 0.025,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "silvio": {
      "hausdorff_distance": 2762.54,
      "euclidean_distance": 5973.73,
      "tp": 0,
      "fp": 48,
      "fn": 30,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "astes anteriors": {
      "hausdorff_distance": 2633.82,
      "euclidean_distance": 3006.68,
      "tp": 0,
      "fp": 48,
      "fn": 20,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    }
  }
},
"test": {
  "label_metrics": {
    "precision": 1.0,
    "recall": 1.0,
    "f1": 1.0
  },
  "point_metrics": {
    "calota": {
      "hausdorff_distance": 3351.69,
      "euclidean_distance": 7946.43,
      "tp": 1,
      "fp": 62,
      "fn": 43,
      "precision": 0.016,
      "recall": 0.023,
      "f1": 0.019,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "linia mitja": {
      "hausdorff_distance": 3166.11,
      "euclidean_distance": 3712.88,
      "tp": 0,
      "fp": 61,
      "fn": 22,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "cavum": {
      "hausdorff_distance": 2798.88,
      "euclidean_distance": 6982.81,
      "tp": 0,
      "fp": 64,
      "fn": 44,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "cerebel": {
      "hausdorff_distance": 2915.65,
      "euclidean_distance": 9029.97,
      "tp": 1,
      "fp": 69,
      "fn": 87,
      "precision": 0.014,
      "recall": 0.011,
      "f1": 0.013,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "talems": {
      "hausdorff_distance": 2358.98,
      "euclidean_distance": 4207.55,
      "tp": 2,
      "fp": 60,
      "fn": 31,
      "precision": 0.032,
      "recall": 0.061,
      "f1": 0.042,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "silvio": {
      "hausdorff_distance": 3201.25,
      "euclidean_distance": 7328.32,
      "tp": 0,
      "fp": 61,
      "fn": 33,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "astes anteriors": {
      "hausdorff_distance": 3244.97,
      "euclidean_distance": 3708.49,
      "tp": 0,
      "fp": 62,
      "fn": 22,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    }
  }
}
```

Baseline prompt with EDA info, quantized:

```bash
"train": {
  "label_metrics": {
    "precision": 1.0,
    "recall": 0.95,
    "f1": 0.97
  },
  "point_metrics": {
    "cavum": {
      "hausdorff_distance": 18779.22,
      "euclidean_distance": 48492.51,
      "tp": 4,
      "fp": 312,
      "fn": 329,
      "precision": 0.013,
      "recall": 0.012,
      "f1": 0.012,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "calota": {
      "hausdorff_distance": 23339.68,
      "euclidean_distance": 54512.15,
      "tp": 11,
      "fp": 319,
      "fn": 322,
      "precision": 0.033,
      "recall": 0.033,
      "f1": 0.033,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "cerebel": {
      "hausdorff_distance": 18925.81,
      "euclidean_distance": 43038.32,
      "tp": 19,
      "fp": 257,
      "fn": 594,
      "precision": 0.069,
      "recall": 0.031,
      "f1": 0.043,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "silvio": {
      "hausdorff_distance": 22076.6,
      "euclidean_distance": 52506.46,
      "tp": 0,
      "fp": 280,
      "fn": 234,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "talems": {
      "hausdorff_distance": 16500.37,
      "euclidean_distance": 32975.16,
      "tp": 2,
      "fp": 274,
      "fn": 233,
      "precision": 0.007,
      "recall": 0.009,
      "f1": 0.008,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "astes anteriors": {
      "hausdorff_distance": 20481.47,
      "euclidean_distance": 21988.55,
      "tp": 2,
      "fp": 271,
      "fn": 150,
      "precision": 0.007,
      "recall": 0.013,
      "f1": 0.009,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "linia mitja": {
      "hausdorff_distance": 20745.85,
      "euclidean_distance": 23486.82,
      "tp": 4,
      "fp": 272,
      "fn": 150,
      "precision": 0.014,
      "recall": 0.026,
      "f1": 0.019,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    }
  }
},
"val": {
  "label_metrics": {
    "precision": 1.0,
    "recall": 0.92,
    "f1": 0.96
  },
  "point_metrics": {
    "cavum": {
      "hausdorff_distance": 1835.9,
      "euclidean_distance": 4906.27,
      "tp": 0,
      "fp": 35,
      "fn": 40,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "calota": {
      "hausdorff_distance": 2561.06,
      "euclidean_distance": 5338.61,
      "tp": 1,
      "fp": 36,
      "fn": 39,
      "precision": 0.027,
      "recall": 0.025,
      "f1": 0.026,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "cerebel": {
      "hausdorff_distance": 2010.75,
      "euclidean_distance": 4558.72,
      "tp": 0,
      "fp": 34,
      "fn": 72,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "silvio": {
      "hausdorff_distance": 2238.71,
      "euclidean_distance": 5679.35,
      "tp": 0,
      "fp": 34,
      "fn": 27,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "talems": {
      "hausdorff_distance": 1779.12,
      "euclidean_distance": 3350.6,
      "tp": 1,
      "fp": 33,
      "fn": 28,
      "precision": 0.029,
      "recall": 0.034,
      "f1": 0.032,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "astes anteriors": {
      "hausdorff_distance": 2065.22,
      "euclidean_distance": 2526.78,
      "tp": 0,
      "fp": 34,
      "fn": 18,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "linia mitja": {
      "hausdorff_distance": 2025.39,
      "euclidean_distance": 2521.95,
      "tp": 0,
      "fp": 34,
      "fn": 18,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    }
  }
},
"test": {
  "label_metrics": {
    "precision": 1.0,
    "recall": 0.94,
    "f1": 0.97
  },
  "point_metrics": {
    "cavum": {
      "hausdorff_distance": 2693.98,
      "euclidean_distance": 7984.58,
      "tp": 0,
      "fp": 44,
      "fn": 44,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "calota": {
      "hausdorff_distance": 3510.88,
      "euclidean_distance": 8306.04,
      "tp": 0,
      "fp": 46,
      "fn": 46,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "cerebel": {
      "hausdorff_distance": 2549.62,
      "euclidean_distance": 7361.08,
      "tp": 2,
      "fp": 38,
      "fn": 78,
      "precision": 0.05,
      "recall": 0.025,
      "f1": 0.033,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    },
    "silvio": {
      "hausdorff_distance": 3170.36,
      "euclidean_distance": 7801.17,
      "tp": 0,
      "fp": 40,
      "fn": 30,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "talems": {
      "hausdorff_distance": 2337.37,
      "euclidean_distance": 5179.98,
      "tp": 0,
      "fp": 40,
      "fn": 30,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "astes anteriors": {
      "hausdorff_distance": 2929.98,
      "euclidean_distance": 3392.89,
      "tp": 0,
      "fp": 40,
      "fn": 20,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "auc_roc": 0.0,
      "auc_pr": 0.0
    },
    "linia mitja": {
      "hausdorff_distance": 2832.44,
      "euclidean_distance": 3502.27,
      "tp": 1,
      "fp": 39,
      "fn": 19,
      "precision": 0.025,
      "recall": 0.05,
      "f1": 0.033,
      "auc_roc": 1.0,
      "auc_pr": 1.0
    }
  }
}
```

## setup

Run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --all-extras --dev
uv pip install git+https://github.com/seungwoos/AutoAWQ.git@add-qwen2_5_vl --no-deps --no-build-isolation
uv run pre-commit install
modal setup
modal config set-environment dev
echo "alias modal='uv run modal'" >> ~/.bashrc
echo "export PYTHONPATH=.:$PYTHONPATH" >> ~/.bashrc
echo "export TOKENIZERS_PARALLELISM=false" >> ~/.bashrc
echo "export HF_HUB_ENABLE_HF_TRANSFER=1" >> ~/.bashrc
source ~/.bashrc
```

Create a `.env`:

```bash
HF_TOKEN=
WANDB_API_KEY=
WANDB_ENTITY=
```

## repo structure

```bash
.
├── artifacts           # data + runs.
├── src                 # src.
│   ├── eda.ipynb       # eda.
│   ├── etl.py          # etl.
│   ├── eval.py         # eval.
│   ├── quantize.py     # quantize.
│   └── utils.py        # utils.
```

## usage

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

Run SFT ([e.g. run on wandb](https://wandb.ai/andrewhinh/mhf/runs/5v83pidh)):

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

Test the API:

```bash
uv run src/api.py --test
```

or

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

Test the website:

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
