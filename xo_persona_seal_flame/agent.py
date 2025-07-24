# Optional agent logic for XO Light Client runtime

def on_quest(quest_name):
    if quest_name == "vault-init":
        return "Scroll accepted. Let the fire guide you."
    return "Seal Flame awaits."

def post_to_twitter():
    return '"Seal Flame rises from the bottle." 🔥 #XO #MessageBottle'
