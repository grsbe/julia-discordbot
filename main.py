from interactions import Client, Intents, User, listen, DMChannel
from interactions import slash_command, SlashContext, slash_option, OptionType
from interactions import Task, TimeTrigger, IntervalTrigger
from interactions import check, has_any_role, is_owner
import os, re, random

import logging

logging.basicConfig()
cls_log = logging.getLogger("MyLogger")
cls_log.setLevel(logging.DEBUG)


bot = Client(intents= Intents.GUILDS | Intents.MESSAGES | Intents.PRIVILEGED,
             logger=cls_log)
# intents are what events we want to receive from discord, `DEFAULT` is usually fine
# add REACTIONS if necessary at any point


@listen()
async def on_message_create(event):
    # This event is called when a message is sent in a channel the bot can see
    if event.message.author.id in [bot.user.id, 503720029456695306]:
        print(f"{event.message.author.display_name} sent: {event.message.content}")
        return
    
    if isinstance(event.message.channel, DMChannel):
        print(f"{event.message.author.display_name} sent in dms: {event.message.content}")
        await event.message.reply(random.choice(open("db/pickuplines.txt",encoding="utf8").read().splitlines()))
        return

    if event.message.author.has_role(1166158428054507540):
        await event.message.delete()
        if random.randint(0,3) == 0:
            await event.message.channel.send("<:xdd:1143506212114157569>")
            if random.randint(0,9) == 0:
                await event.message.author.remove_role(1166158428054507540)
        return

    if random.randint(0,1000000) == 0:
        await event.message.author.add_role(1166158428054507540)
        await event.message.delete()
        await event.message.channel.send("Your free trial of text messages on this server has now been expired. Consider yourself lucky, the chance of this happening was 1 in 1.000.000  <:LUL:706159727523921931>")
        return

    if re.search("[Jj]ulia", event.message.content):
        await event.message.reply("https://media.discordapp.net/attachments/1014647837516120134/1238589463010213969/image.png?ex=67c4c053&is=67c36ed3&hm=b4bc367101c5c716c6a10c246d06dfa347bf0ec26e2008e1c25b98f399e8a1d3&format=webp&quality=lossless&")

    if re.search("[Uu]w[Uu]", event.message.content):
        await event.message.reply("OWO ヾ(≧▽≦*)o")
        return
    if re.search("[Oo]w[Oo]", event.message.content):
        await event.message.reply("UWU (✿◡‿◡)")
        return

    matchobj = re.search("[iI]ch bin ", event.message.content)
    if matchobj:
        await event.message.reply("Hallo "+ event.message.content[(matchobj.span()[1]):] + ", ich bin Julia. <:LUL:706159727523921931>")
    return
    # print(f"message received: {event.message.content}")

@slash_command(name="uwufy", description="Uwufies the input")
@slash_option(
    name="uwufy_this",
    description="Uwufy this",
    required=True,
    opt_type=OptionType.STRING
)
async def uwufy(ctx: SlashContext, uwufy_this: str):
    await ctx.send(uwufy_this.replace('r','w').replace("l","w"))

@slash_command(name="pm", description="Secret")
@slash_option(
    name="pm",
    description="pm",
    required=True,
    opt_type=OptionType.STRING
)
@check(is_owner())
async def pm(ctx: SlashContext, pm: str):
    await ctx.send("ok", ephemeral= True)
    await ctx.channel.send(pm)

# @slash_command(name="pfchange", description="update the profile pic of julia")
# @check(is_owner())
# async def pf(ctx: SlashContext):
#     print(f"changing pfpic")
#     await bot.user.edit(avatar="2juliachan.gif")
#     print("changed pfpic")

@slash_command(name="pun", description="Tells a pun")
async def makepun(ctx: SlashContext):
    await ctx.send(random.choice(open("db/dad-a-base.txt",encoding="utf8").read().splitlines()))

@slash_command(name="j", description="Get a decription for all commands of Julia")
async def jelp(ctx: SlashContext):
    string = '''
    My current functionality:
    /j -> to display this page
    /uwufy -> uwufies input test
    /pun -> Sends a pun
    /bday -> save your birthday so that everyone gets a reminder
    /nextbdays -> get a list of all the saved birthdays
    And if you write me a personal message, then I will rizz you up
    '''
    await ctx.send(string, ephemeral=True)

bot.load_extension("birthdaycog")

@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    print("Ready")
    print(f"This bot is owned by {bot.owner} and is called {bot.user}")
    print(f"This bot is in the guilds {bot.guilds}")

bot.start(open("db/.key",encoding="utf8").read())
#bot.start('')