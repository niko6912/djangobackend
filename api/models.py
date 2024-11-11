from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.utils import timezone
from django.db.models import Max


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_manager = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class InvestorProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    index = models.IntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    surname = models.CharField(max_length=100, null=True, blank=True)
    phone_prefix = models.CharField(max_length=5, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    amount_lost = models.FloatField(null=True, blank=True)
    agree_to_be_called = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.index:
            max_index = InvestorProfile.objects.aggregate(Max("index"))["index__max"]
            self.index = (max_index or 0) + 1

        if self.pk:
            self.updated_at = timezone.now()

        super().save(*args, **kwargs)

    class Meta:
        db_table = "investor_profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} {self.surname}"

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()
