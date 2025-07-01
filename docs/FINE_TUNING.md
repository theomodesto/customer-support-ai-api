# Simple BART Fine-tuning

Ultra-simple fine-tuning for BART-large-MNLI using customer support data.

## Quick Start

### 1. Install Dependencies
```bash
pip install torch transformers datasets accelerate
```

### 2. Run Fine-tuning
```bash
python scripts/fine_tune.py
```

That's it! The script will:
- Load 100 examples from the Hugging Face dataset
- Fine-tune BART-large-MNLI for 1 epoch
- Save the model to `models/fine_tuned_bart`
- Test it with sample cases

## What You Get

- **Training Time**: ~2-3 minutes on Mac withou GPU
- **Model Size**: ~1.5GB
- **Accuracy**: Better than zero-shot model
- **Location**: `models/fine_tuned_bart/`

## Use the Fine-tuned Model

Update your config to use the fine-tuned model:

```python
# In your environment variables or config
CLASSIFIER_MODEL = "fine_tuned_bart"
```

## How It Works

1. **Loads Data**: Downloads Tobi-Bueck/customer-support-tickets dataset
2. **Processes Data**: Converts to NLI format for BART
3. **Trains Model**: Fine-tunes for 1 epoch with 100 examples
4. **Saves Model**: Stores locally for your app to use
5. **Tests Model**: Runs quick test to verify it works
