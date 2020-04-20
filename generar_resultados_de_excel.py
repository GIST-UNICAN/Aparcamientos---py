import glob
import pandas as pd
import numpy as np
import statistics
from collections import defaultdict
from bisect import bisect_left


directorios_base=(r"C:\Users\Tablet\OneDrive - UNICAN\Recordar GIST - VARIOS\Aparcamientos\resultados\simulacion_4_horas_varias_demandas\ola",
                  r"C:\Users\Tablet\OneDrive - UNICAN\Recordar GIST - VARIOS\Aparcamientos\resultados\simulacion_4_horas_varias_demandas\dinamico")





for directorio in directorios_base:
    nombre=directorio.split("\\")[-1]
    archivos=glob.glob(directorio+"/*informe.xlsx")
    df_total=pd.DataFrame()
    suma_distancias=[]
    df_veh_dentro=pd.DataFrame()
    rangos_horarios=tuple(x for x in range(0,14701,60))
    for count, archivo in enumerate(archivos):
        print('iter: ', str(count))
        diccionario_horarios=defaultdict(int)
        try:
            df=pd.read_excel(archivo,index_col=0)
            suma_distancias.append(df['distancia_recorrida'].sum())
            # suma_distancias.append(df['Consumo']['2 Coche- park'])
            def asigna_horarios(fila):
                gap_entra=bisect_left(rangos_horarios, float(fila['Hora Entrada']))-5
                gap_sale=bisect_left(rangos_horarios, float(fila['Hora aparcamiento']))-5
                tupla_rangos=tuple(range(gap_entra,gap_sale+1))
                for gap in tupla_rangos:
                    diccionario_horarios[gap]=diccionario_horarios[gap]+1
                return 
            
            df.apply(func=asigna_horarios, axis=1)
            lista_a_pd=[]
            for key, value in diccionario_horarios.items():
                lista_a_pd.append([count,key, value])
            df_veh_dentro =pd.concat((df_veh_dentro, pd.DataFrame(lista_a_pd, columns=['simulacion','hora','cuenta'])))
            df_total = pd.concat((df_total,df))
        except PermissionError:
            pass
    # print(df_total.columns)
    filtro=((df_veh_dentro['hora'] !=0) & (df_veh_dentro['hora'] !=-1)
            & (df_veh_dentro['hora'] !=-2)& (df_veh_dentro['hora'] !=-3)
            & (df_veh_dentro['hora'] !=-4)& (df_veh_dentro['hora'] !=-5))
    df_veh_dentro[filtro].to_excel(nombre+"_cuenta.xlsx")
    df_total.to_excel(nombre+".xlsx")
    df_total['busqueda_real']=df_total['Hora aparcamiento']-df_total['Hora Entrada']
    print(nombre+ ' media tiempo busqueda todos '+str(df_total['busqueda_real'].mean()/60))
    print(nombre+ ' media tiempo busqueda aparca calle '+str(df_total[df_total['Parking']==False]['busqueda_real'].mean()/60))
    print(nombre+' media distancia '+ str(df_total['Distancia entre nodos'].mean()))
    print('suma '+str(sum(suma_distancias)/len(suma_distancias)))
    print('std ' + str(statistics.pstdev(suma_distancias)))