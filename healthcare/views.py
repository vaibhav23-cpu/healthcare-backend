from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied

from .models import Patient, Doctor, PatientDoctorMapping
from .serializers import (
    UserRegisterSerializer,
    PatientSerializer,
    PatientCreateSerializer,
    DoctorSerializer,
    DoctorCreateSerializer,
    PatientDoctorMappingSerializer,
    PatientDoctorMappingReadSerializer
)

# Custom Permission to allow only the creator of an object to edit/delete it
class IsCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if the object has a created_by attribute and match with the user
        return getattr(obj, 'created_by', None) == request.user

# 1. Authentication Views
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully.",
                "user": {
                    "id": user.id,
                    "name": f"{user.first_name} {user.last_name}".strip(),
                    "email": user.email
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Email is used as username
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = authenticate(username=user.username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}".strip(),
                    'email': user.email
                }
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

# 2. Patient Management Views
class PatientListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retrieve all patients created by the authenticated user
        return Patient.objects.filter(created_by=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PatientCreateSerializer
        return PatientSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            patient = serializer.save()
            output_serializer = PatientSerializer(patient)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCreator]
    queryset = Patient.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PatientCreateSerializer
        return PatientSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Enforce that only the creator can view patient details (for privacy)
        if instance.created_by != request.user:
            raise PermissionDenied("You do not have permission to view this patient's details.")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            patient = serializer.save()
            output_serializer = PatientSerializer(patient)
            return Response(output_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Doctor Management Views
class DoctorListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Doctor.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DoctorCreateSerializer
        return DoctorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            doctor = serializer.save()
            output_serializer = DoctorSerializer(doctor)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCreator]
    queryset = Doctor.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DoctorCreateSerializer
        return DoctorSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            doctor = serializer.save()
            output_serializer = DoctorSerializer(doctor)
            return Response(output_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 4. Patient-Doctor Mapping Views
class PatientDoctorMappingListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = PatientDoctorMapping.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PatientDoctorMappingSerializer
        return PatientDoctorMappingReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            mapping = serializer.save()
            output_serializer = PatientDoctorMappingReadSerializer(mapping)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientDoctorMappingDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        # pk is treated as patient_id
        # Get all doctors mapped to this specific patient
        mappings = PatientDoctorMapping.objects.filter(patient_id=pk)
        doctors = [mapping.doctor for mapping in mappings]
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        # pk is treated as mapping_id
        try:
            mapping = PatientDoctorMapping.objects.get(pk=pk)
        except PatientDoctorMapping.DoesNotExist:
            return Response({"error": "Mapping not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Enforce that only the creator of the patient or the creator of the doctor can remove mapping,
        # or simple authentication. For secure constraints:
        if mapping.patient.created_by != request.user and (mapping.doctor.created_by != request.user):
            raise PermissionDenied("You do not have permission to delete this mapping.")
            
        mapping.delete()
        return Response({"message": "Doctor removed from patient successfully."}, status=status.HTTP_204_NO_CONTENT)
