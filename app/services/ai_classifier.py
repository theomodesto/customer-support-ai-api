import re
from typing import  cast
from openai import AsyncOpenAI
from transformers import pipeline
from app.config import settings
from app.schemas.ai_classifications import AIClassifierSchema, CategoryEnum
from app.utils.logger import logger
import torch
import os
import json

class AIClassifier:
    """Classifier using multiple model options."""
    def __init__(self):
        """Initialize the classification and summarization pipelines."""
        logger.info("Initializing AI Classifier...", component="ai_classification")
        self.model_name = settings.classifier_model
        
        # Debug logging
        logger.debug(f"Classifier model from settings: {self.model_name}")

        if self.model_name == "open_ai":
            if settings.openai_api_key:
                self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized successfully")
            else:
                logger.error(
                    "OpenAI API key is required but not provided.",
                    component="ai_classification",
                )
                raise ValueError("OpenAI API key is required")
        
        # Initialize Hugging Face models (either directly requested or as fallback)
        if self.model_name == "hugging_face":
            device = 0 if torch.cuda.is_available() else -1
            # Zero-shot classification pipeline
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=device
            )
            # Summarization pipeline
            self.summarizer = pipeline(
                "summarization",
                model="sshleifer/distilbart-cnn-12-6",
                device=device
            )
        
        elif self.model_name == "fine_tuned_bart":
            device = 0 if torch.cuda.is_available() else -1
            # Load fine-tuned model
            self._initialize_fine_tuned_model(device)
        
        elif self.model_name == "open_ai":
            # OpenAI client already initialized above, no additional setup needed
            pass
        
        else:
            # This should not be reached as we validate valid models above
            valid_models = ["open_ai", "hugging_face", "fine_tuned_bart"]
            raise ValueError(f"Invalid classifier model: {self.model_name}. Valid models are: {valid_models}")

        # self.category_labels = ["technical", "billing", "general"]
        self.category_labels = [
            "This ticket is about a technical issue such as system configuration, security setup, software malfunction, or data protection",
            "This ticket is about a billing, invoice, or payment-related issue",
            "This ticket is a general question or request that is not related to technical problems or billing"
        ]
        self.category_labels_dict = {
            "This ticket is about a technical issue such as system configuration, security setup, software malfunction, or data protection": "technical",
            "This ticket is about a billing, invoice, or payment-related issue": "billing",
            "This ticket is a general question or request that is not related to technical problems or billing": "general"
        }
                
        self.priority_labels = [
            "The request is not urgent and can be answered later.",
            "The request is important but not urgent.",
            "The request is urgent and needs immediate attention."
        ]
        self.priority_labels_dict = {
            "The request is not urgent and can be answered later.": "low",
            "The request is important but not urgent.": "medium",
            "The request is urgent and needs immediate attention.": "high"
        }
        logger.info(f"AI Classifier initialized with model: {self.model_name}.")

    def _initialize_fine_tuned_model(self, device: int):
        """Initialize fine-tuned BART model for classification."""
        model_path = "models/fine_tuned_bart"  # Updated path to match simple script
        
        if not os.path.exists(model_path):
            logger.warning(f"Fine-tuned model not found at {model_path}. Falling back to zero-shot model.")
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=device
            )
            self.summarizer = pipeline(
                "summarization",
                model="sshleifer/distilbart-cnn-12-6",
                device=device
            )
            self.model_name = "hugging_face"  # Fallback to zero-shot
            return
        
        try:
            # Load fine-tuned model configuration
            config_path = os.path.join(model_path, "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.fine_tuned_config = json.load(f)
                logger.info("Loaded fine-tuned model configuration")
            else:
                self.fine_tuned_config = None
            
            # Load fine-tuned classification pipeline
            self.classifier = pipeline(
                "zero-shot-classification",
                model=model_path,
                device=device
            )
            
            # Summarization pipeline (same as zero-shot)
            self.summarizer = pipeline(
                "summarization",
                model="sshleifer/distilbart-cnn-12-6",
                device=device
            )
            
            logger.info("Fine-tuned BART model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load fine-tuned model: {e}")
            logger.warning("Falling back to zero-shot model")
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=device
            )
            self.summarizer = pipeline(
                "summarization",
                model="sshleifer/distilbart-cnn-12-6",
                device=device
            )
            self.model_name = "hugging_face"  # Fallback to zero-shot



    def _classify_with_huggingface(self, text: str) -> AIClassifierSchema:
        """Classify and summarize using Hugging Face models."""
        try:
            # Category classification
            classification_result = cast(dict, self.classifier(text, self.category_labels, hypothesis_template="{}"))
            category = self.category_labels_dict[classification_result['labels'][0]]
            confidence_score = classification_result['scores'][0]

            print(f"Category: {category}")
            print(f"classification_result: {classification_result}")

            priority = "medium"  
            try:
                priority_result = self.classifier(text, self.priority_labels, hypothesis_template="{}")
               
                # Cast the result to ensure proper typing
                priority_result = cast(dict, priority_result)
                predicted_priority = self.priority_labels_dict[priority_result["labels"][0]]

                # Accept the model prediction only if it is within the allowed labels *and*
                # the confidence score is reasonably high. Otherwise, fall back to "medium".
                priority = predicted_priority.lower()
           
            except Exception as priority_err:
                # Keep default and log.
                logger.warning(
                    "Priority classification failed, defaulting to 'medium'",
                    component="ai_classification",
                    model="huggingface_bart_mnli_distilbart_cnn" if self.model_name != "fine_tuned_bart" else "fine_tuned_bart",
                    error=str(priority_err),
                )
            
            # Summarization
            summary_text = ""
            if len(text.split()) > 20:
                summary_result = cast(list[dict], self.summarizer(text, max_length=50, min_length=10, do_sample=False))
                if summary_result:
                    summary_text = summary_result[0]['summary_text'].strip()
            else:
                summary_text = ' '.join(text.split()[:20]).strip() + '...'

            model_used = "fine_tuned_bart" if self.model_name == "fine_tuned_bart" else "huggingface_bart_mnli_distilbart_cnn"
            
            return AIClassifierSchema(
                priority=priority,
                category=CategoryEnum(category),
                confidence_score=confidence_score,
                summary=summary_text,
                model_used=model_used
            )
        except Exception as e:
            logger.log_ml_error(
                error=e,
                context={
                    "model": "huggingface_bart_mnli_distilbart_cnn" if self.model_name != "fine_tuned_bart" else "fine_tuned_bart",
                    "text_length": len(text),
                    "text_preview": text[:100] + "..." if len(text) > 100 else text
                },
                component="ai_classification"
            )
            return AIClassifierSchema(
                priority="medium",
                category=CategoryEnum.general,
                confidence_score=0.5,
                summary="Error during AI processing.",
                model_used="huggingface_error_fallback"
            )
            
    async def _classify_with_openai(self, text: str) -> AIClassifierSchema:
        """Classify using OpenAI GPT model."""
        try:
            prompt = f"""
            Classify the following customer support request into one of these categories:
            - technical: Technical issues, bugs, system problems, IT support
            - billing: Payment issues, invoices, charges, refunds
            - general: General inquiries, product information, other questions
            
            Also provide a confidence_score score between 0 and 1, a one-sentence summary, and a priority level (low, medium, high).
            
            Customer request: "{text}"
            
            Respond in this exact format:
            Category: [category]
            Confidence: [score]
            Priority: [priority]
            Summary: [one sentence summary]
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.1
            )
                        
            content = response.choices[0].message.content
            
            # Parse response
            if content is None:
                logger.warning(
                    "OpenAI returned empty response",
                    component="ai_classification",
                    model="openai_gpt_3_5_turbo",
                    text_length=len(text)
                )
                return AIClassifierSchema(
                    priority="medium",
                    category=CategoryEnum.general,
                    confidence_score=0.6,
                    summary="AI classification failed to produce a response.",
                    model_used="openai_gpt_fallback"
                )

            category_match = re.search(r'Category:\s*(\w+)', content)
            confidence_match = re.search(r'Confidence:\s*([\d.]+)', content)
            priority_match = re.search(r'Priority:\s*(\w+)', content)
            summary_match = re.search(r'Summary:\s*(.+)', content)
            
            category = category_match.group(1).lower() if category_match else "general"
            confidence_score = float(confidence_match.group(1)) if confidence_match else 0.6
            priority = priority_match.group(1).lower() if priority_match else "medium"
            summary = summary_match.group(1).strip() if summary_match else "Could not generate summary."
            
            # Validate category
            if category not in self.category_labels:
                logger.warning(
                    f"OpenAI returned invalid category: {category}",
                    component="ai_classification",
                    model="openai_gpt_3_5_turbo",
                    category=category,
                    text_length=len(text)
                )
                category = "general"
            
            return AIClassifierSchema(
                priority=priority,
                category=CategoryEnum(category),
                confidence_score=confidence_score,
                summary=summary,
                model_used="openai_gpt_3_5_turbo"
            )
            
        except Exception as e:
            logger.log_ml_error(
                error=e,
                context={
                    "model": "openai_gpt_3_5_turbo",
                    "text_length": len(text),
                    "text_preview": text[:100] + "..." if len(text) > 100 else text
                },
                component="ai_classification"
            )
            return AIClassifierSchema(
                priority="medium",
                category=CategoryEnum.general,
                confidence_score=0.5,
                summary="Error during OpenAI processing.",
                model_used="openai_error_fallback"
            )


    def _combine_body_and_subject(self, body: str, subject: str) -> str:
        """Combine body and subject into a single string."""
        return f"subject: {subject}\nbody: {body}"

    async def classify_and_summarize(self, body: str, subject: str) -> AIClassifierSchema:
        """
        Classify text, generate a confidence score, and create a summary
        using the model specified in the environment configuration.
        """
        if not body or not isinstance(body, str):
            return AIClassifierSchema(
                priority="medium",
                category=CategoryEnum.general,
                confidence_score=0.5,
                summary="No text provided for analysis.",
                model_used="default_fallback"
            )
        
        text = self._combine_body_and_subject(body, subject)

        if self.model_name == "open_ai":
            return await self._classify_with_openai(text)
        
        elif self.model_name in ["hugging_face", "fine_tuned_bart"]:
            return self._classify_with_huggingface(text)
        
        # This part should not be reached if __init__ is correct
        return AIClassifierSchema(
            priority="medium",
            category=CategoryEnum.general,
            confidence_score=0.0,
            summary="Invalid classifier model configured.",
            model_used="config_error_fallback"
        )

# Global classifier instance
ai_classifier = AIClassifier() 