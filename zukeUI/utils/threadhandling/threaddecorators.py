import threading


def daemon(function):
    def wrapped_func(*args):
        parallel_function = threading.Thread(target=function,args=args)
        parallel_function.daemon = True
        parallel_function.start()

    return wrapped_func

def thread(function):
    def wrapped_func(*args):
        parallel_function = threading.Thread(target=function,args=args)
        parallel_function.start()

    return wrapped_func
