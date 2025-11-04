from owlready2 import get_ontology

def load_ontology():
    onto = get_ontology("assets/travel_ontology.owl").load()
    return onto

def suggest_activity(temperature, ontology):
    for activity in ontology.Activity.instances():
        if hasattr(activity, "temperatureRange"):
            low, high = activity.temperatureRange
            if low <= temperature <= high:
                return activity.name
    return "Explore nearby attractions"
