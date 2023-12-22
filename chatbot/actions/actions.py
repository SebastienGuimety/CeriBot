# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

import requests
import os
from typing import List, Dict, Text, Any, Optional

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
        partage = PartageZimbraCom()

        email_address = tracker.get_slot("email")
        full_name = tracker.get_slot("fullname")
        subject = tracker.get_slot("subject")
        message = tracker.get_slot("message")
        print("email_address: ", email_address)
        print("full_name: ", full_name)
        print("subject: ", subject)
        print("message: ", message)
    
        partage.auth()
        #partage.request(partage.inbox_request)
        req = partage.build_msg_request(to={'mail': email_address, 'full_name': full_name}, subject=subject, body=message, html_body=message)
        response = partage.request(req)

        if not response.is_fault():
            dispatcher.utter_message("L'email a été envoyé avec succès.")
        else:   
            dispatcher.utter_message("Échec de l'envoi de l'email.")

            print(f"error\n"
                  f"fault_message: {response.get_fault_message()}\n"
                  f"fault_code: {response.get_fault_code()}")


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
                        dispatcher.utter_message(f"La température actuelle à {city} est de {temperature}°C")
                        dispatcher.utter_message(f"La météo actuelle à {city} est {weather_description}")
                        dispatcher.utter_message(f"La vitesse du vent actuelle à {city} est de {wind_speed} km/h")
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

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

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
