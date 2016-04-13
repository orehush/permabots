from django.core.cache import cache


def generate_key(model, id):
    return '{}.{}-{}'.format(model._meta.app_label, model._meta.model_name, id)

def get_or_set(model, id):
    key = generate_key(model, id)
    obj = cache.get(key)
    if not obj:
        obj = model.objects.get(id=id)
        cache.set(key, obj)
    return obj

def delete(model, id):
    key = generate_key(model, id)
    cache.delete(key)