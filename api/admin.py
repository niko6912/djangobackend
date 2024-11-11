from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, InvestorProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "profile"


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "get_is_manager",
    )

    def get_is_manager(self, obj):
        return obj.profile.is_manager

    get_is_manager.short_description = "Manager Status"
    get_is_manager.boolean = True


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class InvestorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "index",
        "name",
        "surname",
        "phone_number",
        "email",
        "amount_lost",
        "agree_to_be_called",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    list_filter = ("agree_to_be_called", "created_at", "updated_at", "deleted_at")
    search_fields = ("name", "surname", "phone_number", "email")
    ordering = ["-created_at"]
    actions = ["soft_delete_selected"]

    def soft_delete_selected(self, request, queryset):
        """Action to perform a soft delete on selected objects."""
        for obj in queryset:
            obj.soft_delete()
        self.message_user(request, f"{queryset.count()}")

    soft_delete_selected.short_description = "Soft delete selected investor profiles"


admin.site.register(InvestorProfile, InvestorProfileAdmin)
