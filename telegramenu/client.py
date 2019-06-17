import pyrogram
from .callback_handler import on_callback

class Client(pyrogram.Client):
    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)
        super().add_handler(
            pyrogram.CallbackQueryHandler(
                on_callback
            )
        )
    def add_handler(self, handler, group=0):
        if type(handler) is pyrogram.CallbackQueryHandler:
            raise Exception("You can't use custom callback handlers!")
        return super().add_handler(handler, group=group)