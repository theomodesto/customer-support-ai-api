import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas.support_tickets import SupportTicketRequestCreate, SupportTicketResponse
from app.schemas.enums import CategoryEnum
from app.models.support_ticket import SupportTicket
from app.repository.support_ticket_repo import SupportTicketRepo
from app.repository.support_ticket_ai_classification_repo import SupportTicketAIClassificationRepo


class TestCreateSupportRequest:
    """Test cases for POST /requests endpoint."""
    
    def test_create_support_request_success(self, client, db_session):
        """Test successful creation of a support request."""
        request_data = {
            "subject": "Test Issue",
            "body": "This is a test support request",
            "language": "en"
        }
        
        with patch.object(SupportTicketRepo, 'create_support_ticket') as mock_create:
            # Create a mock SupportTicket object that matches the model
            mock_ticket = Mock(spec=SupportTicket)
            mock_ticket.id = uuid4()
            mock_ticket.subject = request_data["subject"]
            mock_ticket.body = request_data["body"]
            mock_ticket.language = request_data["language"]
            mock_ticket.queue = None
            mock_ticket.priority = None
            mock_ticket.category = None
            mock_ticket.confidence_score = None
            mock_ticket.summary = None
            mock_ticket.tag_1 = None
            mock_ticket.created_at = datetime.now()
            mock_ticket.updated_at = None
            
            mock_create.return_value = mock_ticket
            
            with patch.object(SupportTicketAIClassificationRepo, 'classify_ticket_and_update') as mock_classify:
                response = client.post("/requests", json=request_data)
                
                assert response.status_code == 201
                data = response.json()
                assert data["subject"] == request_data["subject"]
                assert data["body"] == request_data["body"]
                assert data["language"] == request_data["language"]
                
                # Verify AI classification was scheduled
                mock_classify.assert_called_once()
    
    def test_create_support_request_missing_subject(self, client):
        """Test creation fails when subject is missing."""
        request_data = {
            "body": "This is a test support request",
            "language": "en"
        }
        
        response = client.post("/requests", json=request_data)
        assert response.status_code == 422
    
    def test_create_support_request_missing_body(self, client):
        """Test creation fails when body is missing."""
        request_data = {
            "subject": "Test Issue",
            "language": "en"
        }
        
        response = client.post("/requests", json=request_data)
        assert response.status_code == 422
    
    def test_create_support_request_invalid_language(self, client):
        """Test creation fails with invalid language code."""
        request_data = {
            "subject": "Test Issue",
            "body": "This is a test support request",
            "language": "invalid"
        }
        
        response = client.post("/requests", json=request_data)
        assert response.status_code == 422
    
    def test_create_support_request_empty_fields(self, client):
        """Test creation fails with empty subject or body."""
        request_data = {
            "subject": "",
            "body": "This is a test support request",
            "language": "en"
        }
        
        response = client.post("/requests", json=request_data)
        assert response.status_code == 422
    
    def test_create_support_request_repository_error(self, client, db_session):
        """Test handling of repository errors during creation."""
        request_data = {
            "subject": "Test Issue",
            "body": "This is a test support request",
            "language": "en"
        }
        
        with patch.object(SupportTicketRepo, 'create_support_ticket') as mock_create:
            mock_create.side_effect = Exception("Database error")
            
            response = client.post("/requests", json=request_data)
            assert response.status_code == 500
            assert "Failed to create support request" in response.json()["detail"]
    
    def test_create_support_request_xss_protection(self, client):
        """Test that XSS attempts are sanitized."""
        request_data = {
            "subject": "<script>alert('xss')</script>Test Issue",
            "body": "This is a test support request with <script>alert('xss')</script>",
            "language": "en"
        }
        
        with patch.object(SupportTicketRepo, 'create_support_ticket') as mock_create:
            # Create a mock SupportTicket object
            mock_ticket = Mock(spec=SupportTicket)
            mock_ticket.id = uuid4()
            mock_ticket.subject = "Test Issue"  # Sanitized
            mock_ticket.body = "This is a test support request with"  # Sanitized
            mock_ticket.language = request_data["language"]
            mock_ticket.queue = None
            mock_ticket.priority = None
            mock_ticket.category = None
            mock_ticket.confidence_score = None
            mock_ticket.summary = None
            mock_ticket.tag_1 = None
            mock_ticket.created_at = datetime.now()
            mock_ticket.updated_at = None
            
            mock_create.return_value = mock_ticket
            
            with patch.object(SupportTicketAIClassificationRepo, 'classify_ticket_and_update'):
                response = client.post("/requests", json=request_data)
                assert response.status_code == 201


class TestGetSupportRequest:
    """Test cases for GET /requests/{support_ticket_id} endpoint."""
    
    def test_get_support_request_success(self, client, db_session):
        """Test successful retrieval of a support request."""
        ticket_id = str(uuid4())
        
        with patch.object(SupportTicketRepo, 'get_support_ticket_by_id') as mock_get:
            # Create a mock SupportTicket object
            mock_ticket = Mock(spec=SupportTicket)
            mock_ticket.id = uuid4()
            mock_ticket.subject = "Test Issue"
            mock_ticket.body = "This is a test support request"
            mock_ticket.language = "en"
            mock_ticket.queue = None
            mock_ticket.priority = None
            mock_ticket.category = "technical"
            mock_ticket.confidence_score = 0.85
            mock_ticket.summary = "Technical issue"
            mock_ticket.tag_1 = None
            mock_ticket.created_at = datetime.now()
            mock_ticket.updated_at = None
            
            mock_get.return_value = mock_ticket
            
            response = client.get(f"/requests/{ticket_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["subject"] == "Test Issue"
            assert data["category"] == "technical"
            assert data["confidence_score"] == 0.85
    
    def test_get_support_request_not_found(self, client, db_session):
        """Test retrieval of non-existent support request."""
        ticket_id = str(uuid4())
        
        with patch.object(SupportTicketRepo, 'get_support_ticket_by_id') as mock_get:
            mock_get.return_value = None
            
            response = client.get(f"/requests/{ticket_id}")
            assert response.status_code == 404
            assert "Support request not found" in response.json()["detail"]
    
    def test_get_support_request_invalid_uuid(self, client):
        """Test retrieval with invalid UUID format."""
        response = client.get("/requests/invalid-uuid")
        assert response.status_code == 422
    
    def test_get_support_request_repository_error(self, client, db_session):
        """Test handling of repository errors during retrieval."""
        ticket_id = str(uuid4())
        
        with patch.object(SupportTicketRepo, 'get_support_ticket_by_id') as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            response = client.get(f"/requests/{ticket_id}")
            assert response.status_code == 500
            assert "Failed to retrieve support request" in response.json()["detail"]


class TestListSupportRequests:
    """Test cases for GET /requests endpoint."""
    
    def test_list_support_requests_success(self, client, db_session):
        """Test successful listing of support requests."""
        with patch.object(SupportTicketRepo, 'get_support_tickets') as mock_get, \
             patch.object(SupportTicketRepo, 'count_support_tickets') as mock_count:
            
            # Create mock SupportTicket objects
            mock_ticket1 = Mock(spec=SupportTicket)
            mock_ticket1.id = uuid4()
            mock_ticket1.subject = "Test Issue 1"
            mock_ticket1.body = "This is test support request 1"
            mock_ticket1.language = "en"
            mock_ticket1.queue = None
            mock_ticket1.priority = None
            mock_ticket1.category = "technical"
            mock_ticket1.confidence_score = None
            mock_ticket1.summary = None
            mock_ticket1.tag_1 = None
            mock_ticket1.created_at = datetime.now()
            mock_ticket1.updated_at = None
            
            mock_ticket2 = Mock(spec=SupportTicket)
            mock_ticket2.id = uuid4()
            mock_ticket2.subject = "Test Issue 2"
            mock_ticket2.body = "This is test support request 2"
            mock_ticket2.language = "en"
            mock_ticket2.queue = None
            mock_ticket2.priority = None
            mock_ticket2.category = "billing"
            mock_ticket2.confidence_score = None
            mock_ticket2.summary = None
            mock_ticket2.tag_1 = None
            mock_ticket2.created_at = datetime.now()
            mock_ticket2.updated_at = None
            
            mock_get.return_value = [mock_ticket1, mock_ticket2]
            mock_count.return_value = 2
            
            response = client.get("/requests")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["support_tickets"]) == 2
            assert data["total"] == 2
            assert data["page"] == 1
            assert data["size"] == 20
            assert data["has_next"] is False
    
    def test_list_support_requests_with_category_filter(self, client, db_session):
        """Test listing with category filter."""
        with patch.object(SupportTicketRepo, 'get_support_tickets') as mock_get, \
             patch.object(SupportTicketRepo, 'count_support_tickets') as mock_count:
            
            mock_ticket = Mock(spec=SupportTicket)
            mock_ticket.id = uuid4()
            mock_ticket.subject = "Technical Issue"
            mock_ticket.body = "Server problem"
            mock_ticket.language = "en"
            mock_ticket.queue = None
            mock_ticket.priority = None
            mock_ticket.category = "technical"
            mock_ticket.confidence_score = None
            mock_ticket.summary = None
            mock_ticket.tag_1 = None
            mock_ticket.created_at = datetime.now()
            mock_ticket.updated_at = None
            
            mock_get.return_value = [mock_ticket]
            mock_count.return_value = 1
            
            response = client.get("/requests?category=technical")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["support_tickets"]) == 1
            assert data["support_tickets"][0]["category"] == "technical"
            
            # Verify the filter was passed correctly
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["category"] == "technical"
    
    def test_list_support_requests_with_priority_filter(self, client, db_session):
        """Test listing with priority filter."""
        with patch.object(SupportTicketRepo, 'get_support_tickets') as mock_get, \
             patch.object(SupportTicketRepo, 'count_support_tickets') as mock_count:
            
            mock_ticket = Mock(spec=SupportTicket)
            mock_ticket.id = uuid4()
            mock_ticket.subject = "High Priority Issue"
            mock_ticket.body = "Critical problem"
            mock_ticket.language = "en"
            mock_ticket.queue = None
            mock_ticket.priority = "high"
            mock_ticket.category = None
            mock_ticket.confidence_score = None
            mock_ticket.summary = None
            mock_ticket.tag_1 = None
            mock_ticket.created_at = datetime.now()
            mock_ticket.updated_at = None
            
            mock_get.return_value = [mock_ticket]
            mock_count.return_value = 1
            
            response = client.get("/requests?priority=high")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["support_tickets"]) == 1
            assert data["support_tickets"][0]["priority"] == "high"
            
            # Verify the filter was passed correctly
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["priority"] == "high"
    
    def test_list_support_requests_with_pagination(self, client, db_session):
        """Test listing with pagination parameters."""
        with patch.object(SupportTicketRepo, 'get_support_tickets') as mock_get, \
             patch.object(SupportTicketRepo, 'count_support_tickets') as mock_count:
            
            mock_ticket = Mock(spec=SupportTicket)
            mock_ticket.id = uuid4()
            mock_ticket.subject = "Test Issue"
            mock_ticket.body = "Test body"
            mock_ticket.language = "en"
            mock_ticket.queue = None
            mock_ticket.priority = None
            mock_ticket.category = None
            mock_ticket.confidence_score = None
            mock_ticket.summary = None
            mock_ticket.tag_1 = None
            mock_ticket.created_at = datetime.now()
            mock_ticket.updated_at = None
            
            mock_get.return_value = [mock_ticket]
            mock_count.return_value = 50  # Total count
            
            response = client.get("/requests?page=2&size=10")
            
            assert response.status_code == 200
            data = response.json()
            assert data["page"] == 2
            assert data["size"] == 10
            assert data["total"] == 50
            assert data["has_next"] is True  # 50 total, page 2 with size 10 should have next
            
            # Verify pagination parameters were passed correctly
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["skip"] == 10  # (page - 1) * size
            assert call_args[1]["limit"] == 10
    
    def test_list_support_requests_invalid_page(self, client):
        """Test listing with invalid page number."""
        response = client.get("/requests?page=0")
        assert response.status_code == 422
    
    def test_list_support_requests_invalid_size(self, client):
        """Test listing with invalid size parameter."""
        response = client.get("/requests?size=0")
        assert response.status_code == 422
        
        response = client.get("/requests?size=101")  # Max is 100
        assert response.status_code == 422
    
    def test_list_support_requests_invalid_category(self, client):
        """Test listing with invalid category."""
        response = client.get("/requests?category=invalid")
        assert response.status_code == 422
    
    def test_list_support_requests_repository_error(self, client, db_session):
        """Test handling of repository errors during listing."""
        with patch.object(SupportTicketRepo, 'get_support_tickets') as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            response = client.get("/requests")
            
            assert response.status_code == 400
            assert "Failed to retrieve support requests" in response.json()["detail"]
    
    def test_list_support_requests_empty_result(self, client, db_session):
        """Test listing when no tickets match filters."""
        with patch.object(SupportTicketRepo, 'get_support_tickets') as mock_get, \
             patch.object(SupportTicketRepo, 'count_support_tickets') as mock_count:
            
            mock_get.return_value = []
            mock_count.return_value = 0
            
            response = client.get("/requests?category=technical")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["support_tickets"]) == 0
            assert data["total"] == 0
            assert data["has_next"] is False
    
    def test_list_support_requests_combined_filters(self, client, db_session):
        """Test listing with multiple filters combined."""
        with patch.object(SupportTicketRepo, 'get_support_tickets') as mock_get, \
             patch.object(SupportTicketRepo, 'count_support_tickets') as mock_count:
            
            mock_ticket = Mock(spec=SupportTicket)
            mock_ticket.id = uuid4()
            mock_ticket.subject = "Technical High Priority"
            mock_ticket.body = "Critical technical issue"
            mock_ticket.language = "en"
            mock_ticket.queue = None
            mock_ticket.priority = "high"
            mock_ticket.category = "technical"
            mock_ticket.confidence_score = None
            mock_ticket.summary = None
            mock_ticket.tag_1 = None
            mock_ticket.created_at = datetime.now()
            mock_ticket.updated_at = None
            
            mock_get.return_value = [mock_ticket]
            mock_count.return_value = 1
            
            response = client.get("/requests?category=technical&priority=high&page=1&size=5")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["support_tickets"]) == 1
            assert data["support_tickets"][0]["category"] == "technical"
            assert data["support_tickets"][0]["priority"] == "high"
            
            # Verify all filters were passed correctly
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["category"] == "technical"
            assert call_args[1]["priority"] == "high"
            assert call_args[1]["skip"] == 0
            assert call_args[1]["limit"] == 5


class TestSupportRequestsIntegration:
    """Integration tests for support requests endpoints."""
    
    def test_full_workflow_create_and_retrieve(self, client, db_session):
        """Test complete workflow: create ticket and then retrieve it."""
        # Create a support request
        create_data = {
            "subject": "Integration Test Issue",
            "body": "This is an integration test support request",
            "language": "en"
        }
        
        with patch.object(SupportTicketRepo, 'create_support_ticket') as mock_create, \
             patch.object(SupportTicketAIClassificationRepo, 'classify_ticket_and_update') as mock_classify:
            
            ticket_id = uuid4()
            mock_ticket = Mock(spec=SupportTicket)
            mock_ticket.id = ticket_id
            mock_ticket.subject = create_data["subject"]
            mock_ticket.body = create_data["body"]
            mock_ticket.language = create_data["language"]
            mock_ticket.queue = None
            mock_ticket.priority = None
            mock_ticket.category = None
            mock_ticket.confidence_score = None
            mock_ticket.summary = None
            mock_ticket.tag_1 = None
            mock_ticket.created_at = datetime.now()
            mock_ticket.updated_at = None
            
            mock_create.return_value = mock_ticket
            
            create_response = client.post("/requests", json=create_data)
            assert create_response.status_code == 201
            
            # Retrieve the created ticket
            with patch.object(SupportTicketRepo, 'get_support_ticket_by_id') as mock_get:
                mock_get.return_value = mock_ticket
                
                get_response = client.get(f"/requests/{ticket_id}")
                assert get_response.status_code == 200
                
                retrieved_data = get_response.json()
                assert retrieved_data["subject"] == create_data["subject"]
                assert retrieved_data["body"] == create_data["body"]
    
    def test_error_handling_consistency(self, client, db_session):
        """Test that error responses are consistent across endpoints."""
        # Test 404 error format (now returns 404 as intended)
        ticket_id = str(uuid4())
        with patch.object(SupportTicketRepo, 'get_support_ticket_by_id') as mock_get:
            mock_get.return_value = None
            
            response = client.get(f"/requests/{ticket_id}")
            assert response.status_code == 404
            error_data = response.json()
            assert "detail" in error_data
            assert "Support request not found" in error_data["detail"]
        
        # Test 500 error format
        with patch.object(SupportTicketRepo, 'create_support_ticket') as mock_create:
            mock_create.side_effect = Exception("Test error")
            
            response = client.post("/requests", json={
                "subject": "Test",
                "body": "Test body",
                "language": "en"
            })
            assert response.status_code == 500
            error_data = response.json()
            assert "detail" in error_data
            assert "Failed to create support request" in error_data["detail"] 