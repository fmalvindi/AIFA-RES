'''
Created on 2024 Feb 22

@author: QD6204
'''
import pandas as pd
import numpy as np
import os 
from Prices import WORKING_FOLDER, PARAMETERS, MATCH_ZONE,\
    PRODUCTION_IMPACT, PRODUCTION, HORIZON, OUTPUT_FOLDER
   
#import pylab

from pathlib import Path
from datetime import datetime, timedelta
import profile
from Prices.utils import retrieve_parameters, compute_time_switch,\
    compute_profile_cod, compute_profile_ppa_end, weighting_function
#import matplotlib.pyplot as plt


# list of available projects and scenarios and resolution
#PROJECTS = ["RAMACCA", "SUBER", "CAPRACOTTA","INTRONATA","LESINA","SAN PAOLO"]
PROJECTS = ["ZEPHYRUS"]
SCENARIOS = ["Ref-e C-L","Afry - C-L","Af-Ba-Re - Central","Engie Impact","Ref-e - Central",'Afry - Central','Af-Ba-Re - Central',"Afry - Low","Baringa - Central","Af-Re - Central"]
RESOLUTIONS = ['HOUR','MONTH']

# user's selection of project and scenario
#SELECT_PROJ = 0
SELECT_SCEN = 3
SELECT_RES = 1

def main(project):
    # selected project and scenario
    PROJECT = project
    SCENARIO = SCENARIOS[SELECT_SCEN]
    RES = RESOLUTIONS[SELECT_RES]
    
    # print running case
    print(PROJECT) 
    print(SCENARIO)
    print (RES)
     
    # Corresponding parameters
    ZONE= MATCH_ZONE[PROJECT]
    PRICES_FILENAME = os.path.join(WORKING_FOLDER,ZONE,"Prices_Hourly.xlsx")
    PROFIT_SHARING_GEMS,PROFIT_SHARING_APPLE, GEMS_MARGIN_1, GEMS_MARGIN_2, COD,PPA_DUR, FLOOR, TUNNEL, CAP = retrieve_parameters(PARAMETERS,PROJECT)
    
    # manipulating datetype 
    COD_date, MARGIN_THRESH_str, END_PPA, END_PPA_date = compute_time_switch(COD, PPA_DUR)
    
    ##Select Production Profile
    #Reading  data
    if SCENARIO == "Engie Impact":    
        df_prod = pd.read_excel(PRODUCTION_IMPACT)
           
    else:
        df_prod = pd.read_excel(PRODUCTION)
         
    #Select project and compute profile
    df_prod_sel = df_prod[["MONTH","DAY","HOUR",PROJECT]]
    df_prod_sel["percentage"] = df_prod_sel[PROJECT].values/df_prod_sel[PROJECT].values.sum()
    profile = df_prod_sel[["MONTH","DAY","HOUR","percentage"]]
    
    #Compute first and final year profiles
    profile_1st_year = compute_profile_cod(df_prod, PROJECT, COD_date)
    profile_last_year = compute_profile_ppa_end(df_prod, PROJECT, END_PPA_date, END_PPA)
    
    
    # Selecting prices
    df_prices= pd.read_excel(PRICES_FILENAME, index_col=0)
    df_prices_sel = df_prices.loc[:, [SCENARIO]]
    # Selecting horizon subset
    df_prices_sel = df_prices_sel[(df_prices_sel.index>=COD)&(df_prices_sel.index<=END_PPA)]
    
    #Grouping production according to the selected resolution
    #if RES != 'HOUR':
        
    #Handling the profile of the first year
    df2=df_prod.copy()
    df2.index = pd.to_datetime({'year': COD_date.year, 'month': df2['MONTH'], 'day': df2['DAY']})    
    df2 =df2[(df2.index>=COD_date)]    
    #Handling the profile of the last year    
    df3=df_prod.copy()
    df3.index = pd.to_datetime({'year': END_PPA.year, 'month': df3['MONTH'], 'day': df3['DAY']})    
    df3 =df3[(df3.index<=END_PPA_date)] 
    
    if RES != "HOUR":
        
        prod_granular = df_prod[PROJECT]/ df_prod.groupby(RES)[PROJECT].transform('sum')
        prod_granular_start = df2[PROJECT]/ df2.groupby(RES)[PROJECT].transform('sum')
        prod_granular_end = df3[PROJECT]/ df3.groupby(RES)[PROJECT].transform('sum')    
    else:
        
        prod_granular = df_prod[PROJECT]/ df_prod[PROJECT].sum()
        prod_granular_start = df2[PROJECT]/ df2[PROJECT].sum()
        prod_granular_end = df3[PROJECT]/ df3[PROJECT].sum()      
            
    #Repeating the profile for all years except for the starting and the final ones
    prod_granular_repeated = np.tile(prod_granular,(len(np.unique(df_prices_sel.index.year))-2))
    #Adding starting one and final years
    prod_granular_repeated_new = np.hstack([prod_granular_start.values, prod_granular_repeated,prod_granular_end.values])
    
    #Multiplying the prices and the production profiles 
    prices_granular_weighted  = df_prices_sel.mul(prod_granular_repeated_new,axis=0)
    
    #Resampling weighted avg prices
    if RES !="HOUR":
        df_prices_sel= prices_granular_weighted.copy()
        df_prices_sel = df_prices_sel.resample(RES[0]).sum()    
    
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
    


    #############################
#    YEAR= 2027
#    plot= df_prices_sel[df_prices_sel.index.year==YEAR]
#    prices = plot.iloc[:,0]
#    cap = CAP

#    gems_margin = GEMS_MARGIN_1

#    floors = df_prices_sel["FLOOR"][df_prices_sel["FLOOR"].index.year==YEAR]
#    tunnels = df_prices_sel["TUNNEL"][df_prices_sel["TUNNEL"].index.year==YEAR] 
#    profit_sharing = df_prices_sel["PROFIT SHARING"][df_prices_sel["PROFIT SHARING"].index.year==YEAR]  

    
#    y1= prices
#    y2= cap*np.ones(len(prices))
#    y3 = FLOOR*np.ones(len(prices))
#    y4= floors
#    y5= tunnels
#    y6= profit_sharing
#    y7= gems_margin*np.ones(len(prices))
    
#    bar_width= 15
#    xx = prices.index
    
#    fig, ax1 =plt.subplots(figsize=(10,6))
    
#    bars7 = ax1.bar(xx, y7, width = bar_width ,color = (255/255, 71/255, 71/255),edgecolor = "black",label= "GEMs margin")  
#    bars2 = ax1.bar(xx, y4, bottom = y7, width = bar_width ,color = (0/255, 210/255, 125/255),edgecolor = "black",label= "floor prices")    
#    bars3 = ax1.bar(xx, y5, bottom = y4+y7,width = bar_width ,color = (0/255, 250/255, 149/255) ,edgecolor = "black",label= "tunnel prices")        
#    bars4 = ax1.bar(xx, y6, bottom = y4+y7+y5, width = bar_width ,color = (155/255, 255/255, 215/255),edgecolor = "black",label= "profit sharing")           
 
       
#    plot1= ax1.plot(xx, y2, color ="orange",linestyle="dashed", label= "CAP")    
#    plot2= ax1.plot(xx, y3,color ="0.75",linestyle="dashed", label = "FLOOR")   

#    ax1.legend(loc= "best") 
#    ax1.set_ylim(0, 150)
#    ax1.set_ylabel("€/MWh")    
#    ax1.set_xticks(xx)
#    ax1.set_xticklabels(xx.strftime('%b')) 
      
#    ax1.set_title(PROJECT)
#    ax2 = ax1.twinx()
#    ax2.set_ylim(0, 150)
#    line1 = ax2.plot(xx, y1 ,color = (68/255, 114/255, 196/255),label= "merchant revenues")    
#    lines1, labels1 = ax1.get_legend_handles_labels()
#    lines2, labels2 = ax2.get_legend_handles_labels()
#    ax1.legend(lines1 + lines2, labels1 + labels2)


    
#    plt.savefig(r"C:\Users\QD6204\OneDrive - ENGIE\Desktop\SanPaolo.png", dpi=1100)
    
    ###############################
     
    
    # Computing the yearly values
    data = []
    for year in np.unique(df_prices_sel.index.year):
    
        # Looping over each year
        df_subset = df_prices_sel[df_prices_sel.index.year==year]
              
        if (year == COD_date.year):
            
            if RES == "HOUR":
                profile_aggregated = profile_1st_year
            else: 
                profile_aggregated = profile_1st_year.groupby(RES).sum()
                
            floor_weighted, tunnel_weighted, profit_weighted, price_weighted = weighting_function(df_subset, profile_aggregated)
    
        elif (year == END_PPA.year): 
            
            if RES == "HOUR":
                profile_aggregated = profile_last_year
            else: 
                profile_aggregated = profile_last_year.groupby(RES).sum()        
            
            floor_weighted, tunnel_weighted, profit_weighted,price_weighted = weighting_function(df_subset, profile_aggregated)        
                                  
        else:
            
            if RES == "HOUR":
                profile_aggregated = profile
            else: 
                profile_aggregated = profile.groupby(RES).sum()           
            
            floor_weighted, tunnel_weighted, profit_weighted, price_weighted = weighting_function(df_subset, profile_aggregated)                      
            
        data.append((floor_weighted,tunnel_weighted,profit_weighted, price_weighted))
    
    # Arranging in a df and exporting to Excel
    df_results = pd.DataFrame(data, columns= ["FLOOR","TUNNEL","PROFIT SHARING","ARP"])    
    df_results.insert(0, "YEAR", np.unique(df_prices_sel.index.year))
    pd.set_option('display.float_format', lambda x: '{:.2f}'.format(x))
    
    print(df_results)
    
    num_digits = 2
    float_format_str = f'%.{num_digits}f'
    
    df_results.to_excel(os.path.join(OUTPUT_FOLDER,"Results %s-%s-%s.xlsx"%(PROJECT,SCENARIO,RES)), float_format=float_format_str,index= False)
    
if __name__ == "__main__":
    
    for project in PROJECTS: 
        
        main(project)