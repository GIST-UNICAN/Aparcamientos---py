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
        with open (r"E:\Program Files\Aimsun\Aimsun Next 8.3\programming\Aimsun Next API\AAPIPython\Micro\log_time.txt",'a') as log:
            print(self.nombre, " tardo ", self.interval, "segundos.", file=log)


def imprime_texto(*txt):
    return
    with open (r"E:\Program Files\Aimsun\Aimsun Next 8.3\programming\Aimsun Next API\AAPIPython\Micro\log.txt",'a') as log:
        print(*txt, file=log)


def seleccionar_vehiculo_rnd():
    numero=int(random.uniform(1, 1))
    return True if numero ==1 else False


def aparca_coche():
    global plazas_park_free, plazas_park_total,plazas_park_full, lista_buscando_sitio, dict_secciones_centroide
    pass

def desaparca_coche(time):
    global plazas_park_free, plazas_park_total,plazas_park_full, dict_vehiculos_aparcados
    for coche, tupla in dict_vehiculos_aparcados.items():
##        imprime_texto("aparcados ", str(dict_vehiculos_aparcados))
##        logging.error(dict_vehiculos_aparcados)
        if tupla and tupla[1]<time:
            del dict_vehiculos_aparcados[coche]
            actualiza_grafico(tupla[0],coche,signo=-1)
    for coche, tupla in dict_vehiculos_aparcados_previos.items():
##        imprime_texto("aparcados ", str(dict_vehiculos_aparcados))
##        logging.error(dict_vehiculos_aparcados)
        if tupla and tupla[1]<time:
            del dict_vehiculos_aparcados_previos[coche]
            actualiza_grafico(tupla[0],coche,signo=-1)
            

def actualiza_grafico(seccion_vehiculo,vehiculo,signo=1,actualizar_todo=True):
    global plazas_park_free, plazas_park_total,plazas_park_full
##    imprime_texto("actualiza_grafico todo? ", str(actualizar_todo))
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


def reasigna_plaza(vehiculo, time):
    global plazas_park_free, plazas_park_total,plazas_park_full, lista_buscando_sitio, dict_secciones_centroide
    info_estatica_vehiculo=AKIVehTrackedGetStaticInf (vehiculo)
    if vehiculo in lista_buscando_sitio:
        pass
    else:
        lista_buscando_sitio.append(vehiculo)
    #buscamos una nueva seccion para el vehiculo
    seccion_destino=df_exportar.loc[vehiculo, 'Nodo destino']
    tiempo_busqueda_transcurrido=(time-df_exportar.loc[vehiculo, 'Hora Entrada'])/60
    seccion_nueva , es_parking, distancia = genera_seccion_aparcamiento(seccion_destino, vehiculo,tiempo_busqueda_transcurrido=tiempo_busqueda_transcurrido)
    if es_parking:
        df_exportar.loc[vehiculo, 'Hora aparcamiento']=time
    df_exportar.loc[vehiculo, 'Secciones intento aparcamiento'].append(int(seccion_nueva))
    centroide_aparcamiento=dict_centroide_secciones[int(seccion_nueva)]
    df_exportar.loc[vehiculo, 'Nodo aparcamiento']=int(seccion_nueva)
    df_exportar.loc[vehiculo, 'Distancia entre nodos']=distancia
    df_exportar.loc[vehiculo, 'Parking']=es_parking
    secciones_destino_vehiculo[vehiculo]=seccion_nueva #es necesario ponerle la nueva seccion de destino
    info_estatica_vehiculo.__setattr__("centroidDest",centroide_aparcamiento)
    info_estatica_vehiculo.__setattr__("width",2.02)#para pintarle de otro color
    AKIVehTrackedSetStaticInf(vehiculo,info_estatica_vehiculo)
##    AKIPrintString("buscando: "+str(lista_buscando_sitio))
    AKIPrintString("Reasignado el vehiculo: {} al centroide {}".format(str(vehiculo),str(centroide_aparcamiento)))

def genera_tiempo_aparcamiento():
    return max(tiempo_coche_aparcado_min, random.gauss(media_duracion_park, std_duracion_park))

def genera_tiempo_aparcamiento_inical():
    return random.randint(0, tiempo_coche_aparcado_max)

def _genera_tiempo_busqueda():
    return 2

def genera_tiempo_acceso(seccion_inicio, seccion_fin):
    return float(df_distancias[(df_distancias['ORIGEN']==seccion_inicio)
                               & (df_distancias['DESTINO']==seccion_fin)]
                 ['DISTANCIA'])/1.38#velocidad peaton

def asigna_tiempos_iniciales(plazas_park_full, contador=count(-1,-1)):
    global dict_vehiculos_aparcados_previos
    for seccion, numero_plazas_llenas in plazas_park_full.items():
        for plaza in range(numero_plazas_llenas):
            dict_vehiculos_aparcados_previos[next(contador)]=(seccion,genera_tiempo_aparcamiento_inical())

def genera_seccion_destino():
    return np.random.choice(lista_secciones_con_comercios,p=lista_probabilidades)

def _calcula_tarifa(ocupacion=None):
    if ocupacion is not None:
        return ocupacion*tarifa_superficie_max
    else:
        return tarifa_subterraneo
        
def _calcula_ocupacion(fila):
    if fila.secciones in plazas_park_total:
        if plazas_park_total[fila.secciones]:
            return plazas_park_full[fila.secciones] / plazas_park_total[fila.secciones]
        else:
            return np.nan
    else:
        return np.nan


def _calcula_utilidad(fila,tiempo_busqueda,
                      tbl_street=-0.056, tad_street=-0.057, tar_street=-0.030, tmax_street=0.028,
                                cte_street=-0.884,
                                tad_park=-0.057,
                                tar_park=-0.030,
                                cte_park=-1.026):
    if fila.secciones in secciones_parking_subterraneo:
        return tad_park*fila.tiempos+tar_park*_calcula_tarifa()+cte_park
    elif fila.secciones in secciones_park:
        return tbl_street*tiempo_busqueda+tad_street*fila.tiempos+tar_street*_calcula_tarifa(fila.ocupacion)+tmax_street*tiempo_coche_aparcado_max/3600+cte_street
    else:
        return np.nan


def genera_seccion_aparcamiento(seccion_destino, idveh,
                                genera_tiempo_busqueda=_genera_tiempo_busqueda,
                                calcula_ocupacion=_calcula_ocupacion,
                                Timer=Timer,
                                calcula_utilidad=_calcula_utilidad,
                                imprime_texto=imprime_texto,
                                tiempo_busqueda_transcurrido=0,
                                seccion_origen=None):
    with Timer("genera_park ") as t:
        try:
            if  pd.isna(df_exportar.loc[idveh, 'T busqueda inicial']):
                tiempo_busqueda=genera_tiempo_busqueda()
                df_exportar.loc[idveh, 'T busqueda inicial']=float(tiempo_busqueda)
                df_exportar.loc[idveh, 'T busqueda real']=float(tiempo_busqueda)
            else:
                tiempo_busqueda=df_exportar.loc[idveh, 'T busqueda inicial'] + tiempo_busqueda_transcurrido
                df_exportar.loc[idveh, 'T busqueda real']=float(tiempo_busqueda)
            calcula_utilidad_con_t_fijo=partial(calcula_utilidad,tiempo_busqueda=tiempo_busqueda)
            # hay que calcular las utilidades para todas las secciones y coger la mejor
            # para ello hay que calcular las utilidades de las secciones que tienen plazas de aparcamiento
            # por otro lado hay que calcular la que tiene parking
            # hay que añadir usuarios con info perfecta y usuarios con info historica        
            # creamos un df para hacer los calculos
            df_calculos=pd.DataFrame()
    ##        filtro_seccion_destino = (df_distancias['ORIGEN']==seccion_destino) & (~ (df_distancias['DESTINO'].isin(df_exportar.loc[idveh, 'Secciones intento aparcamiento'])))
            if seccion_origen:
                seccion_original_aparcamiento=df_exportar.loc[idveh, 'Secciones intento aparcamiento'][-1]
##                logging.error(' original: '+str(seccion_original_aparcamiento))
##                logging.error(' ORIGEN: '+str(seccion_origen))
##                logging.error(' DESTINO: '+str(seccion_destino))
                filtro_seccion_destino = ((df_distancias['ORIGEN'] == seccion_destino) &
                                         (df_distancias['DESTINO'].isin((seccion_origen, seccion_original_aparcamiento))))
##                logging.error(' FILTRO: '+str(sum(filtro_seccion_destino)))
            else:
                filtro_seccion_destino = ((df_distancias['ORIGEN']==seccion_destino) &
                (~ (df_distancias['DESTINO'].isin(df_exportar.loc[idveh, 'Secciones intento aparcamiento']))))
            
            df_calculos['secciones']=df_distancias[filtro_seccion_destino]['DESTINO']
            df_calculos['tiempos']=df_distancias[filtro_seccion_destino]['TIEMPO'] #velocidad peaton
            df_calculos['ocupacion']=df_calculos.apply(calcula_ocupacion, axis=1)
            df_calculos['utilidad']=df_calculos.apply(calcula_utilidad_con_t_fijo, axis=1)
            if seccion_origen:
                utilidad_primaria=df_calculos[df_calculos['secciones']==seccion_original_aparcamiento]['utilidad'].iloc[0]
                utilidad_calle_actual=df_calculos[df_calculos['secciones']==seccion_origen]['utilidad'].iloc[0]
                u_relativa=100-100*abs((abs(utilidad_calle_actual)-abs(utilidad_primaria))/abs(utilidad_primaria))
##                logging.error('Utilidad relativa: '+str(u_relativa))
                if u_relativa>utilidad_relativa_alternativas:
                    distancia_max_utilidad = df_calculos[df_calculos['secciones']==seccion_origen]["tiempos"].iloc[0]*5000 / 60
                    ocupacion_maxima_utilidad = df_calculos[df_calculos['secciones']==seccion_origen]["ocupacion"].iloc[0]
                    df_exportar.loc[idveh, 'Tarifa'].append(_calcula_tarifa(ocupacion_maxima_utilidad))
                    
                    df_exportar.loc[idveh, 'Utilidad relativa']=(utilidad_primaria,utilidad_calle_actual,u_relativa)                    
                    return (seccion_origen, False, distancia_max_utilidad) # No tiene en cuenta pasar por delante de un parking
                else:
                    return (None,None,None)
                
            else:
                indice_fila_maxima_utilidad = df_calculos["utilidad"].idxmax()
                imprime_texto(str(indice_fila_maxima_utilidad))
                fila_maxima_utilidad = df_calculos.loc[indice_fila_maxima_utilidad]
                seccion_maxima_utilidad = fila_maxima_utilidad["secciones"]
                distancia_max_utilidad = fila_maxima_utilidad["tiempos"]*5000 / 60
                ocupacion_maxima_utilidad = fila_maxima_utilidad["ocupacion"]
##                logging.error(' quiere llegar a  : '+str(seccion_destino))
##                logging.error(' va a: '+str(seccion_maxima_utilidad))
                seccion_subterranea = True if  fila_maxima_utilidad.secciones in secciones_parking_subterraneo else False
                df_exportar.loc[idveh, 'Tarifa'].append(_calcula_tarifa(ocupacion_maxima_utilidad))
                return (seccion_maxima_utilidad,seccion_subterranea, distancia_max_utilidad)
        except Exception as e:
            logging.error(traceback.format_exc())
