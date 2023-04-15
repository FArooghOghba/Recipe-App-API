"""
Views for user API.
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.settings import api_settings

from user.serializers import UserModelSerializer, AuthTokenSerializer


class UserCreateAPIView(generics.CreateAPIView):
    """Create a new user in the system."""

    serializer_class = UserModelSerializer


class CustomObtainAuthToken(ObtainAuthToken):
    """Create a new auth token for user."""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            }
        )


class UserProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Manage and update user data"""

    serializer_class = UserModelSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
