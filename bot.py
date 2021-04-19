import re
import discord
import datetime
import asyncio
from discord.ext.commands import Bot
from parsers import parse_tu
import config as conf
import sys
from tasks import Tasks
import threading
from concurrent.futures import ThreadPoolExecutor
import time

bot = Bot(command_prefix='>', self_bot=True)

# declare global tasks object
tasks: Tasks

roll_channel = None
non_roll_channel = None
mudae = None

info = {
  'claim_reset': None,
  'claim_available': None,
  'num_rolls': 0,
  'rolls_reset': None,
}


@bot.event
async def on_ready():
  global info, tasks, non_roll_channel, roll_channel, user
  print(f'Bot connected as {bot.user.name}')
  non_roll_channel = bot.get_channel(conf.NON_ROLL_CHANNEL_ID)
  roll_channel = bot.get_channel(conf.ROLL_CHANNEL_ID)
  await non_roll_channel.send(f'{conf.COMMAND_PREFIX}tu')
  try:
    message = await bot.wait_for('message', check=parse_tu, timeout=3)
    info = parse_tu(message)
  except asyncio.TimeoutError:
    print("could not parse tu, try running bot again")
    sys.exit()
  else:
    tasks = Tasks(bot, non_roll_channel, roll_channel,\
      info['claim_reset'], info['claim_available'],\
        info['num_rolls'], info['rolls_reset'])
    bot.loop.create_task(tasks.wait_for_roll())
    bot.loop.create_task(tasks.wait_for_claim())

# async def parse_roll(message):
#   raise Exception("")

# async def loop():
#   while True:
#     try:
#       message = await bot.wait_for('message', check=parse_tu, timeout=3)
#     except Exception as err:

#     else:

# @bot.event
# async def on_message(message):
#   print(message)


@bot.command(name='chicken')
async def fetchServerInfo(ctx):
  await ctx.send("hello there")

bot.run(conf.TOKEN, bot=False)
