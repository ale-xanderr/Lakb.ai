"""
Unit tests for state controllers.

Tests cover app state management and authentication state controllers.
"""

import pytest
from unittest.mock import Mock, MagicMock
import flet as ft


@pytest.mark.unit
@pytest.mark.state
class TestAppStateManager:
    """Test suite for AppStateManager."""
    
    @pytest.fixture
    def mock_page(self):
        """Create a mock Flet page."""
        page = Mock(spec=ft.Page)
        page.client_storage = Mock()
        page.client_storage.get = Mock(return_value=None)
        page.client_storage.set = Mock()
        page.theme_mode = ft.ThemeMode.SYSTEM
        page.update = Mock()
        return page
    
    @pytest.fixture
    def state_manager(self, mock_page):
        """Create AppStateManager instance."""
        from src.state.app_state_manager import AppStateManager
        return AppStateManager(mock_page)
    
    def test_initialization(self, state_manager, mock_page):
        """Test AppStateManager initializes correctly."""
        assert state_manager is not None
        assert state_manager.page == mock_page
        assert state_manager.is_initialized() is False
    
    def test_initialize_sets_initialized_flag(self, state_manager):
        """Test initialize sets the initialized flag."""
        state_manager.initialize()
        assert state_manager.is_initialized() is True
    
    def test_theme_mode_property(self, state_manager):
        """Test theme_mode property returns current theme."""
        assert state_manager.theme_mode in [ft.ThemeMode.DARK, ft.ThemeMode.LIGHT, ft.ThemeMode.SYSTEM]
    
    def test_set_theme_mode(self, state_manager, mock_page):
        """Test set_theme_mode updates theme."""
        state_manager.set_theme_mode(ft.ThemeMode.DARK)
        assert state_manager.theme_mode == ft.ThemeMode.DARK
        assert mock_page.theme_mode == ft.ThemeMode.DARK
    
    def test_toggle_theme(self, state_manager):
        """Test toggle_theme switches between light and dark."""
        initial_mode = state_manager.theme_mode
        state_manager.toggle_theme()
        assert state_manager.theme_mode != initial_mode


@pytest.mark.unit
@pytest.mark.state
@pytest.mark.auth
class TestAuthStateController:
    """Test suite for AuthStateController."""
    
    @pytest.fixture
    def mock_page(self):
        """Create a mock Flet page."""
        return Mock(spec=ft.Page)
    
    @pytest.fixture
    def auth_controller(self, mock_page):
        """Create AuthStateController with mocked page."""
        from src.state.auth_state_controller import AuthStateController
        return AuthStateController(mock_page)
    
    def test_initialization(self, auth_controller, mock_page):
        """Test AuthStateController initializes correctly."""
        assert auth_controller is not None
        assert auth_controller.page == mock_page
        assert auth_controller.is_authenticated is False
        assert auth_controller.is_guest is False
    
    def test_set_authenticated_updates_state(self, auth_controller):
        """Test set_authenticated updates authentication state."""
        mock_user = {"id": "123", "email": "test@example.com"}
        
        auth_controller.set_authenticated(mock_user)
        
        assert auth_controller.is_authenticated is True
        assert auth_controller.user == mock_user
        assert auth_controller.is_guest is False
    
    def test_set_guest_updates_state(self, auth_controller):
        """Test set_guest updates guest state."""
        auth_controller.set_guest()
        
        assert auth_controller.is_authenticated is False
        assert auth_controller.is_guest is True
        assert auth_controller.user is None
    
    def test_set_unauthenticated_clears_state(self, auth_controller):
        """Test set_unauthenticated clears state."""
        # First authenticate
        auth_controller.set_authenticated({"id": "123"})
        
        # Then clear
        auth_controller.set_unauthenticated()
        
        assert auth_controller.is_authenticated is False
        assert auth_controller.is_guest is False
        assert auth_controller.user is None
    
    def test_reset_clears_state(self, auth_controller):
        """Test reset clears authentication state."""
        auth_controller.set_authenticated({"id": "123"})
        
        auth_controller.reset()
        
        assert auth_controller.is_authenticated is False
        assert auth_controller.user is None
    
    def test_user_setter(self, auth_controller):
        """Test user setter updates authentication."""
        mock_user = {"id": "123"}
        
        auth_controller.user = mock_user
        
        assert auth_controller.user == mock_user
        assert auth_controller.is_authenticated is True
    
    def test_loading_state(self, auth_controller):
        """Test loading state can be set."""
        assert auth_controller.is_loading is False
        
        auth_controller.is_loading = True
        
        assert auth_controller.is_loading is True
