import time
def timedec(func):

    def timewrap(*arg):
        t = time.clock()
        res = func(*arg)
        print(func.__name__, time.clock()-t)
        return res

    return timewrap
