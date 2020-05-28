# FRUIT VENDOR BOT
# Created by @AnnabelleLew
# Go to: https://github.com/AnnabelleLew/FruitVendor for the full respoitory

from random import randrange
import discord
import pickle

# starts client
client = discord.Client()

# creates all the fruits and their corresponding emojis
fruits = ["banana", "cherry", "coconut", "green apple", "grape", "kiwi", "lemon", "mango", "melon", "orange", "peach", "pear", "pineapple", "red apple", "strawberry", "watermelon"]
emojis = ["🍌", "🍒", "🥥", "🍏", "🍇", "🥝", "🍋", "🥭", "🍈", "🍊", "🍑", "🍐", "🍍", "🍎", "🍓", "🍉"]

# used for !eat command
aftertastes = ["It tastes delicious!", "It was old and mushy...", "It's super sweet!", "It was too sour...", "Yummy!", "Nom nom nom...", "It was super juicy!"]

# used for !throw command
splats = ["Splat!", "It explodes in their face!", "It bounces right off them!", "Ewwwww!"]

# inventory stores all the fruit, uses pickle to save user data when bot is taken offline
inventory = dict()

with open('fruit_inventory.pickle', 'rb') as handle:
    inventory = pickle.load(handle)

# sets bot status when online
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    game = discord.Game("!help")
    await client.change_presence(status=discord.Status.online, activity=game)

# reads user messages
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # !help command: explains all the commands to the user
    if message.content == '!help':
        await message.channel.send('Welcome to the fruit vendor!\n*!get*: Get new fruit.\n*!give [user]*: Give fruit.\n*!check [user]*: Check your fruit.\n*!eat*: Eat a fruit of your choice.\n*!throw [user]*: Throw a fruit at someone.')

    # !get command: gives a random fruit to the user
    if message.content == '!get':
        # gets a random fruit and the corresponding emoji (using :[emoji]: format)
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

        # sends message about giving fruit
        await message.channel.send('Congrats {0}, you have gotten a {1}! :{2}:'.format(message.author.mention, gift, emoji))

        # stores the fruit in the user's inventory
        if message.guild.id not in inventory.keys():
            inventory[message.guild.id] = dict()
        if message.author.id not in inventory[message.guild.id].keys():
            inventory[message.guild.id][message.author.id] = dict()
        if gift not in inventory[message.guild.id][message.author.id].keys():
            inventory[message.guild.id][message.author.id][gift] = 1
        else:
            inventory[message.guild.id][message.author.id][gift] += 1

    # !check command: check's a user's fruit inventory
    if message.content.startswith('!check'):
        # sets who's inventory to check
        if len(message.mentions) == 0:
            person = message.author
        elif len(message.mentions) == 1:
            person = message.mentions[0]
        else:
            await message.channel.send("Please only check one person's fruit at a time!")
            return

        # generates message of inventory
        unsent = "{0} currently has:".format(person.mention)
        if message.guild.id not  in inventory.keys():
            await message.channel.send("{0} has no fruit!".format(person.mention))
            return
        if person.id not in inventory[message.guild.id].keys():
            await message.channel.send("{0} has no fruit!".format(person.mention))
            return
        for fruit in inventory[message.guild.id][person.id].keys():
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
            unsent += "\n{0} :{1}:: {2}".format(fruit, emoji, inventory[message.guild.id][person.id][fruit])

        # sends message with inventory
        await message.channel.send(unsent)

    # !give: lets user give a fruit to another user
    if message.content.startswith('!give'):
        # checks who to give fruit to
        if len(message.mentions) == 1:
            person = message.mentions[0]
        else:
            await message.channel.send("Recheck your message, I don't know who to give fruit to!")
            return

        # generates message to figure out giving, waits for reaction in order to give
        await message.channel.send("{0}, what fruit would you like to give to {1}? (React to this message with the fruit of your choice, or react with a non-fruit emoji to cancel!)".format(message.author.mention, person.mention))

    # !eat: user chooses a fruit and eats it
    if message.content == '!eat':
        if message.guild.id not in inventory.keys():
            await message.channel.send("You have no fruit to eat!")
        elif message.author.id not in inventory[message.guild.id].keys():
            await message.channel.send("You have no fruit to eat!")
        else:
            await message.channel.send("{0}, what fruit would you like to eat? (React to this message with the fruit of your choice, or react with a non-fruit emoji to cancel!)".format(message.author.mention))

    # !throw: user throws a fruit at another person
    if message.content.startswith('!throw'):
        # checks who to throw fruit at
        if len(message.mentions) == 1:
            person = message.mentions[0]
        else:
            await message.channel.send("Recheck your message, I don't know who to throw fruit at!")
            return

        # generates message to figure out giving, waits for reaction in order to give
        await message.channel.send("{0}, what fruit would you like to throw at {1}? (React to this message with the fruit of your choice, or react with a non-fruit emoji to cancel!)".format(message.author.mention, person.mention))

    # saves inventory after action
    with open('fruit_inventory.pickle', 'wb') as handle:
        pickle.dump(inventory, handle, protocol=pickle.HIGHEST_PROTOCOL)

# checks reactions, used for !get command, !eat, and !throw command
@client.event
async def on_reaction_add(reaction, user):
    # cares about bot message about giving fruit
    if reaction.message.content.find(", what fruit would you like to give to ") != -1 and reaction.message.author == client.user:
        # only cares about the giver. KNOWN BUG: the "recipient" can hijack the message, and become the giver.
        if user not in reaction.message.mentions:
            pass
            return
        else:
            # if the reaction emoji is a fruit, continue, otherwise, cancel giving
            if reaction.emoji in emojis:
                # if the reaction emoji is in user inventory, give, otherwise, cancel giving
                if fruits[emojis.index(reaction.emoji)] in inventory[reaction.message.guild.id][user.id].keys() and inventory[reaction.message.guild.id][user.id][fruits[emojis.index(reaction.emoji)]] > 0:
                    # checks for the intended recipient
                    if (reaction.message.mentions.index(user) == 0):
                        recipient = reaction.message.mentions[1]
                    else:
                        recipient = reaction.message.mentions[0]

                    # removes fruit from user inventory, and gives it to recipient
                    inventory[reaction.message.guild.id][user.id][fruits[emojis.index(reaction.emoji)]] -= 1
                    if reaction.message.guild.id not in inventory.keys():
                        inventory[reaction.message.guild.id] = dict()
                    if recipient.id not in inventory[reaction.message.guild.id].keys():
                        inventory[reaction.message.guild.id][recipient.id] = dict()
                    if fruits[emojis.index(reaction.emoji)] not in inventory[reaction.message.guild.id][recipient.id].keys():
                        inventory[reaction.message.guild.id][recipient.id][fruits[emojis.index(reaction.emoji)]] = 1
                    else:
                        inventory[reaction.message.guild.id][recipient.id][fruits[emojis.index(reaction.emoji)]] += 1

                    # send successful fruit-giving message
                    await reaction.message.channel.send("{0} has successfully send a {1} {2} to {3}!".format(user.mention, fruits[emojis.index(reaction.emoji)], reaction.emoji, recipient.mention))
                else:
                    await reaction.message.channel.send("You don't have that fruit!")
            else:
                await reaction.message.channel.send("Okay, {0} is not giving fruit anymore.".format(user.mention))

            # delete "giving" message once complete, and save inventory
            await reaction.message.delete()
            with open('fruit_inventory.pickle', 'wb') as handle:
                pickle.dump(inventory, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # cares about bot message about eating fruit
    elif reaction.message.content.find(", what fruit would you like to eat?") != -1 and reaction.message.author == client.user:
        # only cares about the eater.
        if user not in reaction.message.mentions:
            pass
            return
        else:
            # if the reaction emoji is a fruit, continue, otherwise, cancel giving
            if reaction.emoji in emojis:
                # if the reaction emoji is in user inventory, eat, otherwise, cancel eating
                if fruits[emojis.index(reaction.emoji)] in inventory[reaction.message.guild.id][user.id].keys() and inventory[reaction.message.guild.id][user.id][fruits[emojis.index(reaction.emoji)]] > 0:
                    # removes fruit from user inventory
                    inventory[reaction.message.guild.id][user.id][fruits[emojis.index(reaction.emoji)]] -= 1
                    # choose random message to say after eating fruit
                    num = randrange(len(aftertastes))
                    review = aftertastes[num]

                    # send successful eating message
                    await reaction.message.channel.send("{0} has eaten a {1} {2}! {3}".format(user.mention, fruits[emojis.index(reaction.emoji)], reaction.emoji, review))
                else:
                    await reaction.message.channel.send("You don't have that fruit!")
            else:
                await reaction.message.channel.send("Okay, {0} is not hungry anymore.".format(user.mention))

            # delete "eating" message once complete, and save inventory
            await reaction.message.delete()
            with open('fruit_inventory.pickle', 'wb') as handle:
                pickle.dump(inventory, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # cares about bot message about throwing fruit
    elif reaction.message.content.find(", what fruit would you like to throw at ") != -1 and reaction.message.author == client.user:
        # only cares about the giver. KNOWN BUG: the "victim" can hijack the message, and become the attacker.
        if user not in reaction.message.mentions:
            pass
            return
        else:
            # if the reaction emoji is a fruit, continue, otherwise, cancel throwing
            if reaction.emoji in emojis:
                # if the reaction emoji is in user inventory, throw, otherwise, cancel throwing
                if fruits[emojis.index(reaction.emoji)] in inventory[reaction.message.guild.id][user.id].keys() and inventory[reaction.message.guild.id][user.id][fruits[emojis.index(reaction.emoji)]] > 0:
                    # checks for the intended recipient
                    if (reaction.message.mentions.index(user) == 0):
                        recipient = reaction.message.mentions[1]
                    else:
                        recipient = reaction.message.mentions[0]

                    # removes fruit from user inventory, and throws it at recipient
                    inventory[reaction.message.guild.id][user.id][fruits[emojis.index(reaction.emoji)]] -= 1

                    # chooses random message
                    num = randrange(len(splats))
                    splat = splats[num]

                    # send successful fruit-throwing message
                    await reaction.message.channel.send("{0} has thrown a {1} {2} at {3}. {4}".format(user.mention, fruits[emojis.index(reaction.emoji)], reaction.emoji, recipient.mention, splat))
                else:
                    await reaction.message.channel.send("You don't have that fruit!")
            else:
                await reaction.message.channel.send("Okay, {0} has had a change of heart.".format(user.mention))

            # delete "giving" message once complete, and save inventory
            await reaction.message.delete()
            with open('fruit_inventory.pickle', 'wb') as handle:
                pickle.dump(inventory, handle, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        pass
        return

# runs the bot client
print('running client')
client.run('bot.token.here')
