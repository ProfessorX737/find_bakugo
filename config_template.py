# THIS IS TEMPLATE ONLY, TO MAKE REAL CHANGES DO IT IN config.py

# To find your secret user token:
# go to discord on your browser and go to
# developer tools ==> application ==> local storage ==> https://dicord.com
# filter for 'token' and select the phone/tablet toggle button on top left
# DO NOT SHARE YOUR TOKEN WITH ANYONE!

# To find the IDS:
# switch to dev mode in discord
# in user_settings ==> advanced ==> developer mode
# now you can right click on anything and there is an option to copy its ID

############## MUST SET: ################
BOT_NAME = '<name of user/bot>'
TOKEN = "<your secret user token>"
USER_ID = 123456789123456789
ROLL_CHANNEL_ID = 123456789123456789
NON_ROLL_CHANNEL_ID = 123456789123456789
MUDAE_ID = 123456789123456789
# optional
POKEMON_CHANNEL_ID = None 
#########################################

COMMAND_PREFIX = '$'
ROLL_COMMAND = 'ma'

ROLL_DELAY_SECS = 2
CLAIM_DURATION_SECS = 3*60*60
ROLLS_DURATION_SECS = 60*60
MESSAGE_WAIT_SECS = 3
OTHERS_WISH_WAIT_SECS = 10
MIN_KAKERA_CLAIM = 300
NUM_ROLLS = 8
DAILY_DURATION_SECS = 24*60*60
DK_DURATION_SECS = 24*60*60
P_DURATION_SECS = 2*60*60

REACT_EMOJI = '🤖'