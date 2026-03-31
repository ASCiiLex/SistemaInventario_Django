from inventory.models.audit import AuditLog


def log_action(user, action, instance, changes=None):
    if changes is None:
        changes = {}

    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=instance.pk,
        changes=changes,
    )