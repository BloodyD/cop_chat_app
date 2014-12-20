import simplejson as json
from utils import *

from server_v2 import BaseClient as V2BaseClient, Server

class BaseClient(V2BaseClient):
  def onMessage(self, payload, isBinary):
    payload = json.loads(payload)
    if self.version == "v3":
      payload["data"] = bbcode_to_html_with_media(payload["data"])

    V2BaseClient.onMessage(self, json.dumps(payload), isBinary)
