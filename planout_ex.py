from planout.experiment import SimpleExperiment
from planout.ops.random import UniformChoice

class FirstExperiment(SimpleExperiment):
  def assign(self, params, userid):

    params.button_color = UniformChoice(
      choices=['red', 'green'], unit=userid)

    params.button_text = UniformChoice(
      choices=['Join now!', 'Sign up.'], unit=userid)


s = "User{:<4d}{:^12s}{:^10s}"
print s.format(0, "-text-", "-color-")
for i in xrange(1, 15):
  exp = FirstExperiment(userid=i)
  print s.format(i, exp.get('button_text'), exp.get('button_color'))