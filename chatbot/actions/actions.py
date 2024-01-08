# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

import requests
import os
from typing import List, Dict, Text, Any, Optional
import asyncio
import aiohttp


from actions.apiPartage.demo_actions import PartageZimbraCom

from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import sys


class ActionSubmitWeather(Action):
    def name(self) -> Text:
        return "action_submit_weather"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Implement logic to provide a summary or final message
        dispatcher.utter_message("Je traite votre demande... Veuillez patienter s'il vous plaît.")

        return []

# ACTION POUR DEMANDER LA CLASSE ET LE GROUPE DE L'ETUDIANT

class ActionSaySchedule(Action):

    def name(self) -> Text:
        return "action_say_schedule"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        section = tracker.get_slot("section")
        group = tracker.get_slot("group")
        
        if not section:
            dispatcher.utter_message(text="I don't know your section.")
        elif not group:
            dispatcher.utter_message(text="I don't know your group.")
        else:
            dispatcher.utter_message(text=f"Your section is {section} and your group is {group}!")
       
        return []
    

# ACTION POUR LE FORMULAIRE D'ENVOI D'EMAIL

class ActionSendEmail(Action):
    def name(self):
        return "action_send_email"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Obtenir les informations nécessaires de la conversation

        # Assuming the email domain is fixed
        email_domain = "@alumni.univ-avignon.fr"

        

        subject = tracker.get_slot("subject")
        message = tracker.get_slot("message")

        
        print("subject: ", subject)
        print("message: ", message)

        file_path = "actions/login_results.txt"
        current_directory = os.getcwd()
        print(f"Current Working Directory: {current_directory}")


        # Initialize variables to store extracted username and password
        email_sender = None
        email_receiver = None
        password = None
        email_address_receiver = None
        email_address_sender = None

        # Check if the file exists
        if os.path.exists(file_path):
            print('file exists')
            # Read the content of the file
            with open(file_path, "r") as file:
                login_results = file.readlines()

            # Extract login and password information
            for line in login_results:
                if line.startswith("email_sender: "):
                    email_sender = line.strip().split(": ")[1]
                    email_address_sender = email_sender + email_domain
                    print(f"email_sender: {email_address_sender}")
                elif line.startswith("email_receiver: "):
                    email_receiver = line.strip().split(": ")[1]
                    email_address_receiver = email_receiver + email_domain
                    print(f"email_receiver: {email_address_receiver}")
                elif line.startswith("password: "):
                    password = line.strip().split(": ")[1]
                    print(f"password: {password}")

        

        print("email_address_receiver: ", email_address_receiver)
        print("email_address_sender: ", email_address_sender)

        try:
            partage = PartageZimbraCom(email=email_address_sender, passwd=password)
            partage.auth()
            #partage.request(partage.inbox_request)
            req = partage.build_msg_request(to={'mail': email_address_receiver, 'full_name': "Sebastien Guimety"}, subject=subject, body=message, html_body=message)
            response = partage.request(req)

            if not response.is_fault():
                dispatcher.utter_message("L'email a été envoyé avec succès.")
            else:   
                dispatcher.utter_message("Échec de l'envoi de l'email.")

                print(f"error\n"
                    f"fault_message: {response.get_fault_message()}\n"
                    f"fault_code: {response.get_fault_code()}")
                
        except Exception as e:
            print(f"Error: {e}")
            dispatcher.utter_message("Échec de l'envoi de l'email.")
        return []
    

class ActionDisplayWebView(Action):
    def name(self) -> Text:
        return "action_display_webview"

    async def run(self,dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any],) -> List[Dict[Text, Any]]:
        # Implement logic to provide a summary or final message
        # Construire l'URL de l'API en fonction des informations du tracker
        file_path = "login_results.txt"

        # Initialize variables to store extracted username and password
        username = None
        password = None

        # Check if the file exists
        if os.path.exists(file_path):
            # Read the content of the file
            with open(file_path, "r") as file:
                login_results = file.readlines()

            # Extract login and password information
            for line in login_results:
                if line.startswith("Username: "):
                    username = line.strip().split(": ")[1]
                    print(f"Username: {username}")

                elif line.startswith("Password: "):
                    password = line.strip().split(": ")[1]
                    print(f"Password: {password}")


            # Check if the username and password are extracted        
        

        return []

class ActionSendWeather(Action):
    def name(self):
        return "action_send_weather"
    
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Obtenir les informations nécessaires de la conversation

        city = tracker.get_slot("city")
        print("city: ", city)
        affichage = tracker.get_slot("affichage")
        print("affichage: ", affichage)

        api_key = "95747142ae542efed63858e9c0c8bb9e"
        base_url = "http://api.weatherstack.com/current"
        params = {
            "access_key": api_key,
            "query": city,
        }

        if not city:
            dispatcher.utter_message(text="Je ne connais pas votre ville.")
        elif not affichage:
            dispatcher.utter_message(text="Je ne connais pas votre demande.")
        else:
            
            try:
                # Fetch current weather
                response = requests.get(base_url, params=params)
                data = response.json()

                if response.status_code == 200:
                    # localtime = data["location"]["localtime"]
                    temperature = data["current"]["temperature"]
                    weather_description = data["current"]["weather_descriptions"][0]
                    wind_speed = data["current"]["wind_speed"]
                    # wind_degree = data["current"]["wind_degree"]
                    # humidity = data["current"]["humidity"]
                    
                    if affichage == "temperature":
                        dispatcher.utter_message(f"La température actuelle à {city} est de {temperature}°C")
                    elif affichage == "vent":
                        dispatcher.utter_message(f"La vitesse du vent actuelle à {city} est de {wind_speed} km/h")
                    else:
                        dispatcher.utter_message(f"La température actuelle à {city} est de {temperature}°C, la météo est {weather_description} et la vitesse du vent est de {wind_speed} km/h")
                else:
                    dispatcher.utter_message(f"Error: {data['error']['info']}")
            except Exception as e:
                dispatcher.utter_message(f"Error: {e}")
        return []
    
class ActionFetchCourseSchedule(Action):
    def name(self) -> Text:
        return "action_fetch_course_schedule"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        jour = tracker.get_slot('jour')
        groupe = tracker.get_slot('groupe')

        if not jour or not groupe:
            dispatcher.utter_message(text="Veuillez fournir le jour et le groupe pour afficher l'emploi du temps.")
            return []

        response = requests.get(f"http://localhost:5000/cours/jour?jour={jour}&groupe={groupe}")
        if response.status_code == 200:
            schedule = response.json()
            cours_noms = ', '.join([cours['nom_matiere'] for cours in schedule])
            dispatcher.utter_message(text=f"Vous avez {len(schedule)} cours ce jour : {cours_noms}. Voulez-vous plus d'informations sur les cours ?")
            # Enregistrez l'horaire dans un slot pour un usage ultérieur
            return [SlotSet("schedule", schedule)]
        else:
            dispatcher.utter_message(text="Désolée, je n'ai pas pu traiter votre demande.")
            return []

class ActionProvideCourseDetails(Action):
    def name(self) -> Text:
        return "action_provide_course_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        schedule = tracker.get_slot('schedule')
        if schedule:
            for cours in schedule:
                dispatcher.utter_message(text=f"Le cours {cours['nom_matiere']} est de {cours['heure_debut']} à {cours['heure_fin']} dans la {cours['salle']}.")
        else:
            dispatcher.utter_message(text="Je n'ai pas d'informations sur les cours pour ce jour.")

        return []



class ActionFetchLastCourseTime(Action):
    def name(self) -> Text:
        return "action_fetch_last_course_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        jour = tracker.get_slot('jour')
        groupe = tracker.get_slot('groupe')

        # Vérifier si les slots jour et groupe sont remplis
        if not jour or not groupe:
            # Vous pouvez choisir de demander à l'utilisateur de fournir les informations manquantes
            dispatcher.utter_message(text="Veuillez préciser le jour et le groupe pour obtenir l'heure de fin.")
            return []

        # Faire une requête à l'API pour obtenir l'heure de fin
        try:
            response = requests.get(f"http://localhost:5000/heure-fin/jour?jour={jour}&groupe={groupe}")
            if response.status_code == 200:
                data = response.json()
                dispatcher.utter_message(text=f"Le dernier cours pour le groupe {groupe} le {jour} se termine à {data['heure_fin']}.")
            else:
                dispatcher.utter_message(text="Désolée, je n'ai pas pu trouver l'information pour le jour et le groupe spécifiés.")
        except requests.RequestException as e:
            dispatcher.utter_message(text="Une erreur s'est produite lors de la connexion à l'API.")
            print(e)

        return []
