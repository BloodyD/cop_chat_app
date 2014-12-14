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
import simplejson as json

from autobahn.twisted.websocket import WebSocketServerFactory, \
                          WebSocketServerProtocol as BaseProtocol

class BaseClient(object, BaseProtocol):

  # WebSocket interface
  def onOpen(self):
    self.server.register(self)

  def onMessage(self, payload, isBinary):
    if isBinary: raise NotImplemented("Binary content is not supported!")
    payload = json.loads(payload)
    data = payload["data"]
    if payload["method"] == "login":
      if not self.server.username_available(data):
        self.sendMessage("Username already in use!", method = "login")
        return
      self.username = data

      # inform the others
      self.server.inform("%s logged in!" %(self.username), exclude = self)

      # send info to self
      self.sendMessage("OK", method = "login")
      self.sendMessage("You are logged in!", method = "login")
    else:
      self.server.chat(data, self)

  def onClose(self, wasClean, code, reason):
    self.logout()

  def connectionLost(self, reason):
    self.logout()
    BaseProtocol.connectionLost(self, reason)

  def sendMessage(self, content, method = "chat"):
    return BaseProtocol.sendMessage(self, json.dumps({"data": content, "method": method}))

  def logout(self):
    if not self.logged_in: return
    self.server.inform("%s logged out!" %(self.username), exclude = self)
    self.server.unregister(self)
    self.username = None

  # initialization, setter and getter
  def __init__(self, *args, **kw):
    object.__init__(self)
    self.username = None

  @property
  def logged_in(self):
    return self.username is not None

  @logged_in.setter
  def logged_in(self, value):
    pass # no setter!

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
    self._clients = set()

  register = lambda self, client: self._clients.add(client)
  unregister = lambda self, client: self._clients.remove(client)

  def clients(self, exclude = None):
    for c in self._clients:
      if exclude is None or exclude != c:
        yield c

  def username_available(self, username):
    return not any(map(lambda x: x.username == username, self.clients()))

  def inform(self, msg, exclude = None):
    for client in self.clients(exclude):
      client.sendMessage(msg, method = "inform")

  def chat(self, msg, sender):
    if len(msg.strip()) == 0: return
    for client in self.clients():
      client.sendMessage("%s: %s" %(sender.username, msg))
