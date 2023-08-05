import traceback
import subprocess


'''These are the sequences need to get colored output'''
DEFAULT_COLOR = "\033[0m"
BLACK_COLOR = "\033[1;0m"
RED_COLOR = "\033[1;31m"
GREEN_COLOR = "\033[1;32m"
YELLOW_COLOR = "\033[1;33m"
BLUE_COLOR = "\033[1;34m"
MAGENTA_COLOR = "\033[1;35m"
CYAN_COLOR = "\033[1;37m"
WHITE_COLOR = "\033[1;37m"
BOLD_SEQ = "\033[1m"


class UnBuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


def color_string(message, color, default_color):
    message = message.replace("\n", "\n" + color)
    return color + message + default_color


def my_except_hook(typ, value, tb):
    """
    Hook function for except.
    :param typ:
    :param value:
    :param tb:
    """
    tb_text = ''.join(traceback.format_exception(typ, value, tb))
    tb_text = tb_text.replace("\n", "\n" + RED_COLOR)
    print(RED_COLOR + tb_text + DEFAULT_COLOR + "\n")


TEST_TITLE = r"""

 ______        __ 
/_  __/__ ___ / /_
 / / / -_|_-</ __/
/_/  \__/___/\__/ 
                  
"""

BUILD_TITLE = r"""

   ___       _ __   __
  / _ )__ __(_) /__/ /
 / _  / // / / / _  / 
/____/\_,_/_/_/\_,_/  
                      
"""

DEPLOY_TITLE = r"""

   ___           __         
  / _ \___ ___  / /__  __ __
 / // / -_) _ \/ / _ \/ // /
/____/\__/ .__/_/\___/\_, / 
        /_/          /___/  
"""
