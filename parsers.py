import config as conf
import re
import datetime

time_match = "\*\*((:?\d+h )?\d+)\*\*"

def parse_tu(message):
  if message.channel.id != conf.NON_ROLL_CHANNEL_ID\
    or message.author.id != conf.MUDAE_ID:
    return False
  # get username
  match = re.search("^\*\*(\w+)\*\*", message.content)
  if not match: return False
  username = match.group(1)
  if username != conf.BOT_NAME: return False
  # get claim available
  match = re.search("you (__can__|can't) claim", message.content)
  if not match: return False
  claim_available = False
  if match.group(1) == "__can__": claim_available = True
  # get claim reset
  claim_min = 0
  if claim_available: 
    match = re.search(f"next claim reset is in {time_match} min", message.content)
    claim_min = parse_hour_min(match.group(1))
  else:
    match = re.search(f"can't claim for another {time_match} min", message.content)
    claim_min = parse_hour_min(match.group(1))
  # get num rolls left
  match = re.search("You have \*\*(\d+)\*\* rolls? left", message.content)
  num_rolls = int(match.group(1))
  # get next rolls reset
  match = re.search(f"Next rolls reset in {time_match} min", message.content)
  rolls_reset_min = parse_hour_min(match.group(1))
  # get daily reset
  daily_available = False
  daily_reset = None
  match = re.search(f"Next \$daily reset in {time_match} min", message.content)
  if match:
    daily_reset = datetime.datetime.now() + datetime.timedelta(minutes=parse_hour_min(match.group(1)))
  else:
    match = re.search("\$daily is available", message.content)
    if match:
      daily_available = True
      daily_reset = datetime.datetime.now() + datetime.timedelta(minutes=conf.DAILY_DURATION_SECS + 10)
  # get dk reset
  dk_available = False
  dk_reset = None
  match = re.search(f"Next \$dk reset in {time_match} min", message.content)
  if match:
    dk_reset = datetime.datetime.now() + datetime.timedelta(minutes=parse_hour_min(match.group(1)))
  else:
    match = re.search("\$dk is ready", message.content)
    if match:
      dk_available = True
      dk_reset = datetime.datetime.now() + datetime.timedelta(minutes=conf.DK_DURATION_SECS + 10)
  # detect if pokemon roll is available
  p_available = False
  if '$p is available' in message.content: p_available = True

  timing_info = {
    'claim_reset': datetime.datetime.now() + datetime.timedelta(minutes=claim_min),
    'claim_available': claim_available,
    'num_rolls': num_rolls,
    'rolls_reset': datetime.datetime.now() + datetime.timedelta(minutes=rolls_reset_min),
    'daily_available': daily_available,
    'daily_reset': daily_reset,
    'dk_available': dk_available,
    'dk_reset': dk_reset,
    'p_available': p_available,
  }
  return timing_info

# Parse hour + min string e.g. '2h 45' or '45'
# return number of minutes
def parse_hour_min(hour_min):
  if hour_min is None: return 0
  if 'h ' in hour_min:
    hm = hour_min.split('h ')
    return int(hm[0]) * 60 + int(hm[1])
  else:
    return int(hour_min)
