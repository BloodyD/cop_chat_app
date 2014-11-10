###############################################################################
##
##  Copyright (C) 2011-2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

# original source: https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/websocket/broadcast

import sys, simplejson as json, re

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
                                       WebSocketServerProtocol, \
                                       listenWS

from contextpy import layer, base, around, activelayer, proceed

nobbcode = layer("No BBCode")

class Message(object):
   def __init__(self, payload = None, data = None, method = None):
      super(Message, self).__init__()
      if payload is None:
         self.data = data
         self.method = method
      else:
         self.__dict__ = json.loads(payload)

   def as_json(self):
      return json.dumps(self.__dict__)

   @property
   def is_login(self):
      return self.method == "login"

   @property
   def is_chat(self):
      return self.method == "chat"

class BroadcastServerProtocol(WebSocketServerProtocol):

   @base
   def createMessage(self, data, method):
      return Message(data = data, method = method)

   @around(nobbcode)
   def createMessage(self, data, method):
      return Message(data = re.sub(r'\[[\/\w\s]*\]\n{0,1}', "", data), method = method)


   def sendMessage(self, data, method = "chat"):
      # print "sending chat message {}".format(data)
      msg = self.createMessage(data, method)
      WebSocketServerProtocol.sendMessage(self, msg.as_json())

   def onOpen(self):
      self.factory.register(self)

   def onMessage(self, payload, isBinary):
      if isBinary: raise NotImplemented("Binary content is not supported!")
      m = Message(payload = payload)

      if m.is_login and not self.factory.logged_in(self):
         self.factory.login(self, m.data)
         print("user {} logged in".format(payload))

      elif m.is_chat:
         self.factory.broadcast(m.data, self)


   def onClose(self, wasClean, code, reason):
      self.factory.logout(self)

   def connectionLost(self, reason):
      WebSocketServerProtocol.connectionLost(self, reason)
      self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):
   """
   Simple broadcast server broadcasting any message it receives to all
   currently connected clients.
   """

   usernames = {}

   def __init__(self, url, debug = False, debugCodePaths = False):
      WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debugCodePaths)
      self.clients = set()

   def logged_in(self, client):
      return client in self.usernames

   def login(self, client, username):
      if username in self.usernames.values():
         client.sendMessage("Username already in use!", method = "login")
         return

      self.usernames[client] = username
      client.sendMessage("OK", method = "login")
      for c in self.get_clients(client):
         c.sendMessage("%s logged in!" %(self.username(client)))

   def logout(self, client):
      username = self.usernames.pop(client)
      for c in self.get_clients(client):
         c.sendMessage("%s logged out!" %(username))

   def username(self, client, default = "Anonymous"):
      return self.usernames.get(client, default)

   def register(self, client):
      print("registered client {}".format(client.peer))
      self.clients.add(client)

   def get_clients(self, exclude = None):
      # TODO: alle registrierten oder alle angemeldeten?
      #for c in self.clients:
      for c in self.usernames.keys():
         if exclude is None or exclude != c:
            yield c, nobbcode

   def unregister(self, client):
      try:
         print("unregistered client {}".format(client.peer))
         self.clients.remove(client)
      except KeyError, e:
         print("client {} was not yet registered!".format(client.peer))

   def broadcast(self, msg, client):
      # print("broadcasting message '{}' ...".format(msg))
      for c, layer in self.get_clients():
         with activelayer(layer):
            c.sendMessage("%s: %s" %(self.username(client), msg))
         print("message sent to {}".format(c.peer))


if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   factory = BroadcastServerFactory("ws://localhost:9000",
                           debug = debug,
                           debugCodePaths = debug)

   factory.protocol = BroadcastServerProtocol
   factory.setProtocolOptions(allowHixie76 = True)
   listenWS(factory)

   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   reactor.run()
