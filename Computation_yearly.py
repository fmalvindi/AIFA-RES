'''
Created on 2024 Feb 22

@author: QD6204
'''
import pandas as pd
import numpy as np
import os 
from Prices import WORKING_FOLDER, PARAMETERS, MATCH_ZONE,\
    PRODUCTION_IMPACT, PRODUCTION, HORIZON, OUTPUT_FOLDER
import pylab

from pathlib import Path
from datetime import datetime, timedelta
import profile

# list of available projects and scenarios and resolution
PROJECTS = ["RAMACCA", "SUBER", "CAPRACOTTA","INTRONATA","LESINA","SAN PAOLO"]
SCENARIOS = ['Afry - Central','Af-Ba-Re - Central',"Afry - Low","Afry - C-L","Baringa - Central","Ref-e - Central","Af-Ba-Re - Central","Engie Impact"]
RESOLUTIONS = ['HOUR', 'DAY','MONTH']


# user's selection of project and scenario
SELECT_PROJ = 4
SELECT_SCEN = 3
SELECT_RES = 2

# selected project and scenario
PROJECT = PROJECTS[SELECT_PROJ]
SCENARIO = SCENARIOS[SELECT_SCEN]
RES = RESOLUTIONS[SELECT_RES]

print(PROJECT) 
print(SCENARIO)
print (RES)
 
ZONE= MATCH_ZONE[PROJECT]
PRICES_FILENAME = os.path.join(WORKING_FOLDER,ZONE,"Prices_Hourly.xlsx")

# Corresponding parameters --> into a function
DELTA = -2
FLOOR = PARAMETERS[PROJECT]["FLOOR"]+ DELTA
TUNNEL = PARAMETERS[PROJECT]["TUNNEL"]
CAP = FLOOR + TUNNEL

PROFIT_SHARING_GEMS = PARAMETERS[PROJECT]["PS GEMS"]
PROFIT_SHARING_APPLE = PARAMETERS[PROJECT]["PS APPLE"]
GEMS_MARGIN_1 = PARAMETERS[PROJECT]['GEMS MARGIN 1']-2
GEMS_MARGIN_2 = PARAMETERS[PROJECT]['GEMS MARGIN 2']-2
COD = PARAMETERS[PROJECT]["COD"]
PPA_DUR = PARAMETERS[PROJECT]["PPA DURATION"]

# manipulating datetype --> into a function
COD_date = datetime.strptime(COD,"%d/%m/%Y")
MARGIN_THRESH = COD_date + timedelta(days=365*3+1)
MARGIN_THRESH_str = MARGIN_THRESH.strftime("%d/%m/%Y")

END_PPA = COD_date + timedelta(days=365*PPA_DUR)
END_PPA_date = END_PPA.strftime("%d/%m/%Y")

# Select Production Profile
if SCENARIO == "Engie Impact":
    
    df_prod = pd.read_excel(PRODUCTION_IMPACT)
#    profile = df_prod.values
else:
    df_prod = pd.read_excel(PRODUCTION)
#    df_prod_sel = df_prod.loc[:, [PROJECT]]
    df_prod_sel = df_prod[["MONTH","DAY","HOUR",PROJECT]]
    df_prod_sel["percentage"] = df_prod_sel[PROJECT].values/df_prod_sel[PROJECT].values.sum()
    profile = df_prod_sel[["MONTH","DAY","HOUR","percentage"]]

    df_prod_sel2 = df_prod[["MONTH","DAY","HOUR",PROJECT]]
    df_prod_sel2.index = pd.to_datetime({'year': COD_date.year, 'month': df_prod_sel2['MONTH'], 'day': df_prod_sel2['DAY']})
    df_prod_sel2 =df_prod_sel2[(df_prod_sel2.index>=COD_date)] 
    df_prod_sel2["percentage"] = df_prod_sel2[PROJECT].values/df_prod_sel2[PROJECT].values.sum()
    profile_1st_year = df_prod_sel2[["MONTH","DAY","HOUR","percentage"]]    

    df_prod_sel3 = df_prod[["MONTH","DAY","HOUR",PROJECT]]
    df_prod_sel3.index = pd.to_datetime({'year': END_PPA.year, 'month': df_prod_sel3['MONTH'], 'day': df_prod_sel3['DAY']})
    df_prod_sel3 =df_prod_sel3[(df_prod_sel3.index<=END_PPA_date)] 
    df_prod_sel3["percentage"] = df_prod_sel3[PROJECT].values/df_prod_sel3[PROJECT].values.sum()
    profile_last_year = df_prod_sel3[["MONTH","DAY","HOUR","percentage"]]



    

# Selecting prices
df_prices= pd.read_excel(PRICES_FILENAME, index_col=0)
df_prices_sel = df_prices.loc[:, [SCENARIO]]
# Selecting horizon subset
df_prices_sel = df_prices_sel[(df_prices_sel.index>=COD)&(df_prices_sel.index<=END_PPA)]
if RES != 'HOUR':
    
     

    df2=df_prod.copy()
    df2.index = pd.to_datetime({'year': COD_date.year, 'month': df2['MONTH'], 'day': df2['DAY']})    
    df2 =df2[(df2.index>=COD_date)]    
    prod_granular = df_prod[PROJECT]/ df_prod.groupby(RES)[PROJECT].transform('sum')
    prod_granular_start = df2[PROJECT]/ df2.groupby(RES)[PROJECT].transform('sum')
    
    df3=df_prod.copy()
    df3.index = pd.to_datetime({'year': END_PPA.year, 'month': df3['MONTH'], 'day': df3['DAY']})    
    df3 =df3[(df3.index<=END_PPA_date)]    
    prod_granular_end = df3[PROJECT]/ df3.groupby(RES)[PROJECT].transform('sum')    
    
    
    
    prod_granular_repeated = np.tile(prod_granular,(len(np.unique(df_prices_sel.index.year))-2))
    len(prod_granular_repeated)
    prod_granular_repeated_new = np.hstack([prod_granular_start.values, prod_granular_repeated,prod_granular_end.values])
    len(prod_granular_repeated_new)

  
    prices_granular_weighted  = df_prices_sel.mul(prod_granular_repeated_new,axis=0)

    df_prices_sel= prices_granular_weighted.copy()
    df_prices_sel = df_prices_sel.resample("M").sum()
#    df_prices_sel = df_prices_sel.resample(RES[0]).sum()
# Adding Floor
df_prices_sel["FLOOR"] = FLOOR - (df_prices_sel.index<=MARGIN_THRESH_str)*GEMS_MARGIN_1 - (df_prices_sel.index>MARGIN_THRESH_str)*GEMS_MARGIN_2

# Adding Tunnel
GAP_1 = (df_prices_sel[SCENARIO]-FLOOR) * PROFIT_SHARING_GEMS
GAP_1_pos = GAP_1.apply(lambda x: max(x, 0))
GAP_2 = (CAP-FLOOR)* PROFIT_SHARING_GEMS


tunnel_prices = GAP_1_pos.apply(lambda x: min(x, GAP_2))
df_prices_sel["TUNNEL"]= tunnel_prices

# Adding Profit Sharing
profit_sharing = df_prices_sel[SCENARIO]-CAP
profit_sharing[profit_sharing<0] = 0
df_prices_sel["PROFIT SHARING"]= profit_sharing * PROFIT_SHARING_GEMS * PROFIT_SHARING_APPLE


# Compute the yearly values
data = []
for year in np.unique(df_prices_sel.index.year):

    df_subset = df_prices_sel[df_prices_sel.index.year==year]
    
    if RES == 'HOUR':
           
            floor_weighted = (df_subset["FLOOR"].values * profile["percentage"].values).sum()
            tunnel_weighted = (df_subset["TUNNEL"].values * profile["percentage"].values).sum()
            profit_weighted = (df_subset["PROFIT SHARING"].values * profile["percentage"].values).sum()
        
        
    else:
       
        if (year == COD_date.year):
 
            profile_aggregated = profile_1st_year.groupby(RES).sum()
            floor_weighted = (df_subset["FLOOR"].values * profile_aggregated["percentage"].values).sum()
            tunnel_weighted = (df_subset["TUNNEL"].values * profile_aggregated["percentage"].values).sum()
            profit_weighted = (df_subset["PROFIT SHARING"].values * profile_aggregated["percentage"].values).sum()



        elif (year == END_PPA.year): 
            
            profile_aggregated = profile_last_year.groupby(RES).sum()
            floor_weighted = (df_subset["FLOOR"].values * profile_aggregated["percentage"].values).sum()
            tunnel_weighted = (df_subset["TUNNEL"].values * profile_aggregated["percentage"].values).sum()
            profit_weighted = (df_subset["PROFIT SHARING"].values * profile_aggregated["percentage"].values).sum()            
                      
        
        else:
            
            profile_aggregated = profile.groupby(RES).sum()
            floor_weighted = (df_subset["FLOOR"].values * profile_aggregated["percentage"].values).sum()
            tunnel_weighted = (df_subset["TUNNEL"].values * profile_aggregated["percentage"].values).sum()
            profit_weighted = (df_subset["PROFIT SHARING"].values * profile_aggregated["percentage"].values).sum()            
            
            
            
    data.append((floor_weighted,tunnel_weighted,profit_weighted))

df_results = pd.DataFrame(data, columns= ["FLOOR","TUNNEL","PROFIT SHARING"])    
df_results.insert(0, "YEAR", np.unique(df_prices_sel.index.year))
pd.set_option('display.float_format', lambda x: '{:.2f}'.format(x))

print(df_results)

num_digits = 2
float_format_str = f'%.{num_digits}f'

df_results.to_excel(os.path.join(OUTPUT_FOLDER,"Results %s-%s-%s.xlsx"%(PROJECT,SCENARIO,RES)), float_format=float_format_str,index= False)

