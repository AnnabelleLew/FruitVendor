from random import randrange
import discord
import pickle

client = discord.Client()
fruits = ["banana", "cherry", "coconut", "green apple", "grape", "kiwi", "lemon", "mango", "melon", "orange", "peach", "pear", "pineapple", "red apple", "strawberry", "watermelon"]
emojis = ["🍌", "🍒", "🥥", "🍏", "🍇", "🥝", "🍋", "🥭", "🍈", "🍊", "🍑", "🍐", "🍍", "🍎", "🍓", "🍉"]
inventory = dict()

with open('fruit_inventory.pickle', 'rb') as handle:
    inventory = pickle.load(handle)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    game = discord.Game("!help | !get | !give | !check")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '!help':
        await message.channel.send('Welcome to the fruit vendor!\n*!get*: Get new fruit.\n*!give [user]*: Give fruit.\n*!check [user]*: Check your fruit.')

    if message.content == '!get':
        num = randrange(len(fruits))
        gift = fruits[num]
        if gift == "green apple":
            emoji = "green_apple"
        elif gift == "red apple":
            emoji = "apple"
        elif gift == "orange":
            emoji = "tangerine"
        elif gift == "grape":
            emoji = "grapes"
        elif gift == "cherry":
            emoji = "cherries"
        else:
            emoji = gift
        await message.channel.send('Congrats {0}, you have gotten a {1}! :{2}:'.format(message.author.mention, gift, emoji))
        if message.author.id not in inventory.keys():
            inventory[message.author.id] = dict()
        if gift not in inventory[message.author.id].keys():
            inventory[message.author.id][gift] = 1
        else:
            inventory[message.author.id][gift] += 1

    if message.content.startswith('!check'):
        if len(message.mentions) == 0:
            person = message.author
        elif len(message.mentions) == 1:
            person = message.mentions[0]
        else:
            await message.channel.send("Please only check one person's fruit at a time!")
            return
        unsent = "{0} currently has:".format(person.mention)
        if person.id not in inventory.keys():
            await message.channel.send("{0} has no fruit!".format(person.mention))
            return
        for fruit in inventory[person.id].keys():
            if fruit == "green apple":
                emoji = "green_apple"
            elif fruit == "red apple":
                emoji = "apple"
            elif fruit == "orange":
                emoji = "tangerine"
            elif fruit == "grape":
                emoji = "grapes"
            elif fruit == "cherry":
                emoji = "cherries"
            else:
                emoji = fruit
            unsent += "\n{0} :{1}:: {2}".format(fruit, emoji, inventory[person.id][fruit])
        await message.channel.send(unsent)

    if message.content.startswith('!give'):
        if len(message.mentions) == 1:
            person = message.mentions[0]
        else:
            await message.channel.send("Recheck your message, I don't know who to give fruit to!")
            return
        await message.channel.send("{0}, what fruit would you like to give to {1}? (React to this message with the fruit of your choice, or react with a non-fruit emoji to cancel!)".format(message.author.mention, person.mention))

    with open('fruit_inventory.pickle', 'wb') as handle:
        pickle.dump(inventory, handle, protocol=pickle.HIGHEST_PROTOCOL)

@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.content.find(", what fruit would you like to give to ") != -1 and reaction.message.author == client.user:
        if user not in reaction.message.mentions:
            pass
            return
        else:
            if reaction.emoji in emojis:
                if fruits[emojis.index(reaction.emoji)] in inventory[user.id].keys() and inventory[user.id][fruits[emojis.index(reaction.emoji)]] > 0:
                    if (reaction.message.mentions.index(user) == 0):
                        recipient = reaction.message.mentions[1]
                    else:
                        recipient = reaction.message.mentions[0]
                    inventory[user.id][fruits[emojis.index(reaction.emoji)]] -= 1
                    if recipient.id not in inventory.keys():
                        inventory[recipient.id] = dict()
                    if fruits[emojis.index(reaction.emoji)] not in inventory[recipient.id].keys():
                        inventory[recipient.id][fruits[emojis.index(reaction.emoji)]] = 1
                    else:
                        inventory[recipient.id][fruits[emojis.index(reaction.emoji)]] += 1
                    await reaction.message.channel.send("{0} has successfully send a {1} {2} to {3}!".format(user.mention, fruits[emojis.index(reaction.emoji)], reaction.emoji, recipient.mention))
                else:
                    await reaction.message.channel.send("You don't have that fruit!")
            else:
                await reaction.message.channel.send("Okay, {0} is not giving fruit anymore.".format(user.mention))
            await reaction.message.delete()
            with open('fruit_inventory.pickle', 'wb') as handle:
                pickle.dump(inventory, handle, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        pass
        return

# change_status.start()
print('running client')
client.run('bot.token.here')
