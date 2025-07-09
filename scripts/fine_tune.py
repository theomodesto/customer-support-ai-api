#!/usr/bin/env python3
"""
Ultra-simple BART fine-tuning for customer support.
Just run: python scripts/fine_tune.py
"""

import os
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from datasets import load_dataset, Dataset

def main():
    print("Loading dataset...")
    dataset = load_dataset("Tobi-Bueck/customer-support-tickets")
    
    # Prepare data - handle the actual dataset structure
    data = []
    train_data = dataset['train']
    
    # Take only 100 examples for fast training
    count = 0
    for item in train_data:
        if count >= 20000:  
            break
            
        try:
            # Handle different possible dataset structures
            if hasattr(item, 'get'):
                # Dictionary-like object
                subject = str(item.get('subject', ''))
                body = str(item.get('body', ''))
                queue = str(item.get('queue', '')).lower()
            elif isinstance(item, (list, tuple)) and len(item) >= 3:
                # List/tuple structure
                subject = str(item[0] if item[0] else '')
                body = str(item[1] if item[1] else '')
                queue = str(item[2] if len(item) > 2 else '').lower()
            else:
                # Skip unknown format
                continue
            
            text = f"{subject}\n\n{body}".strip()
            
            if not text:
                continue

            # Technical Support/IT Support → technical;
            # Billing and Payments → billing;
            # Customer Service/Product Support → general
                
            # Simple category mapping
            if 'technical' in queue or 'it' in queue or ('it' in queue and 'support' in queue) or ('technical' in queue and 'support' in queue):
                category = "technical"
            elif 'billing' in queue or 'payment' in queue or ('billing' in queue and 'payments' in queue):
                category = "billing"
            else:
                category = "general"
            
            data.append({"text": text, "category": category})
            count += 1
            
        except Exception as e:
            print(f"Skipping item due to error: {e}")
            continue
    
    print(f"Prepared {len(data)} examples")
    
    if len(data) == 0:
        print("No data found! Check dataset structure.")
        return
    
    # Create NLI data
    nli_data = []
    # hypotheses = {
    #     "technical": "This is a technical support request.",
    #     "billing": "This is a billing request.",
    #     "general": "This is a general inquiry."
    # }

    hypotheses = {
        "technical": "This ticket is about a technical issue such as system configuration, security setup, software malfunction, or data protection",
        "billing": "This ticket is about a billing, invoice, or payment-related issue",
        "general": "This ticket is a general question or request that is not related to technical problems or billing"
    }
    
    for item in data:
        for cat, hyp in hypotheses.items():
            label = 2 if cat == item["category"] else 0
            nli_data.append({
                "premise": item["text"],
                "hypothesis": hyp,
                "label": label
            })
    
    # Load model and tokenizer
    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
    model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli", num_labels=3)
    
    # Create proper dataset
    nli_dataset = Dataset.from_list(nli_data)
    
    # Tokenize function
    def tokenize_function(examples):
        result = tokenizer(
            examples["premise"],
            examples["hypothesis"],
            truncation=True,
            padding="max_length",
            max_length=128,  # Reduced from 512 to 256 for speed
            return_tensors=None  # Don't return tensors here
        )
        result["labels"] = examples.get("label")
        return result
    
    # Tokenize the dataset
    tokenized_dataset = nli_dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=["premise", "hypothesis", "label"]
    )

    tokenized_dataset = tokenized_dataset.with_format("torch", columns=["input_ids", "attention_mask", "labels"])
    
    # Split dataset
    split_dataset = tokenized_dataset.train_test_split(test_size=0.2)
    train_dataset = split_dataset["train"]
    eval_dataset = split_dataset["test"]
    
    # Train with much faster settings
    print("Training...")
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir="./models/fine_tuned_bart",
            learning_rate=1e-5,
            per_device_train_batch_size=4,  # Reduced from 4 to 2
            per_device_eval_batch_size=4,   # Reduced from 4 to 2
            num_train_epochs=1,             # Keep at 1 epoch
            save_strategy="epoch",
            push_to_hub=False,
            report_to=None,
            logging_steps=10,               # Log more frequently
            eval_steps=50,                  # Evaluate more frequently
            evaluation_strategy="steps",    # Evaluate during training
        ),
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
    )
    
    trainer.train()
    
    # Save
    os.makedirs("./models/fine_tuned_bart", exist_ok=True)
    trainer.save_model("./models/fine_tuned_bart")
    tokenizer.save_pretrained("./models/fine_tuned_bart")
    
    # Test
    print("Testing...")
    classifier = pipeline("zero-shot-classification", model="./models/fine_tuned_bart")
    
    test_cases = [
        ("Server is down", "technical"),
        ("Payment failed", "billing"),
        ("How to reset password?", "general"),
    ]
    
    for text, expected in test_cases:
        result = classifier(text, ["technical", "billing", "general"])
        predicted = result['labels'][0]
        print(f"{text} -> {predicted} (expected: {expected})")
    
    print("Done! Model saved to ./models/fine_tuned_bart")

if __name__ == "__main__":
    main() 