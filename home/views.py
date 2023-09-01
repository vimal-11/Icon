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
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.db import IntegrityError
import razorpay


from .models import *
from .serializers import *
# Create your views here.



# razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@csrf_exempt
@api_view(['GET'])
@permission_classes([permissions.DjangoModelPermissionsOrAnonReadOnly])
def student_list(request):
    students = Students.objects.all()
    serializer = StudentsSerializer(students, many=True)
    return Response(serializer.data)
    


@api_view(['GET'])
def event_names(request):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    events = Events.objects.all()
    print(events)
    event_names = [event.title for event in events]
    # event_names = [(event.title, event.is_paid) for event in events]
    return JsonResponse(event_names, safe=False)  




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
            user_obj=CustomUser.objects.get(email=email)
            # student=Students.objects.get(email=user_obj)
            uname = None
            try:
                student=user_obj.students_set.first()
                uname = student.name 
            except:
                print("Student Profile not created") 
            print(student)
            return Response({'token': token.key, 'user_id':user.id,'user_name':uname,'success':True}, status=status.HTTP_200_OK)
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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance.get_id_card_url())
        serializer = self.get_serializer(instance)
        print("Student Detail Response:", serializer.data)  # Print the response data
        image_path = 'ID_Cards/giri.png'
        image_url = default_storage.url(image_path)
        print("Generated Image URL:", settings.MEDIA_URL + image_url)
        return Response(serializer.data)





class RegistrationCreateView(generics.CreateAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Access the data from the request here
        event_id = self.request.data.get('event')
        student_id = self.request.data.get('student')
        is_paid = self.request.data.get('is_paid')
        
        print("Received data from frontend:")
        print("Event ID:", event_id)
        print("Student ID:", student_id)
        print("Is Paid:", is_paid)
        
        # Continue with creating the instance using the serializer
        serializer.save()

    def post(self, request, *args, **kwargs):
        print("Received data from frontend:")
        print("Request data:", request.data)
        event = self.request.data.get('event')
        student_id = self.request.data.get('student')
        # student_name=self.request.data.get('name')
        is_paid = self.request.data.get('is_paid')
        event_instance=Events.objects.get(title=event)
        student_instance = Students.objects.get(pk=student_id)
        # print(student_instance,type(student_instance),type(event_instance))
        try:
            registration=Registration(event=event_instance,student=student_instance)
            registration.save()
            team_id=None
            team_ld=None
            uname=None
            # Check if the event is a team event
            if event_instance.is_team:
                # Create a Teams instance with the student as team lead
                team_lead = student_instance
                new_team = Teams.objects.create(team_lead=team_lead, event=event_instance)
                new_team.team_member.add(student_instance)  # Add student as a team member
                team_id = new_team.pk   
                serializer_team = TeamsSerializer(new_team)
                team_ld = serializer_team.data.get("team_lead")
                uname = Students.objects.get(pk=team_ld)
                uname=uname.name
            serializer=RegistrationSerializer(registration)
            data = {"serializer": serializer.data, "team_id": team_id, "team_lead": uname}
            return Response(data,status=status.HTTP_201_CREATED)
        except IntegrityError:
        # Handle the case where a registration already exists for the given event and student
            return Response({"error": "Registration already exists for this event and student."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)






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






class TeamMemberAddView(generics.UpdateAPIView):
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Teams.objects.get(pk=self.kwargs['pk'])
    

    def get_queryset(self):
        instance = self.get_object()
        event = instance.event
        team_members = instance.team_member.all()  # Existing team members
        lead_team_members = Teams.objects.filter(event=event).values_list('team_member', flat=True)  # Members of other teams
        # Exclude students who are already part of the existing team and other teams
        query_set = Students.objects.filter(
            ~Q(pk__in=team_members) & ~Q(pk__in=lead_team_members)
        )
        print(query_set)
        return query_set
    
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = self.get_queryset()
        serializer = StudentsSerializer(queryset, many=True)
        return Response(serializer.data)
    

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance)
        print(request.data)
        student_name=request.data.get("team_member",{})[0].get("name")
        try:
            team_member=Students.objects.get(name=student_name)
        except Students.DoesNotExist:
            return Response({"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        data_dict={"team_member":team_member.id}
        serializer = self.get_serializer(instance, data=data_dict, context={'instance': instance})
        serializer.is_valid(raise_exception=True)
        team_member = serializer.validated_data['team_member']

        instance.team_member.add(team_member)
        Registration.objects.create(event=instance.event, student=team_member)

        return Response({"message": "Team member added successfully"}, status=status.HTTP_200_OK)





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






class EventTeamLeadView(generics.RetrieveAPIView):
    serializer_class = TeamsSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        event_id = self.kwargs['event_id']
        queryset = Teams.objects.filter(event=event_id, team_lead=student_id)
        return queryset

    def get(self, request, *args, **kwargs):
        student_id = self.kwargs['student_id']
        event_id = self.kwargs['event_id']

        try:
            student = Students.objects.get(id=student_id)
            event = Events.objects.get(id=event_id)
            team = Teams.objects.get(event=event, team_lead=student)
            serializer = self.get_serializer(team)
            return Response(serializer.data)
        except Students.DoesNotExist:
            return Response({"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        except Events.DoesNotExist:
            return Response({"message": "Event not found or student is not the team lead"}, status=status.HTTP_404_NOT_FOUND)
        




class EventDetailView(generics.RetrieveAPIView):
    serializer_class = EventsSerializer

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        queryset = Events.objects.filter(id=event_id)
        return queryset

    def get(self, request, *aargs, **kwargs):
        event_id = self.kwargs['event_id']
        try:
            event = Events.objects.get(id=event_id)
            serializer = self.get_serializer(event)
            return Response(serializer.data)
        except Events.DoesNotExist:
            return Response({"message": "Event not found"}, status=status.HTTP_404_NOT_FOUND)




class RegisteredEventDetailView(generics.RetrieveAPIView):
    serializer_class = RegisteredEventSerializer

    def get_queryset(self):
        reg_id = self.kwargs['pk']
        queryset = Registration.objects.filter(id=reg_id)
        return queryset