#!/usr/bin/env python3

from datetime import datetime, time, timedelta, timezone
import discord, requests, asyncio
from discord.ext import commands

CHANNEL_NOTIFY = 318793375136481280
CHANNEL_BOT_LOG = 804209525585608734

ROLE_CHAD = 856529519186673694

ROLE_VIS_WAX = 858911901492445184
ROLE_TMS = 676760858868711436
ROLE_YEWS = 859158679713742889
ROLE_GOEBIEBANDS = 483236107396317195

USER_AGENT = 'wbu_notify_bot'
TMS_ENDPOINT = 'https://api.weirdgloop.org/runescape/tms/current'

client = commands.Bot(command_prefix='.')

@client.listen('on_ready')
async def on_ready():
    print(f'Logged is as {client.user}')
    client.loop.create_task(notify_tms())
    client.loop.create_task(notify_wax())
    client.loop.create_task(notify_yews())
    client.loop.create_task(notify_goebiebands())

# Why we use asyncio sleeps instead of cron
# This is intended to be a drop-in bot that you can clone and run
# after changing the constants up top, so I don't want to add addiniotaly
# config steps with 'copy this into your cron' or 'run this script to
# copy shit into your cron.d'. This makes everything simple and
# self-contained

def secs_until_next(target):
    """
    Accepts a offset-naive time of day, and returns seconds until the next
    occurence of that time until now. Everything is assumed to be in UTC.
    """
    # Handle everything in offset-naive times
    assert(target.tzinfo == None)
    now = datetime.utcnow()
    if target > now.time():
        # Cant subtract two datetime.time objects
        # They have to be datetime objects to get a timedelta
        targetdt = datetime.combine(datetime.today(), target)
    else:
        tmr = datetime.today() + timedelta(days=1)
        targetdt = datetime.combine(tmr, target)
    return (targetdt - now).total_seconds()


async def send_to_channel(id, msg):
    await client.get_channel(id).send(msg)


def get_tms_stock():
    # Can switch to aiohttp if needed
    TMS_PARAMS = {'lang': 'en'}
    TMS_HEADERS = {'user-agent': USER_AGENT}
    r = requests.get(TMS_ENDPOINT, params=TMS_PARAMS, headers=TMS_HEADERS)
    return r.json()


async def notify_tms():
    while not client.is_closed():
        delta = secs_until_next(time(hour=0, minute=10))
        print(f'TMS notification in {delta/60/60} hours')
        await asyncio.sleep(delay=delta)

        stock = get_tms_stock()
        stock_msg = ', '.join(stock[1:])

        await send_to_channel(CHANNEL_NOTIFY, 
            f"<@&{ROLE_TMS}> Merch stock today: {stock_msg}")


async def notify_wax():
    while not client.is_closed():
        delta = secs_until_next(time(hour=0, minute=15))
        print(f'Vis wax notification in {delta/60/60} hours')
        await asyncio.sleep(delay=delta)

        await send_to_channel(CHANNEL_NOTIFY, 
            f"<@&{ROLE_VIS_WAX}> runes for today posted above.")


async def notify_yews():
    while not client.is_closed():
        yews_reset = secs_until_next(time(hour=0, minute=0))
        yews_1750 = secs_until_next(time(hour=17, minute=50))
        delta = min(yews_1750, yews_reset)
        print(f'Yews notification in {delta/60/60} hours')
        await asyncio.sleep(delay=delta)

        await send_to_channel(CHANNEL_NOTIFY, 
            f"<@&{ROLE_YEWS}> happening now.")


async def notify_goebiebands():
    while not client.is_closed():
        wave1 = secs_until_next(time(hour=0, minute=0))
        wave2 = secs_until_next(time(hour=12, minute=0))
        delta = min(wave1, wave2)
        print(f'Goebiebands notification in {delta/3600} hours')
        await asyncio.sleep(delta)

        await send_to_channel(CHANNEL_NOTIFY,
            f'<@&{ROLE_GOEBIEBANDS}> Gobiebands wave now.')
        pass


import sys
if len(sys.argv) < 2:
    print("Usage: ./wbunotify.py <token>")
client.run(sys.argv[1])
