import pytest
from unittest.mock import patch, Mock
from fastapi import HTTPException

from app.repository.stats_repo import StatsRepo
from app.schemas.stats import StatsResponse


class TestGetStatistics:
    """Test cases for GET /stats endpoint."""
    
    def test_get_statistics_success_default_days(self, client, db_session):
        """Test successful retrieval of statistics with default days parameter."""
        mock_stats_data = {
            "total_support_tickets": 25,
            "category_counts": {
                "technical": 15,
                "billing": 7,
                "general": 3
            },
            "priority_counts": {
                "high": 5,
                "medium": 12,
                "low": 8
            },
            "avg_confidence": 0.845,
            "last_7_days": {
                "2024-01-01": 5,
                "2024-01-02": 3,
                "2024-01-03": 7,
                "2024-01-04": 2,
                "2024-01-05": 4,
                "2024-01-06": 3,
                "2024-01-07": 1
            }
        }
        
        with patch.object(StatsRepo, 'get_stats') as mock_get_stats:
            mock_get_stats.return_value = mock_stats_data
            
            response = client.get("/stats")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure matches StatsResponse schema
            assert data["total_support_tickets"] == 25
            assert data["category_counts"]["technical"] == 15
            assert data["category_counts"]["billing"] == 7
            assert data["category_counts"]["general"] == 3
            assert data["priority_counts"]["high"] == 5
            assert data["priority_counts"]["medium"] == 12
            assert data["priority_counts"]["low"] == 8
            assert data["avg_confidence"] == 0.845
            assert len(data["last_7_days"]) == 7
            
            # Verify StatsRepo was called with default days=7
            mock_get_stats.assert_called_once_with(db_session, days=7)
    
    def test_get_statistics_success_custom_days(self, client, db_session):
        """Test successful retrieval of statistics with custom days parameter."""
        mock_stats_data = {
            "total_support_tickets": 100,
            "category_counts": {
                "technical": 60,
                "billing": 25,
                "general": 15
            },
            "priority_counts": {
                "high": 20,
                "medium": 50,
                "low": 30
            },
            "avg_confidence": 0.762,
            "last_7_days": {
                "2024-01-01": 10,
                "2024-01-02": 15,
                "2024-01-03": 8
            }
        }
        
        with patch.object(StatsRepo, 'get_stats') as mock_get_stats:
            mock_get_stats.return_value = mock_stats_data
            
            response = client.get("/stats?days=30")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["total_support_tickets"] == 100
            assert data["avg_confidence"] == 0.762
            
            # Verify StatsRepo was called with days=30
            mock_get_stats.assert_called_once_with(db_session, days=30)
    
    def test_get_statistics_success_minimum_days(self, client, db_session):
        """Test successful retrieval with minimum days value (1)."""
        mock_stats_data = {
            "total_support_tickets": 5,
            "category_counts": {"technical": 3, "billing": 2},
            "priority_counts": {"high": 1, "medium": 4},
            "avg_confidence": 0.9,
            "last_7_days": {"2024-01-01": 5}
        }
        
        with patch.object(StatsRepo, 'get_stats') as mock_get_stats:
            mock_get_stats.return_value = mock_stats_data
            
            response = client.get("/stats?days=1")
            
            assert response.status_code == 200
            mock_get_stats.assert_called_once_with(db_session, days=1)
    
    def test_get_statistics_success_maximum_days(self, client, db_session):
        """Test successful retrieval with maximum days value (365)."""
        mock_stats_data = {
            "total_support_tickets": 1500,
            "category_counts": {"technical": 800, "billing": 400, "general": 300},
            "priority_counts": {"high": 300, "medium": 800, "low": 400},
            "avg_confidence": 0.812,
            "last_7_days": {"2024-01-01": 100}
        }
        
        with patch.object(StatsRepo, 'get_stats') as mock_get_stats:
            mock_get_stats.return_value = mock_stats_data
            
            response = client.get("/stats?days=365")
            
            assert response.status_code == 200
            mock_get_stats.assert_called_once_with(db_session, days=365)
    
    def test_get_statistics_empty_data(self, client, db_session):
        """Test successful retrieval when no data is available."""
        mock_stats_data = {
            "total_support_tickets": 0,
            "category_counts": {},
            "priority_counts": {},
            "avg_confidence": 0.0,
            "last_7_days": {}
        }
        
        with patch.object(StatsRepo, 'get_stats') as mock_get_stats:
            mock_get_stats.return_value = mock_stats_data
            
            response = client.get("/stats")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["total_support_tickets"] == 0
            assert data["category_counts"] == {}
            assert data["priority_counts"] == {}
            assert data["avg_confidence"] == 0.0
            assert data["last_7_days"] == {}
    
    def test_get_statistics_invalid_days_too_low(self, client):
        """Test validation error when days parameter is too low (0)."""
        response = client.get("/stats?days=0")
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data
        # Check that the validation error mentions the constraint
        assert any("greater than or equal to 1" in str(error).lower() 
                 for error in error_data["detail"])
    
    def test_get_statistics_invalid_days_negative(self, client):
        """Test validation error when days parameter is negative."""
        response = client.get("/stats?days=-5")
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data
    
    def test_get_statistics_invalid_days_too_high(self, client):
        """Test validation error when days parameter is too high (>365)."""
        response = client.get("/stats?days=400")
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data
        # Check that the validation error mentions the constraint
        assert any("less than or equal to 365" in str(error).lower() 
                 for error in error_data["detail"])
    
    def test_get_statistics_invalid_days_non_integer(self, client):
        """Test validation error when days parameter is not an integer."""
        response = client.get("/stats?days=invalid")
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data
    
    def test_get_statistics_invalid_days_float(self, client):
        """Test validation error when days parameter is a float."""
        response = client.get("/stats?days=7.5")
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data
    
    def test_get_statistics_repository_error(self, client, db_session):
        """Test handling of repository errors during statistics retrieval."""
        with patch.object(StatsRepo, 'get_stats') as mock_get_stats:
            mock_get_stats.side_effect = Exception("Database connection error")
            
            response = client.get("/stats")
            
            assert response.status_code == 500
            error_data = response.json()
            assert "detail" in error_data
            assert "Failed to retrieve statistics" in error_data["detail"]
            assert "Database connection error" in error_data["detail"]
    
    def test_get_statistics_repository_database_error(self, client, db_session):
        """Test handling of specific database errors."""
        with patch.object(StatsRepo, 'get_stats') as mock_get_stats:
            mock_get_stats.side_effect = Exception("Table 'support_tickets' doesn't exist")
            
            response = client.get("/stats")
            
            assert response.status_code == 500
            error_data = response.json()
            assert "Failed to retrieve statistics" in error_data["detail"]
    
    def test_get_statistics_response_schema_validation(self, client, db_session):
        """Test that the response matches the StatsResponse schema exactly."""
        mock_stats_data = {
            "total_support_tickets": 42,
            "category_counts": {"technical": 20, "billing": 15, "general": 7},
            "priority_counts": {"high": 10, "medium": 20, "low": 12},
            "avg_confidence": 0.876,
            "last_7_days": {
                "2024-01-01": 6,
                "2024-01-02": 8,
                "2024-01-03": 4
            }
        }
        
        with patch.object(StatsRepo, 'get_stats') as mock_get_stats:
            mock_get_stats.return_value = mock_stats_data
            
            response = client.get("/stats")
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate all required fields are present
            required_fields = [
                "total_support_tickets", 
                "category_counts", 
                "priority_counts", 
                "avg_confidence", 
                "last_7_days"
            ]
            for field in required_fields:
                assert field in data, f"Required field '{field}' missing from response"
            
            # Validate data types
            assert isinstance(data["total_support_tickets"], int)
            assert isinstance(data["category_counts"], dict)
            assert isinstance(data["priority_counts"], dict)
            assert isinstance(data["avg_confidence"], float)
            assert isinstance(data["last_7_days"], dict)
            
            # Validate that the response can be parsed by StatsResponse model
            stats_response = StatsResponse(**data)
            assert stats_response.total_support_tickets == 42
            assert stats_response.avg_confidence == 0.876
    
    def test_get_statistics_boundary_values(self, client, db_session):
        """Test statistics retrieval with boundary values for days parameter."""
        test_cases = [
            (1, "minimum boundary"),
            (7, "default value"),
            (30, "common monthly value"),
            (90, "quarterly value"),
            (365, "maximum boundary")
        ]
        
        mock_stats_data = {
            "total_support_tickets": 10,
            "category_counts": {"technical": 5, "billing": 3, "general": 2},
            "priority_counts": {"high": 2, "medium": 5, "low": 3},
            "avg_confidence": 0.75,
            "last_7_days": {"2024-01-01": 10}
        }
        
        for days_value, description in test_cases:
            with patch.object(StatsRepo, 'get_stats') as mock_get_stats:
                mock_get_stats.return_value = mock_stats_data
                
                response = client.get(f"/stats?days={days_value}")
                
                assert response.status_code == 200, f"Failed for {description} (days={days_value})"
                mock_get_stats.assert_called_once_with(db_session, days=days_value)
    
    def test_get_statistics_logging_on_error(self, client, db_session):
        """Test that errors are properly logged when repository fails."""
        with patch.object(StatsRepo, 'get_stats') as mock_get_stats, \
             patch('app.routes.stats.logger') as mock_logger:
            
            test_error = Exception("Test database error")
            mock_get_stats.side_effect = test_error
            
            response = client.get("/stats")
            
            assert response.status_code == 500
            
            # Verify that the error was logged
            mock_logger.log_api_error.assert_called_once_with(
                method="GET",
                path="/stats",
                status_code=500,
                error="Test database error"
            )
    
    def test_get_statistics_query_parameter_parsing(self, client, db_session):
        """Test that query parameters are correctly parsed and passed."""
        mock_stats_data = {
            "total_support_tickets": 15,
            "category_counts": {"technical": 10, "billing": 5},
            "priority_counts": {"high": 3, "medium": 8, "low": 4},
            "avg_confidence": 0.82,
            "last_7_days": {"2024-01-01": 15}
        }
        
        with patch.object(StatsRepo, 'get_stats') as mock_get_stats:
            mock_get_stats.return_value = mock_stats_data
            
            # Test with explicit days parameter
            response = client.get("/stats?days=14")
            
            assert response.status_code == 200
            mock_get_stats.assert_called_once_with(db_session, days=14)
            
            # Reset mock
            mock_get_stats.reset_mock()
            
            # Test without days parameter (should use default)
            response = client.get("/stats")
            
            assert response.status_code == 200
            mock_get_stats.assert_called_once_with(db_session, days=7) 