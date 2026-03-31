from inventory.models.audit import AuditLog


def serialize_instance(instance):
    data = {}
    for field in instance._meta.fields:
        field_name = field.name
        try:
            value = getattr(instance, field_name)
            if hasattr(value, "pk"):
                data[field_name] = value.pk
            else:
                data[field_name] = value
        except Exception:
            continue
    return data


def get_instance_changes(old_data, new_instance):
    new_data = serialize_instance(new_instance)
    changes = {}

    for key, new_value in new_data.items():
        old_value = old_data.get(key)
        if old_value != new_value:
            changes[key] = {
                "old": old_value,
                "new": new_value,
            }

    return changes


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