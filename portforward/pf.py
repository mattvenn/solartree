from twisted.internet import reactor
from twisted.protocols import portforward

if __name__ == '__main__':
   fwd = portforward.ProxyFactory('192.168.2.150', 502)
   reactor.listenTCP(8080, fwd)
   reactor.run()
