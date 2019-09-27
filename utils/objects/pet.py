class Pet:
    def __init__(self, json):
        # Info
        self.owner_id = json.get("owner_id")

        self.name = json.get("name")
        self.type = json.get("type")

        self.hunger = json.get("hunger")
        self.thirst = json.get("thirst")

        self.earns = json.get("earns")
        self.earned = json.get("earned")

        # Others
        self.level = json.get("level", 1)
        
        self.age = json.get("age", self.get_baby_name(self.type))
        self.species = json.get("species")

        self.image_url = json.get("image_url")

        self.kenneled = json.get("kenneled")
    
    def get_baby_name(self, pet_type):
        """Gets a pet's baby name  e.g: Dog => Puppy"""
        conversions = {
            "dog": "puppy",
            "cat": "kitten",
            "mouse": "pup",
            "snake": "hatchling",
            "spider": "spiderling",
            "bird": "chick",
            "horse": "foal"
        }

        return conversions[pet_type.lower()]
    
    def __repr__(self):
        return f"<Pet owner_id={self.owner_id}, name={self.name}, type={self.type}, hunger={self.hunger}, thirst={self.thirst}, earns={self.earns}, level={self.level}, age={self.age}, species={self.species}, kenneled={self.kenneled}>"
