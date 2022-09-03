from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError,ChatAdminRequiredError

class Helper:
    def __init__(self,client) -> None:
        self.__client = client


    async def check_if_exists(self,username,update):
        try:
            offset = 0
            limit = 200
            my_filter = ChannelParticipantsSearch('')
            participanst = await self.__client(GetParticipantsRequest(channel=int(username), filter=my_filter, offset=offset, limit=limit, hash=0))
            print(participanst)
            return True
        except ChatAdminRequiredError:
            update.message.reply_text("You need to be an admin to get the csv")
            print("")
        except TypeError:
            update.message.reply_text("The group/channel does not exist or is private")
        except Exception as e:
            print(type(e))
            print(e)
            return False
        
    async def getAllChats(self):
        chatid=[]
        chatname=[]
        async for dialog in self.__client.iter_dialogs():
            if not dialog.is_group and not dialog.is_channel:
                
                pass
                
            elif dialog.is_channel:
                # #print("Channels",dialog.name,dialog.message.peer_id.channel_id,dialog.entity.participants_count)
                # real_id, peer_type = utils.resolve_id(dialog.message.peer_id)
                chatid.append(dialog.message.peer_id.channel_id)
                chatname.append(dialog.name)
                # #print(dialog.message.peer_id)

            else:
                # #print(dialog)
                # #print("Groups ",dialog.name,dialog.message.peer_id.chat_id,dialog.entity.participants_count)
                chatid.append(dialog.message.peer_id.chat_id)
                chatname.append(dialog.name)
                # real_id, peer_type = utils.resolve_id(dialog.message.peer_id)
                # #print(dialog.message.peer_id)
                # #print(real_id)
                # if(dialog.)
        return [chatid ,chatname]