class PyromodConfig:
    timeout_handler = None
    stopped_handler = None
    throw_exceptions = True
    unallowed_click_alert = True
    unallowed_click_alert_text = (
        "[misskaty] You're not authorized to click this button."
    )


def patch(obj):
    def is_patchable(item):
        return getattr(item[1], "patchable", False)

    def wrapper(container):
        for name, func in filter(is_patchable, container.__dict__.items()):
            old = getattr(obj, name, None)
            if old is not None: # Not adding 'old' to new func
                setattr(obj, "old" + name, old)
            setattr(obj, name, func)
        return container

    return wrapper


def patchable(func):
    func.patchable = True
    return func