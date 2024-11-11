from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"investors", views.InvestorProfileViewSet, basename="investor")


urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path(
        "export/investors/json/",
        views.export_investors_json,
        name="export_investors_json",
    ),
    path(
        "export/investors/excel/",
        views.export_investors_excel,
        name="export_investors_excel",
    ),
    path("", include(router.urls)),
]
