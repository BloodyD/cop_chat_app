from contextpy import layer, base, around, activelayer, proceed

employerLayer = layer("Employer")
lowercase = layer("lowercase")

class Person(object):
  def __init__(self, name, employer):
    self.name = name
    self.employer = employer

  @base
  def getDetails(self):
    return self.name

  @around(employerLayer)
  def getDetails(self):
    return proceed() + ", "+ self.employer

  @around(lowercase)
  def getDetails(self):
    return proceed().lower()

person = Person("Michael Perscheid",  "HPI")
print person.getDetails()

with activelayer(employerLayer):
  print person.getDetails()
  with activelayer(lowercase):
    print person.getDetails()

with activelayer(lowercase):
  print person.getDetails()
  with activelayer(employerLayer):
    print person.getDetails()