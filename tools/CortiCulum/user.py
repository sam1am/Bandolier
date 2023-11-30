DEFAULT_USER_NAME = 'user'

user = {
    'name': DEFAULT_USER_NAME,
}

def set_user_name(name):
    """Set the user's name."""
    user['name'] = name

def get_user_name():
    """Get the user's name."""
    return user['name']
