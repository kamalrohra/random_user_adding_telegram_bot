from telegram import ReplyKeyboardMarkup
class Keyboards:
    def main_keyboard(self):    
        main_board = [["🧑 Users"],["💬 Messages"]]
        return ReplyKeyboardMarkup(main_board,resize_keyboard=True)
    
    def user_keyboard(self): 
        user_board = [["🗨️ Get All Chats"],["➕ Add Users"],["📑 Get CSV"],["🏠 Home"]]
        return ReplyKeyboardMarkup(user_board,resize_keyboard=True)
    
    def messages_keyboard(self):
        messages_board = [["👨‍💼 Manage bulk senders"],["📑 Send Bulk using csv" ],["🏬 Send Bulk using db"],["🏠 Home"]]
        return ReplyKeyboardMarkup(messages_board,resize_keyboard=True)
    
    def manage_db_keyboard(self):
        manage_db_board = [["➕ Add username or id to db" ],["❌ Delete username or id from db"],["Get all usernames"],["🔙 Back to manager"]]
        return ReplyKeyboardMarkup(manage_db_board,resize_keyboard=True)
    
    def confirmation_keyboard(self):
        confirmation_board = [["☑️ Yes"],["❌ No"]]
        return ReplyKeyboardMarkup(confirmation_board,resize_keyboard=True)
    
    def cancel_keyboard(self):
        cancel_board = [["❌ Cancel"]]
        return ReplyKeyboardMarkup(cancel_board)
    