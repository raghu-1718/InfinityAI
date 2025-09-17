from core.usermanager import get_user_by_username

user = get_user_by_username('admin')
print('User found:', user is not None)
if user:
    print('Username:', user['username'])
    print('Role:', user['role'])
else:
    print('Admin user not found in database')
