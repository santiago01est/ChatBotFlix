import nltk
from nltk.tokenize import word_tokenize
import time
import requests
import os
import telebot
import TMDB
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

nltk.download('punkt')
# Función de manejo de mensajes del usuario
def bot_mensajes_bienvenida(message):
    # Obtener el mensaje del usuario
    texto_usuario = message.text

    # Tokenizar el mensaje del usuario
    tokens = nltk.word_tokenize(texto_usuario.lower())

    # Realizar procesamiento adicional con los tokens
    # (por ejemplo, identificar patrones o realizar acciones específicas)
    # Generar respuesta del chatbot
    if "bien" in tokens:
        respuesta = "Me alegra que estes bien \n ¿Qué película quieres buscar?"
        return respuesta
    # Generar respuesta del chatbot
    if "hola" in tokens:
        respuesta = "¡Hola! ¿Cómo estás?"
        return respuesta
    elif "como" in tokens and "estas" in tokens:
        respuesta = "Estoy bien, ¡gracias por preguntar! \n ¿Qué película quieres buscar?"
        return respuesta
    elif "como" in tokens and "estado" in tokens:
        respuesta = "He estado ocupado atendiendo a los usuarios. ¿En qué puedo ayudarte?"
        return respuesta
    else:
        respuesta = "otro"
        return respuesta

# Función para analizar el mensaje del 
# usuario para extraer preferencias de gustos
# de peliculas o generos cinematograficos
def analizador_mensaje_preferences(message):
    # Tokenizar el mensaje en palabras
    palabras = word_tokenize(message)
    # Lista de géneros de películas
    generos_peliculas = ["acción", "aventura", "ciencia ficción", "comedia", "drama", "romance", "terror", "suspenso"]
    # Lista para guardar los géneros de películas encontrados
    generos_encontrados = []

    # Iterar sobre las palabras del mensaje y verificar si están en la lista de géneros de películas
    for palabra in palabras:
        if palabra.lower() in generos_peliculas:
            generos_encontrados.append(palabra.lower())

    # Eliminar duplicados y mostrar los géneros de películas encontrados
    generos_encontrados = list(set(generos_encontrados))
    return generos_encontrados


def buscador_pelicula(message,bot):
    url_photo,resul_busqueda=TMDB.buscarPelicula(message.text)
    if url_photo:
        bot.send_photo(message.chat.id, photo=url_photo, caption='Poster')
    else:
        print('Poster No disponible.')
    bot.send_message(message.chat.id, resul_busqueda)
            #print(url_poster)


def analizador_recomendacion(message,bot):

    # Tokenizar el mensaje del usuario
    tokens = nltk.word_tokenize(message.text.lower())

    # Realizar procesamiento adicional con los tokens
    # (por ejemplo, identificar patrones o realizar acciones específicas)
    # Generar respuesta del chatbot
    if ("recomendar" in tokens or "recomiendas" in tokens or "recomendación" in tokens or "recomendacion" in tokens or "recomiendame" in tokens) and ("unas" in tokens or "varias" in tokens or "algunas" in tokens):
        # Obtener una instancia de la colección y el documento específico
        coleccion = firestore.client().collection('usuarios')
        documento = coleccion.document(f"{message.chat.id}")

        # Obtener el valor del campo específico del documento
        campo_valor = documento.get().get('peliculas_fav')
        nombre_pelicula=campo_valor[0]
        lista_recomendacion=TMDB.buscar_recomendacion_pelicula(nombre_pelicula, 3)
        bot.send_message(message.chat.id, "Claro!, 🍿 Aquí están algunas películas que te pueden gustar:")
        time.sleep(1) 
        # recorrer array de las recomendaciones para enviarlas al usuario
        for pelicula in lista_recomendacion:
            if pelicula["poster_path"]:
                url_poster = "https://image.tmdb.org/t/p/w500"+pelicula["poster_path"]
                bot.send_photo(message.chat.id, photo=url_poster, caption='Poster')
            else:
                print('Poster No disponible.')
            titulo = pelicula["title"]
            sinopsis = pelicula["overview"]
            informacion = f"Título: {titulo}\nSinopsis: {sinopsis}"
            bot.send_message(message.chat.id, informacion)
            time.sleep(3) 
            bot.send_message(message.chat.id, "También puedes escribir el nombre de una película y te buscaré información sobre ella 😊")
    elif ("recomendar" in tokens or "recomiendas" in tokens or "recomendación" in tokens or "recomendacion" in tokens or "recomiendame" in tokens) and ("una" in tokens or "alguna" in tokens):
        # Obtener una instancia de la colección y el documento específico
        coleccion = firestore.client().collection('usuarios')
        documento = coleccion.document(f"{message.chat.id}")

        # Obtener el valor del campo específico del documento
        campo_valor = documento.get().get('peliculas_fav')
        nombre_pelicula=campo_valor[0]
        lista_recomendacion=TMDB.buscar_recomendacion_pelicula(nombre_pelicula,1)
        mensaje=f"Claro!, 🍿 Como te gustó {nombre_pelicula} te puede gustar:"
        bot.send_message(message.chat.id, mensaje)
        time.sleep(1) 
        # recorrer array de las recomendaciones para enviarlas al usuario
        for pelicula in lista_recomendacion:
            if pelicula["poster_path"]:
                url_poster = "https://image.tmdb.org/t/p/w500"+pelicula["poster_path"]
                bot.send_photo(message.chat.id, photo=url_poster, caption='Poster')
            else:
                print('Poster No disponible.')
            titulo = pelicula["title"]
            sinopsis = pelicula["overview"]
            informacion = f"Título: {titulo}\nSinopsis: {sinopsis}"
            bot.send_message(message.chat.id, informacion)
            time.sleep(3) 
            bot.send_message(message.chat.id, "También puedes escribir el nombre de una película y te buscaré información sobre ella 😊")

    # Generar respuesta del chatbot
    else:
        buscador_pelicula(message,bot)

def analizador_tipo_mensaje(message,bot):
    mensaje_respuesta= bot_mensajes_bienvenida(message)
    if mensaje_respuesta.startswith("otro"):
        analizador_recomendacion(message,bot)
    else:
        bot.send_message(message.chat.id, mensaje_respuesta)

def actualizar_preferencias_usuario(chat_id,name_user,array_respuestas):
    # Crear un objeto usuario
    generos_fav_user=[]
    peliculas_fav_user=[]

    for i in range(len(array_respuestas)):
    # Verificar si estamos en la posición 1 del array
        if i == 0:
            peliculas_fav_user.append(array_respuestas[i])
        elif i==1:
            generos_fav_user=analizador_mensaje_preferences(array_respuestas[i])

    usuario = {
        'idChat': chat_id,
        'nombre': name_user,
        'generos_fav':generos_fav_user,
        'peliculas_fav':peliculas_fav_user
    }
    # Obtener una referencia a la colección 'usuarios' en Firebase Cloud Firestore
    db = firestore.client()
    usuarios_ref = db.collection('usuarios')

    # Añadir el objeto de tipo usuario a la colección 'usuarios'
    usuarios_ref.document(f"{chat_id}").set(usuario)

## enviar a db