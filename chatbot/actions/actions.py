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

        fullname_sender = tracker.get_slot("fullname_sender")
        fullname_receiver = tracker.get_slot("fullname_receiver")

        # Split the full name into first name and last name
        parts = fullname_sender.split()
        if len(parts) >= 2:
            first_name = parts[0]
            last_name = parts[-1]
        else:
            # Handle cases where there's only one part (e.g., only the first name or last name)
            first_name = parts[0]
            last_name = ""  # You can set this to an empty string or handle it differently

        # Convert the first name and last name to lowercase and concatenate with a dot
        email_username_sender = f"{first_name.lower()}.{last_name.lower()}"

        # Combine the email username with the email domain to get the email address
        email_address_sender = email_username_sender + email_domain

        # Transform receiver's full name into an email address
        parts_receiver = fullname_receiver.split()
        if len(parts_receiver) >= 2:
            first_name_receiver = parts_receiver[0]
            last_name_receiver = parts_receiver[-1]
        else:
            first_name_receiver = parts_receiver[0]
            last_name_receiver = ""

        email_username_receiver = f"{first_name_receiver.lower()}.{last_name_receiver.lower()}"
        email_address_receiver = email_username_receiver + email_domain

        subject = tracker.get_slot("subject")
        message = tracker.get_slot("message")

        print("email_address_receiver: ", email_address_receiver)
        print("email_address_sender: ", email_address_sender)
        print("full_name: ", fullname_sender)
        print("subject: ", subject)
        print("message: ", message)

        file_path = "actions/login_results.txt"
        current_directory = os.getcwd()
        print(f"Current Working Directory: {current_directory}")


        # Initialize variables to store extracted username and password
        nom = None
        prenom = None

        # Check if the file exists
        if os.path.exists(file_path):
            print('file exists')
            # Read the content of the file
            with open(file_path, "r") as file:
                login_results = file.readlines()

            # Extract login and password information
            for line in login_results:
                if line.startswith("Nom: "):
                    nom = line.strip().split(": ")[1]
                    print(f"Nom: {nom}")
                elif line.startswith("Prenom: "):
                    prenom = line.strip().split(": ")[1]
                    print(f"Nom: {prenom}")


        try:
            partage = PartageZimbraCom(email=email_address_sender, passwd=prenom)
            partage.auth()
            #partage.request(partage.inbox_request)
            req = partage.build_msg_request(to={'mail': email_address_receiver, 'full_name': fullname_sender}, subject=subject, body=message, html_body=message)
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