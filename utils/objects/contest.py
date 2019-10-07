class Contest:
    def __init__(self, json):
        self.id = json.get("id")

        self.owner_id = json.get("owner_id")
        self.participants = json.get("users")
        self.npcs = json.get("npcs")

        self.fee = json.get("fee")
        self.reward = json.get("reward")

        self.status = json.get("status")
    
    def __repr__(self):
        return f"<Contest id={self.id}, owner_id={self.owner_id}, participants={self.participants}, npcs={self.npcs}, fee={self.fee}, reward={self.reward}, status={self.status}>"