import glob
import pandas as pd
import numpy as np
import statistics


directorios_base=(r"C:\Users\Tablet\Desktop\iteraciones_aimsun\modelo dinamico_2",
                  r"C:\Users\Tablet\Desktop\iteraciones_aimsun\modelo ola_2")

for directorio in directorios_base:
    nombre=directorio.split(" ")[1]
    archivos=glob.glob(directorio+"/*informe.xlsx")
    df_total=pd.DataFrame()
    suma_distancias=[]
    for archivo in archivos:
        try:
            df=pd.read_excel(archivo,index_col=0)
            suma_distancias.append(df['distancia_recorrida'].sum())
            # suma_distancias.append(df['Consumo']['2 Coche- park'])
            df_total = pd.concat((df_total,df))
        except PermissionError:
            pass
    # print(df_total.columns)
    df_total.to_excel(nombre+".xlsx")
    df_total['busqueda_real']=df_total['Hora aparcamiento']-df_total['Hora Entrada']
    print(nombre+ ' media tiempo busqueda todos '+str(df_total['busqueda_real'].mean()/60))
    print(nombre+ ' media tiempo busqueda aparca calle '+str(df_total[df_total['Parking']==False]['busqueda_real'].mean()/60))
    print(nombre+' media distancia '+ str(df_total['Distancia entre nodos'].mean()))
    # print('suma '+str(sum(suma_distancias)/len(suma_distancias)))
    # print('std ' + str(statistics.pstdev(suma_distancias)))