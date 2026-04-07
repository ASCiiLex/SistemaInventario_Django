from inventory.models.audit import AuditLog


# ==========================================
# SERIALIZACIÓN / DIFF (EXISTENTE)
# ==========================================

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


# ==========================================
# CORE
# ==========================================

def _resolve_organization(instance, organization):
    if organization:
        return organization
    if instance and hasattr(instance, "organization"):
        return instance.organization
    return None


def log_action(user, action, instance, changes=None, organization=None):
    if changes is None:
        changes = {}

    organization = _resolve_organization(instance, organization)

    if not organization:
        return

    AuditLog.objects.create(
        organization=organization,
        user=user if user and user.is_authenticated else None,
        action=action,
        model_name=instance.__class__.__name__ if instance else "System",
        object_id=instance.pk if instance else 0,
        changes=changes,
    )


# ==========================================
# 🔥 BUSINESS EVENTS (NUEVO)
# ==========================================

def log_status_change(user, instance, field, old, new):
    log_action(
        user=user,
        action="STATUS_CHANGE",
        instance=instance,
        changes={
            field: {
                "old": old,
                "new": new,
            }
        },
    )


def log_business_event(user, action, instance, extra=None):
    log_action(
        user=user,
        action=action,
        instance=instance,
        changes=extra or {},
    )


# ==========================================
# HELPERS SEMÁNTICOS (SaaS)
# ==========================================

def audit_order_sent(order, user, old_status):
    log_status_change(user, order, "status", old_status, "sent")


def audit_order_received(order, user, old_status):
    log_status_change(user, order, "status", old_status, "received")


def audit_order_cancelled(order, user, old_status):
    log_status_change(user, order, "status", old_status, "cancelled")


def audit_transfer_confirmed(transfer, user, old_status):
    log_business_event(
        user,
        "TRANSFER_CONFIRMED",
        transfer,
        {
            "status": {"old": old_status, "new": "received"},
            "quantity": transfer.quantity,
        },
    )


def audit_transfer_cancelled(transfer, user, old_status):
    log_business_event(
        user,
        "TRANSFER_CANCELLED",
        transfer,
        {
            "status": {"old": old_status, "new": "cancelled"},
        },
    )


# ==========================================
# FORMATO UI
# ==========================================

def format_changes(changes: dict):
    if not changes:
        return []

    formatted = []

    for field, values in changes.items():
        if isinstance(values, dict) and "old" in values and "new" in values:
            formatted.append({
                "field": field,
                "old": values["old"],
                "new": values["new"],
            })
        else:
            formatted.append({
                "field": field,
                "old": None,
                "new": values,
            })

    return formatted