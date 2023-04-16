#pip install requests
#pip install nltk
#pip install bs4
#pip install pyTelegramBotAPI
import nltk
import time
import requests
import os
import telebot
from telebot import types
import small_talk
import TMDB
import PreferencesUser
from collections import deque
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


nltk.download('punkt')
# Configurar las credenciales de Firebase
cred = credentials.Certificate('C:/Users/ACER/Documents/2023/IA/Proyecto/chatbotflix-b363b-firebase-adminsdk-ribdy-cc08473f49.json')
firebase_admin.initialize_app(cred)



## Funcion principal al iniciar el Chat, envia un mensaje de bienvenida
bot = telebot.TeleBot("6039561957:AAFkTNwVy-w1H6u_GEhXoQFyCD1Ay2KCU2o", parse_mode=None) 
indice_pregunta = 0
@bot.message_handler(commands=["start"])
def cmd_start(message):

    bot.reply_to(message, f"Hola {message.from_user.first_name} ¡Bienvenido/a, seré tu asistente de cine y series! 🍿 Soy tu chatbot 🤖 personalizado para ayudarte con tus preguntas y consultas relacionadas con películas y series. Te proporcionarte información, recomendaciones y responder a tus preguntas sobre tus películas y series favoritas.")
    print( f"Hola {message.from_user.first_name}")

    # Enviar el mensaje con las opciones de respuesta
    hacer_pregunta(message.chat.id)



'''

@bot.message_handler(content_types=["text"])
def bot_mensajes_texto(message):
    print( f"Hola {message.from_user.first_name}")
    if message.text.startswith("/"):
        bot.send_message(message.chat.id, "Comando no disponible")
    else: 
        small_talk.analizador_mensaje(message,bot)
'''

def hacer_pregunta(chat_id):
    # Crear opciones de respuesta
    opciones = ['Si', ' No']
    # Crear un objeto InlineKeyboardMarkup para mostrar las opciones como botones
    markup = types.InlineKeyboardMarkup()
    # Crear los botones para cada opción
    for opcion in opciones:
        button = types.InlineKeyboardButton(text=opcion, callback_data=opcion)
        markup.add(button)

    # Enviar el mensaje con la pregunta y las opciones de respuesta
    bot.send_message(chat_id, 'Quisiera conocerte para poder brindarte repuestas personalizadas y más precisas \n\nEstás de acuerdo con eso?', reply_markup=markup)

# Array de preguntas
preguntas = ["Pregunta 1: ¿Cuál es tu Película Favoria?", "Pregunta 2: ¿Que géneros de Películas te gustan más?", "Pregunta 3: ¿Cuál fue la última Película que has visto?", "Pregunta 4: ¿Cuál Película me recomendarías?"]
respuestas = {}  # para almacenar las respuestas de los usuarios
cola_preguntas = deque(preguntas)  # Cola para gestionar las preguntas
preguntas_iniciales=True
array_respuestas=[]

# Función para enviar preguntas y obtener respuestas
def obtener_respuestas(chat_id, name_user):
    if not cola_preguntas:
        # Todas las preguntas han sido enviadas
        bot.send_message(chat_id=chat_id, text= "¡Gracias por responder a todas las preguntas!")
        global preguntas_iniciales
        preguntas_iniciales=False
        print(array_respuestas)
        small_talk.actualizar_preferencias_usuario(chat_id,name_user,array_respuestas)
        return

    pregunta = cola_preguntas.popleft()
    # Enviar pregunta al usuario

    bot.send_message(chat_id=chat_id, text= pregunta)

    while True:
        if chat_id in respuestas:
            respuesta = respuestas[chat_id]
            array_respuestas.append(respuesta)
            del respuestas[chat_id]
            print("Respuesta del usuario:", respuesta)
            '''
            if num_pregunta==1:
                small_talk.actualizar_preferencias_usuario(chat_id,name_user,text_user,"pelicula_fav")
            elif num_pregunta==2:
                small_talk.actualizar_preferencias_usuario(chat_id,name_user,text_user,"genero_fav")
            '''
        
            break
        time.sleep(1)  # Esperar 1 segundo antes de comprobar nuevamente

# Manejador de eventos para respuestas de los usuarios
@bot.message_handler(func=lambda message: True)
def handle_user_response(message):
    if preguntas_iniciales:
        chat_id = message.chat.id
        respuesta = message.text
        respuestas[chat_id] = respuesta
        #print(message.text)
        # Llamar a la función recursivamente para la siguiente pregunta
        obtener_respuestas(message.chat.id,message.from_user.first_name)
    else:
        print( f"Hola {message.from_user.first_name}")
        if message.text.startswith("/"):
            bot.send_message(message.chat.id, "Comando no disponible")
        else: 
            small_talk.analizador_tipo_mensaje(message,bot)
    
#función para manejar las respuestas del usuario
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    # Obtener la opción seleccionada por el usuario
    opcion_seleccionada = call.data

    # Procesar la opción seleccionada
    if opcion_seleccionada == 'Si':
        bot.send_message(call.message.chat.id,'¡Genial! Empecemos')
        obtener_respuestas(call.message.chat.id,call.message.from_user.first_name)

    elif opcion_seleccionada == 'No':
        bot.send_message(call.message.chat.id,'Entiendo. Si cambias de opinión, estaré aquí para ayudarte en cualquier momento.')

    # Responder al callback query para cerrar el botón presionado
    bot.answer_callback_query(call.id)

# MAIN #

if __name__=='__main__':
    print('Iniciando bot')
    bot.infinity_polling()
    print('fin')
