# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 10:52:08 2020

@author: Tablet
"""
import pandas as pd
import glob
import matplotlib.pyplot as plt
markers=[".-","v--","s-.","x:","D-"]

directorio=r"C:\Users\Tablet\OneDrive - UNICAN\Recordar GIST - VARIOS\Aparcamientos\resultados\varios escenarios dinamicos (20 40 60 80 100) informados"

#evolución cuenta vehículos que buscan aparcamiento
archivos =glob.glob(directorio+"/*cuenta.xlsx")
df_global=pd.DataFrame()
for archivo in archivos:
    df=pd.read_excel(archivo,index_col=0).drop(['simulacion'], axis=1)
    gr=df.groupby(['hora']).mean()
    gr=gr.rename(columns={'cuenta':int(archivo.split(" ")[-2].split("\\")[-1])})
    df_global=pd.concat((df_global,gr),axis=1)

df_global = df_global.reindex(sorted(df_global.columns), axis=1).drop(13)
df_global.index=df_global.index*5
plt.figure(); df_global.plot(style=markers ); plt.legend(title='% informed'); plt.xlabel("time passed (min)");
plt.ylabel("n car searching")
#%%
#evolución contamienates
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
select sid,ent,avg(CO2) as CO2,avg(PM) as PM,avg(VOC) as VOC, avg(NOX) as NOX
 from MISYSIEM where ent!=0 and sid=0
  and did=({sql_media}) group by sid,ent
"""
df_base=pd.DataFrame()
for archivo in archivos:
    ruta=base+archivo
    with sqlite3.connect(ruta) as conn:
        df2=pd.read_sql_query(sql_emisiones,conn).melt(id_vars=['sid','ent'])
        import re
        col=int(re.findall(re.compile('[0-9]+'),archivo)[0])
        df2=df2.rename(columns={'sid': 'tipo_coche', 'value':col})
        df_base=pd.concat([df2,df_base],axis=1)
df_base= df_base.loc[:,~df_base.columns.duplicated()]
df_base.set_index(['ent'], inplace=True)
df_base.index=df_base.index*5
df_base.drop(['tipo_coche'], axis=1, inplace=True)
dfs=[]
fig, axes = plt.subplots(nrows=2, ncols=2,figsize=(10,7))

for z,x,y in zip(('CO2','PM','VOC','NOX'),(0,0,1,1),(0,1,0,1)): 
    print(x,y)
    df_co2= df_base[df_base['variable']==z]
    df_co2.drop(['variable'], axis=1, inplace=True)
    df_co2 = df_co2.reindex(sorted(df_co2.columns), axis=1).drop(65)
    dfs.append(df_co2)   
    df_co2.plot(style=markers, ax=axes[x, y], legend= False)
    axes[x, y].set_xlabel("time passed (min)")
    axes[x, y].set_ylabel("emissions (g)")
    axes[x,y].set_title(z)
fig.tight_layout() 
lines, labels = fig.axes[-1].get_legend_handles_labels()
    
fig.legend(lines, labels, loc = 'lower center', bbox_to_anchor=(0.5, -0.08),title='% informed'
           ,bbox_transform=fig.transFigure,
          ncol=5, fancybox=True, shadow=True)  
#%%
# tabla comparativa usuarios parking, escenarios conjuntos

archivos =glob.glob(directorio+"/*informados.xlsx")
df_global_total=pd.DataFrame()
for archivo in archivos:
    df=pd.read_excel(archivo,index_col=0).drop(['Utilidades iteraciones','Utilidad relativa', 'track','track_secciones','ID','ID.1','Tarifa'], axis=1)
    df['%info']=int(archivo.split(" ")[-2].split("\\")[-1])
    df['T_bus_real'] = df['Hora aparcamiento'] - df['Hora Entrada']
    df= df[(df['grupo']!=0) & (df['grupo']!=-1)]
    # gr=df.groupby(['hora']).mean()
    # gr=gr.rename(columns={'cuenta':int(archivo.split(" ")[-2].split("\\")[-1])})
    df_global_total=pd.concat((df_global_total,df),axis=0)
df_global_total['Parking'] = df_global_total['Parking'].map({True: 1, False: 0})
df_global_total['Seccion de paso'] = df_global_total['Seccion de paso'].map({'si': 1})
#%%
# Evolución tiempo de búsqueda
gr=df_global_total.groupby(['%info','grupo']).mean()['T_bus_real'].to_frame().reset_index()
gr=gr.pivot(index='grupo',columns='%info')
gr=gr/60
gr.index=gr.index*5
gr.drop(65, inplace=True)
a=plt.figure(); gr.plot(style=markers ); 
plt.legend((20,40,60,80,100),title='% informed',loc = 'upper center', bbox_to_anchor=(0.5, 1.1)
           ,bbox_transform=a.transFigure,
          ncol=5, fancybox=True, shadow=True); 
plt.xlabel("time passed (min)")
plt.ylabel("curb time (min)")

#%%
# diversos factores para informados y no informados
gr1=df_global_total.groupby(['%info','Tipo usuario']).agg({'distancia_recorrida': 'mean',
                                                           'Distancia entre nodos':'mean',
                                                           'Intentos aparcamiento': 'mean',
                                                           'T_bus_real':'mean',
                                                           'Parking':'sum',
                                                           'Seccion de paso':'sum',
                                                          'grupo':'count'}).reset_index().rename(columns={'grupo':'Cuenta'})
from functools import partial
a=partial(round,ndigits=2)
gr1['Parking']=100*gr1['Parking']/gr1['Cuenta']
gr1['Parking']=gr1['Parking'].apply(a)
gr1['Seccion de paso']=100*gr1['Seccion de paso']/gr1['Cuenta']
gr1['Seccion de paso']=gr1['Seccion de paso'].apply(a)
gr1=gr1.T
# gr1=gr1.pivot(index='')



#%%
# Tratar de demostrar linealidad
base=r"C:\Users\Tablet\OneDrive - UNICAN\Recordar GIST - VARIOS\Aparcamientos\archivos aimsun"
archivos=("\dinamico_20_info.sqlite",
          "\dinamico_40_info.sqlite",
          "\dinamico_60_info.sqlite",
          "\dinamico_80_info.sqlite",
          "\dinamico_100_info.sqlite") 
sql_media="""select did from SIM_INFO where type=2"""
sql_datos=f"""select ent,sid,qmean as Cola_Media from MISYS where sid=0 and  ent !=0 and did!=({sql_media}) order by qmean desc"""

df_base_regresion=pd.DataFrame()
for archivo in archivos:
    ruta=base+archivo
    with sqlite3.connect(ruta) as conn:
        df2=pd.read_sql_query(sql_datos,conn).melt(id_vars=['sid','ent'])
        df2=df2.rename(columns={'sid': 'tipo_coche', 'value':archivo})
        df_base_regresion=pd.concat([df2,df_base_regresion],axis=1)
df_base_regresion= df_base_regresion.loc[:,~df_base_regresion.columns.duplicated()]

#%%
#Datos a excel
writer = pd.ExcelWriter(r'análisis datos conjunto.xlsx')

# Write each dataframe to a different worksheet.
df_global.to_excel(writer, sheet_name='EVOLUCION BUSCAN')
df_base.to_excel(writer, sheet_name='EVOLUCION CONTAMINANTES')
gr.to_excel(writer, sheet_name='EVOLUCION TIEMPO BUSQUEDA')
gr1.to_excel(writer, sheet_name='FACTORES TIPOS USUARIOS')
df_base_regresion.to_excel(writer, sheet_name='CORRELACION VALORES')
writer.save()
