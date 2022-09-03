from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser,Channel,Chat,ChatForbidden,ChannelForbidden
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError,ChatWriteForbiddenError,ChatAdminRequiredError
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import UserStatusOffline
import sys
import csv
import traceback
import time
import random
import time
import nest_asyncio
import io
import time

from datasource import Datasource
nest_asyncio.apply()
import pandas as pd

datasource = Datasource("postgres://david_user:password@localhost:5432/david")
class Users:
    def __init__(self,client,inp_file,loop,bot) -> None:
        self.__client = client
        self.__input_file = inp_file
        self.__loop = loop
        self.__bot = bot
        self.__groups = []

    async def  __get_mega_groups(self,update):
        chats = []
        last_date = None
        chunk_size = 200
        groups=[]
        result = await self.__client(GetDialogsRequest(
                    offset_date=last_date,
                    offset_id=0,
                    offset_peer=InputPeerEmpty(),
                    limit=chunk_size,
                    hash = 0
                ))
        chats.extend(result.chats)

        for chat in chats:
            try:
                if (chat.participants_count>500 and chat.megagroup == True and (type(chat)==Channel or type(chat)==Chat) ):
                    print(chat.participants_count)
                    groups.append(chat)
            except:
                continue
        if(len(groups)) ==0:
            return -1
        return groups
    
    async def select_random_group_and_generate_file(self,update):
        update.message.reply_text("Choosing random users please wait")
        groups = await self.__get_mega_groups(update)
        if(groups==-1):
            return
        rand = random.randint(0,len(groups)-1)
        target_group = groups[rand]
        target_group_entity = target_group.id
        print(target_group.title)
        user_data = await self.__get_users_data(target_group_entity)
        final_users =  []
        for user in user_data:
            users_array = []
            users_array.append(user.username)
            users_array.append(user.id)
            users_array.append(user.access_hash)
            final_users.append(users_array)
        print(final_users[:10])
        headers = ["username","id","access_hash"]
        self.generate_csv(headers,final_users,"add.csv")
        
        print("Done getting the data")


    #private method to be used only inside this class
    # @description : to prepare the users array from the csv file
    def __prepare_users_array(self):
        users = []
        with open("add.csv", encoding='UTF-8') as f:
            rows = csv.reader(f,delimiter=",",lineterminator="\n")
            next(rows, None)
            for row in rows:
                user = {}
                user['username'] = row[0]
                user['id'] = int(row[1])
                user['access_hash'] = int(row[2])
                users.append(user)
        return users
    
    #private method to be used only inside this class
    # @description : To return all the group members 
    async def __get_all_groups(self):
        chats = []
        last_date = None
        chunk_size = 200
        result = await self.__client(GetDialogsRequest(
             offset_date=last_date,
             offset_id=0,
             offset_peer=InputPeerEmpty(),
             limit=chunk_size,
             hash = 0
        ))
        chats.extend(result.chats)
        
        return chats
    
    # @description : To iterate through all the groups and return the selected one 
    async def return_selected_group(self):
        self.__groups= await self.__get_all_groups()
        
        print('Choose a group to add members:')
        i=0
        string = ""
        megagroups = []
        for group in self.__groups:
            print(i)
            print(group)
            if(type(group)!=ChatForbidden and type(group)!=ChannelForbidden and group.admin_rights  ):
                megagroups.append(group)

        self.__groups = megagroups
        for group in megagroups:
            string += str(i) + '- ' + group.title +'\n'
            print(str(i) + '- ' + group.title)
            i+=1
        print(self.__groups)
        # g_index = input("Enter a Number: ")
        # 
        # return this for testing purposes channel name = Try test channel 
        # target_group_entity = InputPeerChannel(1709142539,-8772168828802651668)
        # return InputPeerChannel(target_group.id,target_group.access_hash)
        return string
    
    # @description : adds the members using csv file
    # Todo : just for testing purposes to check if it adds groups
    async def add_members(self,index,update):
        target_group=self.__groups[int(index)]
        update.message.reply_text("Preparing users to add")
        n = 0
        count = 0
        users = self.__prepare_users_array()
        print("Adding to : - ",target_group.title)
        target_group_entity = InputPeerChannel(target_group.id,target_group.access_hash)
        update.message.reply_text("Started Adding")
        mode = 1
        for user in users:
            n += 1
            if n % 50 == 0:
                print("50 users added")
                update.message.reply_text("try again after 15 to 20 mins")
                return
                # return
            try:
                print ("Adding {}".format(user['id']))
                if mode == 1:
                    if user['username'] == "":
                        continue
                    user_to_add = await self.__client.get_input_entity(user['username'])
                    print(user_to_add)
                elif mode == 2:
                    user_to_add = InputPeerUser(user['id'], user['access_hash'])
                else:
                    sys.exit("Invalid Mode Selected. Please Try Again.")
                await self.__client(InviteToChannelRequest(target_group_entity,[user_to_add]))
                print("Waiting for 5-10 Seconds...")
                time.sleep(random.randint(5,10))
            except PeerFloodError:
                count +=1
                time.sleep(60)
                return
            except UserPrivacyRestrictedError:
                print("The user's privacy settings do not allow you to do this. Skipping.")
            except:
                traceback.print_exc()
                print("Unexpected Error")
                continue
    
    #----------------------- Functions for adding people to csv file are given here ----------------------
    async def __get_users_data(self,channel_username):
        
        # play with these params to increase or decrease the participants count
        offset = 0
        limit = 200
        my_filter = ChannelParticipantsSearch('')
        all_participants = []
        while_condition = True
        # ---------------------------------------
        # channel = self.__client(GetFullChannelRequest(channel_username))
        i = 0

        while while_condition:
            participants = await self.__client(GetParticipantsRequest(channel=int(channel_username), filter=my_filter, offset=offset, limit=limit, hash=0))
            print(len(participants.users))
            print("Processing for i = ",i)
            i+=1
            all_participants.extend(participants.users)
            print(len(all_participants))
            offset += len(participants.users)
            if len(participants.users) < limit:
                while_condition = False
        return all_participants
    
    async def prepare_users_csv_data(self,channel_username,file):
        all_participants = await self.__get_users_data(channel_username)
        total_participants = []
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
            condition1 = str(type(participant.status)) ==  "<class 'telethon.tl.types.UserStatusOffline'>"
            condition2 = str(type(participant.status)) ==  "<class 'telethon.tl.types.UserStatusLastMonth'>"
            condition3 = str(type(participant.status)) ==  "<class 'telethon.tl.types.UserStatusLastWeek'>"
            condition4 = str(type(participant.status)) ==  "<class 'telethon.tl.types.UserStatusRecently'>"
            condition5 = str(type(participant.status)) ==  "<class 'telethon.tl.types.UserStatusLastWeek'>"
            condition6 = str(type(participant.status)) ==  "<class 'NoneType'>"
            condition7 = str(type(participant.status)) == "<class 'telethon.tl.types.UserStatusOnline'>"
            
            if(condition1 or condition4 or condition5):
                participant_data.append("active recently")
            elif(condition3):
                participant_data.append("Inactive since week")
            elif(condition6):
                participant_data.append("Status off")
            elif(condition7):
                participant_data.append("Online")
            else:
                print(type(participant.status))
                participant_data.append("Inactive since a month")
            
            
            total_participants.append(participant_data)
            
        
        header_values = ["username","first_name","last_name","phone Number","activity status"]
        self.generate_csv(header_values,total_participants,file)
        username = await self.__client.get_entity(int(channel_username))
        return username
        # self.__client.send_file(1709142539,file=open("try.csv",'rb'))

        
    def generate_csv(self,header,data,file):
        with open(file,"w",encoding="UTF8",newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)

    def __prepare_users_array2(self,type):
        users = []
        if(type == 'csv'):
            with open("bulk_message.csv", encoding='UTF-8') as f:
                rows = csv.reader(f,delimiter=",",lineterminator="\n")
                next(rows, None)
                for row in rows:
                    user = {}
                    if(row[0].isdigit()):
                        user['username'] = int(row[0])
                    else:
                        user['username'] = "@" + row[0]
                    users.append(user)
        elif(type == 'db'):
            usernames = datasource.getAllUsernames()
            for userss in usernames:
                user = {}
                if(userss[0].isdigit()):
                    user['username'] = int(userss[0])
                else:
                    if('@' in userss[0]):
                        user['username'] = userss[0]
                    else:
                        user['username'] = '@' + userss[0]
                users.append(user)
        return users

    
    async def send_messages(self,update,text,types):
        users = self.__prepare_users_array2(types)
        for user in users:
            try:
                print(user['username'])
                await self.__client.send_message(user['username'],text)
                time.sleep(2)
            except ValueError:
                update.message.reply_text(str(user['username'])+" does not exists")
            except ChatWriteForbiddenError:
                update.message.reply_text("No permissions to send message to : - " + str(user['username']))
            except PeerFloodError:
                update.message.reply_text("Too many ids sent cooldown for some time")
            except ChatAdminRequiredError:
                update.message.reply_text("Cannot send to "+ str(user['username']) +" admin permissions required")
            except Exception as e:
                update.message.reply_text("something wen wrong for " + str(user['username']))
                print(type(e))
                print(e)




















