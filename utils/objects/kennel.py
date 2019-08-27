import json as js

from utils.objects.pet import Pet

class KenneledPet:
    def __init__(self, json, pet):
        self.owner_id = json.get("owner_id")
        self.name = json.get("name")
        
        self.release_date = json.pop("release_date")
        self.overdue = json.get("overdue")

        self.pet = pet
    
    def __repr__(self):
        return f"<KenneledPet release_date={self.release_date}, pet={self.pet}>"