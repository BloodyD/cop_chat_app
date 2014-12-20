from contextpy import *
import hashlib


red = layer("red")
green = layer("green")
join = layer("join")
sign = layer("sign")

COLORS = [red, green]
TEXTS = [join, sign]

class FirstExperiment(object):

  def __init__(self, userid):
    super(FirstExperiment, self).__init__()
    self.userid = userid
    self.layers = self.estimate_layers([(COLORS, "color"), (TEXTS, "text")])

  def get_choice(self, choices, salt):
    if not choices: return
    hash_val = int(hashlib.sha1('salt.%s.%d' % (salt, self.userid)).hexdigest()[:15], 16)
    return choices[hash_val % len(choices)]

  def estimate_layers(self, vals):
    return map(self.get_choice, *zip(*vals))

  @base
  def button_color(self): return "red"

  @around(green)
  def button_color(self): return "green"


  @base
  def button_text(self): return "Sign up."

  @around(join)
  def button_text(self): return "Join now!"

  def get(self, name):
    if not hasattr(self, name): return None
    with activelayers(*self.layers):
      return getattr(self, name)()



# experiment objects include all input data
s = "User{:<4d}{:^12s}{:^10s}"
print s.format(0, "-text-", "-color-")
for i in xrange(1, 15):
  exp = FirstExperiment(userid=i)
  print s.format(i, exp.get('button_text'), exp.get('button_color'))