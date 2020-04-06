import glob
import pandas as pd
import numpy as np
import statistics
from collections import defaultdict
from bisect import bisect_left


directorios_base=(r"C:\Users\Tablet\Desktop\RESULTADOS AIMSUN\iteraciones_aimsun_tarifa actual y dinamica realista (0.5 1 1.75)\dinamico",
                  r"C:\Users\Tablet\Desktop\RESULTADOS AIMSUN\iteraciones_aimsun_tarifa actual y dinamica realista (0.5 1 1.75)\ola")




for directorio in directorios_base:
    nombre=directorio.split("\\")[-1]
    archivos=glob.glob(directorio+"/*ocupaciones.xlsx")
    df_total=pd.DataFrame()
    df_veh_dentro=pd.DataFrame()
    rangos_horarios=tuple(x for x in range(0,4201,60))
    for count, archivo in enumerate(archivos):
        diccionario_horarios=defaultdict(int)
        try:
            df=pd.read_excel(archivo,index_col=0)
            # suma_distancias.append(df['Consumo']['2 Coche- park'])
        
            
            
            df_total = pd.concat((df_total,df))
        except PermissionError:
            pass
    # print(df_total.columns)
    df_total.to_excel(nombre+"_ocupaciones.xlsx")
