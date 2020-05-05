import pandas as pd
from datetime import date
from datetime import timedelta


class Parameters:
    def __init__(self):
        self.icu_percentage_old = 0.22
        self.ventilation_percentage_old = 0.16
        self.die_percentage = 0.042
        self.cases_hospital_percentage_old = 0.49
        self.total_population = 11400000
        self.icu_capacity = 0
        self.ventilator_capacity = 0
        self.avg_delay_infection = 12
        self.avg_contagious_period = 4
        self.contagious_speed = 0
        self.avg_stay_hospital = 12
        self.delay_confirmed_hospital = 1
        self.avg_stay_icu = 12
        self.avg_stay_ventilator = 12
        self.date_more_20_death = date.fromisoformat('2020-03-19')
        self.days_before_20 = 10
        self.pivotDate = self.date_more_20_death - \
            timedelta(days=self.days_before_20) - \
            timedelta(days=self.avg_delay_infection)
        self.confirmed_pivot_date = 29
        self.cumul_confirmed_pivot_date = 200
        self.gamma = 1/self.avg_contagious_period
        self.date_X = date.fromisoformat('2020-02-28')
        self.estim_percent_infect_date_X = 0.0006
        self.cumul_infect_actuals_date_X = 314  # on real date X + avg_delay_infection
        self.undertest_factor = self.estim_percent_infect_date_X * \
            self.total_population / self.cumul_infect_actuals_date_X
        self.cases_hospital_percentage = self.cases_hospital_percentage_old * \
            (1/self.undertest_factor)
        self.icu_percentage = self.icu_percentage_old * self.cases_hospital_percentage
        self.ventilation_percentage = self.ventilation_percentage_old * \
            self.cases_hospital_percentage

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
        self.avg_contagious_period = value

    def set_avg_stay_icu(self, value):
        self.avg_stay_icu = value

    def set_avg_stay_ventilator(self, value):
        self.avg_stay_ventilator = value

    def __str__(self):
        output = (str(self.pivotDate) + '\n' +
                  str(self.gamma) + '\n' +
                  str(self.undertest_factor) + '\n' +
                  str(self.confirmed_pivot_date) + '\n' +
                  str(self.cumul_confirmed_pivot_date) + '\n' +
                  str(self.total_population) + '\n' +
                  str(self.avg_delay_infection) + '\n' +
                  str(self.days_before_20) + '\n' +
                  str(self.date_more_20_death))
        return output


def main():
    # my code here
    #testList = Measures.default()
    #testList = Measures.fromList(['2020-01-01','2020-02-01'],[1.45, 1.67])
    testParam = Parameters()
    print(testParam.pivotDate)
    print(testParam.gamma)
    print(testParam.undertest_factor)
    print(testParam.confirmed_pivot_date)
    print(testParam.cumul_confirmed_pivot_date)
    print(testParam.total_population)
    print(testParam.avg_delay_infection)
    print(testParam.days_before_20)
    print(testParam.date_more_20_death)
    print('-----')
    print(testParam)


if __name__ == "__main__":
    main()
