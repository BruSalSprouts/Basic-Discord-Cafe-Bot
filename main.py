import discord
import os
import json
import random
from item import item
import tracemalloc
import asyncio
import urllib.parse
from replit import db
from discord.ext import commands

#This was created by user BruSal.
#Find him in BruSalSprouts on GitHub!

menu = []  #List of items with their prices. Easy access and can be added/deleted at any time
# userIDs = []
userItems = {}  #Dictionary so each each user can be found a bit more easily. key:value = User ID:list of user's items
isOpen = True  #boolean to check whether the café is open or not. Start as false when in normal use

#DO NOT TOUCH UNLESS CHANGING LOCATIONS OF STUFF! IF A SIGNLE CHARACTER OF BELOW STUFF IS CHANGED EVERYTHING GOES TO SHIT!!!
mySecret = os.environ['CAFE_TOKEN']  #token to allow bot to be activated
targetChannelID = 608741870058733671  #channel where café is located
adminRoleID = 608742175928483872  #mod role
BruSalID = 303726738750439424 #User ID of the author of this message (BruSal_Sprouts)

#This allows for discord to understand that the stuff I send is allowed
intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!',intents=intents)  #Only messages that start with ! will be accepted

@bot.event  #Beginning event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    global isOpen
    isOpen = True
    await menu_startup()

async def menu_startup():  #Sets up the menu with the starting items, will start with the same items every time
    #Sets up the userItems dictionary of lists by giving me a list so that it exists globally
    global userItems
    # if "userItems" in db.keys():
    #     print('Getting users\' previous items from replit database')
    #     userItems = db["userItems"]
    # userItems = get_userItems_from_database()
    # if userItems is None:
    print('Getting default user items list setup') #Will stick to deleting all users' orders once bot shuts down
    userItems = {}
    # tempList = []
    # userItems[BruSalID] = tempList #Maybe not necessary, need to try
    
    # global userIDs
    # try:
    #     userIDs = db['userIDs']
    #     print('The list of user IDs has been loaded')
    # except KeyError:
    #     print('The userIDs key does not exist')
    #     userIDs = []
    
    global menu #Menu stuff stays, can get stored in database
    try:
        menu = get_item_list_from_database('menu')
    except KeyError:
        menu = menu_setup()
    if menu is None:
        menu = menu_setup()

def get_userItems_from_database():
    serializedUserItems = db.get('userItems')
    if serializedUserItems is not None:
        userItems = json.loads(serializedUserItems)
        return userItems
    return None

def menu_setup():
    #Sets up the menu list by declaring menu a list and then adding the menu items to it
    print('Getting default menu items')
    #make sure to update these items when you have new ones to work with!
    Red_Rose = item("Red_Rose", 0.50, "TempMenuItems/RedRose.png")
    Star_Twins = item("Star_Twins", 5.00,"TempMenuItems/Sanrio_Star_Twins.png")
    United_Kingdom = item("United_Kingdom", 1000000,"TempMenuItems/United-Kingdom-Flag-PNG-180x180.png")
    #Time to append to menu
    menu = []
    menu.append(Red_Rose)
    menu.append(Star_Twins)
    menu.append(United_Kingdom)
    return menu

def get_item_list_from_database(ID):
    print(f'Trying to get an itemList from db[{ID}]')
    try:
        encodedID = ID.encode('utf-8')
        serializedList = db[encodedID] #Retrieve the serialized list from Replit db
        deserializedList = json.loads(serializedList) #Deserialize the JSON string into a list of dictionaries
        tempList = [item(sItem['Name'], sItem['Price'], sItem['picturePath']) for sItem in deserializedList] #Recreates the objects from the dictionaries
        print('Success!')
        return tempList #Returns the list
    except KeyError:    
        print('Failure')
        return None #Returns nothing if the db couldn't find the specific ID

def store_item_list_in_database(itemList, ID):
    encodedID = ID.encode('utf-8')
    serializedList = json.dumps([obj.__dict__ for obj in itemList]) #Serializes  the itemList of objects into a JSON string
    db[encodedID] = serializedList #Stores the serialized list in the Replit db

#use @bot.command to make commands that begin with '!' and do stuff!
#ctx is the context message that allows for a bot to have context of what's been said while it's responding. So cool!!!

@bot.command()
async def admin_help(ctx):
    if ctx.channel.id != targetChannelID:  #Checks to see if the command is being called in the correct channel ID
        return
    await ctx.send('!waitress shows the commands that are available to anyone, regardless of mod status. The following commands are only available to mods')
    await ctx.send("Type in !open to open the restaurant")
    await ctx.send("Type in !close to close the restaurant, preventing many of the commands mentioned in !waitress from working")
    await ctx.send("Type in !add_item_to_menu to add an item to a menu, you'll be prompted by entering a name (Please replace spaces with '_' instead), a number, and an image file that you'll all have to upload when prompted. [NOTE: When the bot shuts down, the menu will revert to default menu options]")
    await ctx.send("Type in !remove_item_from_menu to remove an item from the menu, you'll be prompted to enter the name of the item you want to remove, and it will be removed from the menu. [NOTE: When the bot shuts down, the menu will revert to default menu options]")
    await ctx.send("Type in !shutdown to shut down the bot [NOTE: All menu items will revert back to default stats, and all customers' orders that they can see (and clear) in !bill will be lost]")

@bot.command()
async def waitress(ctx):  #The café's greeting message essentailly
    if ctx.channel.id != targetChannelID:  #Checks to see if the command is being called in the correct channel ID
        return
    global isOpen
    if isOpen:
        await ctx.send('Hello there! Welcome to our café!')
        await ctx.send("Type in '!menu' to see what we have today\n")
        await ctx.send("Type in '!order' followed by any item from the menu to order that item!")
        await ctx.send("Type in '!recommend' to have be recommended an item from the menu!")
        await ctx.send("Type in '!table' to be taken to your seat")
        await ctx.send("Type in '!bill' when you're finished ordering, so you can get your total amount due")
        await ctx.send("Type in '!tip' to give an extra tip for our service!")
    else:
        await ctx.send('Hello there! The café is currently closed, come back later!')


@bot.command()
async def open(ctx):  #Opens the café and changes isOpen to True. Only mods can do this
    if ctx.channel.id != targetChannelID:  #Checks to see if the command is being called in the correct channel ID
        return
    if adminRoleID not in [role.id for role in ctx.author.roles]:  #Checks to see if user has the admin role
        await ctx.send('Sorry, but you\'re not authorized to use this command.')
    global isOpen
    if isOpen:  #Checks to see if the café is already open
        await ctx.send('The café is already open??')
        return

    isOpen = True

    #Image Sending Time
    imagePath = os.path.join(os.getcwd(), 'CafeOperations/Open-Sign-PNG-HD.png'
                             )  #Gets path of image file relative to directory
    #Checks to see if the image file exists
    if not os.path.exists(imagePath):
        await ctx.send('Image file not found.')
        return
    file = discord.File(
        imagePath)  #Create a discord.File object from the image file
    await ctx.send(file=file)

    await ctx.send('The café is now open!')  #Finishing message


@bot.command()
async def close(ctx):  #Closes the café and changes isOpen to false. Only mods can do this
    if ctx.channel.id != targetChannelID:  #Checks to see if the command is being called in the correct channel ID
        return
    if adminRoleID not in [role.id for role in ctx.author.roles
                           ]:  #Checks to see if user has the admin role
        await ctx.send('Sorry, but you\'re not authorized to use this command.')
    global isOpen
    if not isOpen:  #Checks to see if the café is already open
        await ctx.send('The café is already closed??')
        return

    isOpen = False
    
    #Image Sending Time
    imagePath = os.path.join(os.getcwd(),'CafeOperations/Sorry-We-Are-Closed-PNG-Image.png')  #Gets path of image file relative to directory
    #Checks to see if the image file exists
    if not os.path.exists(imagePath):
        await ctx.send('Image file not found.')
        return
    file = discord.File(
        imagePath)  #Create a discord.File object from the image file
    await ctx.send(file=file)

    await ctx.send('The café is now closed!')


@bot.command()
async def table(ctx):  #Displays a table and has little messages before and after
    if ctx.channel.id != targetChannelID:  #Checks to see if the command is being called in the correct channel ID
        return
    if not isOpen:  #Checks to see if the café is currently open
        await ctx.send('I\'m sorry, but you\'ll have to come back later! The café is currently closed!')
        return

    await ctx.send('Alright! Follow me to your table!')  #Opening Message

    #Image Sending Time
    imagePath = os.path.join(os.getcwd(),'CafeOperations/Dining-Room-Table-PNG-File.png')  #Gets path of image file relative to directory
    #Checks to see if the image file exists
    if not os.path.exists(imagePath):
        await ctx.send('Image file not found.')
        return
    file = discord.File(
        imagePath)  #Create a discord.File object from the image file
    await ctx.send(file=file)

    await ctx.send('Let me know when you\'re ready to order!')  #Closing Message

    
@bot.command()
async def menu(ctx):  #Displays the menu
    if ctx.channel.id != targetChannelID:  #Checks to see if the command is being called in the correct channel ID
        return
    if not isOpen:  #Checks to see if the café is currently open
        await ctx.send('I\'m sorry, but you\'ll have to come back later! The café is currently closed!')
        return

    #Image Sending Time
    imagePath = os.path.join(os.getcwd(),'CafeOperations/Carta-menu-cerrada.png')  #Gets path of image file relative to directory
    #Checks to see if the image file exists
    if not os.path.exists(imagePath):
        await ctx.send('Image file not found.')
        return
    file = discord.File(
        imagePath)  #Create a discord.File object from the image file
    await ctx.send(file=file)
    
    #Gets all the menu options' names and prices (Save the images for when we're ordering)
    await ctx.send('============== Café Menu ===============') #This is the top part of the menu
    for itemOption in menu:
        await ctx.send(f'{itemOption.getName()}            ${itemOption.getPrice()}')
    await ctx.send('========================================') #This is the bottom of the menu


@bot.command() 
async def add_item_to_menu(ctx): #Adds a new item to the menu, prompting a new name, price, and file (it has it's own path saved!)
    if ctx.channel.id != targetChannelID:  #Checks to see if the command is being called in the correct channel ID
        return
    if adminRoleID not in [role.id for role in ctx.author.roles]:  #Checks to see if user has the admin role
        await ctx.send('Sorry, but you\'re not authorized to use this command.')
    if not isOpen:  #Checks to see if the café is currently open
        await ctx.send('I\'m sorry, but you\'ll have to come back later! The café is currently closed!')
        return
    #Needs to update so information is stored to database!
    #Getting new name
    await ctx.send('What\'s the name of the new menu item?')
    newItemName = ''
    def check(message):  #function to wait for response
        return not message.content.strip().isspace() #Ignores whitespace-only answers
    try:
        response = await bot.wait_for('message', check=check, timeout=20)
        newItemName = response.content.split(' ', 1)[0]  #Extracts the string until the first space
    except asyncio.TimeoutError:  #Error handling
        await ctx.send('No response received. Please try again.')
        return
        
    #Getting new Price
    await ctx.send(f'How much will {newItemName} cost? (Please insert a numeric answer)')
    newItemPrice = 0
    def check(message):  #function to wait for response
        return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit()
    try:
        response = await bot.wait_for('message', check=check, timeout=60)
        newItemPrice = int(response.content)  #Stores the user's response
    except asyncio.TimeoutError:  #Error handling
        await ctx.send('No response received. Please try again.')
        return

    #Getting new file path
    await ctx.send(f'Please send the image file of {newItemName}.')
    newItemPath = ''
    def check(message):
        return message.author == ctx.author and message.attachments
    try:
        message = await bot.wait_for('message', check=check, timeout=45)
        file = message.attachments[0]
        newItemPath = f'CafeOperations/{file.filename}'
        await file.save(newItemPath)  # Save the file to a desired location
        await ctx.send("File uploaded successfully.")
    except asyncio.TimeoutError:
        await ctx.send("Timeout: No file uploaded.")
    except IndexError:
        await ctx.send("No file attached.")
        
    #Officially adding the new item to the menu
    newItem = item(newItemName, newItemPrice, newItemPath)
    menu.append(newItem)
    #If needed, insert saving menu item to list here
    # print('adding new menu item to both menu list and the database')
    await ctx.send(f'{newItemName} has been added to the menu!')
    
    
@bot.command()
async def remove_item_from_menu(ctx):
    if ctx.channel.id != targetChannelID:  #Checks to see if the command is being called in the correct channel ID
        return
    if adminRoleID not in [role.id for role in ctx.author.roles]:  #Checks to see if user has the admin role
        await ctx.send('Sorry, but you\'re not authorized to use this command.')
    if not isOpen:  #Checks to see if the café is currently open
        await ctx.send('I\'m sorry, but you\'ll have to come back later! The café is currently closed!')
        return
    
    await ctx.send('What is the name of the item you would like to remove from the menu? (Please do not type any spaces in between)')
    stringResponse = ''
    def check(message):  #function to wait for response
        return not message.content.strip().isspace() #Ignores whitespace-only answers
    try:
        response = await bot.wait_for('message', check=check, timeout=20)
        stringResponse = response.content.split(' ', 1)[0]  #Extracts the string until the first space
    except asyncio.TimeoutError:  #Error handling
        await ctx.send('No response received. Please try again.')

    itemResponse = item.search_by_name(stringResponse, menu)
    if itemResponse == False: #Failsafe to check if an item exists in the menu before trying to remove it
        await ctx.send('Hey! That item does not exist! Please try again!')
    else:
        menu.remove(itemResponse)
        # If needed, put in the stuff to save the item's deletion here
        # print('Removed item from menu and the replit database')
        await ctx.send(f'Removed {stringResponse} from the menu')

    
@bot.command()
async def recommend(ctx): #Recommends to the user a random item from the menu, and sends a picture of it
    if ctx.channel.id != targetChannelID:  #Checks to see if the command is being called in the correct channel ID
        return
    if not isOpen:  #Checks to see if the café is currently open
        await ctx.send('I\'m sorry, but you\'ll have to come back later! The café is currently closed!')
        return
    listSize = len(menu)
    if listSize == 0:
        await ctx.send('I\'m sorry, but we currently have nothing to offer, please come again later.')
    else:
        randomItem = random.choice(menu)
        await ctx.send(f'Hello! We recommend you get a {randomItem.getName()}! It costs ${randomItem.getPrice()}')
        
        #Image Sending Time
        imagePath = os.path.join(os.getcwd(), randomItem.getPicturePath())  #Gets path of image file relative to directory
        #Checks to see if the image file exists
        if not os.path.exists(imagePath):
            await ctx.send('Image file not found.')
            return
        file = discord.File(
            imagePath)  #Create a discord.File object from the image file
        await ctx.send(file=file)

    
@bot.command()
async def order(ctx, orderName=None): #Gets an item from the menu and adds it into a user's list
    if ctx.channel.id != targetChannelID:  #Checks to see if the command is being called in the correct channel ID
        return
    if not isOpen:  #Checks to see if the café is currently open
        await ctx.send('I\'m sorry, but you\'ll have to come back later! The café is currently closed!')
        return
    if orderName is None: #Allows for user to enter no paramter after the !order command
        await ctx.send('Hey! If you want to order something, you\'ll have to write the name of what you want to order after this command! Type !menu to see the list of options available.')
    else:
        tempID = ctx.author.id #Gets the ID of the sender of the command
        tempItem = item.search_by_name(orderName, menu)
        if tempItem == False: #Failsafe in case the item doesn't exist
            await ctx.send('Hey! That item does not exist! Please try again!')
        else:
            if tempID in userItems: #If the user already has ordered before (or has a list of items already), an item will simply be appended to it
                userItems[tempID].append(tempItem)
            else: #If the user hasn't ordered before, a new list will be created in the dictionary userItems
                userItems[tempID] = [tempItem]
            # if tempID in db.keys():
            #     tempList = get_item_list_from_database(tempID)
            #     tempList.append(tempItem)
            # else:
            #     tempList = [tempItem]
            # store_item_list_in_database(tempList, tempID)
            
            await ctx.send(f'Thanks for ordering the {tempItem.getName()}!')
            
            #Image Sending Time - Sends image of item just ordered!
            imagePath = os.path.join(os.getcwd(), tempItem.getPicturePath())  #Gets path of image file relative to directory
            #Checks to see if the image file exists
            if not os.path.exists(imagePath):
                await ctx.send('Image file not found.')
                return
            file = discord.File(
                imagePath)  #Create a discord.File object from the image file
            await ctx.send(file=file)
 
@bot.command()
async def bill(ctx): #Prints out the list of everything the user ordered, along with their prices, calculates the total, and removes all items from the user's list
    if ctx.channel.id != targetChannelID:  #Checks to see if the command is being called in the correct channel ID
        return
    if not isOpen:  #Checks to see if the café is currently open
        await ctx.send('I\'m sorry, but you\'ll have to come back later! The café is currently closed!')
        return
    #Needs to be finished!
    total = 0
    tempID = ctx.author.id #Gets the ID of the sender of the command
    if tempID not in userItems:
        await ctx.send('There\'s currently nothing on your bill that you\'ve ordered.')
        return
    else:
        if not userItems[tempID]:
            await ctx.send('There\'s currently nothing on your bill that you\'ve ordered.')
        else:
            tempList = userItems[tempID]
            await ctx.send('================ Total =================') #This is the top part of the menu
            for itemOption in tempList:
                await ctx.send(f'{itemOption.getName()}            ${itemOption.getPrice()}')
                total += itemOption.getPrice()
            await ctx.send(f'Your total is: ${total}')
            await ctx.send('========================================') #This is the bottom of the menu
            await ctx.send('Thanks for eating here! Have a great day!')
            # if tempID in db.keys(): #This is the version that uses the replit db for storing users' items
    #     tempList = get_item_list_from_database(tempID)
    #     if not tempList:
    #         await ctx.send('================ Total =================') #This is the top part of the menu
    #         for itemOption in tempList:
    #             await ctx.send(f'{itemOption.getName()}            ${itemOption.getPrice()}')
    #             total += itemOption.getPrice()
    #         await ctx.send(f'The total is: {total}')
    #         await ctx.send('========================================') #This is the bottom of the menu
    #         tempList.clear()
    #         store_item_list_in_database(tempList, tempID)
    #     else:
    #         await ctx.send('Sorry, but you don\'t have anything on your bill yet!')
    # else:
    #     await ctx.send('Sorry, but you don\'t have anything on your bill yet!')
            userItems[tempID].clear()
    

@bot.command()
async def tip(ctx):  #Prompts user to ask how much they want to tip, receives a numeric response, and then gives a gratitude message responding to the amount tipped
    if ctx.channel.id != targetChannelID:  #Checks to see if the command is being called in the correct channel ID
        return
    if not isOpen:  #Checks to see if the café is currently open
        await ctx.send('I\'m sorry, but you\'ll have to come back later! The café is currently closed!')
        return

    amount = 0
    response = ''

    await ctx.send('How much would you like to tip? (Please send respond only with digits/numbers)')  #Send a message to the user asking for a tip

    def check(message):  #function to wait for response
        return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit()

    try:
        response = await bot.wait_for('message', check=check, timeout=60)
        amount = int(response.content)  #Stores the user's response
    except asyncio.TimeoutError:  #Error handling
        await ctx.send('No response received. Please try again.')

    if amount < 0:
        response = 'Eh?! We won\'t pay you for eating here! Goodbye!'
    if amount == 0:
        response = 'Goodbye!'
    if amount > 0 and amount < 10:
        response = 'Thank you for your tip! Have a nice day!'
    if amount >= 10 and amount < 25:
        response = 'Whoa! Thank you so much! Have a great day!'
    if amount >= 25 and amount < 50:
        response = 'This is a lot! Thank you so very much! Have an amazing day!'
    if amount >= 50:
        response = 'Holy cow! I hope you have all the good luck today!'
    await ctx.send(response)

    
@bot.command()
async def shutdown(ctx):
    if ctx.channel.id != targetChannelID:  #Checks to see if the command is being called in the correct channel ID
        return
    if adminRoleID not in [role.id for role in ctx.author.roles]:  #Checks to see if user has the admin role
        await ctx.send('Sorry, but you\'re not authorized to use this command.')
    if not isOpen:  #Checks to see if the café is currently open
        await ctx.send('I\'m sorry, but you\'ll have to come back later! The café is currently closed!')
        return
    store_item_list_in_database(menu, "menu")
    print('Uploaded and saved menu list to replit database')

    # db['userIDs'] = userIDs
    # print('UserIDs\' lists of items are already stored')
    # for x in userIDs: Might not be necessary if stuff is stored as part of each user's items list in !bill and !order
    #     tempList = userIDs[x]
    #     serializedList = json.dumps([sItem.__dict__ for sItem in tempList])
    #     db[x] = serializedList
    # print("Uploaded and saved all userIDs' lists to replit database")
    print('Bot is now shutting down gracefully.')
    await bot.close()

    
@bot.event 
async def on_disconnect():
    # db["menu"] = menu
    # print('Uploaded and saved menu list to replit database')
    # db["userItems"] = userItems
    # print("Uploaded and saves userItems dictionary to replit database")
    serializedMenu = json.dumps([sItem.__dict__ for sItem in menu])
    db["menu"] = serializedMenu
    
    print('Uploaded and saved menu list to replit database')
    # db['userIDs'] = userIDs
    
    # for x in userIDs: 
    #     tempList = userIDs[x]
    #     serializedList = json.dumps([sItem.__dict__ for sItem in tempList])
    #     db[x] = serializedList
    # print("Uploaded and saved all userIDs' lists to replit database")
    print('Bot is now shutting down gracefully.')

tracemalloc.start()
bot.run(mySecret)
