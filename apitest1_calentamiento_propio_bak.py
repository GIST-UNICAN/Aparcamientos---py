# -*- coding: cp1252 -*-
from AAPI import *
import random
import ctypes
import logging
import traceback
import pandas as pd
from itertools import count
##import pip
##pip.main(['install', 'tkinter'])
logging.basicConfig(level=logging.INFO)
##logging.basicConfig(filename='apitest1.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
#####################################################################
                     ## todo ##
#####################################################################

# incluir funci�n eleccion
# optimizar variable coches aparcados
# retenci�on salida vehiculos


#####################################################################
                     ## variables ##
#####################################################################



### GEOMETRIA APARCAMIENTOS
ruta_excel=r"E:\Program Files\Aimsun\Aimsun Next 8.3\programming\Aimsun Next API\AAPIPython\Micro\plazas_seccion.xlsx"
centroides_objetivo=(34894,34892,34783,34799,34798,34797,34796,34795,34784,34785,34786,34827,34786,34788,34787,34789,34790,34792,34791,34793,34794,34800,34801,34828,34829,34830,34875)
dict_secciones_centroide=dict()
secciones_park=set()#(889,992,998,865,862,899,1129,1092,1089,1042,1059,1058,1056,901,892,1047,1043,934,975,946,1066,1043,1085,1086,1146,1079,1078,968,893,895)
random_plazas_hasta=9
random_plazas_hasta_libres=5
longitud_secciones={}

### VARIABLES INTERNAS
secciones_destino_vehiculo=dict() #Establece donde va cada coche
lista_info_1=[]
lista_info_2=[]
lista_id_objetivo=[]
dict_vehiculos_aparcados=dict() #{idveh:(seccion,  tiempo de salida)}
dict_vehiculos_aparcados_previos=dict() #{idveh:(seccion,  tiempo de salida)}
vehiculos_parados={}# {idveh: comienzo_parada}
lista_buscando_sitio=list()
ejecutar_1_vez=True


### VARIABLES MODELO
tiempo_parada_aparcamiento=30 # en segundos
tiempo_coche_aparcado_min=5*60 # tiempo m�mino que un coche puede estar en una plaza
tiempo_coche_aparcado_max=120*60 # tiempo m�ximo que un coche puede estar en una plaza
duracion_aparcamiento_min=10*60 
tiempo_aparcamiento_avg=tiempo_coche_aparcado_min*0.5+tiempo_coche_aparcado_max*0.5
media_duracion_park=30*60
std_duracion_park=30*60
ocupacion_inicial=85


plazas_park_total=dict()
plazas_park_free=dict()
plazas_park_full=dict()



#####################################################################
                     ## funciones propias ##
#####################################################################

def seleccionar_vehiculo_rnd():
    numero=int(random.uniform(1, 1))
    return True if numero ==1 else False


def aparca_coche():
    global plazas_park_free, plazas_park_total,plazas_park_full, lista_buscando_sitio, dict_secciones_centroide
    pass

def desaparca_coche(time):
    global plazas_park_free, plazas_park_total,plazas_park_full, dict_vehiculos_aparcados
    for coche, tupla in dict_vehiculos_aparcados.items():
##        logging.error(dict_vehiculos_aparcados)
        if tupla and tupla[1]<time:
            del dict_vehiculos_aparcados[coche]
            actualiza_grafico(tupla[0],coche,signo=-1)
    for coche, tupla in dict_vehiculos_aparcados_previos.items():
##        logging.error(dict_vehiculos_aparcados)
        if tupla and tupla[1]<time:
            del dict_vehiculos_aparcados_previos[coche]
            actualiza_grafico(tupla[0],coche,signo=-1)
            

def actualiza_grafico(seccion_vehiculo,vehiculo,signo=1,actualizar_todo=True):
    global plazas_park_free, plazas_park_total,plazas_park_full
    if actualizar_todo:
        #actualizamos el diccionario de plazas disponibles en esa calle
        plazas_park_free[seccion_vehiculo]=plazas_park_free[seccion_vehiculo]-1*signo
        plazas_park_full[seccion_vehiculo]=plazas_park_full[seccion_vehiculo]+1*signo
        plazas_totales_seccion=plazas_park_free[seccion_vehiculo]+plazas_park_full[seccion_vehiculo]
        atr=ANGConnGetAttribute(AKIConvertFromAsciiString("GKSection::ALIAS"))
        ANGConnSetAttributeValueStringA(atr,seccion_vehiculo, "{} libres de {}".format(plazas_park_free[seccion_vehiculo], plazas_totales_seccion))
    ANGConnSetText ( 34835,AKIConvertFromAsciiString("Plazas: \n--------\nlibres {} \naparcados {} \nbuscando {}".format(
        max(0,sum(plazas_park_free.values())),
        sum(plazas_park_full.values()),
        str(len(lista_buscando_sitio)))))


def reasigna_plaza(vehiculo):
    global plazas_park_free, plazas_park_total,plazas_park_full, lista_buscando_sitio, dict_secciones_centroide
    info_estatica_vehiculo=AKIVehTrackedGetStaticInf (vehiculo)
    if vehiculo in lista_buscando_sitio:
        pass
    else:
        lista_buscando_sitio.append(vehiculo)
    solo_libres = {k: v for k, v in plazas_park_free.iteritems() if v>0}
    if solo_libres:
        nuevo_destino=dict_secciones_centroide[random.choice(dict_secciones_centroide.keys())][0]#sacamos la secci�n
        nuevo_centroide_destino=0
    else: #un centroide al azar y da vueltas como un loco
        nuevo_destino=random.choice(centroides_objetivo)
        nuevo_centroide_destino=0
    
    
    #buscamos el centroide de la seccion nueva de destino 
    for centroide in centroides_objetivo:
        if nuevo_destino in  dict_secciones_centroide[centroide]:
            nuevo_centroide_destino=centroide
            continue
    secciones_destino_vehiculo[vehiculo]=nuevo_destino #es necesario ponerle la nueva seccion de destino
    info_estatica_vehiculo.__setattr__("centroidDest",nuevo_centroide_destino)
    info_estatica_vehiculo.__setattr__("width",2.02)#para pintarle de otro color
    AKIVehTrackedSetStaticInf(vehiculo,info_estatica_vehiculo)
    AKIPrintString("buscando: "+str(lista_buscando_sitio))
    AKIPrintString("Reasignado el vehiculo: {} al centroide {}".format(str(vehiculo),str(nuevo_centroide_destino)))

def genera_tiempo_aparcamiento():
    return max(300, random.gauss(media_duracion_park, std_duracion_park))

def genera_tiempo_aparcamiento_inical():
    return random.randint(0, tiempo_coche_aparcado_max)

def asigna_tiempos_iniciales(plazas_park_full, contador=count(-1,-1)):
    global dict_vehiculos_aparcados_previos
    for seccion, numero_plazas_llenas in plazas_park_full.items():
        for plaza in range(numero_plazas_llenas):
            dict_vehiculos_aparcados_previos[next(contador)]=(seccion,genera_tiempo_aparcamiento_inical())


    
#####################################################################
                ## INICIO DEL PROGRAMA DE AIMSUN ##
#####################################################################
    
def AAPILoad():
    global tiempo_aparcamiento_avg,tiempo_parada_aparcamiento,tiempo_coche_aparcado_min,tiempo_coche_aparcado_max,ocupacion_inicial
    AKIPrintString("load")
    #configurar par�metros
    from easygui import multenterbox, diropenbox
    msg = "Par�metros del modelo"
    title = "Aimsum Park Gist"
    fieldNames = ["Tiempo parada aparcamientos (seg)", "Tiempo m�nimo aparcamiento (seg)"
                  , "Tiempo m�ximo aparcamiento (seg)", "Ocupacion inicial (%)"]
    valores_por_defecto=[tiempo_parada_aparcamiento,tiempo_coche_aparcado_min,tiempo_coche_aparcado_max,ocupacion_inicial]
    fieldValues = multenterbox(msg, title, fieldNames,valores_por_defecto)
    if fieldValues is None:
        sys.exit(0)
    # make sure that none of the fields were left blank
    while 1:
        errmsg = ""
        for i, name in enumerate(fieldNames):
            if fieldValues[i].strip() == "":
              errmsg += "{} Es un campo requerido.\n\n".format(name)
        if errmsg == "":
            break # no problems found
        fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)
        if fieldValues is None:
            break
    directorio_salvado = diropenbox(msg='indica la ruta de guardado de los informes', title=title, default=r"C:\Users\Andr�s\Desktop\informes")
    tiempo_parada_aparcamiento,tiempo_coche_aparcado_min,tiempo_coche_aparcado_max,ocupacion_inicial= (int(x) for x in fieldValues)
    tiempo_aparcamiento_avg=tiempo_coche_aparcado_min*0.5+tiempo_coche_aparcado_max*0.5
    #vamos a po
    return 0


def AAPIInit():
    AKIPrintString("init")
    #cargamos el excel de las plazas
    df=pd.read_excel(ruta_excel, header=0)
    df.fillna(0,inplace=True)
    dict_plazas_seccion=df.to_dict('list')
    dict_plazas_seccion={x:int(y) for x, y
                         in zip(
                             dict_plazas_seccion.values()[0],
                             dict_plazas_seccion.values()[1])}
   
    #vamos a relaccionar centroides y secciones que les vierten
    #creamos aqu� una lista de secciones mas correcta
    global secciones_park,plazas_park_total,plazas_park_free,plazas_park_full, dict_secciones_centroide
    for centroide in centroides_objetivo:
        lista_add=list()
        for id_centro in (0,1,2):
            seccion=AKIInfNetGetIdObjectANGofDestinationCentroidConnector(centroide,id_centro, boolp())
            if seccion>0:
                secciones_park.add(seccion)
                lista_add.append(seccion)
        dict_secciones_centroide[centroide]=tuple(lista_add)
    AKIPrintString("centroides objetivo "+str(dict_secciones_centroide))
    plazas_park_total={x:dict_plazas_seccion[x] for x in secciones_park}# plazas totales por calle reales 
    plazas_park_free={x:int(dict_plazas_seccion[x]*(100-ocupacion_inicial)*0.01) for x in secciones_park} # lo estamos haciendo con calentamiento
    plazas_park_full={x:plazas_park_total[x]-plazas_park_free[x] for x in secciones_park}# plazas libres por calle
    asigna_tiempos_iniciales(plazas_park_full)
    atr=ANGConnGetAttribute(AKIConvertFromAsciiString("GKSection::ALIAS"))
    #pintamos
    actualiza_grafico(0,0,actualizar_todo=False)
    for seccion in secciones_park:
        ANGConnSetAttributeValueStringA(atr,seccion, "{} libres de {}".format(plazas_park_free[seccion], plazas_park_total[seccion]))

    return 0

def AAPIManage(time, timeSta, timTrans, SimStep):
    try:
    ##    AKIPrintString("time: {}".format(str(time)))
        #extraemos en la primera ejecuci�n la losgitud de los tramos de control
        #para sacar a los coches justo en la mitad
        global ejecutar_1_vez
        if ejecutar_1_vez:
            for seccion in secciones_park:
                longitud_seccion=AKIInfNetGetSectionANGInf(seccion).length
                longitud_secciones[seccion]=longitud_seccion
            AKIPrintString("Segmentos seccion aparcammiento {}".format(str(longitud_secciones)))
            ejecutar_1_vez=False
            
        #vaciamos las plzas que corresponda cada paso de simulacion
        if time%1==0:
            desaparca_coche(time)
            

        #se recorre la lista de veh�culos que tienene intenci�n de apracar    
        for vehiculo in lista_id_objetivo:
            global plazas_park_free, plazas_park_total,plazas_park_full, lista_buscando_sitio, dict_secciones_centroide
            datos_vehiculo=AKIVehTrackedGetInf(vehiculo)
            longitud_hasta_acabar_seccion = datos_vehiculo.distance2End
            seccion_vehiculo= datos_vehiculo.idSection
            #compromabos las maniobras de aparcamiento y decidimos quien aparca
            if (vehiculo in vehiculos_parados):
                if seccion_vehiculo==893:
                    AKIVehTrackedModifySpeed (vehiculo, 0.0)
                    pass
                if time>=vehiculos_parados[vehiculo]+tiempo_parada_aparcamiento:
                    AKIVehTrackedRemove (vehiculo)
##                    lista_id_objetivo.remove(vehiculo)
##                    AKIPrintString("Fin de la maniobra de aparcamiento del vehiculo {}".format(str(vehiculo)))
                else:
                    AKIVehTrackedModifySpeed (vehiculo, 0.0)
            elif (seccion_vehiculo in secciones_park and seccion_vehiculo == secciones_destino_vehiculo[vehiculo]  
                and longitud_hasta_acabar_seccion<random.uniform(0.5,1)*longitud_secciones[seccion_vehiculo]):
                
                #comprobamos si hay aparcamientos disponibles pen esa calle
                if plazas_park_free[seccion_vehiculo]>0:
                    #comprobamos si el vehiculo estaba buscando sitio
                    if vehiculo in lista_buscando_sitio:
                        AKIPrintString("aparcando el vehiculo que buscaba: "+ str(vehiculo))
                        lista_buscando_sitio.remove(vehiculo)
                    else:
                        pass
##                        AKIPrintString("Aparcando el veh�culo por primera vez {}".format(str(vehiculo)))
        
                    #llevarle a la derecha del todo a aparcar
                    if seccion_vehiculo==893: 
                        AKIVehTrackedModifyLane (vehiculo, -1)
                    else:
                        AKIVehTrackedModifySpeed (vehiculo, 0.0)
                    #actualizamos el gr�fico y quitamos la plaza de la secci�n como no disponible
                    actualiza_grafico(seccion_vehiculo,vehiculo)
                    #a�adir el vehiculo a la lista de aparcados
                    time_salida=float(time)+genera_tiempo_aparcamiento()
                    AKIPrintString(str((time_salida-time)/60))
                    dict_vehiculos_aparcados[vehiculo]=(seccion_vehiculo,time_salida) 
                    #paramos el coche
                    vehiculos_parados[vehiculo]=time
                    #llevarle a la derecha del todo a aparcar
                    if seccion_vehiculo==893: 
                        AKIVehTrackedModifyLane (vehiculo, -1)
                        AKIVehTrackedModifyLane (vehiculo, -1)
                    else:
                        AKIVehTrackedModifySpeed (vehiculo, 0.0)
                    
                else: #cuando no hay plazas disponibles le mandamos a una libre magicamente
                    
                    AKIPrintString("No hay sitio para el vehiculo: {} asignado nuevo destino".format(str(vehiculo)))
                    reasigna_plaza(vehiculo)
                   
    except Exception as e:
        logging.error(traceback.format_exc())
    return 0

def AAPIPostManage(time, timeSta, timTrans, SimStep):
    return 0

def AAPIFinish():
    with open(r"E:\OneDrive - Universidad de Cantabria\Recordar GIST - VARIOS\PASAR DE PC\aimsumapis\logaimsun.log",'w') as file:
        file.write(str(lista_info_1))
        file.write("\n")
        file.write(str(lista_info_2))
    return 0

def AAPIUnLoad():
    return 0

def AAPIEnterVehicle(idveh,idsection):
    
    AKIVehSetAsTracked (idveh)
    info_estatica_vehiculo=AKIVehTrackedGetStaticInf (idveh)
    try: 
        #con el rnd seleccionamos los que aparcan y los que no
        if (info_estatica_vehiculo.centroidDest in centroides_objetivo
            and seleccionar_vehiculo_rnd()):
            # a�adimos la id a una lista para saber cuales estamos trackeando
##            AKIPrintString("Siguiendo al vehiculo {}".format(str(idveh)))
            lista_id_objetivo.append(idveh)
            #guardamos la seccion de destino
            secciones_destino_vehiculo[idveh]=int(info_estatica_vehiculo.idsectionExit)
##            AKIPrintString(str(info_estatica_vehiculo.type))
            
##            AKIPrintString(str(AKIVehGetNbVehTypes()))
##            idg=ANGConnVehGetGKSimVehicleId(idveh)
    ##        ANGConnSetText (idg, ctypes.c_ushort(b"juan"))
            info_estatica_vehiculo.__setattr__("width",2.01)
            info_estatica_vehiculo.__setattr__("type",2)
    ##        info_estatica_vehiculo.__setattr__("centroidDest",1012)
            AKIVehTrackedSetStaticInf(idveh,info_estatica_vehiculo)
       
        else:
            AKIVehSetAsNoTracked (idveh)
    except:
        logging.error(traceback.format_exc())
    lista_info_1.append(info_estatica_vehiculo.centroidDest)
    info_vehiculo_trackeado =AKIVehTrackedGetInf(idveh)
    lista_info_2.append(info_vehiculo_trackeado)
    return 0

def AAPIExitVehicle(idveh,idsection):
    #si el vehiculo esta controlado, lo sacamos de la lista de control
    if idveh in lista_id_objetivo:
        lista_id_objetivo.remove(idveh)
##        AKIPrintString("El vehiculo trackeado {} sale de la simulacion".format(str(idveh)))
    return 0



def AAPIEnterVehicleSection ( idveh,  idsection,  atime):
    return 0

def AAPIExitVehicleSection ( idveh,  idsection,  atime):
    return 0

def AAPIEnterPedestrian ( idPedestrian,  originCentroid):
    return 0

def AAPIExitPedestrian ( idPedestrian,  destinationCentroid):
    return 0

def AAPIPreRouteChoiceCalculation ( time,  timeSta):
    return 0
