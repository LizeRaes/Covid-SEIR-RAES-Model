from parameters import *
from measures import *
import pandas as pd
import time

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 2000)

class Model:
    def __init__(self):
        self.param = Parameters()
        self.R0s = Measures.fromXls('param_test.xlsx')
        self.data = 0
  
    #TO DO
    def calc_basis(self, actual, parameters, measures):
        if actual == 0 or parameters == 0 or measures == 0:
          return 0
        self.data["real_infected"] = []
        self.data["contagious"] = []
    
    def get_beta(R0s, gamma, date):
        R = R0s.getR0(date)
        return R*gamma
    
    # store a vectore as [Sn, In, Rn, dSn, dIn, dRn]
    def store_vector(model, date, values):
        [Sn, In, Rn, dSn, dIn, dRn] = values
        model.loc[date] = values
        return model


    def get_vector(model, date):
        [S, I, R, dS, dI, dR] = np.float64(model.loc[date])
        return [S, I, R, dS, dI, dR]


    def populate_core (model, param, R0s):
        pivotDate = np.datetime64(param.pivotDate)
        pivotDate_min1 = np.datetime64(param.pivotDate-timedelta(days=1))
        
        # n_1 is used to refer to n-1
        
        beta = Model.get_beta(R0s, param.gamma, pivotDate)
        beta_1 = Model.get_beta(R0s, param.gamma, pivotDate_min1)
        
        dSn = param.undertest_factor * param.confirmed_pivot_date
        In_1 = dSn / beta_1
        Sn = param.total_population - (param.undertest_factor * param.cumul_confirmed_pivot_date)
        dRn = param.gamma*In_1
        dIn = dSn - dRn
        Sn_1 = Sn + dSn
        In = In_1 + dIn
        Rn_1 = param.total_population - Sn_1 - In_1
        Rn = Rn_1 + dRn

        dRn_1 = dRn / (1+(Sn * beta/param.total_population))
        dSn_1 = dSn / (1+(Sn * beta/param.total_population))
        dIn_1 = dSn_1 - dRn_1
        
        model = Model.store_vector(model, pivotDate, [Sn, In, Rn, dSn, dIn, dRn])
        model = Model.store_vector(model, pivotDate_min1, [Sn_1, In_1, Rn_1, dSn_1, dIn_1, dRn_1])
        
        return model

    def generate_cumul_infected(model, param, R0s):
        pivotDate = np.datetime64(param.pivotDate)
        pivotIndex = model.index.get_loc(pivotDate)
        dSlist = model['dS'].to_list()
        
        calc = [0]*len(dSlist)
        
        calc[pivotIndex] = param.undertest_factor * param.cumul_confirmed_pivot_date
        for i in range(pivotIndex-1,0,-1):
            calc[i] = calc[i+1]-dSlist[i+1]
        
        for i in range(pivotIndex+1,len(calc)):
            calc[i] = calc[i-1]+dSlist[i]
        
        model['cumul_infected'] = calc
        return model
        


    def calculate_next_step(model, date, param, beta):
        #print('get model for '+str(date+np.timedelta64(1,'D'))+'based on '+str(date)+' with beta '+str(beta))
        [Sn, In, Rn, dSn, dIn, dRn] = Model.get_vector(model, date)
        #print('\n\n\n')
        #print('get model for '+str(date+np.timedelta64(1,'D'))+'based on '+str(date)+' with beta '+str(beta))
        #print('-->'+str([Sn, In, Rn, dSn, dIn, dRn]))
        
        dSn1 = beta * Sn * In / param.total_population
        dRn1 = param.gamma * In
        dIn1 = dSn1 - dRn1
        Sn1 = Sn - dSn1
        In1 = In + dIn1
        Rn1 = Rn + dRn1
        
        #print('++>'+str([Sn1, In1, Rn1, dSn1, dIn1, dRn1]))
        
        model = Model.store_vector(model, date+np.timedelta64(1,'D'), [Sn1, In1, Rn1, dSn1, dIn1, dRn1])
        return model

    def calculate_previous_step(model, date, param, beta):
        [Sn1, In1, Rn1, dSn1, dIn1, dRn1] = Model.get_vector(model, date)
        
        Sn = Sn1 + dSn1
        In = In1 /(1+beta-param.gamma)
        Rn = param.total_population - Sn - In
        dSn = dSn1 / (1+(Sn1 * beta/param.total_population))
        dRn = dRn1 / (1+(Sn1 * beta/param.total_population))
        dIn = dSn - dRn
        
        model = Model.store_vector(model, date-np.timedelta64(1,'D'), [Sn, In1, Rn, dSn, dIn, dRn])
        return model

    def generate_confirmed_today(model, param):
        dSlist = model['dS'].to_list()
        
        calc = [0]*len(dSlist)
        delta = param.avg_delay_infection
        for i in range(delta, len(calc)):
            calc[i] = dSlist[i-delta]/param.undertest_factor
        model['confirmed_today']=calc
        return model

    def generate_confirmed_cumul(model, param):
        cumulList = model['cumul_infected'].to_list()
        
        calc = [0]*len(cumulList)
        delta = param.avg_delay_infection
        for i in range(delta, len(calc)):
            calc[i] = cumulList[i-delta]/param.undertest_factor
        model['confirmed_cumul']=calc
        return model

    def generate_hospital_today(model, param):
        confirmedList = model['confirmed_today'].to_list()
        delay = param.delay_confirmed_hospital
        length = param.avg_stay_hospital
        proportion = param.cases_hospital_percentage
        
        calc = [0]*len(confirmedList)
        
        start = delay+length
        
        for i in range(start, len(calc)):
            count = 0
            for j in range(i-delay-length+1,i-delay+1):
                count += confirmedList[j]
            calc[i] = count*proportion
        
        model['hospital_today']=calc
        return model

    def generate_ICU_today(model, param):
        hospitalList = model['hospital_today'].to_list()
        proportion = param.icu_percentage
        
        calc = [i * proportion for i in hospitalList]
        
        model['ICU_today'] = calc
        return model

    def generate_die_today(model, param):
        hospitalList = model['hospital_today'].to_list()
        proportion = param.die_percentage
        
        calc = [i * proportion for i in hospitalList]
        
        model['die_today'] = calc
        return model

    def generate_projection(actuals, param, R0s):
        print(actuals)
        print(param)
        print(R0s)
        
        start_time = time.time()
        
        dateRange = pd.date_range('2020-01-01', '2020-12-31', freq='D')
        model = df = pd.DataFrame({'Date': dateRange})
        model = model.set_index('Date')
        NaN = np.nan
        model['S'] = NaN
        model['I'] = NaN
        model['R'] = NaN
        model['dS'] = NaN
        model['dI'] = NaN
        model['dR'] = NaN
        #model.loc[model['Date']=='2020-03-12', 'dI'] = 10
        #print(model)
        #print(model.dtypes)
        #model.loc[model['Date']=='2020-03-15', 'dI'] = 15
        #print(model.loc[model['Date']=='2020-03-15', 'dI'])
        #print(model.loc[model['Date']==np.datetime64(param.pivotDate)])
        #print(model.loc[model['Date']==np.datetime64(param.pivotDate-timedelta(days=1))])
        model = Model.populate_core(model, param, R0s)
        #print(model)
        #print(model.loc[(model['Date']<=np.datetime64(param.pivotDate)) & (model['Date']>=np.datetime64(param.pivotDate-timedelta(days=1)))])
        #print(model.loc[np.datetime64(param.pivotDate):np.datetime64(param.pivotDate-timedelta(days=1))])
        #print(model.loc[model['Date']>=np.datetime64(param.pivotDate-timedelta(days=1))])
        #print(R0s)
        
        datesComing = model.loc[np.datetime64(param.pivotDate):max(model.index)].index
        for date in datesComing[:-1]:
            model = Model.calculate_next_step(model, date, param, Model.get_beta(R0s, param.gamma, date))
        
        datesBefore = model.loc[min(model.index):np.datetime64(param.pivotDate-timedelta(days=1))].index
        for date in reversed(datesBefore[1:]):
            model = Model.calculate_previous_step(model, date, param, Model.get_beta(R0s, param.gamma, date))
        
        #print(Model.get_vector(model, np.datetime64(param.pivotDate)))
        
        model = Model.generate_cumul_infected(model, param, R0s)
        model = Model.generate_confirmed_today(model,param)
        model = Model.generate_confirmed_cumul(model,param)
        model = Model.generate_hospital_today(model,param)
        model = Model.generate_ICU_today(model,param)
        model = Model.generate_die_today(model,param)
        
        end_time = time.time()
        
        print(model)
        
        print("--- %s seconds ---" % (end_time - start_time))
  
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


def main():
    # my code here
    testParam = Parameters()
    testMeasure = Measures.fromXls('param_test.xlsx')
    testActuals = {}
    Model.generate_projection(testActuals, testParam, testMeasure)


if __name__ == "__main__":
    main()