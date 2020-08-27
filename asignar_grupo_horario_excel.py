# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal.
"""

import pandas as pd
from bisect import bisect_left
from anadir_a_excel import append_df_to_excel

def dame_grupo(fila, rangos=tuple(x for x in range(0,14701,300))):
    return bisect_left(rangos,fila['Hora Entrada'])-1


archivo=r"D:\Onedrive\OneDrive - UNICAN\Recordar GIST - VARIOS\Aparcamientos\resultados\4 horas varias demandas sin limite de tiempo 50 info tarifa dinamica\resultados 100 info.xlsx"
df=pd.read_excel(archivo, 
                 sheet_name='Sheet1')

df['grupo']=df.apply(func=dame_grupo, axis=1)

append_df_to_excel(archivo, df, sheet_name='Sheet1', startrow=0,
                       truncate_sheet=True)