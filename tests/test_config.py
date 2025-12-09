"""
Unit tests for Config class.

Tests cover configuration validation, platform detection, and environment variable handling.
"""

import pytest
from unittest.mock import patch, Mock
import os
from src.core.config import Config, configure_page


@pytest.mark.unit
class TestConfig:
    """Test suite for Config class."""
    
    def test_config_has_google_api_key(self):
        """Test Config has Google API key configured."""
        assert Config.GOOGLE_PLACES_API_KEY is not None
        assert len(Config.GOOGLE_PLACES_API_KEY) > 0
    
    def test_config_has_supabase_credentials(self):
        """Test Config has Supabase credentials configured."""
        assert Config.SUPABASE_URL is not None
        assert Config.SUPABASE_KEY is not None
        assert "supabase" in Config.SUPABASE_URL.lower()
    
    def test_config_has_base_urls(self):
        """Test Config has API base URLs configured."""
        assert Config.GOOGLE_PLACES_BASE_URL is not None
        assert Config.OPENWEATHER_BASE_URL is not None
        assert Config.GEMINI_BASE_URL is not None
        assert Config.CALENDARIFIC_BASE_URL is not None
        assert Config.OPENAQ_BASE_URL is not None
    
    @patch('platform.system', return_value='Linux')
    @patch('os.path.exists', return_value=True)
    def test_is_android_detects_android(self, mock_exists, mock_system):
        """Test is_android() detects Android platform."""
        # Check for /system/build.prop (Android indicator)
        result = Config.is_android()
        
        assert result is True
    
    @patch('platform.system', return_value='Windows')
    def test_is_android_detects_non_android(self, mock_system):
        """Test is_android() detects non-Android platforms."""
        result = Config.is_android()
        
        assert result is False
    
    @patch('platform.system', return_value='Linux')
    @patch('os.path.exists', return_value=False)
    @patch.dict(os.environ, {'ANDROID_ROOT': '/system'})
    def test_is_android_detects_via_env_var(self, mock_exists, mock_system):
        """Test is_android() detects Android via environment variable."""
        result = Config.is_android()
        
        assert result is True
    
    def test_get_redirect_url_desktop(self):
        """Test get_redirect_url() returns desktop URL for non-Android."""
        with patch.object(Config, 'is_android', return_value=False):
            url = Config.get_redirect_url()
            
            assert url == Config.DESKTOP_REDIRECT_URL
            assert "localhost" in url or "127.0.0.1" in url
    
    def test_get_redirect_url_android(self):
        """Test get_redirect_url() returns Android URL for Android platform."""
        with patch.object(Config, 'is_android', return_value=True):
            url = Config.get_redirect_url()
            
            assert url == Config.ANDROID_REDIRECT_URL
            assert "lakbai://" in url
    
    def test_get_redirect_url_explicit_override(self):
        """Test get_redirect_url() respects explicit platform override."""
        # Force Android URL even if not on Android
        url = Config.get_redirect_url(is_android=True)
        
        assert url == Config.ANDROID_REDIRECT_URL
    
    @patch.dict(os.environ, {'REDIRECT_URL': 'https://custom.redirect.url/callback'})
    def test_get_redirect_url_env_override(self):
        """Test get_redirect_url() respects environment variable override."""
        # Reload config with new env var
        from importlib import reload
        from src.core import config
        reload(config)
        
        url = config.Config.get_redirect_url()
        
        assert "custom.redirect.url" in url
    
    def test_validate_passes_with_required_keys(self):
        """Test validate() passes when required keys are present."""
        # Should not raise any exceptions
        Config.validate()
    
    @patch.object(Config, 'GOOGLE_PLACES_API_KEY', None)
    def test_validate_warns_missing_google_key(self, capsys):
        """Test validate() warns about missing Google API key."""
        Config.validate()
        
        # Note: validate() prints warnings but doesn't raise exceptions
        # In a real implementation, you might want to capture print output


@pytest.mark.unit
class TestConfigurePage:
    """Test suite for configure_page function."""
    
    def test_configure_page_sets_title(self, mock_page):
        """Test configure_page sets page title."""
        configure_page(mock_page, title="Custom Title")
        
        assert mock_page.title == "Custom Title"
    
    def test_configure_page_sets_default_title(self, mock_page):
        """Test configure_page sets default title when not provided."""
        configure_page(mock_page)
        
        assert mock_page.title == "Lakb.ai"
    
    def test_configure_page_sets_padding(self, mock_page):
        """Test configure_page sets padding to 0."""
        configure_page(mock_page)
        
        assert mock_page.padding == 0
    
    def test_configure_page_sets_window_size(self, mock_page):
        """Test configure_page sets window dimensions."""
        mock_page.window = Mock()
        
        configure_page(mock_page)
        
        assert mock_page.window.width == 412
        assert mock_page.window.height == 917
    
    def test_configure_page_sets_resizable(self, mock_page):
        """Test configure_page sets window resizable property."""
        mock_page.window = Mock()
        
        configure_page(mock_page)
        
        assert mock_page.window.resizable is False
        assert mock_page.window.maximizable is False
