from config_reader import config
from telethon import TelegramClient
from telethon.functions import messages
import asyncio
import random
import logging
try:
   loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
class Scraper:
    def __init__(self, channels: list[int], api_id: int, api_hash: int, chat: str, topic_number, loop=loop):
        self.channels = channels
        self.api_id = api_id
        self.api_hash = api_hash
        self.chat = chat
        self.loop = loop
        self.topic_number = topic_number
    async def run(self):
        async with TelegramClient('tests', api_id=self.api_id, api_hash=self.api_hash, loop=self.loop) as client:
           
            for i in range(len(self.channels)):
                try:
                    unread_count = await self.get_unread_count(client, self.channels[i])
                    if unread_count==0:
                        continue
                    if i == 0:
                        await client.send_message(
                            self.chat,
                            'разделитель',
                            reply_to=self.topic_number
                        )
                    result = await client(messages.GetHistoryRequest(
                        offset_id=0,
                        peer=self.channels[i],
                        offset_date=None,
                        limit=unread_count,
                        max_id=0,
                        min_id=0,
                        hash=0,
                        add_offset=0
                    ))
                    ids = await self.get_messages_id(result.messages)
                    await asyncio.sleep(random.uniform(1.0, 3.0))   
                    await self.print_logging_info(client, self.channels[i], )
                    await asyncio.sleep(random.uniform(1.0, 3.0))
                    for j in ids:
                        await client(messages.ForwardMessagesRequest(
                            from_peer=self.channels[i],
                            id=[j],
                            to_peer=self.chat,
                            top_msg_id=self.topic_number
                        ))
                        await asyncio.sleep(random.uniform(1.0, 3.0))
                    
                    await client.send_read_acknowledge(self.channels[i])
                except BaseException as e:
                    print(f'возникла ошибка {e}, поэтому канал был переключен на следующий')
                    continue
                    

    async def get_unread_count(self, client:TelegramClient, channel_id: int) -> int:
        result = await client(messages.GetPeerDialogsRequest(
            peers=[channel_id]
        ))
        await asyncio.sleep(random.uniform(1.0, 3.0))
        return result.dialogs[0].unread_count
    async def get_messages_id(self, messages: list)->list:
        ids = []
        for message in messages:
            if message.message and not message.reply_markup and not "подпишись" in message.message.lower() and not "подписывайся" in message.message.lower():
                ids.append(message.id)
        return ids
    async def print_logging_info(self, client: TelegramClient, channel_id: int) -> None:
        entity = await client.get_entity(channel_id)
        logging.info(f'сейчас обрабатывается канал {entity.title}')
        return 
scr = Scraper(
    [
        -1003139434293,
        -1001769535202,
        -1002442326603,
        -1002081183087,
        -1001639833661,
    ],
    config.api_id.get_secret_value(),
    config.api_hash.get_secret_value(),
    config.chat.get_secret_value(),
    7
    )
if __name__=="__main__":
    asyncio.run(scr.run())
        