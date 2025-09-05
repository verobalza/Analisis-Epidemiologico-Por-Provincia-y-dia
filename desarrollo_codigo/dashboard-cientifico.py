import csv
from collections import defaultdict
from datetime import datetime
from dateutil import parser
import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns



#definimos la agrupamos por dia y por provincia, luego mostramos el acumulado de cada campo que nos piden luego la utilizaremos 
datos_agrupados = defaultdict(lambda:defaultdict(lambda:{
    'num_def':0,
    'new_cases':0,
    'num_hosp': 0,
    'num_uci':0
}))

#Abrimos el archivo con with open para asegurarnos de que se cerrara correctamente 
with open ('recursos_proyectos.csv', newline="", encoding="latin-1") as archivo:

    #dictReader lo usamos para leer el archivo como un diccionario (DictReader) y imprimimos las columnas para constatar que escribimos bien todo en datos_agrupados
    lector = csv.DictReader(archivo, delimiter=';') 
    print("columnas:", lector.fieldnames)

    #Recorremos el archivo 
    for datos in lector:

        #controlamos con try posibles errores
        try:
           
           #Utilizamos parse.parse que es una herramienta de dateutil que detecta el formato y convierte la fecha string en este caso en datetime y luego le decimos que ponga de primero el dia con dayfirst

            fecha = parser.parse(datos['date'], dayfirst=True)
        
            #Convertimos los dias de la semana en español
            dia_español= {
            'Monday':'Lunes',
            'Tuesday':'Martes',
            'Wednesday':'Miércoles',
            'Thursday':'Jueves',
            'Friday':'Viernes',
            'Saturday':'Sábado',
            'Sunday':'Domingo'

            }
            #sacamos el dia en formato texto con strftime e indicando con %A
            dia_semana = dia_español[fecha.strftime('%A')]
           

            #provincia 
            provincia = datos['province'].strip()


                                            #   A G R U P A C I O N 

            datos_agrupados[dia_semana][provincia]['num_def'] += int(datos.get('num_def',0)or 0)
            datos_agrupados[dia_semana][provincia]['new_cases'] += int(datos.get('new_cases',0)or 0)
            datos_agrupados[dia_semana][provincia]['num_hosp'] += int(datos.get('num_hosp',0)or 0)
            datos_agrupados[dia_semana][provincia]['num_uci'] += int(datos.get('num_uci',0)or 0)
        
        except Exception as e:
            print(f" Error en fila con provincia '{datos.get('province', '???')}' y fecha '{datos.get('date', '???')}' --> {e}")




                                
                                
                                #GUARDAMOS EN JSON EN UN  archivo.txt

                                #convertimos defauldict a dict normal ya que json no entiende el defaultdict
datos_convertidos = { dia: dict(provincias) for dia, provincias in datos_agrupados.items()}

with open ('resultados_dias_provincias.txt', 'w', encoding='UTF-8') as salida_json:
    json.dump(datos_convertidos, salida_json, indent=4, ensure_ascii=False)


                                    #COMPROBAMOS QUE ESTE OK EL JSON

with open ('resultados_dias_provincias.txt', 'r',encoding='utf-8') as ar_json:
    datos = json.load(ar_json)

for dia, provincias in datos.items():
 print(f' {dia}: {len(provincias)} provincias registradas')



#comprobamos el numero de provincias por cada dia 
print("\n Días detectados:")
for dia in datos_agrupados:
    print(f"- '{dia}'  --> {len(datos_agrupados[dia])} provincias")




                                                 #IMPRIMIMOS AGRUPACION Y ASI LO VEMOS POR CONSOLA 

print('Resultados agrupados por dia y provincia: ')   

contador=0
for dia, provincias in datos_agrupados.items():
    print(f'\nDia: {dia}\n')
    for provincia, valores in provincias.items():
        print(f'Provincia {provincia}')
        print(f'Número de difunsiones: {valores['num_def']}')
        print(f'Nuevos Casos: {valores['new_cases']}')
        print(f'Número de Hospitalizados: {valores['num_hosp']}')
        print(f'Número de pacientes en UCI: {valores['num_uci']}')
        print()


#Aclaracion: agregue un input en donde presionando enter puedes seguir cargando los print, y asi me sale todos los print por la consola 
        contador += 1
        if contador % 50 == 0:
            input("Presiona Enter para ver más...")



                                             #G R A F I C O S     Y     M E N U 


                        #cargamos el json para luego convertirlo en dataframe
with open("resultados_dias_provincias.txt", "r",encoding='utf-8') as resultados:
    resultados_json= json.load(resultados)

                        #convertimos en dataframe y recorremos para obtener resultados

data_filas=[]

for dia, provincia in resultados_json.items():
    for provincia, valores in provincia.items():
        fila={
            'Día': dia,
            'Provincia':provincia,
            'Defunciones':valores['num_def'],
            'Casos Nuevos':valores['new_cases'],
            'Hospitalizados': valores['num_hosp'],
            'UCI':valores['num_uci']
        }

        data_filas.append(fila)
datafra_datos = pd.DataFrame(data_filas)


                                                    # funcion para  graficar por provincias 


def graficar(columna, eje_x):
        plt.figure(figsize=(15, 10))

        #orden 
        if eje_x == 'Provincia':
            orden = sorted(datafra_datos['Provincia'].unique()) #Alfabéticamente
        elif eje_x == 'Dia':
            orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'] #Semanalmente
        else:
            orden= None #Por si acaso
        
        #creamos grafico tipo barra definimos ejes x, y
        sns.barplot(data=datafra_datos, x=eje_x, y=columna, estimator=sum, ci=None, order= orden)


        #personalizamos grafico
        plt.title(f'Grafico de {columna} por {eje_x}')
        plt.ylabel(columna)
        plt.xlabel(eje_x)
        plt.xticks(rotation=90)

        #ajustamos 
        plt.tight_layout()
        plt.show()



def graficar_chesse(columna, top_n=20):
    #agrupamos por provincia
    resultado_provincias= datafra_datos.groupby('Provincia')[columna].sum()

    #separamos un top de provincias para que veamos el grafico con mas claridad y podamos leerlo mejor 
    top_provincias = resultado_provincias[:top_n]
    otras_provincias =resultado_provincias[top_n:].sum()
    top_provincias['Otros'] = otras_provincias


    plt.close('all')

    #peronalizamos grafico
    plt.figure(figsize=(16,11))
    plt.pie(top_provincias, autopct='1%.1f%%',startangle=140, textprops={'fontsize': 8} )
    plt.legend(top_provincias.index, title="Provincias", bbox_to_anchor=(1, 0.5), loc="center left")
    plt.title(f'Distribucion de {columna} por provincias')
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

    #provincia maximo y minimo 
    maximo_provincia= resultado_provincias.idxmax()
    minimo_provincia = resultado_provincias.idxmin()

    print(f' Provincia con mas {columna}: {maximo_provincia} ({resultado_provincias[maximo_provincia]})')
    print(f' Provincia con mas {columna}: {minimo_provincia} ({resultado_provincias[minimo_provincia]})')






    



                                                #Menu interactivo

while True:
        print('¿Como quieres ver los datos?')
        print('1. Agrupados por días')
        print('2. Agrupados por provincias')
        print('3. Salir')

        datos = input('Elige una opcion: ')

        if datos in ['1', '2']:
            eje = 'Día' if datos == '1' else 'Provincia'


            while True:
                print("Menu de graficos")
                print('1. Defunciones')
                print('2. Casos nuevos')
                print('3. Hospitalizados')
                print('4. Pacientes en UCI')
                print('5. Salir')   

                opcion = input('Elige el grafico que quieras ver: ')  

                grafico = {
                    '1': 'Defunciones',
                    '2':'Casos Nuevos',
                    '3': 'Hospitalizados',
                    '4':'UCI'
                    }

                if opcion in grafico:
                    graficar(grafico[opcion], eje)
                elif opcion == 5:
                    print('¡Hasta luego!')
                    break
                else:
                    print('Opcion incorrecta. Elige una opcion del 1 al 5.')

        elif datos == '3':
            print('Hasta luego!!')
            break
        else:
            print('Opcion invalida elige una opcion del 1 al 3.')   


            #Menu infinito grafico de queso

#nota: sale subrayado porque no se accede a este menu mientras el menu de graficos por barras no este cerrado  

while True:
    print("\n Menú de gráficas tipo queso agrupado por provincias")
    print("1. Defunciones")
    print("2. Casos Nuevos")
    print("3. Hospitalizados")
    print("4. Pacientes en  UCI")
    print("5. Salir")

    opcion = input("Elige una opción: ")

    metricas = {
        "1": "Defunciones",
        "2": "Casos Nuevos",
        "3": "Hospitalizados",
        "4": "UCI"
    }

    if opcion in metricas:
        graficar_chesse(metricas[opcion])
    elif opcion == "5":
        print(" ¡Hasta luego!")
        break
    else:
        print(" Opción inválida. Elige del 1 al 5.")
 


                    



                
            
































