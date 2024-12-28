# users/views.py
from rest_framework import generics
from rest_framework.permissions import AllowAny,IsAuthenticated
from .models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView


class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()  
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
 
    def post(self, request):
        # You can clear the session or token here
        request.auth.delete()  # for token-based auth
        return Response({"detail": "Successfully logged out."}, status=200)
