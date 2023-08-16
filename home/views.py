from django.conf import settings
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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import razorpay


from .models import *
from .serializers import *
# Create your views here.


# razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

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
        user = authenticate(request, username=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id, 'success': True}, status=status.HTTP_200_OK)
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
    



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    user = request.user
    data = {'username': user.email}
    return Response(data)


class StudentListCreateView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Students.objects.all()
    serializer_class = StudentsSerializer

    def post(self, request, *args, **kwargs):
        # Print the received authentication token from frontend
        auth_token = request.auth
        print("Received authentication token:",auth_token)
        print(request.data)
        email=request.user
        user=CustomUser.objects.get(email=email)
        print(user)
        data = {
            'name': request.data.get('name'),
            'college': request.data.get('college'),
            'dept': request.data.get('dept'),
            'year': request.data.get('year'),
            'email': user, 
            'ph_no': request.data.get('ph_no'),
            # 'id_card': request.data.get('id_card'),
        }

        # Create a Student object
        student = Students(**data)
        student.save()
        # get id card file
        id_card_image = request.FILES.get('id_card')
        if id_card_image:
            # Save the ID card image
            student.id_card.save(id_card_image.name, id_card_image, save=True)
        student.save()
        return Response({"message": "Student object created successfully."})




class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
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

    def perform_create(self, serializer):
        team = serializer.save()  # Save the team
        # Create registration objects for each team member
        for member in team.team_member.all():
            Registration.objects.create(event=team.event, student=member)
        # If you want to return the created team along with its registrations in the response
        serializer.instance = team



class TeamsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teams.objects.all()
    serializer_class = TeamsSerializer




class RazorpayPaymentView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, format=None):
        student_id = request.data.get('student_id')
        event_id = request.data.get('event_id')
        amount = request.data.get('amount')  # Amount in paisa

        # Get the student and event
        try:
            student = Students.objects.get(pk=student_id)
            event = Events.objects.get(pk=event_id)
        except (Students.DoesNotExist, Events.DoesNotExist):
            return Response({'error': 'Student or Event not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create an order
        response = razorpay_client.order.create({'amount': amount, 'currency': 'INR'})

        # Save payment details to the database
        payment = Payment.objects.create(
            student=student,
            event=event,
            order_id=response.get('id'),
            amount=response.get('amount'),
            currency=response.get('currency'),
            status='Pending'  # You can set an initial status
        )

        response_data = {
                "callback_url": "http://127.0.0.1:8000/api/callback",
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": response,
                "event_name": event,
                "student_name": student
        }

        print(response_data)
        return Response(response_data, status=status.HTTP_200_OK)
    

# The data we get from Razorpay is given below:
# {
#   "razorpay_payment_id": "pay_29QQoUBi66xm2f",
#   "razorpay_order_id": "order_9A33XWu170gUtm",
#   "razorpay_signature": "9ef4dffbfd84f1318f6739a3ce19f9d85851857ae648f114332d8401e0949a3d"
# }


@csrf_exempt
def order_callback(request):
    if request.method == "POST":
        if "razorpay_signature" in request.POST:
            payment_verification = razorpay_client.utility.verify_payment_signature(request.POST)
            if payment_verification:
                return JsonResponse({"res":"success"})
                # Logic to perform is payment is successful
            else:
                return JsonResponse({"res":"failed"})
                # Logic to perform is payment is unsuccessful