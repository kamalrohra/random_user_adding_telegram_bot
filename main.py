# imports for client sidde
from cgitb import text
from email import message
from logging import Filter
from telethon.sync import TelegramClient

#imports from bot side
from telegram.ext import (Updater,CommandHandler,ConversationHandler,MessageHandler,Filters,CallbackContext)
from telegram import KeyboardButton,ReplyKeyboardMarkup,Update
from helper import Helper
import telegram

#general imports
from users import Users
from keyboards import Keyboards
from datasource import DELETE_USERNAME, Datasource
import asyncio
import nest_asyncio
import os

nest_asyncio.apply()



# handling connections for client
api_id = "<your id here>"
api_hash = '<your hash here>'
phone = '<your phone no here>'
client = TelegramClient(phone, api_id, api_hash)
# asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
loop = asyncio.get_event_loop()




#handling connections for bot
token ="<your token here>"
bot = telegram.Bot(token)

# initializing classes
user_functions = Users(client,"try.csv",loop,"bla")
keyboards = Keyboards()
helper = Helper(client)
datasource = Datasource("<your pg database link here>")


# # user_functions.add_members()
# user_functions.prepare_users_csv_data("battleofguardianschat","try.csv")
# client.run_until_disconnected()
# Handler names
cancel_text = "❌ Cancel"
GET_USER_NAME = range(1)
GET_CSV,SEND_MESAGE = range(2)
ADD_USER = range(1)
DELETE_USER = range(1)
CONFORMATION,SEND_DB_MESSAGE = range(2)
ADD_RANDOM_USERS = range(1) 


# Handler functions
def start_handler(update:Update,context:CallbackContext):
    update.message.reply_text("starting",reply_markup=keyboards.main_keyboard())

def user_handler(update:Update,context:CallbackContext):
    update.message.reply_text("select from keyboard",reply_markup=keyboards.user_keyboard())

def add_csv_handler(update:Update,context:CallbackContext):
    update.message.reply_text("Please enter id to get the CSV",reply_markup=keyboards.cancel_keyboard())
    return GET_USER_NAME

def send_csv_handler(update:Update,context:CallbackContext):
    if(update.message.text == cancel_text):
        update.message.reply_text("Aborting",reply_markup=keyboards.user_keyboard())
        return ConversationHandler.END
    else:
        if( loop.run_until_complete(helper.check_if_exists(update.message.text,update))):
            update.message.reply_text("Generating csv for you please wait")
            username = loop.run_until_complete(user_functions.prepare_users_csv_data(update.message.text,"try.csv"))
            print(username)
            # username = loop.run_until_complete(client.get_entity(update.message.text))
            os.rename("try.csv",username.title+".csv")
            update.message.reply_document(open(username.title+".csv",'rb'),reply_markup=keyboards.user_keyboard())
            os.rename(username.title+".csv","try.csv")

            print("Csv generated")
            return ConversationHandler.END
        else:
            print("Something is wrong")
            return ConversationHandler.END

def add_csv_bulk_send_handler(update:Update,context:CallbackContext):
    update.message.reply_text("Please add a csv file",reply_markup=keyboards.cancel_keyboard())
    # loop.run_until_complete(user_functions.prepare_users_csv_data("1527732953","try.csv"))
    
    
    return GET_CSV

def get_all_chats_handler(update:Update,context:CallbackContext):
        
    update.message.reply_text("Getting chats for you please wait ")
    value=loop.run_until_complete(helper.getAllChats())
    ids=value[0]
    words =value[1]
    each_id = ""
    for i in range(0,len(words)):
        # final_str+=(str(words[i])+"- "+str(ids[i])+",\n")
        each_id+= str(words[i])+" | "+"`"+str(ids[i])+"`"+"\n"
        if(i%20==0):
            update.message.reply_text(each_id,parse_mode="MarkDown")
            each_id = ""
        # update.message.reply_text(words[i])
    if(each_id!=""):
        update.message.reply_text(each_id,parse_mode="MarkDown")


def send_message(update:Update,context:CallbackContext):
    if(update.message.text == cancel_text):
        update.message.reply_text("Aborting",reply_markup=keyboards.messages_keyboard())
        return ConversationHandler.END
    else:
        update.message.reply_text("Please wait while sending messages")
        loop.run_until_complete(user_functions.send_messages(update,update.message.text,'csv')) 
        update.message.reply_text("Messages has been sent",reply_markup=keyboards.messages_keyboard())
        print("sent the messages")
        return ConversationHandler.END

def add_user_handler(update:Update,context:CallbackContext):
    update.message.reply_text("Please enter the username to add",reply_markup=keyboards.cancel_keyboard())
    return ADD_USER

def add_user_db(update:Update,context:CallbackContext):
    if(update.message.text ==cancel_text):
        update.message.reply_text("Aborting",reply_markup=keyboards.manage_db_keyboard())
        return ConversationHandler.END
    else:
        added = datasource.addUsername(update.message.text,update)
        if(added):
            update.message.reply_text("Username has been added",reply_markup=keyboards.manage_db_keyboard())
        else:
            update.message.reply_text("Sorry! Cannot add username",reply_markup=keyboards.manage_db_keyboard())
        return ConversationHandler.END

def delete_user_handler(update:Update,context:CallbackContext):
  
    update.message.reply_text("Enter the username you wish to remove",reply_markup=keyboards.cancel_keyboard())
    return DELETE_USER

def delete_user_db(update:Update,context:CallbackContext):
    if(update.message.text == cancel_text):
        update.message.reply_text("Aborting",reply_markup=keyboards.manage_db_keyboard())
        return ConversationHandler.END
    else:
        if(datasource.checkIfUserExists(update.message.text)):
            datasource.deleteUsername(update.message.text)
            update.message.reply_text("Username has been deleted",reply_markup=keyboards.manage_db_keyboard())
            return ConversationHandler.END
        else:
            update.message.reply_text("Message or id does not exists in the database",reply_markup=keyboards.manage_db_keyboard())
            return ConversationHandler.END



def send_csv_bulk_message_handler(update:Update,context:CallbackContext):
    if(update.message.text == cancel_text):
        update.message.reply_text("Aborting",reply_markup=keyboards.messages_keyboard())
        return ConversationHandler.END
    else:
        newfile = update.message.effective_attachment.get_file()
        if(os.path.exists("bulk_message.csv")):
            os.remove("bulk_message.csv")
        newfile.download("bulk_message.csv")
        update.message.reply_text("please enter the message you want to send!")
        return SEND_MESAGE
   
def message_handler(update:Update,context:CallbackContext):
    update.message.reply_text("Select from keyboard",reply_markup=keyboards.messages_keyboard())


def ask_for_confirmation_handler(update:Update,context:CallbackContext):
    update.message.reply_text("Are you sure you want to send message using database Values",reply_markup=keyboards.confirmation_keyboard())
    return CONFORMATION

def send_db_bulk_message_handler(update:Update,context:CallbackContext):
    if(update.message.text ==cancel_text):
        update.message.reply_text("Aborting",reply_markup=keyboards.messages_keyboard())
        return ConversationHandler.END
    else:
        loop.run_until_complete(user_functions.send_messages(update,update.message.text,'db'))
        update.message.reply_text("Messages have been sent",reply_markup=keyboards.messages_keyboard())
    
        return ConversationHandler.END

def ask_db_message(update:Update,context:CallbackContext):
    if(update.message.text =='☑️ Yes'):
        update.message.reply_text("Please enter the message you want to send",reply_markup=keyboards.cancel_keyboard())
        return SEND_DB_MESSAGE
    elif(update.message.text =='❌ No'):
        update.message.reply_text("Ok! Aborting",reply_markup=keyboards.messages_keyboard())
        return ConversationHandler.END

def home_handler(update:Update,context:CallbackContext):
    update.message.reply_text("going to home",reply_markup=keyboards.main_keyboard())

def manage_bulk_sender_db_handler(update:Update,context:CallbackContext):
    update.message.reply_text("Select from keyboard ",reply_markup=keyboards.manage_db_keyboard())

def back_to_manager_handler(update:Update,context:CallbackContext):
    update.message.reply_text("going back to manager",reply_markup=keyboards.messages_keyboard())

def add_people_handler(update:Update,context:CallbackContext):
    loop.run_until_complete(user_functions.select_random_group_and_generate_file(update))
    string = loop.run_until_complete(user_functions.return_selected_group())
    update.message.reply_text("please enter the number currosponding to the channel you want to add users to: -")
    update.message.reply_text(string)
    return ADD_RANDOM_USERS

def add_random_users(update:Update,context:CallbackContext):
    index = update.message.text
    loop.run_until_complete(user_functions.add_members(index,update))
    update.message.reply_text("Users added")
    return ConversationHandler.END
def get_all_id_from_db(update:Update,context:CallbackContext):
    usernames = datasource.getAllUsernames()
    string = ""
    for username in usernames:
        string+=username[0]+"\n"
    update.message.reply_text(string)
    

if __name__ == '__main__':
    updater = Updater(token,use_context=True)
    datasource.createTables()
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone)
        client.sign_in(phone, input('Enter the code: '))
    print("Connected to client")
    # bot command handlers
    updater.dispatcher.add_handler(CommandHandler("start",start_handler))
    
    #bot message handlers
    updater.dispatcher.add_handler(MessageHandler(Filters.regex("🧑 Users"),user_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex("🗨️ Get All Chats"),get_all_chats_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex("💬 Messages"),message_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex("👨‍💼 Manage bulk senders"),manage_bulk_sender_db_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex("🏠 Home"),home_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex("🔙 Back to manager"),back_to_manager_handler)) 
    updater.dispatcher.add_handler(MessageHandler(Filters.regex("Get all usernames"),get_all_id_from_db))
    # conversation handlers
    conv_handler_csv = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("📑 Get CSV"),add_csv_handler)],
        states={
            GET_USER_NAME:[MessageHandler(Filters.all,send_csv_handler)]
        },
        fallbacks=[]
    )

    conv_handler_csv_bulk_sender = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("📑 Send Bulk using csv"),add_csv_bulk_send_handler)],
        states={
            GET_CSV:[MessageHandler(Filters.all,send_csv_bulk_message_handler)],
            SEND_MESAGE:[MessageHandler(Filters.all,send_message)]
        },
        fallbacks=[]
    )
    conv_handler_db_bulk_sender = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("🏬 Send Bulk using db"),ask_for_confirmation_handler)],
        states={
            CONFORMATION:[MessageHandler(Filters.all,ask_db_message)],
            SEND_DB_MESSAGE:[MessageHandler(Filters.all,send_db_bulk_message_handler)]
        },
        fallbacks=[]
    )

    conv_handler_add_user = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("➕ Add username or id to db"),add_user_handler)],
        states = {
            ADD_USER:[MessageHandler(Filters.all,add_user_db)]
        },
        fallbacks=[]
    )

    conv_handler_delete_user = ConversationHandler(
        entry_points= [MessageHandler(Filters.regex("❌ Delete username or id from db"),delete_user_handler)],
        states={
            DELETE_USER: [MessageHandler(Filters.all,delete_user_db)]
        },
        fallbacks=[]
    )

    conv_handler_add_random_users = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("➕ Add Users"),add_people_handler)],
        states={
            ADD_RANDOM_USERS:[MessageHandler(Filters.regex("^[0-9]*$"),add_random_users)]
        },
        fallbacks=[]
    )



    updater.dispatcher.add_handler(conv_handler_csv)
    updater.dispatcher.add_handler(conv_handler_csv_bulk_sender)
    updater.dispatcher.add_handler(conv_handler_add_user)
    updater.dispatcher.add_handler(conv_handler_delete_user)
    updater.dispatcher.add_handler(conv_handler_db_bulk_sender)
    updater.dispatcher.add_handler(conv_handler_add_random_users)

    print("Bot started")
    updater.start_polling()
    



# id=1527732953



