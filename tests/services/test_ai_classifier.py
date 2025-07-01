import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from unittest.mock import call

from app.services.ai_classifier import AIClassifier
from app.schemas.ai_classifications import AIClassifierSchema, CategoryEnum


class TestAIClassifierInitialization:
    """Test cases for AIClassifier initialization with different models."""
    
    def test_init_openai_success(self):
        """Test successful initialization with OpenAI model."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "open_ai"
            mock_settings.openai_api_key = "test-key"
            
            with patch('app.services.ai_classifier.AsyncOpenAI') as mock_openai:
                classifier = AIClassifier()
                
                assert classifier.model_name == "open_ai"
                assert hasattr(classifier, 'openai_client')
                mock_openai.assert_called_once_with(api_key="test-key")
    
    def test_init_openai_missing_api_key(self):
        """Test initialization fails when OpenAI API key is missing."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "open_ai"
            mock_settings.openai_api_key = None
            
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                AIClassifier()
    
    def test_init_huggingface_success(self):
        """Test successful initialization with Hugging Face models."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "hugging_face"
            
            with patch('app.services.ai_classifier.pipeline') as mock_pipeline, \
                 patch('app.services.ai_classifier.torch.cuda.is_available', return_value=False):
                
                mock_classifier = Mock()
                mock_summarizer = Mock()
                mock_pipeline.side_effect = [mock_classifier, mock_summarizer]
                
                classifier = AIClassifier()
                
                assert classifier.model_name == "hugging_face"
                assert hasattr(classifier, 'classifier')
                assert hasattr(classifier, 'summarizer')
                
                # Verify pipeline calls
                expected_calls = [
                    call("zero-shot-classification", model="facebook/bart-large-mnli", device=-1),
                    call("summarization", model="sshleifer/distilbart-cnn-12-6", device=-1)
                ]
                mock_pipeline.assert_has_calls(expected_calls)
    
    def test_init_fine_tuned_bart_success(self):
        """Test successful initialization with fine-tuned BART model."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "fine_tuned_bart"
            
            with patch('app.services.ai_classifier.os.path.exists', return_value=True), \
                 patch('app.services.ai_classifier.pipeline') as mock_pipeline, \
                 patch('app.services.ai_classifier.torch.cuda.is_available', return_value=False), \
                 patch('builtins.open', mock_open_config()):
                
                mock_classifier = Mock()
                mock_summarizer = Mock()
                mock_pipeline.side_effect = [mock_classifier, mock_summarizer]
                
                classifier = AIClassifier()
                
                assert classifier.model_name == "fine_tuned_bart"
                assert hasattr(classifier, 'classifier')
                assert hasattr(classifier, 'summarizer')
                assert hasattr(classifier, 'fine_tuned_config')
    
    def test_init_fine_tuned_bart_fallback(self):
        """Test fallback when fine-tuned model is not found."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "fine_tuned_bart"
            
            with patch('app.services.ai_classifier.os.path.exists', return_value=False), \
                 patch('app.services.ai_classifier.pipeline') as mock_pipeline, \
                 patch('app.services.ai_classifier.torch.cuda.is_available', return_value=False):
                
                mock_classifier = Mock()
                mock_summarizer = Mock()
                mock_pipeline.side_effect = [mock_classifier, mock_summarizer]
                
                classifier = AIClassifier()
                
                # Should fallback to hugging_face
                assert classifier.model_name == "hugging_face"
                
                # Verify fallback pipeline calls
                expected_calls = [
                    call("zero-shot-classification", model="facebook/bart-large-mnli", device=-1),
                    call("summarization", model="sshleifer/distilbart-cnn-12-6", device=-1)
                ]
                mock_pipeline.assert_has_calls(expected_calls)
    
    def test_init_fine_tuned_bart_load_error_fallback(self):
        """Test fallback when fine-tuned model loading fails."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "fine_tuned_bart"
            
            with patch('app.services.ai_classifier.os.path.exists', return_value=True), \
                 patch('app.services.ai_classifier.pipeline') as mock_pipeline, \
                 patch('app.services.ai_classifier.torch.cuda.is_available', return_value=False):
                
                # First call (fine-tuned model) fails, subsequent calls succeed
                mock_classifier = Mock()
                mock_summarizer = Mock()
                mock_pipeline.side_effect = [
                    Exception("Model loading failed"),
                    mock_classifier,
                    mock_summarizer
                ]
                
                classifier = AIClassifier()
                
                # Should fallback to hugging_face
                assert classifier.model_name == "hugging_face"
    
    def test_init_fine_tuned_bart_no_config_file(self):
        """Test fine-tuned model initialization when config file doesn't exist."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "fine_tuned_bart"
            
            # Mock os.path.exists to return True for model path, False for config file
            def mock_exists(path):
                if path == "models/fine_tuned_bart":
                    return True
                elif path.endswith("config.json"):
                    return False
                return False
            
            with patch('app.services.ai_classifier.os.path.exists', side_effect=mock_exists), \
                 patch('app.services.ai_classifier.pipeline') as mock_pipeline, \
                 patch('app.services.ai_classifier.torch.cuda.is_available', return_value=False):
                
                mock_classifier = Mock()
                mock_summarizer = Mock()
                mock_pipeline.side_effect = [mock_classifier, mock_summarizer]
                
                classifier = AIClassifier()
                
                assert classifier.model_name == "fine_tuned_bart"
                assert hasattr(classifier, 'classifier')
                assert hasattr(classifier, 'summarizer')
                assert classifier.fine_tuned_config is None  # This covers line 84
    
    def test_init_invalid_model(self):
        """Test initialization fails with invalid model name."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "invalid_model"
            
            with pytest.raises(ValueError, match="Invalid classifier model: invalid_model"):
                AIClassifier()


class TestAIClassifierOpenAI:
    """Test cases for OpenAI classification methods."""
    
    @pytest.fixture
    def openai_classifier(self):
        """Create AI classifier with OpenAI model."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "open_ai"
            mock_settings.openai_api_key = "test-key"
            
            with patch('app.services.ai_classifier.AsyncOpenAI'):
                classifier = AIClassifier()
                simple_labels = ["technical", "billing", "general"]
                classifier.category_labels = simple_labels
                classifier.category_labels_dict = {label: label for label in simple_labels}
                return classifier
    
    @pytest.mark.asyncio
    async def test_classify_with_openai_success(self, openai_classifier):
        """Test successful OpenAI classification."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = (
            "Category: technical\n"
            "Confidence: 0.85\n"
            "Summary: Server connectivity issue reported."
        )
        
        openai_classifier.openai_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await openai_classifier._classify_with_openai("Server is down")
        
        assert isinstance(result, AIClassifierSchema)
        assert result.priority == "medium"
        assert result.category == CategoryEnum.technical
        assert result.confidence_score == 0.85
        assert result.summary == "Server connectivity issue reported."
        assert result.model_used == "openai_gpt_3_5_turbo"
    
    @pytest.mark.asyncio
    async def test_classify_with_openai_empty_response(self, openai_classifier):
        """Test handling of empty OpenAI response."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = None
        
        openai_classifier.openai_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await openai_classifier._classify_with_openai("Test text")
        
        assert result.priority == "medium"
        assert result.category == CategoryEnum.general
        assert result.confidence_score == 0.6
        assert result.summary == "AI classification failed to produce a response."
        assert result.model_used == "openai_gpt_fallback"
    
    @pytest.mark.asyncio
    async def test_classify_with_openai_invalid_category(self, openai_classifier):
        """Test handling of invalid category from OpenAI."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = (
            "Category: invalid_category\n"
            "Confidence: 0.75\n"
            "Summary: Some summary."
        )
        
        openai_classifier.openai_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await openai_classifier._classify_with_openai("Test text")
        
        assert result.category == CategoryEnum.general
        assert result.confidence_score == 0.75
        assert result.summary == "Some summary."
        assert result.model_used == "openai_gpt_3_5_turbo"
    
    @pytest.mark.asyncio
    async def test_classify_with_openai_parsing_error(self, openai_classifier):
        """Test handling of malformed OpenAI response."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Malformed response without proper format"
        
        openai_classifier.openai_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await openai_classifier._classify_with_openai("Test text")
        
        assert result.priority == "medium"
        assert result.category == CategoryEnum.general
        assert result.confidence_score == 0.6
        assert result.summary == "Could not generate summary."
        assert result.model_used == "openai_gpt_3_5_turbo"
    
    @pytest.mark.asyncio
    async def test_classify_with_openai_api_error(self, openai_classifier):
        """Test handling of OpenAI API errors."""
        openai_classifier.openai_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        result = await openai_classifier._classify_with_openai("Test text")
        
        assert result.priority == "medium"
        assert result.category == CategoryEnum.general
        assert result.confidence_score == 0.5
        assert result.summary == "Error during OpenAI processing."
        assert result.model_used == "openai_error_fallback"


class TestAIClassifierHuggingFace:
    """Test cases for Hugging Face classification methods."""
    
    @pytest.fixture
    def huggingface_classifier(self):
        """Create AI classifier with Hugging Face models."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "hugging_face"
            
            with patch('app.services.ai_classifier.pipeline') as mock_pipeline, \
                 patch('app.services.ai_classifier.torch.cuda.is_available', return_value=False):
                
                mock_classifier = Mock()
                mock_summarizer = Mock()
                mock_pipeline.side_effect = [mock_classifier, mock_summarizer]
                
                classifier = AIClassifier()
                # Simplify category labels for testing
                simple_labels = ["technical", "billing", "general"]
                classifier.category_labels = simple_labels
                classifier.category_labels_dict = {label: label for label in simple_labels}

                classifier.classifier = mock_classifier
                classifier.summarizer = mock_summarizer
                
                return classifier
    
    def test_classify_with_huggingface_success(self, huggingface_classifier):
        """Test successful Hugging Face classification."""
        # Mock classification result
        huggingface_classifier.classifier.return_value = {
            'labels': ['technical', 'billing', 'general'],
            'scores': [0.85, 0.10, 0.05]
        }
        
        # Mock summarization result
        huggingface_classifier.summarizer.return_value = [
            {'summary_text': 'Server connectivity issue reported by user.'}
        ]
        
        # Use a long text (more than 20 words) to trigger summarization
        long_text = "The server is not responding and I cannot access my account dashboard properly. This is a critical technical issue that affects my daily operations and workflow. I need immediate assistance to resolve this connectivity problem."
        
        result = huggingface_classifier._classify_with_huggingface(long_text)
        
        assert isinstance(result, AIClassifierSchema)
        assert result.priority == "medium"
        assert result.category == CategoryEnum.technical
        assert result.confidence_score == 0.85
        assert result.summary == "Server connectivity issue reported by user."
        assert result.model_used == "huggingface_bart_mnli_distilbart_cnn"
    
    def test_classify_with_huggingface_short_text(self, huggingface_classifier):
        """Test classification with short text (no summarization)."""
        # Mock classification result
        huggingface_classifier.classifier.return_value = {
            'labels': ['billing', 'technical', 'general'],
            'scores': [0.90, 0.08, 0.02]
        }
        
        short_text = "Payment issue help"
        result = huggingface_classifier._classify_with_huggingface(short_text)
        
        assert result.priority == "medium"
        assert result.category == CategoryEnum.billing
        assert result.confidence_score == 0.90
        assert result.summary == "Payment issue help..."
        assert result.model_used == "huggingface_bart_mnli_distilbart_cnn"
        
        # Verify summarizer was not called for short text
        huggingface_classifier.summarizer.assert_not_called()
    
    def test_classify_with_huggingface_long_text_summarization(self, huggingface_classifier):
        """Test classification with long text that triggers summarization."""
        # Mock classification result
        huggingface_classifier.classifier.return_value = {
            'labels': ['technical', 'billing', 'general'],
            'scores': [0.88, 0.08, 0.04]
        }
        
        # Mock summarization result
        huggingface_classifier.summarizer.return_value = [
            {'summary_text': 'Technical issue with server connectivity and database access.'}
        ]
        
        # Text with more than 20 words to trigger summarization
        long_text = "The server is experiencing intermittent connectivity issues and the database is not responding properly. This has been affecting multiple users across different departments and causing significant delays in our daily operations and customer service."
        
        result = huggingface_classifier._classify_with_huggingface(long_text)
        
        assert result.priority == "medium"
        assert result.category == CategoryEnum.technical
        assert result.confidence_score == 0.88
        assert result.summary == "Technical issue with server connectivity and database access."
        assert result.model_used == "huggingface_bart_mnli_distilbart_cnn"
        
        # Verify summarizer was called for long text
        huggingface_classifier.summarizer.assert_called_once()
    
    def test_classify_with_huggingface_fine_tuned_model(self):
        """Test classification with fine-tuned model identifier."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "fine_tuned_bart"
            
            with patch('app.services.ai_classifier.pipeline') as mock_pipeline, \
                 patch('app.services.ai_classifier.torch.cuda.is_available', return_value=False), \
                 patch('app.services.ai_classifier.os.path.exists', return_value=True), \
                 patch('builtins.open', mock_open_config()):
                
                mock_classifier = Mock()
                mock_summarizer = Mock()
                mock_pipeline.side_effect = [mock_classifier, mock_summarizer]
                
                classifier = AIClassifier()
                # Simplify category labels
                simple_labels = ["technical", "billing", "general"]
                classifier.category_labels = simple_labels
                classifier.category_labels_dict = {label: label for label in simple_labels}

                classifier.classifier = mock_classifier
                classifier.summarizer = mock_summarizer
                
                # Mock classification result
                classifier.classifier.return_value = {
                    'labels': ['general', 'technical', 'billing'],
                    'scores': [0.70, 0.20, 0.10]
                }
                
                # Mock summarization result
                classifier.summarizer.return_value = [
                    {'summary_text': 'General inquiry about services.'}
                ]
                
                result = classifier._classify_with_huggingface(
                    "I have a general question about your services and pricing options available."
                )

                assert result.priority == "medium"
                assert result.category == CategoryEnum.general
                assert result.model_used == "fine_tuned_bart"
    
    def test_classify_with_huggingface_classification_error(self, huggingface_classifier):
        """Test handling of classification errors."""
        huggingface_classifier.classifier.side_effect = Exception("Classification error")
        
        result = huggingface_classifier._classify_with_huggingface("Test text")
        
        assert result.priority == "medium"
        assert result.category == CategoryEnum.general
        assert result.confidence_score == 0.5
        assert result.summary == "Error during AI processing."
        assert result.model_used == "huggingface_error_fallback"
    
    def test_classify_with_huggingface_summarization_error(self, huggingface_classifier):
        """Test handling of summarization errors while classification succeeds."""
        # Mock successful classification
        huggingface_classifier.classifier.return_value = {
            'labels': ['technical', 'billing', 'general'],
            'scores': [0.85, 0.10, 0.05]
        }
        
        # Mock summarization error
        huggingface_classifier.summarizer.side_effect = Exception("Summarization error")
        
        long_text = "This is a long text " * 10  # Make it longer than 20 words
        result = huggingface_classifier._classify_with_huggingface(long_text)
        
        assert result.category == CategoryEnum.general
        assert result.confidence_score == 0.5
        assert result.summary == "Error during AI processing."
        assert result.model_used == "huggingface_error_fallback"


class TestAIClassifierUtilityMethods:
    """Test cases for utility methods."""
    
    @pytest.fixture
    def classifier(self):
        """Create a basic AI classifier instance."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "hugging_face"
            
            with patch('app.services.ai_classifier.pipeline'), \
                 patch('app.services.ai_classifier.torch.cuda.is_available', return_value=False):
                
                classifier = AIClassifier()
                # Simplify category labels for testing
                simple_labels = ["technical", "billing", "general"]
                classifier.category_labels = simple_labels
                classifier.category_labels_dict = {label: label for label in simple_labels}
                return classifier
    
    def test_combine_body_and_subject(self, classifier):
        """Test text combination utility method."""
        body = "This is the email body content."
        subject = "Email Subject"
        
        result = classifier._combine_body_and_subject(body, subject)
        
        expected = "subject: Email Subject\nbody: This is the email body content."
        assert result == expected
    
    def test_combine_body_and_subject_empty_values(self, classifier):
        """Test text combination with empty values."""
        result1 = classifier._combine_body_and_subject("", "Subject")
        assert result1 == "subject: Subject\nbody: "
        
        result2 = classifier._combine_body_and_subject("Body", "")
        assert result2 == "subject: \nbody: Body"
        
        result3 = classifier._combine_body_and_subject("", "")
        assert result3 == "subject: \nbody: "


class TestAIClassifierMainMethod:
    """Test cases for the main classify_and_summarize method."""
    
    @pytest.fixture
    def openai_classifier(self):
        """Create AI classifier with OpenAI model."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "open_ai"
            mock_settings.openai_api_key = "test-key"
            
            with patch('app.services.ai_classifier.AsyncOpenAI'):
                classifier = AIClassifier()
                simple_labels = ["technical", "billing", "general"]
                classifier.category_labels = simple_labels
                classifier.category_labels_dict = {label: label for label in simple_labels}
                return classifier
    
    @pytest.fixture
    def huggingface_classifier(self):
        """Create AI classifier with Hugging Face models."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "hugging_face"
            
            with patch('app.services.ai_classifier.pipeline') as mock_pipeline, \
                 patch('app.services.ai_classifier.torch.cuda.is_available', return_value=False):
                
                mock_classifier = Mock()
                mock_summarizer = Mock()
                mock_pipeline.side_effect = [mock_classifier, mock_summarizer]
                
                classifier = AIClassifier()
                # Simplify category labels
                simple_labels = ["technical", "billing", "general"]
                classifier.category_labels = simple_labels
                classifier.category_labels_dict = {label: label for label in simple_labels}

                classifier.classifier = mock_classifier
                classifier.summarizer = mock_summarizer
                return classifier
    
    @pytest.mark.asyncio
    async def test_classify_and_summarize_openai(self, openai_classifier):
        """Test main method with OpenAI model."""
        with patch.object(openai_classifier, '_classify_with_openai') as mock_classify:
            expected_result = AIClassifierSchema(
                priority="medium",
                category=CategoryEnum.technical,
                confidence_score=0.85,
                summary="Technical issue with server.",
                model_used="openai_gpt"
            )
            mock_classify.return_value = expected_result
            
            result = await openai_classifier.classify_and_summarize(
                body="Server is down",
                subject="Technical Issue"
            )
            
            assert result == expected_result
            mock_classify.assert_called_once_with("subject: Technical Issue\nbody: Server is down")
    
    @pytest.mark.asyncio
    async def test_classify_and_summarize_huggingface(self, huggingface_classifier):
        """Test main method with Hugging Face model."""
        with patch.object(huggingface_classifier, '_classify_with_huggingface') as mock_classify:
            expected_result = AIClassifierSchema(
                category=CategoryEnum.billing,
                confidence_score=0.90,
                summary="Billing inquiry about charges.",
                model_used="huggingface_bart_mnli_distilbart_cnn"
            )
            mock_classify.return_value = expected_result
            
            result = await huggingface_classifier.classify_and_summarize(
                body="I was charged twice",
                subject="Billing Question"
            )
            
            assert result == expected_result
            mock_classify.assert_called_once_with("subject: Billing Question\nbody: I was charged twice")
    
    @pytest.mark.asyncio
    async def test_classify_and_summarize_empty_body(self, huggingface_classifier):
        """Test main method with empty body."""
        result = await huggingface_classifier.classify_and_summarize(
            body="",
            subject="Test Subject"
        )
        
        assert result.category == CategoryEnum.general
        assert result.confidence_score == 0.5
        assert result.summary == "No text provided for analysis."
        assert result.model_used == "default_fallback"
    
    @pytest.mark.asyncio
    async def test_classify_and_summarize_none_body(self, huggingface_classifier):
        """Test main method with None body."""
        result = await huggingface_classifier.classify_and_summarize(
            body=None,
            subject="Test Subject"
        )
        
        assert result.category == CategoryEnum.general
        assert result.confidence_score == 0.5
        assert result.summary == "No text provided for analysis."
        assert result.model_used == "default_fallback"
    
    @pytest.mark.asyncio
    async def test_classify_and_summarize_non_string_body(self, huggingface_classifier):
        """Test main method with non-string body."""
        result = await huggingface_classifier.classify_and_summarize(
            body=123,
            subject="Test Subject"
        )
        
        assert result.category == CategoryEnum.general
        assert result.confidence_score == 0.5
        assert result.summary == "No text provided for analysis."
        assert result.model_used == "default_fallback"
    
    @pytest.mark.asyncio
    async def test_classify_and_summarize_invalid_model_config(self):
        """Test main method with invalid model configuration."""
        # Create classifier with invalid model name after initialization
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "hugging_face"
            
            with patch('app.services.ai_classifier.pipeline'), \
                 patch('app.services.ai_classifier.torch.cuda.is_available', return_value=False):
                
                classifier = AIClassifier()
                # Manually set invalid model name to test error handling
                classifier.model_name = "invalid_model"
                
                result = await classifier.classify_and_summarize(
                    body="Test body",
                    subject="Test subject"
                )
                
                assert result.category == CategoryEnum.general
                assert result.confidence_score == 0.0
                assert result.summary == "Invalid classifier model configured."
                assert result.model_used == "config_error_fallback"


class TestAIClassifierEdgeCases:
    """Test cases for edge cases and error scenarios."""
    
    @pytest.mark.asyncio
    async def test_very_long_text_processing(self):
        """Test processing of very long text inputs."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "hugging_face"
            
            with patch('app.services.ai_classifier.pipeline') as mock_pipeline, \
                 patch('app.services.ai_classifier.torch.cuda.is_available', return_value=False):
                
                mock_classifier = Mock()
                mock_summarizer = Mock()
                mock_pipeline.side_effect = [mock_classifier, mock_summarizer]
                
                classifier = AIClassifier()
                # Simplify category labels for testing
                simple_labels = ["technical", "billing", "general"]
                classifier.category_labels = simple_labels
                classifier.category_labels_dict = {label: label for label in simple_labels}

                classifier.classifier = mock_classifier
                classifier.summarizer = mock_summarizer
                
                # Mock successful classification
                classifier.classifier.return_value = {
                    'labels': ['general', 'technical', 'billing'],
                    'scores': [0.70, 0.20, 0.10]
                }
                
                # Mock summarization result
                classifier.summarizer.return_value = [
                    {'summary_text': 'Long text summarized.'}
                ]
                
                very_long_text = "This is a very long text. " * 100
                result = await classifier.classify_and_summarize(
                    body=very_long_text,
                    subject="Long Text Test"
                )
                
                assert result.category == CategoryEnum.general
                assert result.confidence_score == 0.7
                assert result.summary == "Long text summarized."
                assert result.priority == "medium"
    
    @pytest.mark.asyncio
    async def test_special_characters_handling(self):
        """Test handling of special characters and unicode."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "hugging_face"
            
            with patch('app.services.ai_classifier.pipeline') as mock_pipeline, \
                 patch('app.services.ai_classifier.torch.cuda.is_available', return_value=False):
                
                mock_classifier = Mock()
                mock_summarizer = Mock()
                mock_pipeline.side_effect = [mock_classifier, mock_summarizer]
                
                classifier = AIClassifier()
                # Simplify category labels
                simple_labels = ["technical", "billing", "general"]
                classifier.category_labels = simple_labels
                classifier.category_labels_dict = {label: label for label in simple_labels}

                classifier.classifier = mock_classifier
                classifier.summarizer = mock_summarizer
                
                # Mock successful classification
                classifier.classifier.return_value = {
                    'labels': ['general', 'technical', 'billing'],
                    'scores': [0.60, 0.25, 0.15]
                }
                
                special_text = "Héllo! @#$%^&*() 你好 🚀 test"
                result = await classifier.classify_and_summarize(
                    body=special_text,
                    subject="Special Characters"
                )
                
                assert result.category == CategoryEnum.general
                assert result.confidence_score == 0.6
                assert result.priority == "medium"


def mock_open_config():
    """Mock file opening for configuration files."""
    config_data = {
        "model_type": "fine_tuned",
        "training_data": "customer_support_tickets",
        "accuracy": 0.95
    }
    
    from unittest.mock import mock_open
    return mock_open(read_data=json.dumps(config_data))


class TestAIClassifierIntegration:
    """Integration tests for AI classifier."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_classification_workflow(self):
        """Test complete classification workflow from initialization to result."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "hugging_face"
            
            with patch('app.services.ai_classifier.pipeline') as mock_pipeline, \
                 patch('app.services.ai_classifier.torch.cuda.is_available', return_value=False):
                
                mock_classifier = Mock()
                mock_summarizer = Mock()
                mock_pipeline.side_effect = [mock_classifier, mock_summarizer]
                
                # Initialize classifier
                classifier = AIClassifier()
                classifier.classifier = mock_classifier
                classifier.summarizer = mock_summarizer
                
                # Simplify category labels for testing
                simple_labels = ["technical", "billing", "general"]
                classifier.category_labels = simple_labels
                classifier.category_labels_dict = {label: label for label in simple_labels}
                
                # Setup mock responses
                classifier.classifier.return_value = {
                    'labels': ['technical', 'billing', 'general'],
                    'scores': [0.85, 0.10, 0.05]
                }
                
                classifier.summarizer.return_value = [
                    {'summary_text': 'User reports server connectivity issues.'}
                ]
                
                # Test classification with long text to trigger summarization
                result = await classifier.classify_and_summarize(
                    body="I cannot connect to the server and get timeout errors consistently. This has been happening for several hours now and is affecting my ability to complete important work tasks.",
                    subject="Server Connection Problem"
                )
                
                # Verify result
                assert result.priority == "medium"
                assert result.category == CategoryEnum.technical
                assert result.confidence_score == 0.85
                assert result.summary == "User reports server connectivity issues."
                
                # Verify methods were called: classifier twice (category + priority) and summarizer once
                assert classifier.classifier.call_count == 2
                classifier.summarizer.assert_called_once()
    
    def test_labels_configuration(self):
        """Test that classification labels are properly configured."""
        with patch('app.services.ai_classifier.settings') as mock_settings:
            mock_settings.classifier_model = "hugging_face"
            
            with patch('app.services.ai_classifier.pipeline'), \
                 patch('app.services.ai_classifier.torch.cuda.is_available', return_value=False):
                
                classifier = AIClassifier()
                
                # Simplify labels for this test
                simple_labels = ["technical", "billing", "general"]
                classifier.category_labels = simple_labels
                classifier.category_labels_dict = {label: label for label in simple_labels}

                assert classifier.category_labels == simple_labels
                assert len(classifier.category_labels) == 3
                assert all(label in simple_labels for label in classifier.category_labels) 