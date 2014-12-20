###############################################################################
##
##  Copyright (C) 2011-2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

# original source: https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/websocket/broadcast
import sys

from twisted.internet import reactor
from twisted.python import log
# from twisted.web.server import Site
# from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
                          WebSocketServerProtocol,\
                          listenWS

class Handler(object, WebSocketServerProtocol):

  def __init__(self):
    object.__init__(self)
    self.username = None

  def onOpen(self):
    self.server.register(self)

  def onClose(self, was_clean, code, reason):
    self.server.unregister(self)
    if self.username is not None:
      self.server.inform(self, "User %s logged out!" %self.username)
      self.username = None
    print "closed a connection!(%s, %d, %s)" %(str(was_clean), code, reason)

  def onMessage(self, payload, isBinary):
    method, content = payload.split(":")
    if method == "login":
      if self.server.login(self, content):
        self.username = content
        self.sendMessage("login:OK")
        self.server.inform(self, "User %s logged in!"%(self.username))
      else:
        self.sendMessage("login:inuse")
    else:
      self.server.chat(self, content)
    # print "got message: %s" %(payload)

  # only for naming
  @property
  def server(self):
    return self.factory

  @server.setter
  def server(self, value):
    self.factory = value


class Server(WebSocketServerFactory):
  """
  Simple broadcast server broadcasting any message it receives to all
  currently connected clients.
  """

  def __init__(self, url, debug = False, debugCodePaths = False):
    WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debugCodePaths)
    self.clients = set()

  register = lambda self, client_handler: self.clients.add(client_handler)
  unregister = lambda self, client_handler: self.clients.remove(client_handler)

  def login(self, client_handler, username):
    return username not in map(lambda handler: handler.username, self.clients)

  def inform(self, client_handler, content):
    for client in self.clients:
      if client_handler == client: continue
      client.sendMessage("chat: %s" %(content))


  def chat(self, client_handler, content):
    if client_handler.username is None: return
    self.inform(client_handler, "%s: %s" %(client_handler.username, content))

  #   self._clients = set()

  # register = lambda self, client: self._clients.add(client)
  # unregister = lambda self, client: self._clients.remove(client)

  # def clients(self, exclude = None):
  #   for c in self._clients:
  #     if exclude is None or exclude != c:
  #       yield c

  # def username_available(self, username):
  #   return not any(map(lambda x: x.username == username, self.clients()))

  # def inform(self, msg, exclude = None):
  #   for client in self.clients(exclude):
  #     client.sendMessage(msg, method = "inform")

  # def chat(self, msg, sender):
  #   if len(msg.strip()) == 0: return
  #   for client in self.clients():
  #     client.sendMessage("%s: %s" %(sender.username, msg))


if __name__ == '__main__':

  log.startLogging(sys.stdout)
  debug = True

  server = Server("ws://localhost:9000",
                  debug = debug,
                  debugCodePaths = debug)

  server.protocol = Handler
  server.setProtocolOptions(allowHixie76 = True)
  listenWS(server)

  # webdir = File(".")
  # web = Site(webdir)
  # reactor.listenTCP(8080, web)

  reactor.run()
