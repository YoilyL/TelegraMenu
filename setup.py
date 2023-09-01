from setuptools import setup

import sys
if sys.version_info < (3,6):
    sys.exit('Sorry, Python < 3.6 is not supported')
      
setup(name='TelegraMenu',
      version='0.0.1',
      description='Telegram Menus',
      url='https://github.com/YoilyL/TelegraMenu',
      author='Yoily',
      author_email='yoilyl@telegram.org',
      license='GPL',
      packages=['telegramenu'],
      zip_safe=False)
