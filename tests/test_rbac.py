import pytest
from core.rbac import RBAC_MATRIX

def test_admin_permissions():
    perms = RBAC_MATRIX["admin"]
    assert "view_users" in perms
    assert "edit_users" in perms
    assert "view_trades" in perms
    assert "edit_trades" in perms
    assert "view_audit" in perms
    assert "edit_audit" in perms
    assert "view_analytics" in perms
    assert "edit_analytics" in perms

def test_user_permissions():
    perms = RBAC_MATRIX["user"]
    assert "view_trades" in perms
    assert "edit_trades" in perms
    assert "view_analytics" in perms
    assert "edit_audit" not in perms

def test_auditor_permissions():
    perms = RBAC_MATRIX["auditor"]
    assert "view_audit" in perms
    assert "view_users" in perms
    assert "edit_users" not in perms
