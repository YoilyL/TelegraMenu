from pyrogram import InlineKeyboardButton,InlineKeyboardMarkup
from functools import wraps
from inspect import signature,Parameter
from .callback_encoder import callback_encode


actions = [] 


class CallbackAction:
    _button_text = None
    callback_answer_text = None

    @classmethod
    def __init_subclass__(cls):
        actions.append(cls)
        cls.action_id = len(actions) -1 #index of last item

        original_init = cls.__init__
        original_sig = signature(original_init)
        #get the default args. reversed because it is only needed that way. (remove the first==self [last here because reverse])
        rev_defaults = [param.default for param in original_sig.parameters.values()][:1:-1]
        
        #save the args used to initialize the object, and set the parent
        @wraps(original_init)
        def new_init(self,*args,**kwargs):
            if 'parent' in kwargs:
                #if parent? check that parent isn't null, so that default is used? but maybe allow, for override
                self.parent = kwargs['parent']
                del kwargs['parent']
            #convert kwargs to positional args https://stackoverflow.com/questions/33448997/convert-kwargs-arguments-to-positional/33448998#33448998
            bound = original_sig.bind(self,*args,**kwargs)
            bound.apply_defaults()
            #if there are still keywords, prompt to set the args property themself
            if bound.kwargs:
                print(f'You must set the args yourself for {self} because it has keyword only params')
            else:
                #remove self from args
                new_args = list(bound.args)[1:]
                #keep only needed args, remove defaults
                #while the last args are the same as default, remove them. only last, because position isn't needed
                #check only the defaults for the current args (exclude *args from defaults if there aren't any in the args)
                for default in rev_defaults[:len(args)]:
                    #if the last arg is the same as current default, remove it
                    #last is always current, because the previous was either poped, or the loop broken
                    if new_args[-1] == default:
                        new_args.pop()
                    #otherwise break and don't check anymore, to keep the position in place
                    else:
                        break
                #set the args to serializable args required to recostruct the object
                self.args = tuple(arg if isinstance(arg,str) else int(arg) for arg in new_args)
            return original_init(self,*args,**kwargs)
        cls.__init__ = new_init
    def on_click(self,cb):
        return self
    @property
    def button_text(self):
        return self._button_text or self.title
    @button_text.setter
    def button_text(self, value):
        self._button_text = value
    def get_callback_args(self):
        return (self.action_id,*self.args)
    def get_inline_button(self,button_text=None):
        data = callback_encode([self.get_callback_args()])
        return InlineKeyboardButton(
                        text=button_text or self.button_text,
                        callback_data=data
                    )


class Menu(CallbackAction):
    parent = None
    keyboard = []
    _text = None
    parse_mode = 'html'
    back_text = 'Back'
    home_text = 'Home'

    @property
    def text(self):
        return self._text or self.paths_as_string()
    @text.setter
    def text(self,val):
        self._text = val
    @property
    def paths(self):
        try:
            return self._paths 
        except AttributeError:
            paths = [self]
            menu = self
            while menu.parent:
                menu = menu.parent
                if type(menu) != type(self):
                    paths.append(menu)
            self._paths = paths[::-1]
            return self._paths
    def paths_as_string(self,delim=' > '):
        return delim.join(menu.title for menu in self.paths)
    def get_reply_markup(self):
        keyboard = [row[:] for row in self.keyboard[:]]
        for i, row in enumerate(keyboard):
            for j,button in enumerate(row):
                button.parent = self
                keyboard[i][j] = button.get_inline_button()
        if self.back_text and self.parent:
            keyboard += [[
                self.parent.get_inline_button(self.back_text),
            ]]
        #make sure this isn't root menu
        if self.home_text and type(self) != type(self.paths[0]):
            home_button = self.paths[0].get_inline_button(self.home_text)
            if self.back_text and self.parent:
                keyboard[-1] += [home_button]
            else:
                keyboard += [[home_button]]
        return InlineKeyboardMarkup(keyboard)
    def get_inline_button(self,button_text=None):
        paths = self.paths
        if not self.back_text:
            paths = paths[-1:]
        data = callback_encode([menu.get_callback_args() for menu in self.paths])
        return InlineKeyboardButton(
                        text=button_text or self.button_text,
                        callback_data=data
                    )