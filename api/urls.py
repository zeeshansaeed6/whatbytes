from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view()),
    path('auth/login/', views.LoginView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('patients/', views.PatientList.as_view()),
    path('patients/<int:pk>/', views.PatientDetail.as_view()),
    path('doctors/', views.DoctorList.as_view()),
    path('doctors/<int:pk>/', views.DoctorDetail.as_view()),
    path('mappings/', views.MappingList.as_view()),
    path('mappings/<int:pk>/', views.MappingDetail.as_view()),
]
