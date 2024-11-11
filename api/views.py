# api/views.py
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, LoginSerializer, InvestorProfileSerializer
from .permissions import IsManager
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import InvestorProfile, UserProfile
from utils.export import export_to_json, export_to_excel
from django.http import HttpResponse


class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user_id": user.id,
                "username": user.username,
                "is_manager": user.profile.is_manager,
            }
        )


class InvestorPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class InvestorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = InvestorProfileSerializer
    pagination_class = InvestorPagination

    def get_queryset(self):
        if (
            self.action in ["retrieve", "list"]
            and self.request.user.is_authenticated
            and self.request.user.profile.is_manager
        ):
            return InvestorProfile.objects.all()
        return InvestorProfile.objects.filter(deleted_at__isnull=True)

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsManager]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """Public endpoint for investor registration"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def list(self, request, *args, **kwargs):
        """Manager only - get all investors with pagination"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Manager only - get specific investor"""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Manager only - update investor"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        """Manager only - hard delete"""
        instance.delete()

    @action(detail=True, methods=["post"])
    def soft_delete(self, request, pk=None):
        """Manager only - soft delete"""
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsManager])
def export_investors_json(request):
    queryset = InvestorProfile.objects.all()
    file_path = export_to_json(queryset, "investors")
    return HttpResponse(open(file_path, "rb"), content_type="application/json")


@api_view(["GET"])
@permission_classes([IsManager])
def export_investors_excel(request):
    queryset = InvestorProfile.objects.all()
    file_path = export_to_excel(queryset, "investors")
    response = HttpResponse(
        open(file_path, "rb"),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="investors.xlsx"'
    return response
