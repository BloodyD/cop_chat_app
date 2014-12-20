# original source: https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/websocket/broadcast
from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
                          WebSocketServerProtocol as BaseProtocol, \
                          listenWS



VERSION = "v3"


if VERSION == "v1":
  from server_v1 import BaseClient, Server
elif VERSION == "v2":
  from server_v2 import BaseClient, Server
else:
  from server_v3 import BaseClient, Server

if __name__ == '__main__':
  import sys
  log.startLogging(sys.stdout)
  debug = True

  server = Server("ws://localhost:9000",
                  debug = debug,
                  debugCodePaths = debug)

  server.protocol = BaseClient
  server.setProtocolOptions(allowHixie76 = True)
  listenWS(server)

  webdir = File(".")
  web = Site(webdir)
  reactor.listenTCP(8080, web)

  reactor.run()