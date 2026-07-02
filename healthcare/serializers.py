import secrets
# pyrefly: ignore [missing-import]
from rest_framework import serializers
# pyrefly: ignore [missing-import]
from django.contrib.auth.models import User
from .models import Patient, Doctor, PatientDoctorMapping

# User Registration Serializer
class UserRegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password']
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        name = validated_data.pop('name')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        parts = name.strip().split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        return user

# Patient Serializer (for output representation)
class PatientSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['id', 'name', 'email', 'age', 'gender', 'medical_history', 'created_by', 'created_at']

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    def get_email(self, obj):
        return obj.user.email

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else None

# Patient Create/Update Serializer
class PatientCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'name', 'email', 'age', 'gender', 'medical_history']

    def validate_email(self, value):
        request = self.context.get('request')
        if request and request.method == 'POST':
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        elif request and (request.method in ['PUT', 'PATCH']):
            patient = self.instance
            if User.objects.filter(email=value).exclude(id=patient.user.id).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        name = validated_data.pop('name')
        email = validated_data.pop('email')
        
        parts = name.strip().split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=secrets.token_urlsafe(16),
            first_name=first_name,
            last_name=last_name
        )
        
        created_by = self.context['request'].user
        patient = Patient.objects.create(user=user, created_by=created_by, **validated_data)
        return patient

    def update(self, instance, validated_data):
        name = validated_data.pop('name', None)
        email = validated_data.pop('email', None)
        
        user = instance.user
        if name is not None:
            parts = name.strip().split(' ', 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''
        if email is not None:
            user.email = email
            user.username = email
        user.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

# Doctor Serializer (for output representation)
class DoctorSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = ['id', 'name', 'email', 'specialization', 'phone', 'available', 'created_by']

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    def get_email(self, obj):
        return obj.user.email

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else None

# Doctor Create/Update Serializer
class DoctorCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'name', 'email', 'specialization', 'phone', 'available']

    def validate_email(self, value):
        request = self.context.get('request')
        if request and request.method == 'POST':
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        elif request and (request.method in ['PUT', 'PATCH']):
            doctor = self.instance
            if User.objects.filter(email=value).exclude(id=doctor.user.id).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        name = validated_data.pop('name')
        email = validated_data.pop('email')
        
        parts = name.strip().split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=secrets.token_urlsafe(16),
            first_name=first_name,
            last_name=last_name
        )
        
        created_by = self.context['request'].user
        doctor = Doctor.objects.create(user=user, created_by=created_by, **validated_data)
        return doctor

    def update(self, instance, validated_data):
        name = validated_data.pop('name', None)
        email = validated_data.pop('email', None)
        
        user = instance.user
        if name is not None:
            parts = name.strip().split(' ', 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''
        if email is not None:
            user.email = email
            user.username = email
        user.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

# Patient-Doctor Mapping Serializer
class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())

    class Meta:
        model = PatientDoctorMapping
        fields = ['id', 'patient', 'doctor']

    def validate(self, attrs):
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')
        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError("This doctor is already mapped to this patient.")
        return attrs

# Patient-Doctor Mapping Read Serializer (with nested representations)
class PatientDoctorMappingReadSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ['id', 'patient', 'doctor']
