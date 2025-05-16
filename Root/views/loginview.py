from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from Root.serializers.baseserializers import *
from Root.serializers.loginserializer import *
from django.contrib.auth import authenticate
from rest_framework import status, exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

class ExampleView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        data = { 
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        return Response(data)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Manually authenticate user using email
            user = authenticate(request, username=email, password=password)
            if user is not None:
                # Generate JWT token
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                # Ensure user has a related customer object, if applicable
                try:
                    customer_id = user.customer.id  # Assuming you have a related Customer model
                except AttributeError:
                    customer_id = None  # Handle if customer doesn't exist

                # Prepare user data for response
                user_data = {
                    'id': str(user.id),
                    'name': user.get_full_name(),  # Use get_full_name() or user.username
                    'customer_id': customer_id,
                    'isSuperAdmin': user.is_superuser,
                }

                # Determine user role
                role = "ADMIN" if user.is_superuser else "USER"

                return Response({
                    'user': user_data,
                    'token': access_token,
                    'role': role,
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            return Response({'access': str(access_token)})
        except TokenError:
            return Response({'error': 'Invalid refresh token'}, status_code=401)

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Returns the user associated with the given token, if any.
        """
        try:
            user_id = validated_token['user_id']
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
    def authenticate(self, request):
        # Get the Authorization header from the request
        header = self.get_header(request)
        if header is None:
            return None

        # Get the raw token from the header
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        # Validate the token
        validated_token = self.get_validated_token(raw_token)
        print(validated_token)
        if not validated_token:
            raise exceptions.AuthenticationFailed(
                'Invalid or expired token',
                code=status.HTTP_401_UNAUTHORIZED
            )

        # Get the user from the validated token
        user = User.objects.get(pk=validated_token['user_id'])
        if not user:
            raise exceptions.AuthenticationFailed(
                'User not found',
                code=status.HTTP_401_UNAUTHORIZED
            )

        # Return the user and the validated token
        return (user, validated_token)