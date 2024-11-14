'''
Created on 2024 Mar 5

@author: QD6204
'''
from datetime import datetime, timedelta
import pandas as pd

def retrieve_parameters(parameters,project):
    
    profit_sharing_gems = parameters[project]["PS GEMS"]
    profit_sharing_apple = parameters[project]["PS APPLE"]
    gems_margin_1 = parameters[project]['GEMS MARGIN 1']
    gems_margin_2 = parameters[project]['GEMS MARGIN 2']
    cod = parameters[project]["COD"]
    ppa_dur = parameters[project]["PPA DURATION"]
    floor = parameters[project]["FLOOR"]
    tunnel = parameters[project]["TUNNEL"]
    cap = floor + tunnel
    
    return profit_sharing_gems,profit_sharing_apple,gems_margin_1,gems_margin_2, cod,ppa_dur, floor, tunnel, cap

def compute_time_switch(cod, ppa_dur):
    
    COD_date = datetime.strptime(cod,"%d/%m/%Y")
    MARGIN_THRESH = datetime( COD_date.year+3, COD_date.month, COD_date.day)
    MARGIN_THRESH_str = MARGIN_THRESH.strftime("%d/%m/%Y")
    
    END_PPA = datetime(COD_date.year+ppa_dur, COD_date.month, COD_date.day)
    END_PPA_date = END_PPA.strftime("%d/%m/%Y")
    
    return COD_date, MARGIN_THRESH_str, END_PPA, END_PPA_date  
    
def compute_profile_cod(df_prod, project, cod_date):
    
    df_prod_cod = df_prod[["MONTH","DAY","HOUR",project]]
    df_prod_cod.index = pd.to_datetime({'year': cod_date.year, 'month': df_prod_cod["MONTH"], 'day': df_prod_cod['DAY']})
    df_prod_cod =df_prod_cod[(df_prod_cod.index>=cod_date)] 
    df_prod_cod["percentage"] = df_prod_cod[project].values/df_prod_cod[project].values.sum()
    profile_1st_year = df_prod_cod[["MONTH","DAY","HOUR","percentage"]]     
    
    return profile_1st_year 


def compute_profile_ppa_end(df_prod, project, end_ppa_date, end_ppa):
    
    df_prod_end = df_prod[["MONTH","DAY","HOUR",project]]
    df_prod_end.index = pd.to_datetime({'year': end_ppa.year, 'month': df_prod_end["MONTH"], 'day': df_prod_end['DAY']})
    df_prod_end =df_prod_end[(df_prod_end.index<=end_ppa_date)] 
    df_prod_end["percentage"] = df_prod_end[project].values/df_prod_end[project].values.sum()
    profile_last_year = df_prod_end[["MONTH","DAY","HOUR","percentage"]]
         
    return profile_last_year

def weighting_function(df_subset,final_profile):
    
            floor_weighted = (df_subset["FLOOR"].values * final_profile["percentage"].values).sum()
            tunnel_weighted = (df_subset["TUNNEL"].values * final_profile["percentage"].values).sum()
            profit_weighted = (df_subset["PROFIT SHARING"].values * final_profile["percentage"].values).sum()    
            price_weighted = (df_subset.iloc[:, 0]* final_profile["percentage"].values).sum()    
            
            return floor_weighted, tunnel_weighted, profit_weighted,price_weighted
