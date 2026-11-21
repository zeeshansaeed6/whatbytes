from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Doctor, Mapping, Patient


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value.lower()

    def create(self, data):
        # email doubles as username so login is by email
        return User.objects.create_user(
            username=data['email'], email=data['email'], password=data['password'], first_name=data['name'])


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude = ('created_by',)
        read_only_fields = ('created_at',)


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        exclude = ('created_by',)
        read_only_fields = ('created_at',)


class MappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mapping
        fields = '__all__'
        read_only_fields = ('created_at',)

    def validate_patient(self, patient):
        if patient.created_by != self.context['request'].user:
            raise serializers.ValidationError('Patient not found.')
        return patient
