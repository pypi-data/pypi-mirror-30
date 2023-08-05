import code
import inspect
import readline
import rlcompleter
import sys
import traceback
from pprint import pprint
sys.displayhook = pprint

frame = inspect.currentframe()
while True:
    module = inspect.getmodule(frame)
    in_importlib = not module and 'importlib' in frame.f_code.co_filename
    if not in_importlib and (not module or module.__name__ != 'debugme'):
        break
    frame_, frame = frame, frame.f_back
    del(frame_)

vars = frame.f_globals
vars.update(frame.f_locals)

class formatted_repr(str):
    def __repr__(self):
        return self

class debugme:
    def __init__(self, frame):
        self.frame = frame
        self.exit = True
        self.traceback = formatted_repr(''.join(traceback.format_stack(self.frame)).strip())

    def __del__(self):
        del(self.frame)

vars['debugme'] = debugme(frame)
del(frame)

readline.set_completer(rlcompleter.Completer(vars).complete)
readline.parse_and_bind("tab: complete")
shell = code.InteractiveConsole(vars)
shell.interact()
if vars['debugme'].exit:
    sys.exit(1)
