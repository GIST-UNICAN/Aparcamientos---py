# -*- coding: cp1252 -*-
from __future__ import print_function
from __future__ import division
import sys
sys.path.insert(1, 'C:\Program Files\Aimsun\Aimsun Next 8.3\programming\Aimsun Next API\AAPIPython\Micro')
from AAPI import *
SITEPACKAGES = "C:\\Python27\\lib\\site-packages"
if SITEPACKAGES not in sys.path:
	sys.path.append(SITEPACKAGES)
import random
import ctypes
import math
import logging
import traceback
import pandas as pd
import numpy as np
from itertools import count
from functools import partial
from time import clock
from numpy import dtype
from datetime import datetime
import pip
from multiprocessing.connection import Listener
from multiprocessing.connection import Client
from multiprocessing import Queue
import threading
from socket import socket, AF_INET, SOCK_STREAM, error as socket_error
from contextlib import closing
from marshal import dumps
import Queue
from bisect import bisect_left
logging.basicConfig(level=logging.DEBUG)
import os
from subprocess import Popen
from collections import defaultdict

##    logging.error('no hay socket')


#pip.main(['install','pandas'])

logging.error('No pasa')

#####################################################################
## todo ##
#####################################################################

# incluir funci�n eleccion
# optimizar variable coches aparcados
# retenci�on salida vehiculos
# terminar funcion timepo de busqueda
# parametrizar v peaton

#####################################################################
## variables ##
#####################################################################


# GEOMETRIA APARCAMIENTOS
ruta_excel = r"E:\Program Files\Aimsun\Aimsun Next 8.3\programming\Aimsun Next API\AAPIPython\Micro\plazas_seccion.xlsx"
ruta_excel_distancias = r"E:\Program Files\Aimsun\Aimsun Next 8.3\programming\Aimsun Next API\AAPIPython\Micro\distancias.xls"
centroides_objetivo = (
    34894,
    34892,
    34783,
    34799,
    34798,
    34797,
    34796,
    34795,
    34784,
    34785,
    34786,
    34827,
    34786,
    34788,
    34787,
    34790,
    34792,
    34791,
    34793,
    34794,
    34800,
    34801,
    34828,
    34829,
    34830,
    34875)
dict_secciones_centroide = dict()
# se ponen directamente las de aparcamiento
dict_centroide_secciones = {1276: 1331, 1294: 1333}
secciones_parking_subterraneo = (1294, 1276)
secciones_park = set()  # (889,992,998,865,862,899,1129,1092,1089,1042,1059,1058,1056,901,892,1047,1043,934,975,946,1066,1043,1085,1086,1146,1079,1078,968,893,895)
random_plazas_hasta = 9
random_plazas_hasta_libres = 5
longitud_secciones = {}

# multiproceso
conn = None
candado = threading.Lock()


# VARIABLES INTERNAS
secciones_destino_vehiculo = dict()  # Establece donde va cada coche
posibles_secciones_destino_vehiculo = dict()
lista_info_1 = []
lista_info_2 = []
lista_id_objetivo = []
dict_vehiculos_aparcados = dict()  # {idveh:(seccion,  tiempo de salida)}
# {idveh:(seccion,  tiempo de salida)}
dict_vehiculos_aparcados_previos = dict()
vehiculos_parados = {}  # {idveh: comienzo_parada}
lista_buscando_sitio = list()
ejecutar_1_vez = True
lista_secciones_con_comercios = list()
lista_probabilidades = list()
tiempo_global=0
tipos_usuarios=('informado','no_informado')
tipo_vehiculo=0


# Exportacion
ruta_excel_exportar = ""
columnas_exportar = ['ID',
                     'Tipo usuario',
                     'distancia_recorrida',
    'Hora Entrada',
    'T busqueda inicial',
    'T busqueda real',
    'Nodo destino',
    'Nodo aparcamiento',
    'Distancia entre nodos',
    'Intentos aparcamiento',
    'Tarifa',
    'Hora aparcamiento',
    'Duracion aparcamiento',
    'Parking',
    'Secciones intento aparcamiento',
    'Seccion de paso',
    'Utilidad relativa',
    'Utilidades iteraciones','track',
    'track_secciones']
indice_exportar = pd.Index([], dtype=dtype(int), name="ID")
df_exportar = pd.DataFrame(columns=columnas_exportar, index=indice_exportar)
##df_exportar.set_index('ID', inplace=True)
columnas_exportar_tarifas=['seccion', 'tarifa','tiempo']
df_exportar_secciones = pd.DataFrame(columns=columnas_exportar_tarifas)
columnas_exportar_ocupaciones=['seccion', 'tiempo', 'ocupacion']
df_exportar_ocupaciones = pd.DataFrame(columns=columnas_exportar_ocupaciones)
columnas_exportar_buscando=['seccion', 'tiempo', 'ocupacion']
df_exportar_ocupaciones = pd.DataFrame(columns=columnas_exportar_ocupaciones)

# VARIABLES MODELO
tiempo_parada_aparcamiento = 22  # en segundos
# tiempo mímino que un coche puede estar en una plaza
tiempo_coche_aparcado_min = 5 * 60
# tiempo máximo que un coche puede estar en una plaza
tiempo_coche_aparcado_max = 120 * 60 #segundos
duracion_aparcamiento_min = 10 * 60
tiempo_aparcamiento_avg = tiempo_coche_aparcado_min * \
    0.5 + tiempo_coche_aparcado_max * 0.5
media_duracion_park = 60 * 60
std_duracion_park = 60 * 60
ocupacion_inicial = 95
tiempo_busqueda_min = 1 * 60
tiempos_busqueda_desviacion = 120
tiempos_busqueda_medio = 240
tiempo_acceso_destino = 120
rangos_tarifa_superficie = (0.5,1,1.75) #(1,2,3.5)
tarifa_generica_calle = 1.45/2
rangos_ocupa_superficie = (60,80,100)
tiempo_actualizacion_tarifas=15
tarifa_subterraneo = 1.60#2.75
utilidad_relativa_alternativas = 90
transito = 0
tiempo_busqueda_min = 2
media_tiempo_busqueda = 6.58
std_tiempo_busqueda = 4.87
tiempo_busqueda_subterraneo= 1.54
porcentaje_informados=0
porcentaje_no_informados=100-porcentaje_informados
tiempo_salvado_ocupaciones=60


plazas_park_total = dict()
plazas_park_free = dict()
plazas_park_full = dict()
precios_parking_street = defaultdict(int)

info=0
no_info=0


#####################################################################
## multiproceso ##
#####################################################################

# hay que hacer una funcion que este esperando
# a ser llamada para que mande el ok del diccionario creado
def recibe_datos():
    """[summary]
    """
    AKIPrintString("hilo 1 lanzado")
    max_queued_connections = 5
    tamagno_del_bufer = 524288
    host = ''                 # Symbolic name meaning all available interfaces
    puerto_inicial = 50000
    cuenta_ports = count(50000)
    ejecutable_python = 'C:\\Users\\Tablet\\AppData\\Local\\Programs\\Python\\Python38\\python.exe'
    script_python = "C:\\Users\\Tablet\\Documents\\GitHub\\Aparcamientos-visualizacion---py\\rec37.py"
    s = socket(AF_INET, SOCK_STREAM)
    while True:
        port = next(cuenta_ports)
        try:
            s.bind((host, port))
        except socket_error:
            continue
        else:
            logging.error("Puerto: {}".format(port))
            break
    try:
        s.listen(max_queued_connections)
        logging.error("Llego aquiii")
        Popen((ejecutable_python, script_python, str(port)))
        while True:
            conn, addr = s.accept()
            print('Connected by', addr)
            with candado:
                enviar = dumps(cola_diccionarios, 1)
            with closing(conn):
                orden = conn.recv(tamagno_del_bufer)
                if orden == b"g":
                    ##                    print("Oido cocina,", addr)
                    conn.sendall(enviar)
                else:
                    conn.sendall("Comando no reconocido.")
                conn.recv(tamagno_del_bufer)
                conn.sendall(b"Fin")
                print("Cerrando socket.")
    except:
        logging.error(traceback.format_exc())
##        s.shutdown()
        s.close()
        raise
    else:
##        s.shutdown()
        s.close()




##    while True:
##        p = Popen((ejecutable_python, script_python, next(port)))
    #lanzamos el otro script
##    os.system(r'py -3.7 "E:\OneDrive - Universidad de Cantabria\Recordar GIST - VARIOS\Aparcamientos\SCRIPTS PARK\rec37.py" {}'.format(port))
##    while True:
##        with closing(socket(AF_INET, SOCK_STREAM)) as s:
##            s.bind((host, port))
##            s.listen(max_queued_connections)
##            conn, addr = s.accept()  # conn es un nuevo socket.
##            print('Connected by', addr)
##            # pedimos a la cola el ultimo diccionario y lo serializamos para
##            # enviar
##            with candado:
##                enviar = dumps(cola_diccionarios, 1)
##            with closing(conn):
##                orden = conn.recv(tamagno_del_bufer)
##                if orden == b"g":
##                    ##                    print("Oido cocina,", addr)
##                    conn.sendall(enviar)
##                else:
##                    conn.sendall("Comando no reconocido.")
##                conn.recv(tamagno_del_bufer)
##                conn.sendall(b"Fin")
##                print("Cerrando socket.")
##            print("Cerrando servidor.")

#####################################################################
            ## funciones propias ##
#####################################################################


class Timer:
    def __init__(self, nombre):
        self.nombre = nombre

    def __enter__(self):
        self.start = clock()
        return self

    def __exit__(self, *args):
        self.end = clock()
        self.interval = self.end - self.start
        with open(r"E:\Program Files\Aimsun\Aimsun Next 8.3\programming\Aimsun Next API\AAPIPython\Micro\log_time.txt", 'a') as log:
            print(self.nombre, " tardo ", self.interval, "segundos.", file=log)


def imprime_texto(*txt):
    with open(r"E:\Program Files\Aimsun\Aimsun Next 8.3\programming\Aimsun Next API\AAPIPython\Micro\log.txt", 'a') as log:
        print(*txt, file=log)


def seleccionar_vehiculo_rnd():
    numero = int(random.uniform(1, 1))
    return True if numero == 1 else False


def selecciona_tipo_usuario():
    global info, no_info
    usuario=np.random.choice(tipos_usuarios, p=((porcentaje_informados/100),1-(porcentaje_informados/100)))
    if usuario =="informado":
        info=info+1
    else:
        no_info=no_info+1
    # AKIPrintString("PASA POR ELECCIÓN " + str(usuario)+" info "+str(info)+" no info "+ str(no_info))
    return usuario


def aparca_coche():
    global plazas_park_free, plazas_park_total, plazas_park_full, lista_buscando_sitio, dict_secciones_centroide
    pass


def desaparca_coche(time):
    """[summary]
    
    Arguments:
        time {[type]} --  Tiempo desde que ha encontrado plaza de aparcamiento
    """
    global plazas_park_free, plazas_park_total, plazas_park_full, dict_vehiculos_aparcados
    for coche, tupla in dict_vehiculos_aparcados.items():
        ##        imprime_texto("aparcados ", str(dict_vehiculos_aparcados))
        # logging.error(dict_vehiculos_aparcados)
        if tupla and tupla[1] < time:
            del dict_vehiculos_aparcados[coche]
            actualiza_grafico(tupla[0], coche, signo=-1)
    for coche, tupla in dict_vehiculos_aparcados_previos.items():
        ##        imprime_texto("aparcados ", str(dict_vehiculos_aparcados))
        # logging.error(dict_vehiculos_aparcados)
        if tupla and tupla[1] < time:
            del dict_vehiculos_aparcados_previos[coche]
            actualiza_grafico(tupla[0], coche, signo=-1)


def actualiza_grafico(
        seccion_vehiculo,
        vehiculo,
        signo=1,
        actualizar_todo=True):
    """[summary]
    Función para mandar los datos al otro 
    Arguments:
        seccion_vehiculo {[type]} -- [description]
        vehiculo {[type]} -- [description]
    
    Keyword Arguments:
        signo {int} -- [description] (default: {1})
        actualizar_todo {bool} -- [description] (default: {True})
    """
    global plazas_park_free, plazas_park_total, plazas_park_full
##    imprime_texto("actualiza_grafico todo? ", str(actualizar_todo))
    if actualizar_todo:
        # actualizamos el diccionario de plazas disponibles en esa calle
        if seccion_vehiculo not in secciones_parking_subterraneo:
            plazas_park_free[seccion_vehiculo] = plazas_park_free[seccion_vehiculo] - 1 * signo
            plazas_park_full[seccion_vehiculo] = plazas_park_full[seccion_vehiculo] + 1 * signo
            plazas_totales_seccion = plazas_park_free[seccion_vehiculo] + \
                plazas_park_full[seccion_vehiculo]
            atr = ANGConnGetAttribute(
                AKIConvertFromAsciiString("GKSection::ALIAS"))
            ANGConnSetAttributeValueStringA(
                atr, seccion_vehiculo, "{} libres de {}".format(
                    plazas_park_free[seccion_vehiculo], plazas_totales_seccion))
    libres = str(max(0, sum(plazas_park_free.values())))
    aparcados = str(sum(plazas_park_full.values()))
    buscando = str(len(lista_buscando_sitio))
    camino = str(len(lista_id_objetivo))
    # map(conn.send, ((0, aparcados), (1, camino),
    #                 (2, transito), (3, buscando), (4, libres)))
# ANGConnSetText ( 34835,AKIConvertFromAsciiString("Plazas: \n--------\nlibres {} \naparcados {} \nbuscando {}".format(
# libres,
# aparcados,
# buscando)))


def reasigna_plaza(vehiculo, time):
    global plazas_park_free, plazas_park_total, plazas_park_full, lista_buscando_sitio, dict_secciones_centroide
    info_estatica_vehiculo = AKIVehTrackedGetStaticInf(vehiculo)
    if vehiculo in lista_buscando_sitio:
        pass
    else:
        lista_buscando_sitio.append(vehiculo)
    # buscamos una nueva seccion para el vehiculo
    seccion_destino = df_exportar.loc[vehiculo, 'Nodo destino']
    tiempo_busqueda_transcurrido = (
        time - df_exportar.loc[vehiculo, 'Hora Entrada']) / 60
    seccion_nueva, es_parking, distancia = genera_seccion_aparcamiento(
        seccion_destino, vehiculo, tiempo_busqueda_transcurrido=tiempo_busqueda_transcurrido)
    if es_parking:
        df_exportar.loc[vehiculo, 'Hora aparcamiento'] = time
    df_exportar.loc[vehiculo, 'Secciones intento aparcamiento'].append(
        int(seccion_nueva))
    centroide_aparcamiento = dict_centroide_secciones[int(seccion_nueva)]
    df_exportar.loc[vehiculo, 'Nodo aparcamiento'] = int(seccion_nueva)
    df_exportar.loc[vehiculo, 'Distancia entre nodos'] = distancia
    df_exportar.loc[vehiculo, 'Parking'] = es_parking
    # es necesario ponerle la nueva seccion de destino
    secciones_destino_vehiculo[vehiculo] = seccion_nueva
    info_estatica_vehiculo.__setattr__("centroidDest", centroide_aparcamiento)
    info_estatica_vehiculo.__setattr__(
        "width", 2.02)  # para pintarle de otro color
    AKIVehTrackedSetStaticInf(vehiculo, info_estatica_vehiculo)
##    AKIPrintString("buscando: "+str(lista_buscando_sitio))
##    AKIPrintString("Reasignado el vehiculo: {} al centroide {}".format(str(vehiculo),str(centroide_aparcamiento)))


def genera_tiempo_aparcamiento():
    return max(
        tiempo_coche_aparcado_min,
        min(random.gauss(
            media_duracion_park,
            std_duracion_park),tiempo_coche_aparcado_max))


def genera_tiempo_aparcamiento_inical():
    return random.randint(0, tiempo_coche_aparcado_max)


def _genera_tiempo_busqueda():
    return max(
        tiempo_busqueda_min,
        random.gauss(
            media_tiempo_busqueda,
            std_tiempo_busqueda))


def genera_tiempo_acceso(seccion_inicio, seccion_fin):
    return float(df_distancias[(df_distancias['ORIGEN'] == seccion_inicio)
                               & (df_distancias['DESTINO'] == seccion_fin)]
                 ['DISTANCIA']) / 1.38  # velocidad peaton


def asigna_tiempos_iniciales(plazas_park_full, contador=count(-1, -1)):
    global dict_vehiculos_aparcados_previos
    for seccion, numero_plazas_llenas in plazas_park_full.items():
        for plaza in range(numero_plazas_llenas):
            dict_vehiculos_aparcados_previos[next(contador)] = (
                seccion, genera_tiempo_aparcamiento_inical())


def genera_seccion_destino():
    return np.random.choice(
        lista_secciones_con_comercios,
        p=lista_probabilidades)


def _calcula_tarifa(seccion=None, ocupacion=None, idveh=None):
    global tiempo_global, tiempo_actualizacion_tarifas, precios_parking_street
    if ocupacion is not None:
        if df_exportar['Tipo usuario'][idveh] == 'informado':
            return precios_parking_street[seccion]
        else:
            return tarifa_generica_calle
    else:
        return tarifa_subterraneo


def _calcula_ocupacion(fila):
    if fila.secciones in plazas_park_total:
        if plazas_park_total[fila.secciones]:
            return plazas_park_full[fila.secciones] / \
                plazas_park_total[fila.secciones]
        else:
            return np.nan
    else:
        return np.nan


def _calcula_utilidad_calles(
        fila,
        tiempo_busqueda,
        tiempo_destino=0,
        nodo_logit=1, #como es un logit jerarquico si el nodo es 0 necesitamos las utilidades de los bloques para e
        u_para_sumatorio=[],
        seccion_interes=0,
        tar_bl=-0.9506,
        td_bl=-0.0776,
        tb_bl=-0.0726,
        ocu_bl=0.00707,
        tmax_bl=0.5288,
        cte_sub=2.5982,
        tar_sub=-0.9506,
        td_sub=-0.0776,
        tb_sub=-0.0726,
        cte_street=0.6813,
        cte_bl=1.4577,
        idveh=0):
    if nodo_logit ==0:
        if seccion_interes in secciones_parking_subterraneo:
            return  cte_sub + td_sub * tiempo_destino + tar_sub * _calcula_tarifa() + tb_sub * tiempo_busqueda_subterraneo
        else:
            try:
                return  cte_street * math.log (sum(math.exp(cte_bl*x) for x in u_para_sumatorio))
            except ValueError: # ya es venirse arriba con la tarifa
                return -1000
    elif nodo_logit ==1:
        if fila.secciones in secciones_parking_subterraneo:
            return np.nan
        elif fila.secciones in secciones_park:
            if df_exportar['Tipo usuario'][idveh] == 'informado':
                # AKIPrintString('info: '+str(idveh)+str(df_exportar['Tipo usuario'][idveh]))
                if plazas_park_free[fila.secciones]:
                    tiempo_busqueda = tiempo_busqueda - df_exportar.loc[idveh, 'T busqueda inicial']
                tarifa =  _calcula_tarifa(fila.secciones,fila.ocupacion,idveh)
            else:
                # AKIPrintString('no info: '+str(idveh)+str(df_exportar['Tipo usuario'][idveh]))
                tarifa = tarifa_generica_calle
            #AKIPrintString('U: '+str(tiempo_busqueda)+'  '+str(fila.tiempos)+'  '+str( _calcula_tarifa(fila.ocupacion))+'  '+str(tiempo_coche_aparcado_max / 3600))
            return tb_bl * tiempo_busqueda + td_bl * fila.tiempos + tar_bl * tarifa + tmax_bl * tiempo_coche_aparcado_max / 3600  #horas
        else:
            return np.nan
    else:
        return np.nan


def genera_seccion_aparcamiento(seccion_destino, idveh,
                                genera_tiempo_busqueda=_genera_tiempo_busqueda,
                                calcula_ocupacion=_calcula_ocupacion,
                                Timer=Timer,
                                calcula_utilidad=_calcula_utilidad_calles,
                                imprime_texto=imprime_texto,
                                tiempo_busqueda_transcurrido=0,
                                seccion_origen=None):
    with Timer("genera_park ") as t:
        try:
            tipo_usuario=df_exportar['Tipo usuario'][idveh]
            if pd.isna(df_exportar.loc[idveh, 'T busqueda inicial']):
                tiempo_busqueda = genera_tiempo_busqueda()
                df_exportar.loc[idveh,
                                'T busqueda inicial'] = float(tiempo_busqueda)
                #df_exportar.loc[idveh,
                #                'T busqueda real'] = float(tiempo_busqueda)
            else:
                tiempo_busqueda = df_exportar.loc[idveh,
                                                  'T busqueda inicial'] + tiempo_busqueda_transcurrido
                #df_exportar.loc[idveh,
                #                'T busqueda real'] = float(tiempo_busqueda)
            calcula_utilidad_con_t_fijo_calle = partial(
                calcula_utilidad, tiempo_busqueda=tiempo_busqueda, nodo_logit=1, idveh=idveh)
            # hay que calcular las utilidades para todas las secciones y coger la mejor
            # para ello hay que calcular las utilidades de las secciones que tienen plazas de aparcamiento
            # por otro lado hay que calcular la que tiene parking
            # hay que añadir usuarios con info perfecta y usuarios con info historica
            # creamos un df para hacer los calculos
            
            def genera_dataframe_calculos(seccion_destino,filtro=None, comparativa=None):
                df_calculos = pd.DataFrame()
        ##        filtro_seccion_destino = (df_distancias['ORIGEN']==seccion_destino) & (~ (df_distancias['DESTINO'].isin(df_exportar.loc[idveh, 'Secciones intento aparcamiento'])))
                try:
                    if not filtro: # si no se define un filtro previamente se hace uno que elimina parking y las secciones donde ya ha intentado aparcar
                        filtro = ((df_distancias['ORIGEN'] == seccion_destino) &
                                                        (~ (df_distancias['DESTINO'].isin(df_exportar.loc[idveh, 'Secciones intento aparcamiento']))) &
                                                        (~ (df_distancias['DESTINO'].isin(secciones_parking_subterraneo))))
                except ValueError: #EL FILTRO VIENE DEFINIDO CON LA FUNCION
                    pass
                    #AKIPrintString(str('Pasa por filtro 2'))
                df_calculos['secciones'] = df_distancias[filtro]['DESTINO']
                # velocidad peaton
                df_calculos['tiempos'] = df_distancias[filtro]['TIEMPO']
                df_calculos['ocupacion'] = df_calculos.apply(
                    calcula_ocupacion, axis=1)
                df_calculos['utilidad_calles'] = df_calculos.apply(
                    calcula_utilidad_con_t_fijo_calle, axis=1)
                if not comparativa:
                    utilidad_parking=[]
                    for x in secciones_parking_subterraneo:
                        filtro=((df_distancias['ORIGEN'] == seccion_destino) & (df_distancias['DESTINO'] == x))
                        tiempo_destino = df_distancias[filtro]['TIEMPO'].values[0]
                        utilidad_parking.append((x, _calcula_utilidad_calles(None,tiempo_busqueda_subterraneo,
                                                                    tiempo_destino=tiempo_destino,
                                                                    nodo_logit=0,
                                                                    seccion_interes=x )))
                    #AKIPrintString(str(utilidad_parking))
                    max_u= max(x[1] for x in utilidad_parking)
                    seccion_park=  next(x for x in utilidad_parking if x[1]==max_u)[0]
                    utilidad_calle= _calcula_utilidad_calles(None,tiempo_busqueda=tiempo_busqueda,
                                                                    nodo_logit=0,
                                                                    u_para_sumatorio=df_calculos[df_calculos['utilidad_calles'].notna()]['utilidad_calles'].tolist())
                    return (df_calculos,(max_u,seccion_park),utilidad_calle)
                else:
                    return (df_calculos,None,None)
            if seccion_origen:
                seccion_original_aparcamiento = df_exportar.loc[idveh,
                                                                'Secciones intento aparcamiento'][-1]

                # filtramos para coger solamente las secciones de origen y destino
                filtro_seccion_destino_comparativa_unitaria = (
                    (df_distancias['ORIGEN'] == seccion_destino) & (
                        df_distancias['DESTINO'].isin(
                            (seccion_origen, seccion_original_aparcamiento))) &
                                            (~ (df_distancias['DESTINO'].isin(secciones_parking_subterraneo))))
                # generamos las utilidades relativas, pero tenemos que tener en cuenta que la sección original no sea un parking porque en ese caso hay que recalcular todas
                if seccion_original_aparcamiento not in secciones_parking_subterraneo and seccion_origen not in secciones_parking_subterraneo:
                    #AKIPrintString('1')
                    df_calculos=genera_dataframe_calculos(seccion_destino,filtro=filtro_seccion_destino_comparativa_unitaria, comparativa=True)[0]
                    utilidad_primaria = df_calculos[df_calculos['secciones']
                                                == seccion_original_aparcamiento]['utilidad_calles'].iloc[0]
                    utilidad_calle_actual = df_calculos[df_calculos['secciones']
                                                    == seccion_origen]['utilidad_calles'].iloc[0]
                    #AKIPrintString('actual: '+str(utilidad_calle_actual)+'original '+str(utilidad_primaria))
                elif seccion_original_aparcamiento in secciones_parking_subterraneo:
                    #AKIPrintString('2')
                    df_calculos,utilidad_parking,utilidad_calle=genera_dataframe_calculos(seccion_destino)
                    utilidad_primaria=utilidad_parking[0]
                    utilidad_calle_actual=utilidad_calle
                elif seccion_origen in secciones_parking_subterraneo:
                    #AKIPrintString('3')
                    df_calculos,utilidad_parking,utilidad_calle=genera_dataframe_calculos(seccion_destino)
                    utilidad_primaria=utilidad_calle
                    utilidad_calle_actual=utilidad_parking[0]
                u_relativa = 100 - 100 * \
                    abs((abs(utilidad_calle_actual) - abs(utilidad_primaria)) / abs(utilidad_primaria))
##                logging.error('Utilidad relativa: '+str(u_relativa))
                if u_relativa > utilidad_relativa_alternativas:
                    distancia_max_utilidad = df_calculos[df_calculos['secciones']
                                                         == seccion_origen]["tiempos"].iloc[0] * 5000 / 60
                    ocupacion_maxima_utilidad = df_calculos[df_calculos['secciones']
                                                            == seccion_origen]["ocupacion"].iloc[0]
                    df_exportar.loc[idveh, 'Tarifa'].append(
                        _calcula_tarifa(seccion_origen,ocupacion_maxima_utilidad,idveh))
                    df_exportar.loc[idveh, 'Utilidad relativa'] = (
                        utilidad_primaria, utilidad_calle_actual, u_relativa)
                    # No tiene en cuenta pasar por delante de un parking
                    df_exportar.loc[idveh, 'Utilidades iteraciones'].append({'cambio': True, 'utilidades': {x:y for x, y in zip(df_calculos['secciones'].apply(int),df_calculos['utilidad_calles'])}})
                    return (seccion_origen, False, distancia_max_utilidad)
                else:
                    return (None, None, None)
            else:
                df_calculos,utilidad_parking,utilidad_calle=genera_dataframe_calculos(seccion_destino)
                #AKIPrintString('parking '+str(utilidad_parking[0]) +'calle '+str(utilidad_calle))
                if utilidad_calle>utilidad_parking[0]:
                    indice_fila_maxima_utilidad = df_calculos["utilidad_calles"].idxmax()
                    imprime_texto(str(indice_fila_maxima_utilidad))
                    fila_maxima_utilidad = df_calculos.loc[indice_fila_maxima_utilidad]
                    seccion_maxima_utilidad = fila_maxima_utilidad["secciones"]
                    distancia_max_utilidad = fila_maxima_utilidad["tiempos"] * 5000 / 60
                    ocupacion_maxima_utilidad = fila_maxima_utilidad["ocupacion"]
                else:
                    seccion_maxima_utilidad = utilidad_parking[1]
                    filtro=((df_distancias['ORIGEN'] == seccion_destino) & (df_distancias['DESTINO'] == seccion_maxima_utilidad))
                    distancia_max_utilidad = df_distancias[filtro]['TIEMPO'].values[0] * 5000 / 60
                    ocupacion_maxima_utilidad = None
##                logging.error(' quiere llegar a  : '+str(seccion_destino))
##                logging.error(' va a: '+str(seccion_maxima_utilidad))
                seccion_subterranea = True if seccion_maxima_utilidad in secciones_parking_subterraneo else False
                df_exportar.loc[idveh, 'Tarifa'].append(
                    _calcula_tarifa(seccion_maxima_utilidad,ocupacion_maxima_utilidad, idveh))
                df_exportar.loc[idveh, 'Utilidades iteraciones'].append({'cambio': False, 'utilidades': {x:y for x, y in zip(df_calculos['secciones'],df_calculos['utilidad_calles'])}})

                return (
                    seccion_maxima_utilidad,
                    seccion_subterranea,
                    distancia_max_utilidad)
        except Exception as e:
            logging.error(traceback.format_exc())


#####################################################################
            ## INICIO DEL PROGRAMA DE AIMSUN ##
#####################################################################

def AAPILoad():
    global conn, cola_diccionarios

    AKIPrintString("load")
    cola_diccionarios = ""
    # t1 = threading.Thread(target=recibe_datos)  # , args=(cola_diccionarios,))
    # t1.start()


# imprime_texto(1)
    global porcentaje_informados,tiempo_actualizacion_tarifas, utilidad_relativa_alternativas, ruta_excel_exportar, tarifa_subterraneo, rangos_tarifa_superficie,rangos_ocupa_superficie, tiempos_busqueda_medio, tiempos_busqueda_desviacion, tiempo_busqueda_min, tiempo_aparcamiento_avg, tiempo_parada_aparcamiento, tiempo_coche_aparcado_min, tiempo_coche_aparcado_max, ocupacion_inicial

    logging.error("Executable: "+str(sys.executable))
    # configurar par�metros
    from easygui import multenterbox, diropenbox
    msg = "Parametros del modelo"
    title = "Aimsum Park Gist"
    fieldNames = [
        "Tiempo parada aparcamientos (seg)",
        "Tiempo minimo aparcamiento (seg)",
        "Tiempo maximo aparcamiento (seg)",
        "Ocupacion inicial (%)",
        "Rangos tarifa on-street *tupla (eur/h)",
        "Rangos ocup on-street *tupla (%)",
        "Tarifa generica calle (eur/h)",
        "Tarifa parking (eur/h)",
        "Tiempo busqueda medio (seg)",
        "Tiempo busqueda desviacion (seg)",
        "Utilidad maxima relativa (%)",
        "Tiempo actualización tarifas (min)",
        "% Usuarios informados (%)"]
    def genera_tupla(string):
        lista=string.split(',')
        return tuple(map(float,lista))
    try:
        valores_por_defecto = [ # tipo 0 float tipo 1 # tupla
            (tiempo_parada_aparcamiento,float),
            (tiempo_coche_aparcado_min,float),
            (tiempo_coche_aparcado_max,float),
            (ocupacion_inicial,float),
            (rangos_tarifa_superficie,genera_tupla),
            (rangos_ocupa_superficie,genera_tupla),
            (tarifa_generica_calle, float),
            (tarifa_subterraneo,float),
            (tiempos_busqueda_medio,float),
            (tiempos_busqueda_desviacion,float),
            (utilidad_relativa_alternativas,float),
            (tiempo_actualizacion_tarifas, float),
            (porcentaje_informados,float)]
        valores_por_defecto_nombres = [
            'tiempo_parada_aparcamiento',
            'tiempo_coche_aparcado_min',
            'tiempo_coche_aparcado_max',
            'ocupacion_inicial',
            'rangos_tarifa_superficie',
            'rangos_ocupa_superficie',
            'tarifa_generica_calle',
            'tarifa_subterraneo',
            'tiempos_busqueda_medio',
            'tiempos_busqueda_desviacion',
            'utilidad_relativa_alternativas',
            'tiempo_actualizacion_tarifas',
            'porcentaje_informados']
        #tipos = nth(zip(*valores_por_defecto), 1)
        # fieldValues = multenterbox(msg, title, fieldNames, [x[0] for x in valores_por_defecto])
        # if fieldValues is None:
        #     sys.exit(0)
        # # make sure that none of the fields were left blank
        # while True:
        #     errmsg = ""
        #     for i, name in enumerate(fieldNames):
        #         if fieldValues[i].strip() == "":
        #             errmsg += "{} Es un campo requerido.\n\n".format(name)
        #     if errmsg == "":
        #         break  # no problems found
        #     fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)
        #     if fieldValues is None:
        #         break
        ruta_excel_exportar = r"E:\OneDrive - Universidad de Cantabria\Recordar GIST - VARIOS\Aparcamientos\resultados_temporales"
        # diropenbox(
        #     msg='indica la ruta de guardado de los informes',
        #     title=title,
        #     default=r"C:\Users\Andrés\Desktop\informes")
        logging.error(ruta_excel_exportar)
        # for indice, valor  in enumerate(fieldValues):
        #     variable=valores_por_defecto_nombres[indice]
        #     funcion=valores_por_defecto[indice][1]
        #     valor=funcion(valor)
        #     exec('{}={}'.format(variable,valor),globals())
        #     AKIPrintString(str('{}={}'.format(variable,valor)))
    except:
        logging.error(traceback.format_exc())
    tiempo_aparcamiento_avg = tiempo_coche_aparcado_min * \
        0.5 + tiempo_coche_aparcado_max * 0.5
    # vamos a po
    # try:
    #     address = ('localhost', 6005)     # family is deduced to be 'AF_INET'
    #     listener = Listener(address)
    #     conn = listener.accept()
    # except BaseException:
    #     logging.error(traceback.format_exc())

    return 0


def AAPIInit():
    # imprime_texto(2)
    global lista_secciones_con_comercios, lista_probabilidades, df_distancias
    ever=sys.executable
    AKIPrintString(str(ever))
    AKIPrintString("init")
    # �cargamos el excel de las distancias
    df_distancias = pd.read_excel(ruta_excel_distancias, header=0)
    # cargamos el excel de las plazas y el ded los comercios
    df = pd.read_excel(ruta_excel, header=0)
    df.fillna(0, inplace=True)
    dict_plazas_seccion_list = df.to_dict('list')
    dict_plazas_seccion = {x: int(y) for x, y
                           in zip(
        dict_plazas_seccion_list['seccion'],
        dict_plazas_seccion_list['plazas'])}
    # generamos la lista de comercios por seccion y la p de acabar en cada uno
    # de ellos
    lista_secciones_con_comercios = dict_plazas_seccion_list['seccion']
    lista_probabilidades = dict_plazas_seccion_list['prob_park']
    # vamos a relaccionar centroides y secciones que les vierten
    # creamos aqu� una lista de secciones mas correcta
    global secciones_park, plazas_park_total, plazas_park_free, plazas_park_full, dict_secciones_centroide
    for centroide in centroides_objetivo:
        lista_add = list()
        for id_centro in (0, 1, 2):
            seccion = AKIInfNetGetIdObjectANGofDestinationCentroidConnector(
                centroide, id_centro, boolp())
            if seccion > 0:
                secciones_park.add(seccion)
                lista_add.append(seccion)
                dict_centroide_secciones[seccion] = centroide
        dict_secciones_centroide[centroide] = tuple(lista_add)

    AKIPrintString("centroides objetivo " + str(dict_secciones_centroide))
    # plazas totales por calle reales
    plazas_park_total = {x: dict_plazas_seccion[x] for x in secciones_park}
    plazas_park_free = {
        x: int(
            dict_plazas_seccion[x] *
            (
                100 -
                ocupacion_inicial) *
            0.01) for x in secciones_park}  # lo estamos haciendo con calentamiento
    plazas_park_full = {
        x: plazas_park_total[x] -
        plazas_park_free[x] for x in secciones_park}  # plazas libres por calle
    asigna_tiempos_iniciales(plazas_park_full)
    atr = ANGConnGetAttribute(AKIConvertFromAsciiString("GKSection::ALIAS"))
    # pintamos
    actualiza_grafico(0, 0, actualizar_todo=False)
    for seccion in secciones_park:
        ANGConnSetAttributeValueStringA(
            atr, seccion, "{} libres de {}".format(
                plazas_park_free[seccion], plazas_park_total[seccion]))

    return 0


def AAPIManage(time, timeSta, timTrans, SimStep):
    # imprime_texto(3)
    try:
        #AKIPrintString("time: {}".format(str(time)))
        # extraemos en la primera ejecuci�n la losgitud de los tramos de control
        # para sacar a los coches justo en la mitad
        global ejecutar_1_vez, tiempo_global, plazas_park_total, plazas_park_free, df_exportar_secciones, df_exportar_ocupaciones,  precios_parking_street
        tiempo_global=time
        #actulizamos las tarifas si ha lugar
        if tiempo_global % (tiempo_salvado_ocupaciones)==0 or ejecutar_1_vez:
            for seccion in secciones_park:
                ocup = 1- (plazas_park_free[seccion] / plazas_park_total[seccion])
                df_exportar_ocupaciones=df_exportar_ocupaciones.append({'seccion':seccion, 'tiempo':tiempo_global, 'ocupacion': ocup},ignore_index=True)
        if tiempo_global % (tiempo_actualizacion_tarifas*60)==0 or ejecutar_1_vez:
            AKIPrintString("seciones: {}".format(str('ACTUALIZAR PRECIOS')))
            for seccion in secciones_park:
                if plazas_park_total[seccion]>0:
                    ocup = 1- (plazas_park_free[seccion] / plazas_park_total[seccion])
                    tarif = rangos_tarifa_superficie[bisect_left(rangos_ocupa_superficie, 100*ocup)]
                    precios_parking_street[seccion]=tarif
                    #AKIPrintString("seciones: {}".format(str(df_exportar_secciones)))
                    df_exportar_secciones=df_exportar_secciones.append({'seccion':seccion, 'tarifa':tarif,'tiempo':tiempo_global},ignore_index=True)
        if ejecutar_1_vez:
            todas_las_secciones=AKIInfNetNbSectionsANG()
            for seccion in range(0, todas_las_secciones):
                id_de_la_seccion=AKIInfNetGetSectionANGId(seccion)
                longitud_seccion = AKIInfNetGetSectionANGInf(id_de_la_seccion).length
                longitud_secciones[id_de_la_seccion] = longitud_seccion
            AKIPrintString(
                "Todas_las _secciones {}".format(
                    str(longitud_secciones)))
            ejecutar_1_vez = False

        # vaciamos las plzas que corresponda cada paso de simulacion
        if time % 1 == 0:
            desaparca_coche(time)

        # se recorre la lista de veh�culos que tienene intenci�n de apracar
        for vehiculo in lista_id_objetivo:
            if pd.isna(df_exportar.loc[vehiculo, 'Hora Entrada']):
                df_exportar.loc[vehiculo, 'Hora Entrada'] = time
# imprime_texto(4)
            global plazas_park_free, plazas_park_total, plazas_park_full, lista_buscando_sitio, dict_secciones_centroide
            datos_vehiculo = AKIVehTrackedGetInf(vehiculo)
            longitud_hasta_acabar_seccion = datos_vehiculo.distance2End
            seccion_vehiculo = datos_vehiculo.idSection
            # compromabos las maniobras de aparcamiento y decidimos quien
            # aparca
            if (vehiculo in vehiculos_parados):
                if time >= vehiculos_parados[vehiculo] + \
                        tiempo_parada_aparcamiento:
                    AKIVehTrackedRemove(vehiculo)
                    df_exportar.loc[vehiculo, 'Hora aparcamiento'] = time
                else:
                    AKIVehTrackedModifySpeed(vehiculo, 0.0)
            elif (seccion_vehiculo in secciones_park and seccion_vehiculo == secciones_destino_vehiculo[vehiculo]
                  and longitud_hasta_acabar_seccion < random.uniform(0.5, 1) * longitud_secciones[seccion_vehiculo]):

                # comprobamos si hay aparcamientos disponibles pen esa calle
                if plazas_park_free[seccion_vehiculo] > 0:

                    # comprobamos si el vehiculo estaba buscando sitio
                    if vehiculo in lista_buscando_sitio:
                        ##                        AKIPrintString("aparcando el vehiculo que buscaba: "+ str(vehiculo))
                        lista_buscando_sitio.remove(vehiculo)
                    AKIVehTrackedModifySpeed(vehiculo, 0.0)
                    # actualizamos el gr�fico y quitamos la plaza de la secci�n
                    # como no disponible
                    actualiza_grafico(seccion_vehiculo, vehiculo)
                    # a�adir el vehiculo a la lista de aparcados
                    tiempo_aparcamiento = genera_tiempo_aparcamiento()
                    time_salida = float(time) + tiempo_aparcamiento
                    df_exportar.loc[vehiculo,
                                    'Duracion aparcamiento'] = tiempo_aparcamiento / 60
##                    AKIPrintString('tiempo estacionamiento minutos '+ str((time_salida-time)/60))
                    dict_vehiculos_aparcados[vehiculo] = (
                        seccion_vehiculo, time_salida)
                    # paramos el coche
                    vehiculos_parados[vehiculo] = time
                    df_exportar.loc[vehiculo, 'track'].append((seccion_vehiculo,time,'aparca'))

                else:  # cuando no hay plazas disponibles le mandamos a una libre

                    ##                    AKIPrintString("No hay sitio para el vehiculo: {} asignado nuevo destino".format(str(vehiculo)))
                    df_exportar.loc[vehiculo, 'Intentos aparcamiento'] += 1
                    df_exportar.loc[vehiculo, 'track'].append((seccion_vehiculo,time,'no sitio'))
                    df_exportar.loc[vehiculo, 'track_secciones'].append([])
                    reasigna_plaza(vehiculo, time)
            elif (seccion_vehiculo in secciones_parking_subterraneo and seccion_vehiculo == secciones_destino_vehiculo[vehiculo]):
                if vehiculo in lista_buscando_sitio:
                    lista_buscando_sitio.remove(vehiculo)
                AKIVehTrackedModifySpeed(vehiculo, 0.0)
                tiempo_aparcamiento = genera_tiempo_aparcamiento()
                time_salida = float(time) + tiempo_aparcamiento
                df_exportar.loc[vehiculo,
                                        'Duracion aparcamiento'] = tiempo_aparcamiento / 60
                dict_vehiculos_aparcados[vehiculo] = (
                            seccion_vehiculo, time_salida)

                df_exportar.loc[vehiculo, 'track'].append((seccion_vehiculo,time,'aparca'))
                AKIVehTrackedRemove(vehiculo)
                df_exportar.loc[vehiculo, 'Hora aparcamiento'] = time

    except Exception as e:
        # imprime_texto(str(traceback.format_exc()))
        logging.error(traceback.format_exc())
    return 0


def AAPIPostManage(time, timeSta, timTrans, SimStep):
    return 0


def AAPIFinish():
    #calculo consumos hay que hace un artificio para que se tengan en cuenta el diferencial de calcular el consumo en la suma de las seciones
    
    consumos=defaultdict(float)
    factor_expansion=1
    for vehiculo in range(1,AKIVehGetNbVehTypes ()+1 ):
        anyNonAsciiChar = boolp()
        nombre = AKIConvertToAsciiString(AKIVehGetVehTypeName(vehiculo), True, anyNonAsciiChar)
        todas_las_secciones=AKIInfNetNbSectionsANG()
        coches_entran=float(AKIEstGetGlobalStatisticsSystem(vehiculo).inputCount)
        consumen=float(AKIEstGetGlobalStatisticsSystemFuelCons(vehiculo))
        for seccion in range(0, todas_las_secciones):
            id_de_la_seccion=AKIInfNetGetSectionANGId(seccion)
            consumo_seccion=AKIEstGetGlobalStatisticsSectionFuelCons( id_de_la_seccion, vehiculo)
            consumos[str(vehiculo)+" "+str(nombre)]=consumos[str(vehiculo)+" "+str(nombre)]+consumo_seccion
            # AKIPrintString("consumo seccion {} 1 {} 2 {}".format(str(id_de_la_seccion), str(consumo_seccion),str(consumo_seccion)))
        if vehiculo==1:
            factor_expansion = (consumen-float(consumos[str(vehiculo)+" "+str(nombre)]))/coches_entran
        consumos[str(vehiculo)+" "+str(nombre)]=consumos[str(vehiculo)+" "+str(nombre)]+factor_expansion*coches_entran
    a=AKIEstGetGlobalStatisticsSystemFuelCons(1)
    b=AKIEstGetGlobalStatisticsSystemFuelCons(2)
    consumos['c']=a
    consumos['par']=b
    df_consumos=pd.DataFrame.from_dict(consumos, columns=['Consumo',], orient='index')
    
    logging.error('fin')
    mascara = df_exportar['Hora aparcamiento'].notnull()
    df_enviar = df_exportar[mascara]
    fecha_hora_txt = datetime.now().strftime(r'\%Y-%m-%d__%H_%M_%S_')
# df_exportar.to_csv(path_or_buf=ruta_excel_exportar+fecha_hora_txt+r"informe.csv")
    df_enviar.to_excel(
        ruta_excel_exportar +
        fecha_hora_txt +
        r"informe.xlsx",
        engine="xlsxwriter")
    df_exportar_ocupaciones.to_excel(ruta_excel_exportar +
        fecha_hora_txt +
        r"informe_ocupaciones.xlsx",
        engine="xlsxwriter")
    df_exportar_secciones.to_excel(ruta_excel_exportar +
        fecha_hora_txt +
        r"informe_tarifas.xlsx",
        engine="xlsxwriter")
    df_consumos.to_excel(ruta_excel_exportar +
        fecha_hora_txt +
        r"informe_consumos.xlsx",
        engine="xlsxwriter")
    with open(r"E:\Program Files\Aimsun\Aimsun Next 8.3\programming\Aimsun Next API\AAPIPython\Micro\logaimsun.log", 'w') as file:
        file.write(str(lista_info_1))
        file.write("\n")
        file.write(str(lista_info_2))
    return 0


def AAPIUnLoad():
    return 0


def AAPIEnterVehicle(idveh, idsection):
    # conn.send(idveh)
    global transito, tipo_vehiculo
    AKIVehSetAsTracked(idveh)
    info_estatica_vehiculo = AKIVehTrackedGetStaticInf(idveh)
    tipo_vehiculo=info_estatica_vehiculo.type
    try:
        # con el rnd seleccionamos los que aparcan y los que no
        if (info_estatica_vehiculo.centroidDest in centroides_objetivo
                and seleccionar_vehiculo_rnd()):

            # hay que aplicar el modelo para saber donde lo mandamos
            seccion_destino = genera_seccion_destino()
            tipo_usuario=selecciona_tipo_usuario()
            #AKIPrintString("tipo: {}".format(str(tipo_usuario)))
##            imprime_texto("seccion_ dest: ",str(seccion_destino))
            df_exportar.loc[idveh, 'Hora Entrada'] = tiempo_global
            df_exportar.loc[idveh, 'Tipo usuario'] = tipo_usuario
            df_exportar.loc[idveh, 'distancia_recorrida']=0
            df_exportar.loc[idveh, 'Tarifa'] = []
            df_exportar.loc[idveh, 'ID'] = idveh
            df_exportar.loc[idveh, 'Utilidades iteraciones'] = []
            df_exportar.loc[idveh, 'track'] = []
            df_exportar.loc[idveh, 'track'].append((idsection,0,'entra'))
            df_exportar.loc[idveh, 'track_secciones'] = [[],]
            df_exportar.loc[idveh, 'Secciones intento aparcamiento'] = []
            seccion_aparcamiento, es_parking, distancia = genera_seccion_aparcamiento(
                seccion_destino, idveh)  # 893,True
            df_exportar.loc[idveh, 'Nodo aparcamiento'] = int(
                seccion_aparcamiento)
            df_exportar.loc[idveh, 'Nodo destino'] = int(seccion_destino)
            df_exportar.loc[idveh, 'Secciones intento aparcamiento'] = [
                int(seccion_aparcamiento)]
            df_exportar.loc[idveh, 'Distancia entre nodos'] = distancia
            df_exportar.loc[idveh, 'Parking'] = es_parking
            df_exportar.loc[idveh, 'Intentos aparcamiento'] = 0
##            archivo_temporal = NamedTemporaryFile()
# with NamedTemporaryFile() as archivo_temporal:
##                df_exportar.to_pickle(archivo_temporal, "bz2")
# conn.send(df_exportar.to_dict())
#            imprime_texto("seccion_ park: ",str(seccion_aparcamiento))
            centroide_aparcamiento = dict_centroide_secciones[int(
                seccion_aparcamiento)]
##            imprime_texto("centroide_ dest: ", str(centroide_aparcamiento))
            info_estatica_vehiculo.__setattr__(
                "centroidDest", int(centroide_aparcamiento))
            # a�adimos la id a una lista para saber cuales estamos trackeando
            AKIPrintString("Siguiendo al vehiculo con destino a {}, dirigiendose a {}, tipo {}".format(str(seccion_destino),
                            str(seccion_aparcamiento), str(tipo_usuario)))
            lista_id_objetivo.append(idveh)
            # guardamos la seccion de destino
            secciones_destino_vehiculo[idveh] = int(seccion_aparcamiento)
# AKIPrintString(str(info_estatica_vehiculo.type))

# AKIPrintString(str(AKIVehGetNbVehTypes()))
# idg=ANGConnVehGetGKSimVehicleId(idveh)
    ##        ANGConnSetText (idg, ctypes.c_ushort(b"juan"))
            info_estatica_vehiculo.__setattr__("width", 2.01)
            # info_estatica_vehiculo.__setattr__("type", 2)
    # info_estatica_vehiculo.__setattr__("centroidDest",1012)
# imprime_texto(5)
            a = AKIVehTrackedSetStaticInf(idveh, info_estatica_vehiculo)
# imprime_texto(6,str(a))
##            imprime_texto("centroide_ dest: ", str(info_estatica_vehiculo.centroidDest))

        else:
            transito = transito + 1
            AKIVehSetAsNoTracked(idveh)
    except BaseException:
        logging.error(traceback.format_exc())
# imprime_texto(7)
    lista_info_1.append(info_estatica_vehiculo.centroidDest)
# imprime_texto(8)
    info_vehiculo_trackeado = AKIVehTrackedGetInf(idveh)
# imprime_texto(9)
    lista_info_2.append(info_vehiculo_trackeado)
# imprime_texto(10)
    return 0


def AAPIExitVehicle(idveh, idsection):
    global transito, cola_diccionarios, candado
    if idveh in lista_buscando_sitio:
        lista_buscando_sitio.remove(idveh)
    # si el vehiculo esta controlado, lo sacamos de la lista de control
    if idveh in lista_id_objetivo:
        mascara = df_exportar['Hora aparcamiento'].notnull()
        df_enviar = df_exportar[mascara]
        with candado:
            cola_diccionarios = df_enviar.to_json()
        df_exportar.loc[idveh, 'track'].append((idsection,99999999999999,'sale'))
        lista_id_objetivo.remove(idveh)
    else:
        transito = transito - 1
##        AKIPrintString("El vehiculo trackeado {} sale de la simulacion".format(str(idveh)))
    return 0

def AAPIEnterVehicleSection(idveh, idsection, atime):
    try:
        #guardamos las seciones por las que va pasando el vehiculo en su busqueda de de sitio
        if idveh in lista_id_objetivo:
            
            df_exportar.loc[idveh, 'distancia_recorrida']=df_exportar.loc[idveh, 'distancia_recorrida']+longitud_secciones[idsection]
            df_exportar.loc[idveh, 'track_secciones'][-1].append(idsection)
            df_exportar.loc[idveh, 'track'].append((idsection,atime,'paso'))
            if idsection in secciones_park and idsection != secciones_destino_vehiculo[
                idveh] and plazas_park_free[idsection] > 0:
                tiempo_busqueda_transcurrido = (
                    atime - df_exportar.loc[idveh, 'Hora Entrada']) / 60
                seccion_destino = df_exportar.loc[idveh, 'Nodo destino']
                seccion_aparcamiento, es_parking, distancia = genera_seccion_aparcamiento(
                    seccion_destino, idveh, seccion_origen=idsection, tiempo_busqueda_transcurrido=tiempo_busqueda_transcurrido)
                if seccion_aparcamiento:
                    df_exportar.loc[idveh, 'Nodo aparcamiento'] = int(
                        seccion_aparcamiento)
                    df_exportar.loc[idveh, 'Nodo destino'] = int(seccion_destino)
                    df_exportar.loc[idveh, 'Secciones intento aparcamiento'].append(
                        int(seccion_aparcamiento))
                    df_exportar.loc[idveh,
                                    'Distancia entre nodos'] = float(distancia)
                    df_exportar.loc[idveh, 'Parking'] = es_parking
                    df_exportar.loc[idveh, 'Seccion de paso'] = 'si'
                    centroide_aparcamiento = dict_centroide_secciones[int(
                        seccion_aparcamiento)]
                    info_estatica_vehiculo = AKIVehTrackedGetStaticInf(idveh)
                    info_estatica_vehiculo.__setattr__(
                        "centroidDest", int(centroide_aparcamiento))
                    AKIVehTrackedSetStaticInf(idveh, info_estatica_vehiculo)
                    secciones_destino_vehiculo[idveh] = int(seccion_aparcamiento)
                    df_exportar.loc[idveh, 'track'].append((idsection,atime,'seccion_recalculada'))
##                    df_exportar.loc[idveh, 'track_secciones'].append([])

    except BaseException:
        logging.error(traceback.format_exc())
    return 0


def AAPIExitVehicleSection(idveh, idsection, atime):
    return 0


def AAPIEnterPedestrian(idPedestrian, originCentroid):
    return 0


def AAPIExitPedestrian(idPedestrian, destinationCentroid):
    return 0


def AAPIPreRouteChoiceCalculation(time, timeSta):
    return 0
