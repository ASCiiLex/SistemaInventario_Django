from django.forms.models import model_to_dict


def serialize_instance(instance):
    data = model_to_dict(instance)

    for field, value in data.items():

        # 🔥 Files → string
        if hasattr(value, "url"):
            data[field] = value.url

        # 🔥 FK → id
        elif hasattr(value, "pk"):
            data[field] = value.pk

        # 🔥 Otros no serializables
        else:
            try:
                import json
                json.dumps(value)
            except TypeError:
                data[field] = str(value)

    return data