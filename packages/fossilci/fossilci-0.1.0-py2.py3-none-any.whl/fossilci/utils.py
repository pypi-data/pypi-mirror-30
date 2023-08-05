import traceback

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
  _____         _   
 |_   _|__  ___| |_ 
   | |/ _ \/ __| __|
   | |  __/\__ \ |_ 
   |_|\___||___/\__|
                    
"""

BUILD_TITLE = r"""
  ____        _ _     _ 
 | __ ) _   _(_) | __| |
 |  _ \| | | | | |/ _` |
 | |_) | |_| | | | (_| |
 |____/ \__,_|_|_|\__,_|
                        
"""

DEPLOY_TITLE = r"""
  ____             _             
 |  _ \  ___ _ __ | | ___  _   _ 
 | | | |/ _ \ '_ \| |/ _ \| | | |
 | |_| |  __/ |_) | | (_) | |_| |
 |____/ \___| .__/|_|\___/ \__, |
            |_|            |___/ 
"""
