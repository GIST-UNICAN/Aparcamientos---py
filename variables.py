#####################################################################
                     ## variables ##
#####################################################################



### GEOMETRIA APARCAMIENTOS
ruta_excel=r"E:\Program Files\Aimsun\Aimsun Next 8.3\programming\Aimsun Next API\AAPIPython\Micro\plazas_seccion.xlsx"
ruta_excel_distancias=r"E:\Program Files\Aimsun\Aimsun Next 8.3\programming\Aimsun Next API\AAPIPython\Micro\distancias.xls"
centroides_objetivo=(34894,34892,34783,34799,34798,34797,34796,34795,34784,34785,34786,34827,34786,34788,34787,34789,34790,34792,34791,34793,34794,34800,34801,34828,34829,34830,34875)
dict_secciones_centroide=dict()
dict_centroide_secciones={1276:1331,1294:1333}# se ponen directamente las de aparcamiento
secciones_parking_subterraneo=(1294,1276)
secciones_park=set()#(889,992,998,865,862,899,1129,1092,1089,1042,1059,1058,1056,901,892,1047,1043,934,975,946,1066,1043,1085,1086,1146,1079,1078,968,893,895)
random_plazas_hasta=9
random_plazas_hasta_libres=5
longitud_secciones={}



### VARIABLES INTERNAS
secciones_destino_vehiculo=dict() #Establece donde va cada coche
posibles_secciones_destino_vehiculo=dict()
lista_info_1=[]
lista_info_2=[]
lista_id_objetivo=[]
dict_vehiculos_aparcados=dict() #{idveh:(seccion,  tiempo de salida)}
dict_vehiculos_aparcados_previos=dict() #{idveh:(seccion,  tiempo de salida)}
vehiculos_parados={}# {idveh: comienzo_parada}
lista_buscando_sitio=list()
ejecutar_1_vez=True
lista_secciones_con_comercios=list()
lista_probabilidades=list()


### Exportacion
ruta_excel_exportar=""
columnas_exportar=['Hora Entrada', 'T busqueda inicial',
                   'T busqueda real', 'Nodo destino',
                   'Nodo aparcamiento', 'Distancia entre nodos',
                   'Intentos aparcamiento', 'Tarifa',
                   'Hora aparcamiento', 'Duracion aparcamiento',
                   'Parking', 'Secciones intento aparcamiento','Seccion de paso', 'Utilidad relativa']
indice_exportar = pd.Index([], dtype=dtype(int), name="ID")
df_exportar=pd.DataFrame(columns=columnas_exportar, index=indice_exportar)
##df_exportar.set_index('ID', inplace=True)


### VARIABLES MODELO
tiempo_parada_aparcamiento=30 # en segundos
tiempo_coche_aparcado_min=5*60 # tiempo mímino que un coche puede estar en una plaza
tiempo_coche_aparcado_max=120*60 # tiempo máximo que un coche puede estar en una plaza
duracion_aparcamiento_min=10*60 
tiempo_aparcamiento_avg=tiempo_coche_aparcado_min*0.5+tiempo_coche_aparcado_max*0.5
media_duracion_park=30*60
std_duracion_park=30*60
ocupacion_inicial=85
tiempo_busqueda_min=1*60
tiempos_busqueda_desviacion=120
tiempos_busqueda_medio=240
tiempo_acceso_destino=120
tarifa_superficie_max=2
tarifa_subterraneo=2.5
utilidad_relativa_alternativas=90


plazas_park_total=dict()
plazas_park_free=dict()
plazas_park_full=dict()




    