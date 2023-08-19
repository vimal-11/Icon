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
        instance = self.context['instance']
        event = instance.event
        if value in event.teams.team_member.all():
            raise serializers.ValidationError("This student is already in a team for this event.")
        return value