from telegramenu import Client, Menu, CallbackAction


class Action(CallbackAction):
    title = 'this has no text/buttons'

class SubMenu1(Menu):
    def __init__(self,arg):
        self.title = 'Record number {}'.format(arg)
    keyboard = [
        [Action()]
    ]
class SubMenu2(Menu):
    title = 'Sub 2'
    def on_click(self, cb):
        raise Exception('sample exception')

class MainMenu(Menu):
    title = 'Main Menu'
    text = 'Welcome to Main Menu'
    keyboard = [
        [SubMenu1(3)],
        [SubMenu2()]
    ]

token = 'token'
bot = Client('example',bot_token=token)

@bot.on_message()
def _hello(_,msg):
    menu = MainMenu()
    msg.reply(
        menu.text,
        reply_markup=menu.get_reply_markup()
    )

bot.run()
