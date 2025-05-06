from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from django.forms.models import model_to_dict
from Root.models import UserActivityLog

# Track user logins
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    user.last_login = now()
    user.save(update_fields=['last_login'])
    UserActivityLog.objects.create(user=user, action='LOGIN', timestamp=now())

# For all app model saves
@receiver(post_save)
def track_model_save(sender, instance, created, **kwargs):
    if sender._meta.app_label.startswith("django") or sender._meta.app_label == 'contenttypes':
        return  # Skip Django internal models

    user = getattr(instance, '_logged_in_user', None)
    if user:
        UserActivityLog.objects.create(
            user=user,
            action='CREATE' if created else 'UPDATE',
            model_name=sender.__name__,
            object_id=str(instance.pk),
            changes=model_to_dict(instance),
            timestamp=now()
        )

# For all app model deletes
@receiver(post_delete)
def track_model_delete(sender, instance, **kwargs):
    if sender._meta.app_label.startswith("django") or sender._meta.app_label == 'contenttypes':
        return

    user = getattr(instance, '_logged_in_user', None)
    if user:
        UserActivityLog.objects.create(
            user=user,
            action='DELETE',
            model_name=sender.__name__,
            object_id=str(instance.pk),
            changes=model_to_dict(instance),
            timestamp=now()
        )
