# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

import requests
import os
from typing import List, Dict, Text, Any, Optional

from actions.apiPartage.demo_actions import PartageZimbraCom

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import sys


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