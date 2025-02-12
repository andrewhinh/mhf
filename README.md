# mhf

MHF Automated Labelling

## results

Baseline evaluation:

```bash
Metrics for split 'train':
  Label-level metrics: {'precision': 1.0, 'recall': 0.29, 'f1': 0.45}
  Point-level metrics: {'precision': 0.67, 'recall': 1.0, 'f1': 0.8, 'avg_euclidean_distance': 160.72}
Metrics for split 'valid':
  Label-level metrics: {'precision': 1.0, 'recall': 0.25, 'f1': 0.4}
  Point-level metrics: {'precision': 0.67, 'recall': 1.0, 'f1': 0.8, 'avg_euclidean_distance': 138.82}
Metrics for split 'test':
  Label-level metrics: {'precision': 1.0, 'recall': 0.26, 'f1': 0.41}
  Point-level metrics: {'precision': 0.67, 'recall': 1.0, 'f1': 0.8, 'avg_euclidean_distance': 152.89}
```

## setup

Run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --all-extras --dev
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
│   ├── etl.py          # etl.
│   ├── eval.py         # eval.
│   ├── quantize.py     # quantize.
│   └── utils.py        # utils.
└── artifacts           # data + runs.
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

Run SFT:

```bash
cd LLaMA-Factory && uv pip install -e ".[torch,metrics]" && cd .. && FORCE_TORCHRUN=1 uv run src/train.py --sft
```

or

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
cd LLaMA-Factory && uv pip install -e ".[torch,metrics]" && cd .. && FORCE_TORCHRUN=1 uv run src/train.py --dpo
```

or

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
uv run api.py
```

or

```bash
modal run api.py
```

Deploy the API:

```bash
modal deploy --env=main api.py
```
