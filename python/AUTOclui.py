#! /usr/bin/env python
import AUTOutil
import sys
import string
import os
import ConfigParser
import AUTOCommands

_functionTemplate="""
def %s(self,*args,**kw):
    return self._queueCommand(%s.%s,args,kw)
"""

_functionTemplateAlias="""
def %s(self,*args,**kw):
    return apply(%s,args,kw)
"""

class AUTOSimpleFunctions:
    def __init__(self,outputRecorder=None):
        # Initialize the output recorder (if any)
        self.__outputRecorder = outputRecorder

        # Read in the aliases.
        self._aliases = {}
        parser = ConfigParser.ConfigParser()
        parser.add_section("AUTO_command_aliases")
        if(os.path.exists(os.path.expandvars("$AUTO_DIR/.autorc"))):
            parser.read(os.path.expandvars("$AUTO_DIR/.autorc"))
        if(os.path.exists(os.path.expandvars("$HOME/.autorc"))):
            parser.read(os.path.expandvars("$HOME/.autorc"))
        if(os.path.exists("./.autorc")):
            parser.read("./.autorc")

        for option in parser.options("AUTO_command_aliases"):
            self._aliases[option] = parser.get("AUTO_command_aliases",option)

        self._addCommands([AUTOCommands])

        # Now I resolve the aliases
        for key, alias in self._aliases.items():
            AUTOSimpleFunctions.__dict__[key] = getattr(self, alias)
            exec _functionTemplateAlias%(key,alias)
            AUTOSimpleFunctions.__dict__[key] = locals()[key]

    def _addCommands(self,moduleList):
        for module in [AUTOCommands]:
            # Now we copy the commands from the module
            for key in module.__dict__.keys():
                # Check to see if it is a descendent of AUTOCommands.command
                if AUTOutil.findBaseClass(module.__dict__[key],AUTOCommands.command):
                    exec _functionTemplate%(key,module.__name__,key)
                    AUTOSimpleFunctions.__dict__[key] = locals()[key]

    def _queueCommand(self,commandType,args=[],kw={}):
        # Put back in the arguments
        # I am not 100% sure if this is the best way to do this,
        # but it seems to work.
        command = apply(commandType,args,kw)
        output = command()
        if not(self.__outputRecorder is None):
            self.__outputRecorder.write(str(output))
        sys.stdout.write(str(output))
        # check to see if the command returned any data.  If so, pass it on.
        try:
            return output.data
        except:
            return None

# Export the functions inside AUTOSimpleFunctions in this modules namespace
# This is to make "from AUTOclui import *" work
# ALMOST like the AUTOInteractiveConsole.  Things that
# don't work are help, shell, !, ls, cd, and any changes
# to the aliases
_AUTOSimpleFunctionsGlobalInstance = AUTOSimpleFunctions()
for name in AUTOSimpleFunctions.__dict__.keys():
    if name[0] != '_':
        globals()[name] = getattr(_AUTOSimpleFunctionsGlobalInstance, name)

# Export the functions inside AUTOSimpleFunctions in a dictionary
# This also allows the setting of the log
def exportFunctions(log=None):
    AUTOSimpleFunctionsInstance = AUTOSimpleFunctions(log)
    dict = {}
    for name in AUTOSimpleFunctions.__dict__.keys():
        if name[0] != '_':
            dict[name] = getattr(AUTOSimpleFunctionsInstance, name)
    return dict

def test():
    import interactiveBindings
    interactiveBindings._testFilename("../demos/python/fullTest.auto","test_data/fullTest.log")

if __name__ == "__main__":
    test()







