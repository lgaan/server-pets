from .accountmanager import AccountManager

from utils.objects.contest import Contest

class ContestManager:
    def __init__(self, bot):
        self.bot = bot

        self.accounts = AccountManager(bot)
    
    async def create_contest(self, json):
        """Create a contest"""
        await self.bot.db.execute("INSERT INTO contests (owner_id, id, name, users, npcs, fee, reward, status) VALUES ($7, $1, $2, $3, $4, $5, $6, $8)", json.get("id"), json.get("name"), json.get("users"), json.get("npcs"), json.get("fee"), json.get("reward"), json.get("owner_id"), "idle")

        return await self.get_contest(json.get("id"))
    
    async def delete_contest(self, contest_id, owner_id):
        """Delete a contest"""
        await self.bot.db.execute("DELETE FROM contests WHERE id = $1 AND owner_id = $2", contest_id, owner_id)

    async def get_account_contests(self, account_id):
        """Get account contests"""
        account = await self.accounts.get_account(account_id)

        if not account:
            return None
        
        fetch = await self.bot.db.fetch("SELECT * FROM contests")

        return [Contest(entry) for entry in fetch if account_id in [e["owner_id"] for e in entry["users"]]]
    
    async def get_contests(self):
        """Get all contests"""
        fetch = await self.bot.db.fetch("SELECT * FROM contests")

        if not fetch:
            return None
        
        return [Contest(entry) for entry in fetch]
    
    async def get_contest(self, contest_id):
        """Get a contest"""
        fetch = await self.bot.db.fetch("SELECT * FROM contests WHERE id = $1", contest_id)

        if not fetch:
            return None
        
        return Contest(fetch[0])