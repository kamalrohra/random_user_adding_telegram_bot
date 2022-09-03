from pydoc import cli
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import UserStatusOffline
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import ChannelParticipantsSearch
import nest_asyncio
nest_asyncio.apply()
import asyncio
loop = asyncio.get_event_loop()
import csv,io

api_id = "12221895"
api_hash = '014313ad539b7c75f4bef1006f189e30'
phone_number = '+917666255267'
################################################
channel_username = 'befbfhjjjjjj'
channel_username2 = 'testingChannel1908'
################################################

client = TelegramClient('session_name',api_id,api_hash)
client.start()
file = r"try.csv"



# ---------------------------------------
# set offset to -ve to increase the amount of users
offset = 0
limit = 200
my_filter = ChannelParticipantsSearch('')
all_participants = []
while_condition = True
# ---------------------------------------
channel = client(GetFullChannelRequest(channel_username2))
i = 0

while while_condition:
    participants = loop.run_until_complete(client(GetParticipantsRequest(channel=channel_username, filter=my_filter, offset=offset, limit=limit, hash=0)))
    # print(participants.users[0])
    print(len(participants.users))
    print("Processing for i = ",i)
    i+=1
    all_participants.extend(participants.users)
    print(len(all_participants))
    offset += len(participants.users)
    if len(participants.users) < limit:
         while_condition = False


count = 0
print(len(all_participants))
print()
# print(all_participants[0].status.was_online)
print(str(type(all_participants[0].status))=="<class 'telethon.tl.types.UserStatusOffline'>")
print(type(UserStatusOffline))
total_participants=[]


for participant in all_participants:
    participant_data = []
    if(participant.username==None):
        participant_data.append("Null")
    else:
        participant_data.append(participant.username)
    participant_data.append(participant.first_name)
    participant_data.append(participant.last_name)
    if(participant.phone!=None):
        print("Found a phone number")
    participant_data.append(str(participant.phone))
    condition1 = str(type(all_participants[0].status)) ==  "<class 'telethon.tl.types.UserStatusOffline'>"
    condition2 = str(type(all_participants[0].status)) ==  "<class 'telethon.tl.types.UserStatusLastMonth'>"
    condition3 = str(type(all_participants[0].status)) ==  "<class 'telethon.tl.types.UserStatusLastWeek'>"
    condition4 = str(type(all_participants[0].status)) ==  "<class 'telethon.tl.types.UserStatusRecently'>"
    condition5 = str(type(all_participants[0].status)) ==  "<class 'telethon.tl.types.UserStatusLastWeek'>"
    condition6 = str(type(all_participants[0].status)) ==  "<class 'telethon.tl.types.UserStatusEmpty'>"
    if(condition1 or condition4 or condition5):
        participant_data.append("active recently")
    elif(condition3):
        participant_data.append("Inactive since week")
    elif(condition6):
        participant_data.append("Status off")
    else:
        participant_data.append("Inactive since a month")
    
    
    total_participants.append(participant_data)
    # if(participant.phone != None):
    #     print("Phone: - ",participant.phone,"access_hash: - ",participant.access_hash,"  id:-",participant.id,"  name:- ",participant.first_name," username: -",participant.username ,'   count: - ',count,)
    #     count+=1
    #     print("================================================")

# # inserting into the csv
header_values = ["username","first_name","last_name","phone Number","activity status"]
# s = io.StringIO()
# data = [header_values,total_participants]
# csv.writer(s).writerows(data)
# s.seek(0)
# buf = io.BytesIO()
# buf.write(s.getvalue().encode())
# buf.seek(0)
# buf.name = f'secret_report_for_cool_guys.csv'






with open("try.csv","w",encoding="UTF8",newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header_values)
    writer.writerows(total_participants)
chats = []
last_date = None
chunk_size = 200
result = loop.run_until_complete(client(GetDialogsRequest(
             offset_date=last_date,
             offset_id=0,
             offset_peer=InputPeerEmpty(),
             limit=chunk_size,
             hash = 0
         )))
chats.extend(result.chats)
for i in range(len(chats)):
    if(chats[i].title =="Try test channel"):
        loop.run_until_complete(client.send_file(chats[i].id,file=open("try.csv",'rb')))
    
print("Finished printing")
client.run_until_disconnected()