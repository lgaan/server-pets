import json as js


class Account:
    def __init__(self, json):
        self.id = json.get("owner_id")

        self.balance = json.get("balance")

        self.items = js.loads(json.get("items")) if isinstance(json.get("items"), str) else json.get("items")
        self.settings = json.get("settings") if isinstance(json.get("settings"), str) else json.get("settings")

        self.pets = json.get("pets")
    
    async def sort_pets(self):
        """Sorts the account's pets into their respective types"""
        pet_types = {}

        for pet in self.pets:
            if pet.type in pet_types.keys():
                pet_types[pet.type] + 1
            else:
                pet_types[pet.type] = 1
        
        if "mouse" in pet_types.keys() and pet_types["mouse"] > 1:
            print("mouse")
            pet_types["mice"] = pet_types["mouse"]
            del pet_types["mouse"]

        return pet_types

    def __repr__(self):
        return f"<Account id={self.id}, balance={self.balance}, items={self.items}, pets={self.pets}>"
    