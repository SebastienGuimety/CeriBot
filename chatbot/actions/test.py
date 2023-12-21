from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions import ActionFetchCourseSchedule  # Assurez-vous que c'est le bon chemin d'import

# Simuler les slots
slots = {
    "jour": "Lundi",
    "groupe": "1"
}

# Créer un Tracker de test avec les arguments minimum requis
tracker = Tracker(
    sender_id="test_sender",
    slots=slots,
    latest_message={"intent": {}, "entities": [], "text": ""},
    paused=False,
    followup_action=None,
    active_loop=None,
    latest_action_name=None,
    events=[]
)

# Créer un dispatcher de collecte
dispatcher = CollectingDispatcher()

# Créer et exécuter l'action
action = ActionFetchCourseSchedule()
action.run(dispatcher, tracker, {})

# Afficher les messages envoyés par le dispatcher
for message in dispatcher.messages:
    print(message["text"])
