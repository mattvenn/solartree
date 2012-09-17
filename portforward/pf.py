from twisted.internet import reactor
from twisted.protocols import portforward

"""
class LoggingProxyServer(portforward.ProxyServer):
    def dataReceived(self, data):
        portforward.ProxyServer.dataReceived(self, data)

class LoggingProxyFactory(portforward.ProxyFactory):
    protocol = LoggingProxyServer
"""
if __name__ == '__main__':
    #fwd = portforward.ProxyFactory('192.168.2.150', 502)
    fwd = portforward.ProxyFactory('192.168.2.150', 80)
    reactor.listenTCP(8080, fwd)
    reactor.run()
