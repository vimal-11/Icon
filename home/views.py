from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import generics, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate, login, logout


from .models import *
from .serializers import *
# Create your views here.


# razorpay client
# razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@api_view(['GET'])
@permission_classes([permissions.DjangoModelPermissionsOrAnonReadOnly])
def student_list(request):
    students = Students.objects.all()
    serializer = StudentsSerializer(students, many=True)
    return Response(serializer.data)
    


class CustomUserCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]



class CustomAuthTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomAuthTokenView, self).post(request, *args, **kwargs)
        token = response.data['token']
        user = CustomUser.objects.get(auth_token=token)
        return Response({'token': token, 'email': user.email})


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')
        print(email, password)
        user = authenticate(request, username=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'success':True}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'success': True}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



# class LogoutView(APIView):
#     def post(self, request, format=None):
#         logout(request)
#         return Response(status=status.HTTP_204_NO_CONTENT)
    


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the user's token
        token = request.auth
        # Delete the token
        token.delete()
        return Response({'message': 'Logged out successfully.'})
    


class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Students.objects.all()
    serializer_class = StudentsSerializer



class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Students.objects.all()
    serializer_class = StudentsSerializer



class RegistrationCreateView(generics.CreateAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer



class RegisteredEventsView(generics.ListAPIView):
    serializer_class = RegistrationSerializer

    def get_queryset(self):
        # Get the student_id from the URL parameters
        student_id = self.kwargs['student_id']
        # Filter registrations by the student_id
        queryset = Registration.objects.filter(student__id=student_id)
        return queryset
    


class EventsByCategoryView(generics.ListAPIView):
    serializer_class = EventsSerializer

    def get_queryset(self):
        # Get the category from the URL parameters
        category = self.kwargs['category']
        # Filter events by the category
        queryset = Events.objects.filter(category=category)
        return queryset
    


class TeamsListCreateView(generics.ListCreateAPIView):
    queryset = Teams.objects.all()
    serializer_class = TeamsSerializer



class TeamsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teams.objects.all()
    serializer_class = TeamsSerializer