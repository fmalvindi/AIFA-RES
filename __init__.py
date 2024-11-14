
import pandas as pd
import os as path
import os 

WORKING_FOLDER = r"Z:\AIFA\04. Projects\AIFA_DB\PPA Apple\3. Curve prezzi\2. Curve per Impianto\7. Python"
PRODUCTION = os.path.join(WORKING_FOLDER,"Production_external.xlsx")
PRODUCTION_IMPACT = os.path.join(WORKING_FOLDER,"Production_Impact.xlsx")
OUTPUT_FOLDER = os.path.join(WORKING_FOLDER,"Output")

HORIZON = [year for year in range(2023,2043 + 1)]


MATCH_ZONE = {
                'RAMACCA': "SICI",
                'SUBER' : 'SICI',
                'CAPRACOTTA': 'SUD',
                'INTRONATA': 'SICI',
                'LESINA':'SUD',
                'SAN PAOLO': 'SUD',
                'ZEPHYRUS': 'SUD',
                       
                }                   

PARAMETERS = {
               'RAMACCA':   {
#                              'FLOOR': 70.94,
                              'FLOOR': 75.94,
                              'TUNNEL': 2.5,               
#                              'COD': '31/10/2026',             
                              'COD': '31/12/2026',   
                              'GEMS MARGIN 1': 7.17,     
                              'GEMS MARGIN 2': 6,                                                 
                              'PS GEMS': 1,   
                              'PS APPLE': 0.25,   
                              'PPA DURATION': 12,                              
                             },     
               
               'SUBER':   {
                              'FLOOR': 77.31,
                              'TUNNEL': 0,               
#                              'COD': '31/12/2024',     
# base case                             'COD': '31/03/2025',   
                              'GEMS MARGIN 1': -11.69,   
                              'GEMS MARGIN 2': -12.93,                 
                              'PS GEMS': 1,   
                              'PS APPLE': 0.25,   
                              'PPA DURATION': 12,                                                             
                             },                 
               'CAPRACOTTA':   {
#                              'FLOOR': 86.32,
#                               'FLOOR': 96.32,
                              'FLOOR': 92.32,
                              'TUNNEL': 2.50,               
#                              'COD': '30/11/2025',       
#  basecase                             'COD': '31/12/2025',  
                              'COD': '30/11/2025',       
#                              'GEMS MARGIN 1': 9.49,  
                              'GEMS MARGIN 1': 7.49,  
#                              'GEMS MARGIN 2': 6,        
                              'GEMS MARGIN 2': 4,                                       
                              'PS GEMS': 1,   
                              'PS APPLE': 0.25,   
                              'PPA DURATION': 15,                                                            
                             },                 
               'INTRONATA':   {
                              'FLOOR': 87.04,
                              'TUNNEL': 1.96,               
                              'COD': '31/12/2025',            
                              'GEMS MARGIN 1': 9.15,   
                              'GEMS MARGIN 2': 6,                 
                              'PS GEMS': 1,   
                              'PS APPLE': 0.2, 
                              'PPA DURATION': 15,                                 
                                                            
                             },                    
               'LESINA':   {
                              'FLOOR': 84.6,
                              'TUNNEL': 3.37,               
#                              'COD': '31/05/2026',
                              'COD': '31/05/2026',
                              'GEMS MARGIN 1': 14.03,   
                              'GEMS MARGIN 2': 6.44,                 
                              'PS GEMS': 1,   
                              'PS APPLE': 0.25,   
                              'PPA DURATION': 15,                                                             
                             },                 
               'SAN PAOLO':   {
#                              'FLOOR': 84.6, 
#                              'FLOOR': 79.02,    
# basecase                            'FLOOR': 82.10,      
                              'FLOOR': 82.6,                                                                              
                              'TUNNEL': 3.37,
#                              'COD': '31/05/2026',  
#  base case                            'COD': '31/12/2026',      
                              'COD': '30/09/2026',                                                          
#                              'GEMS MARGIN 1': 14.03,   
#                              'GEMS MARGIN 2': 6.44,        
                              'GEMS MARGIN 1': 17.61,   
                              'GEMS MARGIN 2': 10.02,   
         
                              'PS GEMS': 1,   
                              'PS APPLE': 0.25,   
                              'PPA DURATION': 15,                                                             
                             },                   
               'ZEPHYRUS':   {

                              'FLOOR': 87.04,
                              'TUNNEL': 1.96,               
                              'COD': '31/12/2026',            
                              'GEMS MARGIN 1': 9.15,   
                              'GEMS MARGIN 2': 6,                 
                              'PS GEMS': 1,   
                              'PS APPLE': 0.2, 
                              'PPA DURATION': 15,                                                                  
                             }                     
                                          
              }

