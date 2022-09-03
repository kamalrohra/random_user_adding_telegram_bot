from pydoc import cli
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
api_id = "12221895"
api_hash = '014313ad539b7c75f4bef1006f189e30'
phone = '+917666255267'
client = TelegramClient(phone, api_id, api_hash)
client.start()

chats = []
last_date = None
chunk_size = 200
result = client(GetDialogsRequest(
             offset_date=last_date,
             offset_id=0,
             offset_peer=InputPeerEmpty(),
             limit=chunk_size,
             hash = 0
         ))

chats.extend(result.chats)
print("------size: ",len(chats))
for i in range(len(chats)):
    if(chats[i].title =="Career Banayenge!!"):
        print(chats[i])
data = client.get_entity(1527732953)
print(data)


client.run_until_disconnected()






