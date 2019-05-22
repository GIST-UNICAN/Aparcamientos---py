# -*- coding: cp1252 -*-
from AAPI import *
import random
import ctypes
import logging
logging.basicConfig(level=logging.WARNING)
logging.basicConfig(filename='apitest1.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
#####################################################################
                     ## todo ##
#####################################################################

# incluir el tiempo en las plazas llenas
# mejorar el algoritmo de vaciado ded plazas
# incluir función eleccion


#####################################################################
                     ## variables ##
#####################################################################



### GEOMETRIA APARCAMIENTOS
centroides_objetivo=(34783,34799,34798,34797,34796,34795,34784,34785,34786,34827,34786,34788,34787,34789,34790,34792,34791,34793,34794,34800,34801,34828,34829,34830,34875)
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
dict_vehiculos_aparcados=dict() #{idveh:(seccion, timestart, tiempo de salida)}
vehiculos_parados={}# {idveh: comienzo_parada}
lista_buscando_sitio=list()
ejecutar_1_vez=True


### VARIABLES MODELO
tiempo_parada_aparcamiento=30 # en segundos
tiempo_coche_aparcado_min=5*60 # tiempo mímino que un coche puede estar en una plaza
tiempo_coche_aparcado_max=120*60 # tiempo máximo que un coche puede estar en una plaza
duracion_aparcamiento_min=10*60 
tiempo_aparcamiento_avg=tiempo_coche_aparcado_min*0.5+tiempo_coche_aparcado_max*0.5

plazas_park_total=dict()
plazas_park_free=dict()
plazas_park_full=dict()



#####################################################################
                     ## funciones propias ##
#####################################################################

def seleccionar_vehiculo_rnd():
    numero=int(random.uniform(1, 3))
    return True if numero ==1 else False

def AAPILoad():
    AKIPrintString("load")
    
    #vamos a poner las plazas libres en cada seccion
    #vamos a añadir un atributo con las plazas libres ebn cada uno de los diferenbtes arcos que admiten plazas de aparcamiento
    
##    AKIConvertToAsciiString( name, false, &anyNonAsciiChar )
    
##    AKIPrintString(help(AAPI.InfVeh))
    return 0


def aparca_coche():
    global plazas_park_free, plazas_park_total,plazas_park_full, lista_buscando_sitio, dict_secciones_centroide
    pass

def desaparca_coche():
    global plazas_park_free, plazas_park_total,plazas_park_full
    solo_ocupadas = {k: v for k, v in plazas_park_full.iteritems() if v>0}
    vaciar_plaza=random.choice(solo_ocupadas.keys())
    plazas_park_free[vaciar_plaza]=plazas_park_free[vaciar_plaza]+1
    plazas_park_full[vaciar_plaza]=plazas_park_full[vaciar_plaza]-1
    # TODO actualizar los info gráfica 

def actualiza_grafico(seccion_vehiculo,vehiculo):
    global plazas_park_free, plazas_park_total,plazas_park_full
    #actualizamos el diccionario de plazas disponibles en esa calle
    plazas_park_free[seccion_vehiculo]=plazas_park_free[seccion_vehiculo]-1
    plazas_park_full[seccion_vehiculo]=plazas_park_full[seccion_vehiculo]+1
    atr=ANGConnGetAttribute(AKIConvertFromAsciiString("GKSection::ALIAS"))
    ANGConnSetAttributeValueStringA(atr,seccion_vehiculo, "{} libres de {}".format(plazas_park_free[seccion_vehiculo], plazas_park_total[seccion_vehiculo]))
    ANGConnSetText ( 34835,AKIConvertFromAsciiString("Plazas libres {} aparcados {} buscando {}".format(
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
        nuevo_destino=dict_secciones_centroide[random.choice(dict_secciones_centroide.keys())][0]#sacamos la sección
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


#####################################################################
                ## INICIO DEL PROGRAMA DE AIMSUN ##
#####################################################################
    

def AAPIInit():
    AKIPrintString("init")
    #vamos a relaccionar centroides y secciones que les vierten
    #creamos aquí una lista de secciones mas correcta
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
    plazas_park_total={x:random.randint(random_plazas_hasta_libres,random_plazas_hasta) for x in secciones_park}# plazas totales por calle
    plazas_park_free={x:random.randint(0,random_plazas_hasta_libres) for x in secciones_park}# plazas libres por calle
    plazas_park_full={x:plazas_park_total[x]-plazas_park_free[x] for x in secciones_park}# plazas libres por calle
    #hay que establecer la sección y el tiempo que llevan llenas las plazas ocupadas
    vehiculo=-1
    for seccion, plazas in plazas_park_full.values:
        for n in range(0,plazas):
            # a cada coche aparcado le damos un tiempo de comienzo aleatorio y de fin siguiendo una distribucion normal



            
            tiempo_start=random.randint(-tiempo_aparcamiento_max,-1)
            duracion_park=int(random.normalvariate(tiempo_aparcamiento_avg,0.33*tiempo_aparcamiento_avg)
            dict_vehiculos_aparcados[vehiculo]=(seccion,tiempo_start,duracion_park)
            vehiculo=vehiculo-1



                              
    dict_vehiculos_aparcados[vehiculo]
    atr=ANGConnGetAttribute(AKIConvertFromAsciiString("GKSection::ALIAS"))
    for seccion in secciones_park:
        ANGConnSetAttributeValueStringA(atr,seccion, "{} libres de {}".format(plazas_park_free[seccion], plazas_park_total[seccion]))

    return 0

def AAPIManage(time, timeSta, timTrans, SimStep):
    #extraemos en la primera ejecución la losgitud de los tramos de control
    #para sacar a los coches justo en la mitad
    global ejecutar_1_vez
    if ejecutar_1_vez:
        for seccion in secciones_park:
            longitud_seccion=AKIInfNetGetSectionANGInf(seccion).length
            longitud_secciones[seccion]=longitud_seccion
        AKIPrintString("Segmentos seccion aparcammiento {}".format(str(longitud_secciones)))
        ejecutar_1_vez=False
        
    #vaciamos una plaza cada minuto
    if time%60==0:
        desaparca_coche()
        

    #se recorre la lista de vehículos que tienene intención de apracar    
    for vehiculo in lista_id_objetivo:
        global plazas_park_free, plazas_park_total,plazas_park_full, lista_buscando_sitio, dict_secciones_centroide
        datos_vehiculo=AKIVehTrackedGetInf(vehiculo)
        longitud_hasta_acabar_seccion = datos_vehiculo.distance2End
        seccion_vehiculo= datos_vehiculo.idSection
        #compromabos las maniobras de aparcamiento y decidimos quien aparca
        if (vehiculo in vehiculos_parados):
            if time>=vehiculos_parados[vehiculo]+tiempo_parada_aparcamiento:
                AKIVehTrackedRemove (vehiculo)
                lista_id_objetivo.remove(vehiculo)
                dict_vehiculos_aparcados[vehiculo]=(seccion_vehiculo,time)
                AKIPrintString("Fin de la maniobra de aparcamiento del vehiculo {}".format(str(vehiculo)))
            else:
                AKIVehTrackedModifySpeed (vehiculo, 0.0)
        elif (seccion_vehiculo in secciones_park and seccion_vehiculo == secciones_destino_vehiculo[vehiculo]  
            and longitud_hasta_acabar_seccion<random.uniform(0.5,1)*longitud_secciones[seccion_vehiculo]):
            
            #comprobamos si hay aparcamientos disponibles pen esa calle
            if plazas_park_free[seccion_vehiculo]>0:
                #comprobamos si el vehiculo estaba buscando sitio
                if vehiculo in lista_buscando_sitio:
                    AKIPrintString("aparcando el vehicuro que buscaba: "+ str(vehiculo))
                    lista_buscando_sitio.remove(vehiculo)
    
                        
                #actualizamos el gráfico
                actualiza_grafico(seccion_vehiculo,vehiculo)

                #paramos el coche
                vehiculos_parados[vehiculo]=time
                AKIPrintString("Aparcando el vehículo por primera vez {}".format(str(vehiculo)))
                AKIVehTrackedModifySpeed (vehiculo, 0.0)
            else: #cuando no hay plazas disponibles le mandamos a una libre magicamente
                
                AKIPrintString("No hay sitio para el vehiculo: {} asignado nuevo destino".format(str(vehiculo)))
                reasigna_plaza(vehiculo)
               

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

    #con el rnd seleccionamos los que aparcan y los que no
    if (info_estatica_vehiculo.centroidDest in centroides_objetivo
        and seleccionar_vehiculo_rnd()):
        # añadimos la id a una lista para saber cuales estamos trackeando
##        AKIPrintString("Siguiendo al vehiculo {}".format(str(idveh)))
        lista_id_objetivo.append(idveh)
        #guardamos la seccion de destino
        secciones_destino_vehiculo[idveh]=int(info_estatica_vehiculo.idsectionExit)
##        AKIPrintString(str(type(info_estatica_vehiculo.type)))
        
##        AKIPrintString(str(AKIVehGetNbVehTypes()))
        idg=ANGConnVehGetGKSimVehicleId(idveh)
##        ANGConnSetText (idg, ctypes.c_ushort(b"juan"))
        info_estatica_vehiculo.__setattr__("width",2.01)
##        info_estatica_vehiculo.__setattr__("centroidDest",1012)
        AKIVehTrackedSetStaticInf(idveh,info_estatica_vehiculo)
        
    else:
        AKIVehSetAsNoTracked (idveh)
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
