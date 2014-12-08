
def choice(choices, userid, salt):
    if len(choices) == 0:
      return []
    import hashlib
    hash_val = int(hashlib.sha1('salt.%s.%d' % (salt, userid)).hexdigest()[:15], 16)
    return choices[hash_val % len(choices)]

class FirstExperiment(object):

  def __init__(self, userid):
    super(FirstExperiment, self).__init__()
    self.userid = userid
    self._assignment = {
      "button_color":
        choice(['red', 'green'], userid, "color"),
      "button_text":
        choice(['Join now!', 'Sign up.'], userid, "text")
    }

  def get(self, name):
    return self._assignment.get(name)

# experiment objects include all input data
s = "User{:<4d}{:^12s}{:^10s}"
print s.format(0, "-text-", "-color-")
for i in xrange(1, 15):
  exp = FirstExperiment(userid=i)
  print s.format(i, exp.get('button_text'), exp.get('button_color'))