


class Parameters:
  def __init__(self):
    self.icu_percentage = 0
    self.ventilation_percentage = 0
    self.cases_hospital_percentage = 0
    self.total_population = 0
    self.icu_capacity = 0
    self.ventilator_capacity = 0
    self.avg_delay_infection = 0
    self.avg_contagious_period = 0
    self.contagious_speed = 0
    self.avg_stay_icu = 0
    self.avg_stay_ventilator = 0

  def set_icu_pc(self, value):
    self.icu_percentage = value

  def set_ventilation_pc(self, value):
    self.ventilation_percentage = value

  def set_cases_hospital_pc(self, value):
    self.cases_hospital_percentage = value

  def set_total_population(self, value):
    self.total_population = value

  def set_icu_capacity(self, value):
    self.icu_capacity = value

  def set_ventilator_capacity(self, value):
    self.ventilator_capacity = value

  def set_avg_delay_infection(self, value):
    self.avg_delay_infection = value

  def set_avg_contagious_period(self, value):
    self.avg_contagious_period  = value

  def set_avg_stay_icu(self, value):
    self.avg_stay_icu = value

  def set_avg_stay_ventilator(self, value):
    self.avg_stay_ventilator = value