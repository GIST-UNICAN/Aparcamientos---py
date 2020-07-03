import glob
import pandas as pd
import numpy as np
import statistics
from collections import defaultdict
from bisect import bisect_left


directorios_base=(r"C:\Users\Tablet\OneDrive - UNICAN\Recordar GIST - VARIOS\Aparcamientos\resultados\varios escenarios dinamicos (20 40 60 80 100) informados\20 informados",
                  r"C:\Users\Tablet\OneDrive - UNICAN\Recordar GIST - VARIOS\Aparcamientos\resultados\varios escenarios dinamicos (20 40 60 80 100) informados\40 informados",
                  r"C:\Users\Tablet\OneDrive - UNICAN\Recordar GIST - VARIOS\Aparcamientos\resultados\varios escenarios dinamicos (20 40 60 80 100) informados\60 informados",
                  r"C:\Users\Tablet\OneDrive - UNICAN\Recordar GIST - VARIOS\Aparcamientos\resultados\varios escenarios dinamicos (20 40 60 80 100) informados\80 informados",
                  r"C:\Users\Tablet\OneDrive - UNICAN\Recordar GIST - VARIOS\Aparcamientos\resultados\varios escenarios dinamicos (20 40 60 80 100) informados\100 informados")



for directorio in directorios_base:
    nombre=directorio.split("\\")[-1]
    archivos=glob.glob(directorio+"/*consumos.xlsx")
    df_total=pd.DataFrame()
    df_veh_dentro=pd.DataFrame()
    rangos_horarios=tuple(x for x in range(0,14701,300))
    for count, archivo in enumerate(archivos):
        diccionario_horarios=defaultdict(int)
        try:
            df=pd.read_excel(archivo,index_col=0)
            # suma_distancias.append(df['Consumo']['2 Coche- park'])
        
            
            
            df_total = pd.concat((df_total,df))
        except PermissionError:
            pass
    # print(df_total.columns)
    consumo_park=df_total.filter(like='2 Coche- park', axis=0).mean()
    print(nombre+' consumo park '+ str(consumo_park))
    df_total.to_excel(nombre+"_consumos.xlsx")
