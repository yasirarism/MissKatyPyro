def patch(obj):
    def is_patchable(item):
        return getattr(item[1], 'patchable', False)

    def wrapper(container):
        for name,func in filter(is_patchable, container.__dict__.items()):
            old = getattr(obj, name, None)
            setattr(obj, 'old'+name, old)
            setattr(obj, name, func)
        return container
    return wrapper

def patchable(func):
    func.patchable = True
    return func