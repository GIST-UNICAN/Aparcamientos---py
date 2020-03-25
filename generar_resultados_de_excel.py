import glob
import pandas as pd

directorio_base=r"C:\Users\Tablet\Desktop\iteraciones_aimsun"
archivos=glob.glob(directorio_base+"/*informe.xlsx")
df_total=pd.DataFrame()

for archivo in archivos:
    try:
        df=pd.read_excel(archivo)
        df_total = pd.concat((df_total,df))
    except PermissionError:
        pass
# print(df_total.columns)
print(df_total['distancia_recorrida'].mean())