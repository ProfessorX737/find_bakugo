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
  'daily_available': False,
  'daily_reset': None
}

@bot.event
async def on_ready():
  global info, tasks, non_roll_channel, roll_channel, user

  print(f'Bot connected as {bot.user.name}')

  non_roll_channel = bot.get_channel(conf.NON_ROLL_CHANNEL_ID)
  roll_channel = bot.get_channel(conf.ROLL_CHANNEL_ID)
  pokemon_channel = None
  if conf.POKEMON_CHANNEL_ID:
    pokemon_channel =  bot.get_channel(conf.POKEMON_CHANNEL_ID)

  # send 'tu' command to initialise the times
  await non_roll_channel.send(f'{conf.COMMAND_PREFIX}tu')
  try:
    message = await bot.wait_for('message', check=parse_tu, timeout=conf.MESSAGE_WAIT_SECS)
    info = parse_tu(message)
  except asyncio.TimeoutError:
    print("could not parse tu, try running bot again")
    sys.exit()
  else:
    tasks = Tasks(bot, non_roll_channel, roll_channel, pokemon_channel,\
      info['claim_reset'], info['claim_available'],\
      info['num_rolls'], info['rolls_reset'],\
      info['daily_available'], info['daily_reset'],\
      info['dk_available'], info['dk_reset'])
    # loop to roll and claim
    bot.loop.create_task(tasks.wait_for_roll())
    # loop to update claim availability
    bot.loop.create_task(tasks.wait_for_claim())
    # loop for free daily kakera
    bot.loop.create_task(tasks.wait_for_dk())
    # loop for free daily roll
    bot.loop.create_task(tasks.wait_for_daily())
    # loop for pokemon rolls
    bot.loop.create_task(tasks.wait_for_p())

bot.run(conf.TOKEN, bot=False)
