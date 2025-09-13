# RBAC roles and permissions
RBAC_MATRIX = {
    'admin': ['view_users', 'edit_users', 'view_trades', 'edit_trades', 'view_audit', 'edit_audit', 'view_analytics', 'edit_analytics'],
    'user': ['view_trades', 'edit_trades', 'view_analytics'],
    'auditor': ['view_audit', 'view_users', 'view_trades', 'view_analytics']
}
