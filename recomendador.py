# importamos las librerias necesarias para llevara  cabo el programa
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import re, unicodedata
from IPython.display import display

def eleccion_filtro(filtros): # defino la función que permite elegir los filtros que vamos a aplicar a la búsqueda
    filtros_elegidos = []
    eleccion = ''
    añadir = True
    for filtro in filtros: # mostramos al usuario los posibles filtros aplicables
        print(filtro)
    while añadir: # creamos un bucle para añadir todos los filtros que quiera el usuario
        eleccion = ''
        seguir = ''
        while eleccion not in filtros: # el ususario debe introducir un filtro disponible
            if filtros_elegidos == []:
                eleccion = input('¿Qué filtro desea aplicar a la búsqueda?:  ')
            else:
                eleccion = input('¿Qué filtro desea añadir?:  ')
        if eleccion not in filtros_elegidos: # si el filtro no se había añadido previamente, lo añadimos
            filtros_elegidos.append(eleccion)
            print('Filtro añadido correctamente')
        else:
            print('El filtro seleccionado ya se había añadido')
        while seguir not in ['yes', 'no']: # preguntamos al usuario si quiere seguir introduciendo filtros
            seguir = input('¿Desea añadir más filtros?[yes/no]: ').lower()
        if seguir == 'no': # si no quiere añadir más filtros, salimos del bucle 
            añadir = False
    return filtros_elegidos # devolvemos los filtros elegidos por el usuario

def filtrar_dataframe(df, filtros_elegidos): # creamos la función que va a filtrar el dataframe 
    filtros_nombres = {}
    df_final = pd.DataFrame(columns = df.columns) # creamos un dataframe que va a contener la información ya filtrada
    for i in range(len(filtros_elegidos)-1,-1,-1): # comenzamos filtrando desde el último hasta el primer filtro
        if filtros_elegidos[i] == 'name': # si filtramos por el nombre de una canción preguntamos por el nombre de la canción
            entrada_sinfiltrar = input('\nIntroduce el nombre de la canción que desea escuchar: ')  
            # quitamos las tildes para no tenerlas en cuenta a la hora de comparar con la información del dataframe
            entrada_sintildes = unicodedata.normalize('NFKD', entrada_sinfiltrar).encode('ASCII','ignore') 
            entrada = re.compile(entrada_sintildes, re.IGNORECASE) # ignoramos las mayúsculas y las minúsculas
        
        elif filtros_elegidos[i] == 'artists': # si filtramos por el nombre del artista preguntamos al usuario por dicho nombre
            entrada_sinfiltrar = input('\nIntroduce el nombre del artista de la canción que desea escuchar: ')
            # quitamos las tildes para no tenerlas en cuenta a la hora de comparar con la información del dataframe
            entrada_sintildes = unicodedata.normalize('NFKD', entrada_sinfiltrar).encode('ASCII','ignore')
            entrada = re.compile(entrada_sintildes, re.IGNORECASE) # ignoramos las mayúsculas y las minúsculas
            
        elif filtros_elegidos[i] != 'name' and filtros_elegidos[i] != 'artists': 
            # si no filtramos ni por el nombre de la canción ni por el nombre del artista, entonces ordenamos el dataframe
            # por orden descendente en la columna indicada
            df = df.sort_values(by = filtros_elegidos[i], ascending = False)
            df_final = df.reset_index() # reseteamos los índices del dataframe y almacenamos los valores en el nuevo orden en nuestro df final
            
        if filtros_elegidos[i] in ['name', 'artists']: #si el filtro es el nombre de la canción o el nombre del artista
            filtros_nombres[filtros_elegidos[i]]= entrada  # vamos a almacenar la entrada indicada por el usuario en un diccionario
            if not df_final.empty: # si el dataframe final no está vacio 
                df = df_final # almacenamos su informacion como el df normal para poder actualizar el final con el siguiente filtro
                df_final = pd.DataFrame(columns = df.columns) # creo el nuevo df final al que le vamos a aplicar el siguiente filtro
            for j in range(len(df)): # para cada fila del dataframe
                # quitamos las tildes del dataframe por cada entrada a comparar con el nombre indicado por el usuario
                comparar = unicodedata.normalize('NFKD',df[filtros_elegidos[i]][j]).encode('ASCII','ignore')
                if re.search(entrada, comparar): # si la entrada del usuario coincide con el valor del dataframe en la columna del filtro aplicado
                    df_final = df_final.append(df.iloc[j], ignore_index = True) # añadimos esa fila en nuestro dataframe final
    return df_final, filtros_nombres # devolvemos nuestro conjunto de datos filtrado y el nombre de las entradas del usuario 

def recomendar(df, filtros, filtros_nombres): # creamos la función que va a buscar más recomendaciones
    df_recomendar = pd.DataFrame(columns = df.columns) # creo el df con las recomendaciones extras
    if 'name' in filtros and 'artists' in filtros: # si el usuario está filtrando por nombre y por artista
            for i in range(len(df)): # entonces vamos a buscar más canciones del mismo artista, sin repetir la canción indicada
                if re.search(filtros_nombres['artists'], df['artists'][i]) and filtros_nombres['name'] != df['name'][i]:
                    df_recomendar = df_recomendar.append(df.iloc[i], ignore_index = True)
    
    return df_recomendar # devuelvo el conjunto de recomendaciones

def imprimir_recomendaciones(df_filtrado, df_recomendaciones): # creamos la función que va a imprimir las recomendaciones
    numero = 0
    seguir_enseñando = True
    while seguir_enseñando: # mientras el usuario quiera que siga enseñando recomendaciones
        respuesta = ''
        if df_filtrado[numero:numero+10].empty and df_recomendaciones.empty: # si no tenemos más recomendaciones se lo hacemos saber al ususario
            print('No hay mas recomendaciones disponibles') 
            respuesta = 'no'
        elif df_filtrado[numero:numero+10].empty and not df_recomendaciones.empty:
            # si no tengo más recomendaciones con los filtros indicados pero hay recomendaciones extras del mismo artista que el indicado por el 
            # usuario, pregunto si quiere que se las mostremos 
            print('No se han encontrado recomendaciones con todos los filtros indicados. Otras recomendaciones: ')
            enseñar = True
            num = 0
            while enseñar:
                seguir = ''
                if df_recomendaciones[num:num+10].empty: # si no quedan recomendaciones en las recomendaciones extras, se lo hacemos saber al usuario
                    print('No hay más recomendaciones disponibles')
                else: # si quedan recomendaciones extras imprimimos las 10 siguientes
                    display(df_recomendaciones[num:num+10])
                
                while seguir not in ['yes', 'no']: # preguntamos si el usuario sigue queriendo recomendaciones extras
                    seguir = input('¿Quieres más recomendaciones?[yes/no]: ')
                    seguir.lower()
                if seguir == 'no': # si no quiere más reconmendaciones se finaliza el bucle
                    enseñar = False
                else: # si sigue queriendo recomendaciones, sumamos diez al contador para luego imprimir las 10 siguientes
                    num += 10
            respuesta = 'no' 
        else: # si sigue habiendo recomendaciones en nuestro df, imprimirmos las 10 siguientes
            display(df_filtrado[numero:numero+10])
        while respuesta not in ['yes','no']: # preguntamos al usuario si sigue queriendo más recomendaciones con los filtros que hemos aplicados
            respuesta = input('¿Quieres más recomendaciones? [yes/no] ')
            respuesta.lower()
        if respuesta == 'no': # si la respuesta es negativa, finalizamos el bucle y por lo tanto, la función
            seguir_enseñando = False
        else: # si la respuesta es afirmativa sumo 10 al contador para luego imprimir las 10 siguientes recomendaciones
            numero += 10

# como este recomedador sigue una estructura de ETL, definimos las tres funciones:
def extract(): #defimimos la función que extrae los datos
    df_spotify = pd.read_csv('tracks.csv') # convertimos el csv con todos los datos en un dataframe
    return df_spotify

def transform(df_spotify): # definimos la función que transforma los datos de nuestro conjunto de datos
    df_spotify_trans = df_spotify.fillna('None') # rellenamos todos los datos vacios con None
    df_filtrado, filtros_nombres = filtrar_dataframe(df_spotify_trans, filtros_elegidos) 
    # llamamos a filtrar el df con los filtros indicados por el usuario
    df_recomendaciones = recomendar(df_spotify_trans, filtros_elegidos, filtros_nombres) # creamos más recomendaciones
    return df_filtrado, df_recomendaciones
    
def load(df_filtrado, df_recomendaciones): # definimos la función que carga los datos pedidos por el usuario
    imprimir_recomendaciones(df_filtrado, df_recomendaciones) # imprimimos por pantalla todas las recomendaciones

if __name__ == "__main__":
    # como vamos a seguir una estructura de ETL
    df_spotify = extract() # llamamos a extract
    filtros = ['name','artists','popularity','explicit','energy','danceability'] # definimos los filtros posibles
    filtros_elegidos = eleccion_filtro(filtros) # pedimos al usuario que introduzca los filtros
    df_filtrado, df_recomendaciones = transform(df_spotify) # transformamos el df
    load(df_filtrado, df_recomendaciones) # cargamos los datos