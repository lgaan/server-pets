from utils.objects.pet import Pet
from utils.objects.account import Account


class AccountManager:
    def __init__(self, bot):
        self._bot = bot

    async def create_account(self, account_id):
        """Create an account"""
        items = {"water bowls": 0}
        settings = {"dm_notifications": True, "death_reminder": True}
        
        return await self._bot.db.execute(
            "INSERT INTO accounts (owner_id, balance, items, settings) VALUES ($1,600,$2,$3)",
            account_id, items, settings)

    async def get_account_pets(self, account_id):
        """Gets a list of pet objects for an account"""
        fetch = await self._bot.db.fetch("SELECT * FROM pets WHERE owner_id = $1", account_id)

        if not fetch:
            return None

        return [Pet(p) for p in fetch]

    async def get_account(self, account_id):
        """Gets an account"""
        fetch = await self._bot.db.fetch("SELECT * FROM accounts WHERE owner_id = $1", account_id)

        if not fetch:
            return None

        fetch = dict(fetch[0])

        fetch["pets"] = await self.get_account_pets(account_id)

        return Account(fetch)
    
    async def get_pet_named(self, account_id, pet_name):
        """Gets a pet with a certain name"""
        fetch = await self._bot.db.fetch("SELECT * FROM pets WHERE owner_id = $1 AND name = $2", account_id, pet_name.lower())

        if not fetch:
            return None
        
        return Pet(fetch[0])
    
    async def get_lb_accounts(self, ctx, lb_type="server"):
        """Gets a list of account objects for the leaderboard"""
        if lb_type.lower() == "server":
            accounts = await self._bot.db.fetch("SELECT * FROM accounts ORDER BY balance")
            accounts = [a for a in accounts if a["owner_id"] in [member.id for member in ctx.guild.members]][:5]; accounts.reverse()
        else:
            accounts = await self._bot.db.fetch("SELECT * FROM accounts ORDER BY balance DESC LIMIT 5")
        
        accs = []

        for acc in accounts:
            acc = dict(acc)
            acc["pets"] = await self.get_account_pets(acc["owner_id"])

            accs.append(Account(acc))

        return accs
    
    async def get_all_accounts(self):
        """Returns an account object for every account"""
        fetch = await self._bot.db.fetch("SELECT * FROM accounts")

        if not fetch:
            return None
        
        accounts = []

        for acc in fetch:
            json = dict(acc)
            json["pets"] = await self.get_account_pets(acc["owner_id"])

            accounts.append(Account(json))
        
        return accounts