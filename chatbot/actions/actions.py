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
    
