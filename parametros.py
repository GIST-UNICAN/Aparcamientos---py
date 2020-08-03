# -*- coding: cp1252 -*-
### RUTAS (mantener la r en las que la llevan)

# paquetes python 2.7
python_site_packages="C:\\Python27\\lib\\site-packages"

# carpeta aimsum (poner la carpeta donde este el archivo aapi generalmente Program Files\Aimsun\Aimsun Next 8.3\programming\Aimsun Next API\AAPIPython\Micro)
aimsun_micro_folder='C:\Program Files\Aimsun\Aimsun Next 8.3\programming\Aimsun Next API\AAPIPython\Micro'

# excel datos de entrada
excel_parking_slots_sections=r"D:\Documentos\GitHub\Aparcamientos---py\plazas_seccion.xlsx"
excel_distance_between_sections=r"D:\Documentos\GitHub\Aparcamientos---py\distancias.xls"

# logs (descomentar los que se usen)
# time_log_file=r"D:\Documentos\GitHub\Aparcamientos---py\log_time.txt"
# log_file=r"D:\Documentos\GitHub\Aparcamientos---py\log.txt"
# log_aimsun_file=r"D:\Documentos\GitHub\Aparcamientos---py\logaimsun.log"

# carpeta resultados
results_export_path = r"D:\Onedrive\OneDrive - UNICAN\Recordar GIST - VARIOS\Aparcamientos\resultados_temporales"


### GEOMETRY
dic_parking_centroid_section= {1276: 1331, 1294: 1333}
sections_parking= (1294, 1276)
centroids_parking=(
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


### MODEL INPUTS

parking_stop_time = 22  #seconds

# tiempo mimino que un coche puede estar en una plaza
min_parking_time = 5 * 60 #seconds
# tiempo maximo que un coche puede estar en una plaza
max_parking_time = 120 * 60 #seconds

# para el modelo de distribucion de tiempo de aparcamiento
avg_parking_duration = 60 * 60 #seconds
std_parking_duration = 60 * 60 #seconds

initial_ocupancy = 95 #%

# para el tiempo de busqueda de la funcion de utilidad (no informados)
min_search_time = 2 #minutes
std_search_time = 4.87 #minutes
avg_search_time = 6.58 #minutes
min_search_time_parking= 1.54 #minutes

# para el tiempo de acceso a destino de la funcion de utilidad
walking_time_to_destination = 120 #seconds

# tarifas, en el caso de estaticas poner siempre la misma (mantener el formato de tupla)
on_street_rates = (0.5,1,1.75) #(1,2,3.5) #euros/hour
on_street_standart_rate_not_informed = 1.45/2 #euros/hour
ocupation_ranges = (60,80,100) #%
time_rates_update = 15 #minutes
of_street_rate = 1.60#2.75 #euros/hour

# utilidad que define si aparcan al encontrase un sitio mientras buscan
utilidad_relativa_alternativas = 90 #%

# tipos de usuarios
percentage_informed=50 #%

# parametros exportacion
time_occupancy_saved=60 #seconds
