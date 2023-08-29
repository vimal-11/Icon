from rest_framework import serializers
from .models import Students, Events, Registration, FacultyIncharge, Teams, CustomUser


class StudentsSerializer(serializers.ModelSerializer):
     class Meta:
        model = Students
        fields = '__all__'



class EventsSerializer(serializers.ModelSerializer):
     class Meta:
        model = Events
        fields = '__all__'



class RegistrationSerializer(serializers.ModelSerializer):
     class Meta:
        model = Registration
        fields = '__all__'



class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user



class FacultyInchargeSerializer(serializers.ModelSerializer):
     class Meta:
        model = FacultyIncharge
        fields = '__all__'



class TeamsSerializer(serializers.ModelSerializer):
     class Meta:
        model = Teams
        fields = '__all__'



class RegisteredEventSerializer(serializers.ModelSerializer):
    event = EventsSerializer()  # Include the event details
    class Meta:
        model = Registration
        fields = ('event', 'is_paid')  # Customize fields as needed
        


class TeamMemberSerializer(serializers.Serializer):
    team_member = serializers.PrimaryKeyRelatedField(queryset=Students.objects.all())

    def validate_team_member(self, value):
         # Get the event associated with this registration
        event = self.instance.event
        team_lead = self.instance.team_lead
        print(event, team_lead, type(self.instance))
        # Get the team instance for this event's team_lead
        try:
            team = Teams.objects.get(event=event, team_lead=team_lead)
        except Teams.DoesNotExist:
            raise serializers.ValidationError("You are not a team lead for this event.")
        # Check if the team member is already in the team_member list
        if value in team.team_member.all():
            raise serializers.ValidationError("Student is already a team member for this event.")
        return value