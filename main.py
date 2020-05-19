import os
from urllib import request
import discord
from dotenv import load_dotenv
import json
import asyncio

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
twitch_client_id = os.getenv("TWITCH_CLIENT_ID")
twitch_client_secret = os.getenv("TWITCH_CLIENT_SECRET")
oauth_token = os.getenv("OAUTH_TOKEN")
channel_id = os.getenv("CHANNEL_ID")
game_id = os.getenv("GAME_ID")
client = discord.Client()
stream_search_url = f"https://api.twitch.tv/helix/streams?game_id={game_id}"
hdr = {"Client-ID": twitch_client_id, "Authorization": f"Bearer {oauth_token}"}

posted_stream_ids = []
@client.event
async def main(channel):
    online_stream_ids = []
    req = request.Request(stream_search_url, headers=hdr)
    twitch_bytes = request.urlopen(req).read()
    twitch_json = json.loads(twitch_bytes.decode())
    stream_dicts = [stream_dict for stream_dict in twitch_json["data"]]
    for stream_dict in stream_dicts:
        stream_id = stream_dict["id"]
        online_stream_ids.append(stream_id)
        if stream_id in posted_stream_ids:
            continue
        username = stream_dict["user_name"]
        stream_url = f"https://www.twitch.tv/{username}"
        stream_title = stream_dict["title"]
        await channel.send(f"{username} is streaming \"{stream_title}\" live"\
                f"at {stream_url} with id {stream_id}")
        posted_stream_ids.append(stream_id)
    await remove_old_streams(channel, online_stream_ids, posted_stream_ids)

@client.event
async def remove_old_streams(channel, online_stream_ids, posted_stream_ids):
    async for message in channel.history():
        posted_id = message.content[-11:]
        if posted_id not in online_stream_ids:
            try:
                posted_stream_ids.remove(posted_id)
            except ValueError:
                pass
            await message.delete()
    

@client.event
async def on_ready():
    channel = client.get_channel(channel_id)
    while True:
        await main(channel)
        await asyncio.sleep(60)

client.run(token)
