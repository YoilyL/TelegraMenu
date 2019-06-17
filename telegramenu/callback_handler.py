from pyrogram import Client, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, errors
import json
from .callback_actions import actions, Menu
from .callback_encoder import callback_decode

def on_callback(client: Client, cb: CallbackQuery):
    
    #print(len(cb.data))
    #decode the data to a list of lists
    paths = callback_decode(cb.data)
    
    #root action is None
    action = None
    
    #for every item in the list get the action_id and args for the action
    for action_id, *args in paths:
        #get the action by the id and call with the args and previous action as the parent
        action = actions[action_id](*args,parent=action)
    
    try:
        #finally, call the last/current action with the callback, and get an optionally different action as response
        action = action.on_click(cb) or action
        if not isinstance(action,Menu):
            return cb.answer(action.callback_answer_text or action.title)
        
        #TODO handle if the text and/or keyboard are the same as last
        cb.message.edit(
            action.text,
            parse_mode=action.parse_mode,
            reply_markup=action.get_reply_markup()
        )
        try:
            cb.answer(action.callback_answer_text or action.title)
        except errors.QueryIdInvalid:
            pass
    except Exception as e:
        #show alert with exception
        cb.answer(str(e),True)
        raise



