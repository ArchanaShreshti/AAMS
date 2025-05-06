from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
       
        print(f"Attempting to authenticate user with email: {username}")  # Debugging line
        try:
            # Look up the user by email
            user = get_user_model().objects.get(email=username)
            print(f"User found: {user}")  # Debugging line
            if user.check_password(password):
                print(f"Password correct for user: {user}")  # Debugging line
                return user
            else:
                print(f"Password incorrect for user: {user}")  # Debugging line
        except get_user_model().DoesNotExist:
            print("User not found")  # Debugging line
            return None