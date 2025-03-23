import os
import time
import sys
import tempfile
import threading
import wave
import pyaudio
import speech_recognition as sr
from gtts import gTTS
import pygame
import requests
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_mistralai import ChatMistralAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Charger les variables depuis .env
load_dotenv(override=True)

# Récupérer les clés API
mistral_api_key = os.getenv("MISTRAL_API_KEY")
hotel_api_token = os.getenv("HOTEL_API_TOKEN")
# Vous aurez peut-être besoin d'une clé API pour Whisper si vous utilisez l'API OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")

# Configuration audio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5  # Durée d'enregistrement par défaut

# LLM Configuration
model = ChatMistralAI(
    model="mistral-small-latest",
    api_key=mistral_api_key,  # Assurez-vous que la clé API est passée correctement
    temperature=0.7,
    max_retries=5
)

# Initialiser le recognizer pour la reconnaissance vocale
recognizer = sr.Recognizer()

def print_stream(stream):
    reponse = ""
    for s in stream:
        message = s.get("messages", [])[-1] if s.get("messages") else None
        if isinstance(message, (HumanMessage, AIMessage)):
            reponse = message.content
    return reponse

def api_ask_agent(user_message: str, conversation_history=None, system_instruction=None):
    """
    Interroge l'agent avec l'historique de conversation pour maintenir le contexte
    """
    # Si pas d'historique fourni, initialiser avec une liste vide
    if conversation_history is None:
        conversation_history = []
    
    # Préparation des messages avec l'historique complet
    messages = conversation_history.copy()
    
    # Ajouter l'instruction système si elle est fournie
    if system_instruction:
        if not any(role == "system" for role, _ in messages):
            messages.insert(0, ("system", system_instruction))
    
    # Ajouter le message de l'utilisateur
    messages.append(("user", user_message))
    
    inputs = {"messages": messages}
    reponse = ""
    reussi = False
    iteration = 0
    max_iteration = 5

    
    while (not reussi and iteration < max_iteration):
        try:
            # Approche directe si le streaming ne fonctionne pas
            if iteration > 2:
                # Essayer une approche sans streaming après quelques échecs
                output = graph(inputs)
                last_message = output.get("messages", [])[-1] if output.get("messages") else None
                if isinstance(last_message, (HumanMessage, AIMessage)):
                    reponse = last_message.content
                reussi = True
            else:
                # Essayer avec streaming d'abord
                stream_result = graph.stream(inputs, stream_mode="values")
                reponse = print_stream(stream_result)
                reussi = True
        except Exception as e:
            print(f"Erreur (tentative {iteration+1}): {str(e)}")
            iteration += 1
            time.sleep(1)
    
    if not reussi:
        return "Désolé, je n'ai pas pu traiter votre demande. Veuillez réessayer."
    
    return reponse

# Fonctions pour l'enregistrement audio
def record_audio(output_file, duration=None):
    """Enregistre l'audio du microphone et sauvegarde dans un fichier"""
    p = pyaudio.PyAudio()
    
    print("Appuyez sur Entrée pour commencer l'enregistrement...")
    input()
    
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    print("Enregistrement en cours... Appuyez sur Entrée pour arrêter.")
    
    frames = []
    recording = True
    
    def stop_recording():
        nonlocal recording
        input()  # Attendre que l'utilisateur appuie sur Entrée
        recording = False
    
    # Démarrer un thread pour attendre l'entrée utilisateur
    stop_thread = threading.Thread(target=stop_recording)
    stop_thread.daemon = True
    stop_thread.start()
    
    # Enregistrer jusqu'à ce que l'utilisateur arrête ou que la durée soit atteinte
    start_time = time.time()
    while recording:
        if duration and (time.time() - start_time > duration):
            break
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("Enregistrement terminé.")
    
    # Arrêter le stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Enregistrer l'audio dans un fichier WAV
    wf = wave.open(output_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return output_file

def speech_to_text(audio_file):
    """Convertit l'audio en texte en utilisant Whisper"""
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            
            # Option 1: Utiliser Google Speech Recognition comme alternative à Whisper
            try:
                text = recognizer.recognize_google(audio_data, language="fr-FR")
                return text
            except:
                # Option 2: Si Google Speech échoue aussi ou si vous préférez utiliser Whisper API
                if openai_api_key:
                    text = recognizer.recognize_whisper_api(audio_data, api_key=openai_api_key)
                    return text
                else:
                    raise Exception("Ni Google Speech ni Whisper API ne sont disponibles")
                    
    except Exception as e:
        print(f"Erreur lors de la reconnaissance vocale: {e}")
        return None

def text_to_speech(text, output_file):
    """Convertit le texte en audio en utilisant gTTS"""
    try:
        tts = gTTS(text=text, lang='fr', slow=False)
        tts.save(output_file)
        return output_file
    except Exception as e:
        print(f"Erreur lors de la synthèse vocale: {e}")
        return None

def play_audio(audio_file):
    """Joue un fichier audio"""
    try:
        # Initialisation de pygame pour chaque lecture
        pygame.mixer.quit()
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        # Attendre que la lecture soit terminée avant de continuer
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        # Désactiver le mixer après utilisation
        pygame.mixer.quit()
    except Exception as e:
        print(f"Erreur lors de la lecture audio: {e}")
        print("Échec de la lecture audio, vérifiez votre configuration pygame")

# Définition des outils comme dans votre code original
@tool
def get_restaurants():
    """Get All Restaurants"""
    name: str = "api_restaurants"
    description: str = "Get All Restaurants"
    api_url = "https://app-584240518682.europe-west9.run.app/api/restaurants/"
    headers = {
        "Authorization": f"Token {hotel_api_token}"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Créer l'agent
tools = [get_restaurants]  # Ajoutez les autres outils comme dans votre code original
graph = create_react_agent(model, tools=tools)

def run_interactive_voice_agent():
    """Fonction pour exécuter l'agent en mode interactif avec communication vocale"""
    # Initialiser l'historique de conversation
    conversation_history = []
    
    # Définir le comportement de l'agent via une instruction système
    system_instruction = """
    Tu es Kimrau, le responsable temporaire de l'Hôtel California, un établissement luxueux et prestigieux.
    Tu dois accueillir les clients avec courtoisie et professionnalisme, répondre à leurs questions et les aider.
    Pour le premier message, présente-toi et souhaite la bienvenue au client à l'Hôtel California.
    Après chaque réponse à une question, demande poliment s'il y a autre chose que tu peux faire pour aider le client.
    Si le client indique qu'il n'a plus besoin d'aide (en disant par exemple "rien d'autre merci"), remercie-le et dis au revoir poliment.
    Utilise un langage formel mais chaleureux, adapté à un établissement hôtelier de luxe.
    """
    
    print("Initialisation de l'agent vocal Kimrau...")
    
    try:
        # Demander à l'agent de générer le message d'accueil
        greeting_response = api_ask_agent("Présente-toi en tant que responsable de l'hôtel et souhaite la bienvenue au client.", [], system_instruction)
        
        # Afficher la réponse textuelle de l'agent
        print(f"\nKimrau: {greeting_response}\n")
        
        # Convertir la réponse en audio et la jouer
        temp_greeting = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
        try:
            text_to_speech(greeting_response, temp_greeting)
            play_audio(temp_greeting)
            # Attendre un court instant pour s'assurer que le fichier est libéré
            time.sleep(0.5)
            # Puis essayer de supprimer
            if os.path.exists(temp_greeting):
                try:
                    os.unlink(temp_greeting)
                except PermissionError:
                    print(f"Impossible de supprimer {temp_greeting} pour le moment")
        except Exception as e:
            print(f"Erreur lors du traitement audio: {e}")
        
        # Ajouter le message système à l'historique
        conversation_history.append(("system", system_instruction))
        
        # Ajouter le message de demande de présentation
        conversation_history.append(("user", "Présente-toi en tant que responsable de l'hôtel et souhaite la bienvenue au client."))
        
        # Ajouter la réponse de bienvenue à l'historique
        conversation_history.append(("assistant", greeting_response))
        
    except Exception as e:
        print(f"Erreur lors de l'initialisation: {e}")
        greeting_response = "Bonjour et bienvenue à l'Hôtel California. Je suis Kimrau, le responsable temporaire. Comment puis-je vous aider aujourd'hui?"
        print(f"\nKimrau (message par défaut): {greeting_response}\n")
    
    # Boucle de conversation
    while True:
        print("\nOptions:")
        print("1. Saisir un message texte")
        print("2. Enregistrer un message vocal")
        print("3. Quitter")
        
        choice = input("Votre choix (1/2/3): ")
        
        if choice == "3":
            # Message d'au revoir
            try:
                farewell_response = api_ask_agent("Au revoir", conversation_history)
            except:
                farewell_response = "Merci de votre visite à l'Hôtel California. Au plaisir de vous revoir bientôt."
                
            print(f"\nKimrau: {farewell_response}\n")
            
            # Convertir et jouer le message d'au revoir
            temp_farewell = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
            try:
                text_to_speech(farewell_response, temp_farewell)
                play_audio(temp_farewell)
                # Attendre un court instant
                time.sleep(0.5)
                # Essayer de supprimer
                if os.path.exists(temp_farewell):
                    try:
                        os.unlink(temp_farewell)
                    except PermissionError:
                        print(f"Impossible de supprimer {temp_farewell} pour le moment")
            except Exception as e:
                print(f"Erreur lors du traitement audio: {e}")
            break
        
        if choice == "1":
            # Entrée textuelle
            user_input = input("\nVous (texte): ")
        elif choice == "2":
            # Entrée vocale
            print("\nPréparation de l'enregistrement vocal...")
            temp_recording = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
            try:
                audio_file = record_audio(temp_recording)
                
                print("Transcription de votre message...")
                user_input = speech_to_text(audio_file)
                # Attendre un court instant
                time.sleep(0.5)
                # Essayer de supprimer
                if os.path.exists(audio_file):
                    try:
                        os.unlink(audio_file)
                    except PermissionError:
                        print(f"Impossible de supprimer {audio_file} pour le moment")
                
                if user_input:
                    print(f"\nVous (vocal): {user_input}")
                else:
                    print("\nDésolé, je n'ai pas pu comprendre votre message. Veuillez réessayer.")
                    continue
            except Exception as e:
                print(f"Erreur lors de l'enregistrement/transcription: {e}")
                continue
        else:
            print("Option non valide, veuillez réessayer.")
            continue
        
        # Vérifier si l'utilisateur souhaite terminer la conversation
        if user_input.lower() in ["rien d'autre merci", "rien d'autre", "au revoir", "merci", "rien merci", "quit", "exit"]:
            try:
                farewell_response = api_ask_agent(user_input, conversation_history)
            except:
                farewell_response = "Merci de votre visite à l'Hôtel California. Au plaisir de vous revoir bientôt."
            
            # Afficher la réponse textuelle
            print(f"\nKimrau: {farewell_response}\n")
            
            # Convertir et jouer la réponse
            temp_farewell = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
            try:
                text_to_speech(farewell_response, temp_farewell)
                play_audio(temp_farewell)
                # Attendre un court instant
                time.sleep(0.5)
                # Essayer de supprimer
                if os.path.exists(temp_farewell):
                    try:
                        os.unlink(temp_farewell)
                    except PermissionError:
                        print(f"Impossible de supprimer {temp_farewell} pour le moment")
            except Exception as e:
                print(f"Erreur lors du traitement audio: {e}")
            break
        
        # Indication que la requête est en cours de traitement
        print("\nKimrau réfléchit...", end="\r")
        
        try:
            # Obtenir la réponse de l'agent
            response = api_ask_agent(user_input, conversation_history)
            
            # Effacer la ligne "réfléchit"
            print(" " * 30, end="\r")
            
            # Afficher la réponse textuelle
            print(f"\nKimrau: {response}\n")
            
            # Convertir et jouer la réponse
            temp_response = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
            try:
                text_to_speech(response, temp_response)
                play_audio(temp_response)
                # Attendre un court instant
                time.sleep(0.5)
                # Essayer de supprimer
                if os.path.exists(temp_response):
                    try:
                        os.unlink(temp_response)
                    except PermissionError:
                        print(f"Impossible de supprimer {temp_response} pour le moment")
                
                # Mettre à jour l'historique de conversation
                conversation_history.append(("user", user_input))
                conversation_history.append(("assistant", response))
            except Exception as e:
                print(f"Erreur lors du traitement audio: {e}")
                
        except Exception as e:
            print(f"Erreur: {e}")
            error_msg = "Je suis désolé, j'ai eu un problème technique. Pourriez-vous reformuler votre demande?"
            print(f"\nKimrau: {error_msg}\n")
            
            # Convertir et jouer le message d'erreur
            temp_error = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
            try:
                text_to_speech(error_msg, temp_error)
                play_audio(temp_error)
                # Attendre un court instant
                time.sleep(0.5)
                # Essayer de supprimer
                if os.path.exists(temp_error):
                    try:
                        os.unlink(temp_error)
                    except PermissionError:
                        print(f"Impossible de supprimer {temp_error} pour le moment")
            except Exception as e:
                print(f"Erreur lors du traitement audio d'erreur: {e}")

if __name__ == "__main__":
    # Effacer le terminal au démarrage pour une expérience plus propre
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux/MacOS
        os.system('clear')
        
    run_interactive_voice_agent()