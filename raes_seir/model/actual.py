import pandas as pd

class Actual:
  def __init__(self):
    self.data = 0


  #TO DO
  def import_data_from_csv(self, csv_path):
    self.data = 0
    self.calc_icu_hopi_vs_today()
    self.calc_venti_vs_hospi_today()


  #TO DO
  def calc_icu_vs_hospi_today(self):
    self.data["icu_vs_hosp_today"] = 0

  # TO DO
  def calc_venti_vs_hospi_today(self):
    self.data["venti_vs_hosp_today"] = 0