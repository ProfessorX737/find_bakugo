import config
import datetime
import time
import asyncio
import re

class Tasks:
  def __init__(self, bot, non_roll_channel, roll_channel, pokemon_channel,\
    claim_reset, claim_available,\
    num_rolls_left, rolls_reset,\
    daily_available, daily_reset,\
    dk_available, dk_reset):
    self.bot = bot
    self.non_roll_channel = non_roll_channel
    self.roll_channel = roll_channel
    self.pokemon_channel = pokemon_channel
    self.claim_reset = claim_reset
    self.claim_available = claim_available
    self.num_rolls_left = num_rolls_left
    self.rolls_reset = rolls_reset
    self.daily_available = daily_available
    self.daily_reset = daily_reset
    self.dk_available = dk_available
    self.dk_reset = dk_reset
    self.msgka = {}

  async def wait_for_claim(self):
    while True:
      x = (self.claim_reset - datetime.datetime.now()).total_seconds()
      await asyncio.sleep(x)
      self.claim_reset += datetime.timedelta(seconds=config.CLAIM_DURATION_SECS)
      self.claim_available = True
  
  async def wait_for_daily(self):
    if not self.daily_available and not self.daily_reset: return
    while True:
      if self.daily_available:
        print('attempting to get free daily roll')
        await self.non_roll_channel.send(f'{config.COMMAND_PREFIX}daily')
      x = (self.daily_reset - datetime.datetime.now()).total_seconds()
      self.daily_reset += datetime.timedelta(seconds=config.DAILY_DURATION_SECS)
      print(f'wait for daily sleeping for {x} seconds till next daily reset')
      await asyncio.sleep(x)
      self.daily_available = True

  async def wait_for_dk(self):
    if not self.dk_available and not self.dk_reset: return
    while True:
      if self.dk_available:
        print('attempting to get free daily kakera')
        await self.non_roll_channel.send(f'{config.COMMAND_PREFIX}dk')
      x = (self.dk_reset - datetime.datetime.now()).total_seconds()
      self.dk_reset += datetime.timedelta(seconds=config.DK_DURATION_SECS)
      print(f'dk sleeping for {x} seconds for reset')
      await asyncio.sleep(x)
      self.dk_available = True
  
  async def wait_for_p(self):
    if not self.pokemon_channel: return
    while True:
      print('attempting to do a pokemon roll')
      await self.pokemon_channel.send(f'{config.COMMAND_PREFIX}p')
      print(f'wait for {config.P_DURATION_SECS} seconds for pokemon roll reset')
      await asyncio.sleep(config.P_DURATION_SECS)
  
  def check_roll(self, message):
    isNotOk = message.author.id != config.MUDAE_ID or\
      message.channel.id != config.ROLL_CHANNEL_ID or\
      len(message.embeds) != 1
    if isNotOk: return False
    desc = message.embeds[0].description
    # if someone is looking up a character using 'im' then it will
    # contain words 'Claim Rank' in the desc so ignore this message
    if "Claim Rank" in desc: return False
    return True
  
  # assume valid roll message
  # return true if we want to claim this roll immediately otherwise false
  # if not claimed append to map message.id => kakera value
  async def parse_roll(self, message):
    # parse the roll to get the name, series and kakera value
    embed = message.embeds[0]
    name = embed.author.name
    desc = embed.description
    footer = embed.footer.text
    if footer and 'Belongs to' in footer:
      print('Attempting to get kakera from claimed character')
      await message.add_reaction(config.REACT_EMOJIS[0])
      return False
    # if last line of desc is not the following then roll is not claimable
    #if 'React with any emoji to claim' not in desc[-1]: return False
    # TODO series name may be split into multiple lines, do a join instead
    series = None
    # extract the kakera value. It is usually the second last line in desc
    match = re.search(r'\*\*(\d+)\*\*<:kakera:', desc)
    kakera = 0
    if match: kakera = int(match.group(1))
    print(f'{name} worth {kakera} kakera')
    return {
      'name': name,
      'series': series,
      'kakera': kakera
    }
  
  def check_claimed(self, message):
    if message.author.id != config.MUDAE_ID or\
      message.channel.id != config.ROLL_CHANNEL_ID:
      return False
    match = re.search(f"\*\*{self.bot.user.name}\*\* and \*\*.*?\*\* are now married!", message.content)
    if not match: return False
    return True
  
  async def claim_waifu(self, message):
    for emoji in config.REACT_EMOJIS:
      try:
        # sleep for claim_delay_secs before claiming
        await asyncio.sleep(config.CLAIM_DELAY_SECS)
        # attempt to claim the character on a different thread
        self.bot.loop.create_task(message.add_reaction(emoji))
        # wait for mudae to confirm whether I was able to claim
        res = await self.bot.wait_for('message', check=self.check_claimed, timeout=config.MESSAGE_WAIT_SECS)
      except asyncio.TimeoutError:
        print('Failed to claim...')
      else:
        print('Successful claim')
        # if claim was successful then set claim_available to true
        self.claim_available = False
        return True
    return False
  
  async def wait_for_roll(self):
    while True:
      # if cannot claim wait for next claim reset 
      if not self.claim_available:
        # the next rolls reset to be claim reset + rolls duration
        self.rolls_reset = self.claim_reset + datetime.timedelta(seconds=config.ROLLS_DURATION_SECS)
        x = (self.claim_reset - datetime.datetime.now()).total_seconds()
        print(f'waiting {x} seconds till next claim reset')
        await asyncio.sleep(x)
      # empty the message_id => {kakera, message} map
      self.msgka = {}
      # start rolling
      for i in range(self.num_rolls_left):
        await asyncio.sleep(config.ROLL_DELAY_SECS)
        # don't roll if we don't have a claim
        if not self.claim_available: break
        print(f'roll {i+1}')
        try:
          # send the roll command but on a different thread
          self.bot.loop.create_task(self.roll_channel.send(f'{config.COMMAND_PREFIX}{config.ROLL_COMMAND}'))
          # wait for response from mudae
          message = await self.bot.wait_for('message', check=self.check_roll, timeout=config.MESSAGE_WAIT_SECS)
        except asyncio.TimeoutError:
          print('could not find mudae roll response')
          break
        else:
          roll = await self.parse_roll(message)
          # continue if roll is not claimable
          if not roll: continue
          # if roll is a wish
          if message.content != '':
            # if is one of my wishes my user_id will be in the message_content
            if str(config.USER_ID) in message.content:
              print('Attempting to claim my wish')
              await self.claim_waifu(message)
            # else is someone else's wish
            else:
              # wait some time before claiming for them
              await self.roll_channel.send(f'Will claim wish in {config.OTHERS_WISH_WAIT_SECS} secs if no one claims')
              await asyncio.sleep(config.OTHERS_WISH_WAIT_SECS)
              await self.claim_waifu(message)
          # else if it is an expensive character then claim
          elif roll['kakera'] >= config.MIN_KAKERA_CLAIM:
            print('Attempting to claim expensive character for the $$')
            await self.claim_waifu(message)
          # else roll is claimable but not worth enough to claim immediately
          else:
            # add roll to message_id => kakera map
            self.msgka[message.id] = [roll['kakera'], message]
      
      x = (self.claim_reset - datetime.datetime.now()).total_seconds()
      # if last set of rolls till next claim reset then claim most expensive
      if self.claim_available and x < config.ROLLS_DURATION_SECS and len(self.msgka) > 0:
        # claim the most expensive character found for the $$
        print("Attempting to claim because last set of rolls till next claim reset")
        msg_id = sorted(self.msgka, key=lambda x: self.msgka[x][0])[-1]
        await self.claim_waifu(self.msgka[msg_id][1])

      # get seconds till rolls reset
      x = (self.rolls_reset - datetime.datetime.now()).total_seconds() + 5
      # set next time to roll
      self.rolls_reset += datetime.timedelta(seconds=config.ROLLS_DURATION_SECS)
      # sleep until ready to roll
      print(f'waiting {x} seconds till next set of rolls')
      await asyncio.sleep(x)
      self.num_rolls_left = config.NUM_ROLLS







