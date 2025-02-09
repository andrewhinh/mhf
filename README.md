# mho

MHO Automated Labelling

- [ ] TODO: add results

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
├── etl.py              # etl.
├── eval.py             # eval.
├── quantize.py         # quantize.
├── train.py            # train.
└── utils.py            # utils.
```

## usage

Download data:

```bash
uv run etl.py --sft
```

Eval base model:

```bash
uv run eval.py --base
```

or

```bash
modal run eval.py --base
```

Eval quantized base model:

```bash
uv run eval.py --base --quant
```

or

```bash
modal run eval.py --base --quant
```

Run SFT:

```bash
cd LLaMA-Factory && uv pip install -e ".[torch,metrics]" && cd .. && FORCE_TORCHRUN=1 uv run train.py --sft
```

or

```bash
modal run train.py --sft
```

Eval SFT model:

```bash
uv run eval.py --sft
```

or

```bash
modal run eval.py --sft
```

Quantize the SFT model:

```bash
uv run quantize.py --sft
```

or

```bash
modal run quantize.py --sft
```

Eval quantized SFT model:

```bash
uv run eval.py --sft --quant
```

or

```bash
modal run eval.py --sft --quant
```

Run trained VLM on train data and construct new dataset with only relabelled incorrect examples:

```bash
uv run etl.py --dpo
```

or

```bash
modal run etl.py --dpo
```

Run DPO:

```bash
cd LLaMA-Factory && uv pip install -e ".[torch,metrics]" && cd .. && FORCE_TORCHRUN=1 uv run train.py --dpo
```

or

```bash
modal run train.py --dpo
```

Eval DPO model:

```bash
uv run eval.py --dpo
```

or

```bash
modal run eval.py --dpo
```

Quantize the DPO model:

```bash
uv run quantize.py --dpo
```

or

```bash
modal run quantize.py --dpo
```

Eval quantized DPO model:

```bash
uv run eval.py --dpo --quant
```

or

```bash
modal run eval.py --dpo --quant
```

Test the API:

```bash
modal run --env=main api.py
```

Deploy the API:

```bash
modal deploy --env=main api.py
```
