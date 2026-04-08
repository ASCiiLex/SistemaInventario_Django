def serialize_instance(instance):
    data = {}

    for field in instance._meta.fields:
        value = getattr(instance, field.name)

        if value is None:
            data[field.name] = None
            continue

        # 🔥 File/ImageField seguro
        if hasattr(value, "name"):
            try:
                data[field.name] = value.url if value.name else None
            except Exception:
                data[field.name] = value.name or None
            continue

        # 🔥 FK
        if hasattr(value, "pk"):
            data[field.name] = value.pk
            continue

        # 🔥 Tipos primitivos
        if isinstance(value, (int, float, str, bool)):
            data[field.name] = value
            continue

        # 🔥 Fallback seguro
        try:
            import json
            json.dumps(value)
            data[field.name] = value
        except Exception:
            data[field.name] = str(value)

    return data