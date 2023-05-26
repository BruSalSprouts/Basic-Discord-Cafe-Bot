import discord
import os
import item
import tracemalloc
from replit import db 
from discord.ext import commands

menu = [] #List of items with their prices. Easy access and can be added/deleted at any time
userItems = {} #Dictionary so each each user can be found a bit more easily. key:value = username:list of user's items
isOpen = True #boolean to check whether the café is open or not

#DO NOT TOUCH UNLESS CHANGING LOCATIONS OF STUFF! IF A SIGNLE CHARACTER OF BELOW STUFF IS CHANGED EVERYTHING GOES TO SHIT!!!
mySecret = os.environ['CAFE_TOKEN'] #token to allow bot to be activated
targetChannelID = 608741870058733671 #channel where café is located
adminRoleID = 608742175928483872 #mod role

#This allows for discord to understand that the stuff I send is allowed
intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents) #Only messages that start with ! will be accepted

@bot.event #Beginning event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    isOpen = True

#use @bot.command to make commands that begin with '!' and do stuff! 
#ctx is the context message that allows for a bot to have context of what's been said while it's responding. So cool!!!

@bot.command() 
async def waitress(ctx): #The café's greeting message essentailly
    if ctx.channel.id != targetChannelID: #Checks to see if the command is being called in the correct channel ID
        return
    global isOpen
    if isOpen:
        await ctx.send('Hello there! Welcome to our café!')
    else:
        await ctx.send('Hello there! The café is currently closed, come back later!')

@bot.command() 
async def open(ctx): #Opens the café and changes isOpen to True. Only mods can do this
    if ctx.channel.id != targetChannelID: #Checks to see if the command is being called in the correct channel ID
        return
    if adminRoleID not in [role.id for role in ctx.author.roles]: #Checks to see if user has the admin role
        await ctx.send('Sorry, but you\'re not authorized to use this command.')
    global isOpen
    if isOpen: #Checks to see if the café is already open
        await ctx.send('The café is already open??')
        return
    
    isOpen = True

    #Image Sending Time
    imagePath = os.path.join(os.getcwd(), 'CafeOperations/Open-Sign-PNG-HD.png') #Gets path of image file relative to directory
    #Checks to see if the image file exists
    if not os.path.exists(imagePath):
        await ctx.send('Image file not found.')
        return
    file = discord.File(imagePath) #Create a discord.File object from the image file
    await ctx.send(file=file)
    
    await ctx.send('The café is now open!') #Finishing message

@bot.command() 
async def close(ctx): #Closes the café and changes isOpen to false. Only mods can do this
    if ctx.channel.id != targetChannelID: #Checks to see if the command is being called in the correct channel ID
        return
    if adminRoleID not in [role.id for role in ctx.author.roles]: #Checks to see if user has the admin role
        await ctx.send('Sorry, but you\'re not authorized to use this command.')
    global isOpen
    if not isOpen: #Checks to see if the café is already open
        await ctx.send('The café is already closed??')
        return
    
    isOpen = False
    #Please finish the part where the Closed sign is displayed
    #Image Sending Time
    imagePath = os.path.join(os.getcwd(), 'CafeOperations/Sorry-We-Are-Closed-PNG-Image.png') #Gets path of image file relative to directory
    #Checks to see if the image file exists
    if not os.path.exists(imagePath):
        await ctx.send('Image file not found.')
        return
    file = discord.File(imagePath) #Create a discord.File object from the image file
    await ctx.send(file=file)
    
    await ctx.send('The café is now closed!')
          
@bot.command()
async def table(ctx): #Displays a table and has little messages before and after
    if ctx.channel.id != targetChannelID: #Checks to see if the command is being called in the correct channel ID
        return
    if not isOpen: #Checks to see if the café is currently open
        await ctx.send('I\'m sorry, but you\'ll have to come back later! The café is currently closed!')
        return

    await ctx.send('Alright! Follow me to your table!') #Opening Message

    #Image Sending Time
    imagePath = os.path.join(os.getcwd(), 'CafeOperations/Dining-Room-Table-PNG-File.png') #Gets path of image file relative to directory
    #Checks to see if the image file exists
    if not os.path.exists(imagePath):
        await ctx.send('Image file not found.')
        return
    file = discord.File(imagePath) #Create a discord.File object from the image file
    await ctx.send(file=file)
    
    await ctx.send('Let me know when you\'re ready to order!') #Closing Message

@bot.command()
async def menu(ctx): #Displays the menu
    if ctx.channel.id != targetChannelID: #Checks to see if the command is being called in the correct channel ID
        return
    if not isOpen: #Checks to see if the café is currently open
        await ctx.send('I\'m sorry, but you\'ll have to come back later! The café is currently closed!')
        return 
    #Needs to be finished! So much work

@bot.command()
async def edit_menu(ctx):
    if ctx.channel.id != targetChannelID: #Checks to see if the command is being called in the correct channel ID
        return
    if adminRoleID not in [role.id for role in ctx.author.roles]: #Checks to see if user has the admin role
        await ctx.send('Sorry, but you\'re not authorized to use this command.')
    if not isOpen: #Checks to see if the café is currently open
        await ctx.send('I\'m sorry, but you\'ll have to come back later! The café is currently closed!')
        return
    #Needs to be finished! So much work! Implement menu command first before doing this!

@bot.command()
async def recommend(ctx):
    if ctx.channel.id != targetChannelID: #Checks to see if the command is being called in the correct channel ID
        return
    if not isOpen: #Checks to see if the café is currently open
        await ctx.send('I\'m sorry, but you\'ll have to come back later! The café is currently closed!')
        return
    #Needs to be finished! So much work! Implement menu command first before doing this!

@bot.command()
async def tip(ctx): #Prompts user to ask how much they want to tip, receives a numeric response, and then gives a gratitude message responding to the amount tipped
    if ctx.channel.id != targetChannelID: #Checks to see if the command is being called in the correct channel ID
        return
    if not isOpen: #Checks to see if the café is currently open
        await ctx.send('I\'m sorry, but you\'ll have to come back later! The café is currently closed!')
        return
    
    amount = 0
    response = ''

    await ctx.send('How much would you like to tip? (Please send respond only with digits/numbers)') #Send a message to the user asking for a tip
    
    def check(message): #function to wait for response
        return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit()

    try: 
        response = await bot.wait_for('message', check=check, timeout=60)
        amount = int(response.content) #Stores the user's response

        # await ctx.send(f'You entered: {amount} dollars') #Prints the stored integer
    except asyncio.TimeoutError: #Error handling
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




tracemalloc.start()
bot.run(mySecret)
