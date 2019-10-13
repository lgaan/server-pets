class Contest:
    def __init__(self, json):
        self.id = json.get("id")

        self.owner_id = json.get("owner_id")
        self.participants = json.get("users")
        self.npcs = json.get("npcs")

        self.fee = json.get("fee")
        self.reward = json.get("reward")

        self.round_num = json.get("round_num")
        self.status = json.get("status")

        self.winner = json.get("winner")
    
    def __repr__(self):
        return f"<Contest id={self.id}, owner_id={self.owner_id}, participants={self.participants}, npcs={self.npcs}, fee={self.fee}, reward={self.reward}, status={self.status}>"