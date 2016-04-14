from django.core.cache import cache


def generate_key(model, id, related=None):
    if related:
        return '{}.{}.{}-{}'.format(model._meta.app_label, model._meta.model_name, related, id)
    return '{}.{}-{}'.format(model._meta.app_label, model._meta.model_name, id)

def get_or_set(model, id):
    key = generate_key(model, id)
    obj = cache.get(key)
    if not obj:
        obj = model.objects.get(id=id)
        cache.set(key, obj)
    return obj

def get(model, id):
    key = generate_key(model, id)
    return cache.get(key)

def delete(model, instance, related=None):
    key = generate_key(model, instance.id, related)
    cache.delete(key)    
    
def set(obj):
    key = generate_key(obj._meta.model, obj.id)
    cache.set(key, obj)
    
def get_or_set_related(instance, related):
    key = generate_key(instance._meta.model, instance.id, related)
    objs = cache.get(key)
    if objs is None:
        objs = getattr(instance, related).all()
        cache.set(key, objs)
    return objs