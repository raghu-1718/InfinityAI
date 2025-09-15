
import pytest
from core.usermanager import get_user_credentials

def test_get_user_credentials():
    user = get_user_credentials(1)
    assert user is not None
