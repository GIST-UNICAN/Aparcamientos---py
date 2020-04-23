# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 15:22:32 2020

@author: Tablet
"""


import pandas as pd
import sqlite3

base=r"C:\Users\Tablet\OneDrive - UNICAN\Recordar GIST - VARIOS\Aparcamientos\archivos aimsun"
archivos=("\dinamico_20_info.sqlite",
          "\dinamico_40_info.sqlite",
          "\dinamico_60_info.sqlite",
          "\dinamico_80_info.sqlite",
          "\dinamico_100_info.sqlite") 
sql_media="""select did from SIM_INFO where type=2"""
sql_datos=f"""select sid,qmean as Cola_Media,
fuelc as Consumo,density as Densidad,travel as Distancia_Recorrida,
dtime as Tiempo_Demora,traveltime as Tiempo_viaje from MISYS where ent =0 and did=({sql_media}) order by qmean desc"""

sql_emisiones=f"""
select sid,avg(CO2) as CO2,avg(PM) as PM
 from MISYSIEM where ent!=0 
  and did=({sql_media}) group by sid
"""
df_base=pd.DataFrame()
for archivo in archivos:
    ruta=base+archivo
    with sqlite3.connect(ruta) as conn:
        df=pd.read_sql_query(sql_datos,conn).melt(id_vars=['sid'])
        df2=pd.read_sql_query(sql_emisiones,conn).melt(id_vars=['sid'])
        df2=df2.rename(columns={'sid': 'tipo_coche', 'value':archivo})
        df=df.rename(columns={'sid': 'tipo_coche', 'value':archivo})
        df1=pd.concat([df,df2], axis=0)
        df_base=pd.concat([df1,df_base],axis=1)
df_base= df_base.loc[:,~df_base.columns.duplicated()]
df_base.to_excel('resumen_parámetros.xlsx')

