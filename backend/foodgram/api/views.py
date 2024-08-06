from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import authenticate
from .serializers import UserCreateSerializer


class RegisterView(GenericAPIView):
    serializer_class = UserCreateSerializer
    #permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=serializer.validated_data['email'],
                            password=serializer.validated_data['password'])
        if user:
            access = AccessToken.for_user(user)
            return Response({'auth_token': str(access)}, status=status.HTTP_200_OK)
        return Response({'message': 'Wrong credentials'}, status=status.HTTP_400_BAD_REQUEST)