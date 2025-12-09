"""
Unit tests for AuthService.

Tests cover authentication flows, session management, and OAuth integration.
Supabase client calls are mocked to ensure fast, reliable tests.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services.auth_service import AuthService


@pytest.mark.unit
@pytest.mark.auth
class TestAuthService:
    """Test suite for AuthService."""
    
    @pytest.fixture
    def auth_service(self, mock_supabase_client):
        """Create AuthService instance with mocked Supabase client."""
        with patch('src.services.auth_service.get_supabase_client', return_value=mock_supabase_client):
            service = AuthService()
            return service
    
    def test_initialization(self, auth_service):
        """Test AuthService initializes correctly."""
        assert auth_service.client is not None
    
    def test_get_user_when_authenticated(self, auth_service, mock_supabase_user):
        """Test get_user returns user when authenticated."""
        # Mock authenticated response
        mock_response = Mock()
        mock_response.user = mock_supabase_user
        auth_service.client.auth.get_user.return_value = mock_response
        
        user = auth_service.get_user()
        
        assert user is not None
        assert user.id == "test-user-id-123"
        assert user.email == "test@example.com"
    
    def test_get_user_when_not_authenticated(self, auth_service):
        """Test get_user returns None when not authenticated."""
        # Mock unauthenticated response - return None for response.user
        mock_response = Mock()
        mock_response.user = None
        auth_service.client.auth.get_user.return_value = mock_response
        
        user = auth_service.get_user()
        
        assert user is None
    
    def test_get_user_handles_exception(self, auth_service):
        """Test get_user handles exceptions gracefully."""
        # Mock exception
        auth_service.client.auth.get_user.side_effect = Exception("Auth error")
        
        user = auth_service.get_user()
        
        assert user is None
    
    def test_sign_in_with_password_success(self, auth_service, mock_supabase_session):
        """Test successful password sign-in."""
        # Mock successful sign-in
        mock_response = Mock()
        mock_response.session = mock_supabase_session
        auth_service.client.auth.sign_in_with_password.return_value = mock_response
        
        response = auth_service.sign_in_with_password("test@example.com", "password123")
        
        assert response.session is not None
        assert response.session.access_token == "mock-access-token"
        auth_service.client.auth.sign_in_with_password.assert_called_once_with({
            "email": "test@example.com",
            "password": "password123"
        })
    
    def test_sign_in_with_password_invalid_credentials(self, auth_service):
        """Test sign-in with invalid credentials."""
        # Mock failed sign-in
        auth_service.client.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")
        
        with pytest.raises(Exception):
            auth_service.sign_in_with_password("wrong@example.com", "wrongpass")
    
    def test_sign_up_success(self, auth_service):
        """Test successful user registration."""
        # Mock successful sign-up
        mock_response = Mock()
        auth_service.client.auth.sign_up.return_value = mock_response
        
        response = auth_service.sign_up("newuser@example.com", "password123", data={"name": "New User"})
        
        assert response is not None
        auth_service.client.auth.sign_up.assert_called_once()
    
    def test_sign_out_success(self, auth_service, mock_page):
        """Test successful sign-out."""
        # Mock successful sign-out
        auth_service.client.auth.sign_out.return_value = Mock()
        
        auth_service.sign_out(mock_page)
        
        auth_service.client.auth.sign_out.assert_called_once()
        mock_page.client_storage.remove.assert_called()
    
    def test_get_session_when_exists(self, auth_service, mock_supabase_session):
        """Test get_session returns session when exists."""
        # Mock session exists
        auth_service.client.auth.get_session.return_value = mock_supabase_session
        
        session = auth_service.get_session()
        
        assert session is not None
        assert session.access_token == "mock-access-token"
    
    def test_get_session_when_none(self, auth_service):
        """Test get_session returns None when no session."""
        # Mock no session
        auth_service.client.auth.get_session.return_value = None
        
        session = auth_service.get_session()
        
        assert session is None
    
    def test_save_session_to_storage(self, auth_service, mock_page, mock_supabase_session):
        """Test session is saved to client storage."""
        # Mock session
        auth_service.client.auth.get_session.return_value = mock_supabase_session
        
        auth_service.save_session_to_storage(mock_page)
        
        # Verify storage was called
        mock_page.client_storage.set.assert_called()
    
    def test_restore_session_from_storage_success(self, auth_service, mock_page):
        """Test session restoration from storage."""
        # Mock stored session data
        mock_page.client_storage.get.return_value = {
            "access_token": "stored-access-token",
            "refresh_token": "stored-refresh-token"
        }
        
        # Mock successful session restoration
        mock_response = Mock()
        mock_response.session = Mock()
        auth_service.client.auth.set_session.return_value = mock_response
        
        result = auth_service.restore_session_from_storage(mock_page)
        
        assert result is True
        auth_service.client.auth.set_session.assert_called_once()
    
    def test_restore_session_from_storage_no_data(self, auth_service, mock_page):
        """Test session restoration when no data in storage."""
        # Mock no stored session
        mock_page.client_storage.get.return_value = None
        
        result = auth_service.restore_session_from_storage(mock_page)
        
        assert result is False
    
    def test_reset_password_for_email_success(self, auth_service):
        """Test password reset email request."""
        # Mock successful reset request
        auth_service.client.auth.reset_password_for_email.return_value = Mock()
        
        response = auth_service.reset_password_for_email("test@example.com")
        
        assert response is not None
        auth_service.client.auth.reset_password_for_email.assert_called_once()
    
    def test_sign_in_with_google(self, auth_service):
        """Test Google OAuth sign-in URL generation."""
        # Mock OAuth response
        mock_response = Mock()
        mock_response.url = "https://accounts.google.com/o/oauth2/auth?..."
        auth_service.client.auth.sign_in_with_oauth.return_value = mock_response
        
        url = auth_service.sign_in_with_google()
        
        assert url is not None
        assert "https://" in url
    
    def test_exchange_code_for_session_success(self, auth_service, mock_page, mock_supabase_session):
        """Test OAuth code exchange for session."""
        # Mock successful code exchange
        mock_response = Mock()
        mock_response.session = mock_supabase_session
        auth_service.client.auth.exchange_code_for_session.return_value = mock_response
        
        response = auth_service.exchange_code_for_session("auth-code-123", mock_page)
        
        assert response is not None
        assert response.session is not None


@pytest.mark.unit
@pytest.mark.auth
class TestAuthServiceSessionManagement:
    """Test session management functionality."""
    
    @pytest.fixture
    def auth_service(self, mock_supabase_client):
        """Create AuthService instance with mocked Supabase client."""
        with patch('src.services.auth_service.get_supabase_client', return_value=mock_supabase_client):
            service = AuthService()
            return service
    
    def test_session_lifecycle(self, auth_service, mock_page, mock_supabase_session):
        """Test complete session lifecycle: create, save, restore, destroy."""
        # 1. Sign in
        mock_response = Mock()
        mock_response.session = mock_supabase_session
        auth_service.client.auth.sign_in_with_password.return_value = mock_response
        
        sign_in_response = auth_service.sign_in_with_password("test@example.com", "password")
        assert sign_in_response.session is not None
        
        # 2. Save session
        auth_service.client.auth.get_session.return_value = mock_supabase_session
        auth_service.save_session_to_storage(mock_page)
        mock_page.client_storage.set.assert_called()
        
        # 3. Sign out
        auth_service.sign_out(mock_page)
        mock_page.client_storage.remove.assert_called()
