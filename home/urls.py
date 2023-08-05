from django.urls import path
from .views import *

urlpatterns = [
    path('', student_list),
    path('register/', CustomUserCreateView.as_view(), name='user-register'),
    path('login/', CustomAuthTokenView.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='user-logout'),

    path('student/', StudentListCreateView.as_view(), name='student-list'),
    path('student/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
]