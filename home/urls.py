from django.urls import path
from .views import *

urlpatterns = [
    path('', student_list),
    path('signup/', CustomUserCreateView.as_view(), name='user-register'),
    path('login/', CustomAuthTokenView.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='user-logout'),

    path('student/', StudentListCreateView.as_view(), name='student-list'),
    path('student/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),

    path('register/', RegistrationCreateView.as_view(), name='register-event'),
    path('students/<int:student_id>/events/', RegisteredEventsView.as_view(), name='registered-events'),
]