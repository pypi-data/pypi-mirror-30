import gevent

class G(gevent.Greenlet):
    def __init__(self, name, *a, **ka):
        gevent.Greenlet.__init__(self, *a, **ka)
        self.__name = name

    def __str__(self):
        return self.__name

def pg(name):
    g = gevent.getcurrent()
    print "{0}: in greenlet {1} launched from {2}".format(name, g, g.parent_greenlet)
    print "{0}: gr_frame={1}".format(name, g.gr_frame)

def f():
    pg('f')

def g():
    pg('g')
    task_f = gevent.spawn(f)
    #task_f.join()

def h():
    pg('h')
    task_g = gevent.spawn(g)
    #task_g.join()

def go(n):
    g = gevent.getcurrent()
    print "{0}: in greenlet {1}; gr_frame={2}".format(n, g, g.gr_frame)
    if n>0:
        gevent.spawn(go, n-1).join()

#gevent.spawn(go, 2).join()
go(2)
