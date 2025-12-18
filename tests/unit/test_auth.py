import pytest

from app.bootstrap.config import Settings
from app.core.exceptions import TwitterAuthenticationError
from app.infrastructure.twitter.auth import TwitterAuthenticator


class TestTwitterAuthenticator:
    def test_init_with_valid_token(self, test_settings: Settings):
        auth = TwitterAuthenticator(test_settings)
        
        assert auth.settings == test_settings
    
    def test_init_with_empty_token_raises_error(self, test_settings: Settings):
        test_settings.twitter_bearer_token = ""
        
        with pytest.raises(TwitterAuthenticationError) as exc_info:
            TwitterAuthenticator(test_settings)
        
        assert "Twitter Bearer Token is not configured" in str(exc_info.value)
    
    def test_get_headers_returns_correct_format(self, test_settings: Settings):
        auth = TwitterAuthenticator(test_settings)
        
        headers = auth.get_headers()
        
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_bearer_token"
        assert headers["Content-Type"] == "application/json"
    
    def test_get_headers_includes_all_required_fields(self, test_settings: Settings):
        auth = TwitterAuthenticator(test_settings)
        
        headers = auth.get_headers()
        
        assert len(headers) == 2
        assert "Authorization" in headers
        assert "Content-Type" in headers

