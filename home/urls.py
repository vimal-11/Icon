from django.urls import path
from .views import *

urlpatterns = [
    path('', student_list),
    path('get_user_data/', get_user_data, name='get-user'),

    path('signup/', CustomUserCreateView.as_view(), name='user-register'),
    # path('login/', CustomAuthTokenView.as_view(), name='user-login'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='user-logout'),

    path('student/', StudentListCreateView.as_view(), name='student-list'),
    path('student/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),

    path('register/', RegistrationCreateView.as_view(), name='register-event'),
    path('students/<int:student_id>/events/', RegisteredEventsView.as_view(), name='registered-events'),
    path('add-team-member/<int:pk>/', TeamMemberAddView.as_view(), name='add-team-member'),
    path('event-team-lead/<int:student_id>/<int:event_id>/', EventTeamLeadView.as_view(), name='event-team-lead'),

    path('teams/', TeamsListCreateView.as_view(), name='teams-list'),
    path('teams/<int:pk>/', TeamsDetailView.as_view(), name='teams-detail'),

    path('api/razorpay/', RazorpayPaymentView.as_view(), name='razorpay'),

    path('events/', EventsList.as_view(), name='event-names'),
    path('event-detail/<int:event_id>/', EventDetailView.as_view(), name='event-detail'),
    path('reg-detail/<int:pk>/', RegisteredEventDetailView.as_view(), name='reg-detail'),

    path('feedback/', feedback, name='feedback'),
]