
class Model:
  def __init__(self):
    self.data = 0



  #TO DO
  def calc_basis(self, actual, parameters, measures):
    if actual == 0 or parameters == 0 or measures == 0:
      return 0
    self.data["real_infected"] = []
    self.data["contagious"] = []


  #TO DO
  def set_date(self):
    self.data["date"] = []

  def calc_growth_factor(self, measures):
    self.data["growth_factor"] = []


  def calc_confirmed_cases(self, parameters):
    self.data["confirmed_cases"] = []

  def calc_cumul_confirmed_cases(self, measures):
    self.data["cumul_confirmed_cases"] = []

  def calc_real_infected(self, parameters):
    self.data["cumul_confirmed_cases"] = []

  def calc_transmission_rate(self):
    self.data["transmission_rate"] = []

  def calc_contagious(self, parameters):
    self.data["contagious"] = []

  def calc_contagious_pc(self, parameters):
    self.data["contagious_pc"] = []

  def calc_cumul_real_infected(self, parameters):
    self.data["cumul_real_infected"] = []

  def calc_pop_infected_recovered_pc(self, parameters):
    self.data["pop_infected_recovered_pc"] = []

  def calc_pop_susceptible_pc(self):
    self.data["pop_susceptible_pc"] = []