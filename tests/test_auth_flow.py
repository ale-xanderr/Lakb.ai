"""
Integration tests for authentication workflows.

Tests cover complete authentication flows including sign-up, sign-in,
session persistence, and password reset.
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.integration
@pytest.mark.auth
class TestAuthenticationFlows:
    """Integration tests for authentication workflows."""
    
    @pytest.fixture
    def auth_service(self, mock_supabase_client):
        """Create AuthService with mocked Supabase."""
        from src.services.auth_service import AuthService
        with patch('src.services.auth_service.get_supabase_client', return_value=mock_supabase_client):
            return AuthService()
    
    def test_complete_sign_up_flow(self, auth_service, mock_page):
        """Test complete user sign-up workflow."""
        # Step 1: Sign up new user
        mock_response = Mock()
        mock_response.user = Mock(id="new-user-123", email="newuser@example.com")
        auth_service.client.auth.sign_up.return_value = mock_response
        
        result = auth_service.sign_up("newuser@example.com", "password123")
        
        assert result is not None
        auth_service.client.auth.sign_up.assert_called_once()
    
    def test_complete_sign_in_flow(self, auth_service, mock_page, mock_supabase_session):
        """Test complete user sign-in workflow."""
        # Step 1: Sign in with credentials
        mock_response = Mock()
        mock_response.session = mock_supabase_session
        auth_service.client.auth.sign_in_with_password.return_value = mock_response
        
        sign_in_result = auth_service.sign_in_with_password("test@example.com", "password123")
        
        assert sign_in_result.session is not None
        
        # Step 2: Save session to storage
        auth_service.client.auth.get_session.return_value = mock_supabase_session
        auth_service.save_session_to_storage(mock_page)
        
        mock_page.client_storage.set.assert_called()
        
        # Step 3: Verify user is authenticated
        mock_user = Mock(id="test-user-123", email="test@example.com")
        auth_service.client.auth.get_user.return_value = mock_user  # Return user directly
        
        user = auth_service.get_user()
        
        assert user is not None
        assert user.email == "test@example.com"
    
    def test_session_persistence_flow(self, auth_service, mock_page, mock_supabase_session):
        """Test session persists across app restarts."""
        # Step 1: User signs in and session is saved
        mock_page.client_storage.get.return_value = {
            "access_token": "saved-token",
            "refresh_token": "saved-refresh"
        }
        
        # Step 2: App restarts, session is restored
        mock_restore = Mock()
        mock_restore.session = mock_supabase_session
        auth_service.client.auth.set_session.return_value = mock_restore
        
        restored = auth_service.restore_session_from_storage(mock_page)
        
        assert restored is True
        auth_service.client.auth.set_session.assert_called_once()
    
    def test_password_reset_flow(self, auth_service):
        """Test complete password reset workflow."""
        # Step 1: Request password reset
        auth_service.client.auth.reset_password_for_email.return_value = Mock()
        
        reset_request = auth_service.reset_password_for_email("test@example.com")
        
        assert reset_request is not None
        auth_service.client.auth.reset_password_for_email.assert_called_once()
    
    def test_sign_out_flow(self, auth_service, mock_page):
        """Test complete sign-out workflow."""
        # User is signed in
        auth_service.client.auth.sign_out.return_value = Mock()
        
        # Sign out
        auth_service.sign_out(mock_page)
        
        # Verify session cleared
        auth_service.client.auth.sign_out.assert_called_once()
        mock_page.client_storage.remove.assert_called()
