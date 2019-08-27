from utils.managers.accountmanager import AccountManager

from utils.objects.kennel import KenneledPet

class KennelManager:
    def __init__(self, bot):
        self.bot = bot
        self.accountmanager = AccountManager(bot)

        self.deposits = {
            **dict.fromkeys(["dog","cat","mouse","bird"], 100),
            **dict.fromkeys(["snake","spider"], 200),
            "horse": 300
        }

    async def get_price(self, pet_type, time):
        """Get the price of a pet"""
        total = self.deposits.get(pet_type)
        
        return total + (50*time.days)

    async def get_removal_price(self, pet_type):
        """Get the removal price of a pet"""
        return 500

    async def charge_account(self, account, price):
        """Charge an account a certain price"""
        return await self.bot.db.execute("UPDATE accounts SET balance = $1 WHERE owner_id = $2", (account.balance - price), account.id)

    async def get_pet(self, owner_id, name):
        """Get a pet from the kennel"""
        fetch = await self.bot.db.fetch("SELECT * FROM kennel WHERE owner_id = $1 AND name = $2", owner_id, name)

        if not fetch:
            return None

        pet = await self.accountmanager.get_pet_named(owner_id, name)
        return KenneledPet(dict(fetch[0]), pet)
    
    async def add_pet(self, owner_id, name, release_date):
        """Add a pet to the kennel"""
        await self.bot.db.execute("INSERT INTO kennel (owner_id, name, release_date, overdue) VALUES ($1,$2,$3,False)", owner_id, name, release_date)
        await self.bot.db.execute("UPDATE pets SET kenneled = True WHERE owner_id = $1 AND name = $2", owner_id, name)

        return await self.get_pet(owner_id, name)
    
    async def remove_pet(self, owner_id, name):
        """Remove a pet from the kennel"""
        await self.bot.db.execute("UPDATE pets SET kenneled = False WHERE owner_id = $1 AND name = $2", owner_id, name)
        return await self.bot.db.execute("DELETE FROM kennel WHERE owner_id = $1 AND name = $2", owner_id, name)

    async def get_kennel(self, owner_id):
        """Get a kennel for an account"""
        fetch = await self.bot.db.fetch("SELECT * FROM kennel WHERE owner_id = $1", owner_id)

        if not fetch:
            return None
        
        pets = []

        for pet in fetch:
            p = await self.get_pet(owner_id, pet["name"])
            pets.append(p)

        return pets
    
    async def get_active_kennels(self):
        fetch = await self.bot.db.fetch("SELECT * FROM kennel")

        if not fetch:
            return None
        
        pets = []

        for pet in fetch:
            pets.append(await self.get_pet(pet["owner_id"], pet["name"]))
        
        return pets
