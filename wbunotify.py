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

    client.loop.create_task(create_specific_time_notif(
        name='Travelling Merchant',
        times=[time(hour=0, minute=5)],
        channel=CHANNEL_NOTIFY,
        msgfn=get_tms_message
    ))

    client.loop.create_task(create_specific_time_notif(
        name='Vis wax',
        times=[time(hour=0, minute=10)],
        channel=CHANNEL_NOTIFY,
        msgfn=lambda: f'<@&{ROLE_VIS_WAX}> runes for today posted above (or below if the vis wax fc got delayed).'
    ))

    client.loop.create_task(create_specific_time_notif(
        name='Reset yews',
        times=[time(hour=23, minute=45)],
        channel=CHANNEL_NOTIFY,
        msgfn=lambda: f'<@&{ROLE_YEWS}> yews starting on world 48.'
    ))

    client.loop.create_task(create_specific_time_notif(
        name='140 yews',
        times=[time(hour=17, minute=45)],
        channel=CHANNEL_NOTIFY,
        msgfn=lambda: f'<@&{ROLE_YEWS}> yews starting on world 140.'
    ))

    client.loop.create_task(create_specific_time_notif(
        name='Goebiebands',
        times=[time(hour=11, minute=45), time(hour=23, minute=45)],
        channel=CHANNEL_NOTIFY,
        msgfn=lambda: f'<@&{ROLE_GOEBIEBANDS}> starting in 15 minutes.'
    ))


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


def create_specific_time_notif(name, times, channel, msgfn):
    """
    Params:
    - times: list of `datetime.time` objects that will determine when
      the message will go out
    - channel: which channel to send the message
    - msgfn: message to call with time of day for the ping message
    """
    async def notiffn():
        mindelta = 60 * 60 * 24
        for t in times:
            s = secs_until_next(t)
            mindelta = min(mindelta, s)
        print(f'Notifying about {name} in {mindelta/60/60:5} hours')
        await asyncio.sleep(delay=mindelta)

        msg = msgfn()
        await send_to_channel(channel, msg)

    return notiffn()


def get_tms_message():
    # Can switch to aiohttp if needed
    TMS_PARAMS = {'lang': 'en'}
    TMS_HEADERS = {'user-agent': USER_AGENT}
    r = requests.get(TMS_ENDPOINT, params=TMS_PARAMS, headers=TMS_HEADERS)
    j = r.json()
    stock = ', '.join(j[1:])
    return f'<@&{ROLE_TMS}> stock today: {stock}'


import sys
if len(sys.argv) < 2:
    print("Usage: ./wbunotify.py <token>")
client.run(sys.argv[1])
