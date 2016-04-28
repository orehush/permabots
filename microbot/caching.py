from django.core.cache import cache


def generate_key(model, pk, related=None):
    if related:
        return '{}.{}.{}-{}'.format(model._meta.app_label, model._meta.model_name, related, pk)
    return '{}.{}-{}'.format(model._meta.app_label, model._meta.model_name, pk)

def get_or_set(model, pk):
    key = generate_key(model, pk)
    obj = cache.get(key)
    if not obj:
        obj = model.objects.get(pk=pk)
        cache.set(key, obj)
    return obj

def get(model, pk):
    key = generate_key(model, pk)
    return cache.get(key)

def delete(model, instance, related=None):
    key = generate_key(model, instance.pk, related)
    cache.delete(key)    
    
def set(obj):
    key = generate_key(obj._meta.model, obj.pk)
    cache.set(key, obj)
    
def get_or_set_related(instance, related, *args):
    key = generate_key(instance._meta.model, instance.pk, related)
    objs = cache.get(key)
    if objs is None:
        objs = getattr(instance, related).select_related(*args).all()
        cache.set(key, objs)
    return objs