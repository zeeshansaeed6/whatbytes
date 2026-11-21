from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Doctor, Mapping, Patient
from .serializers import (DoctorSerializer, LoginSerializer, MappingSerializer,
                          PatientSerializer, RegisterSerializer)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = authenticate(username=s.validated_data['email'].lower(), password=s.validated_data['password'])
        if not user:
            return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), 'refresh': str(refresh)})


class PatientList(generics.ListCreateAPIView):
    serializer_class = PatientSerializer

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)


class DoctorList(generics.ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DoctorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        # doctors are readable by all, but only the creator may modify
        if request.method != 'GET' and obj.created_by != request.user:
            self.permission_denied(request, message='Only the creator can modify this doctor.')


class MappingList(generics.ListCreateAPIView):
    serializer_class = MappingSerializer

    def get_queryset(self):
        return Mapping.objects.filter(patient__created_by=self.request.user)


class MappingDetail(generics.RetrieveDestroyAPIView):
    """GET /mappings/<patient_id>/ lists that patient's doctors; DELETE /mappings/<id>/ removes a mapping."""
    serializer_class = MappingSerializer

    def get_queryset(self):
        return Mapping.objects.filter(patient__created_by=self.request.user)

    def retrieve(self, request, pk):
        if not Patient.objects.filter(pk=pk, created_by=request.user).exists():
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        qs = self.get_queryset().filter(patient_id=pk).select_related('doctor')
        return Response(DoctorSerializer([m.doctor for m in qs], many=True).data)
