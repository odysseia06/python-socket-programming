def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper
@run_once
def myfunc():
    print("AAA")

class Protocol:
    def __init__(self):
        pass


