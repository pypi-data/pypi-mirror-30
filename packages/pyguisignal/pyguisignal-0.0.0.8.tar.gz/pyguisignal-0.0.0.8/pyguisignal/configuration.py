from os import path
import re


class Config:
    def __init__( self ) -> None:
        ###############################################################################################################
        #                                                                                                             #
        # PROJECT STRUCTURE                                                                                           #
        #                                                                                                             #
        ###############################################################################################################
        
        # Input resource file pattern matching, where `*` is the wildcard
        self.resource_designer = "*.qrc"
        
        # Generated resource file, where * matches the * in `resource_designer` 
        self.resource_initialisation = "*_rc.py"
        
        # We'll create an enumeration of the `resource_initialisation` file here, where * matches the * in `resource_designer` 
        self.resource_logic = "*.py"
        
        # Input dialogue file pattern matching, where `*` is the wildcard
        self.dialogue_designer = "*_designer.ui"
        
        # Generated dialogue file, where * matches the * in `dialogue_designer` 
        self.dialogue_initialisation = "*_designer.py"
        
        # Dialogue logic file, where * matches the * in `dialogue_designer` 
        self.dialogue_logic = "../*.py"
        
        ###############################################################################################################
        #                                                                                                             #
        # SIGNAL PROCESSING                                                                                           #
        #                                                                                                             #
        ###############################################################################################################
        
        # The signals to create
        #
        # This is a Dictionary[key, value] where:
        #        key   : str = Name of widget
        #        value : Tuple[n] =
        #            value[0...n] : Tuple[2] =
        #                 value[0] : str = signal
        #                 value[1] : str = arguments
        self.handlers = \
            {
                "QPushButton"       : [["clicked", ""]],
                "QAction"           : [["triggered", ""]],
                "QCommandLinkButton": [["clicked", ""]],
                "QToolButton"       : [["clicked", ""]],
                "QDialogButtonBox"  : [["accepted", ""], ["rejected", ""]],
            }
        
        # How we format the signal handlers, where the following substitutions are made:
        #       {0}: Name
        #       {1}: Type
        #       {2}: Signal
        #       {3}: Params
        #       {4}: Function name (i.e. `self.function_format`)
        #       {5}: Formatted params, including "self"
        self.command_format = \
            """@exqtSlot({3})
            def {4}({5}) -> None:
                \"\"\"
                Signal handler:
                \"\"\"
                pass
            """
        
        # How we format the function names (same format as for `command_format`)
        self.function_format = "on_{0}_{2}"
        
        # The following lines will be removed from the dialogue initialisation code
        #
        # This is a Dictionary[key, value] where:
        #   key   : str = find
        #   value : str = replace
        self.garbage_regex = [
            [re.escape( r"def setupUi(self, Dialog):" ), r"def __init__(self, Dialog):"],  # Swap our setupUi method for a constructor, so the IDE can see the field types properly
            [re.escape( r"QtWidgets.QDockWidget.DockWidgetFeatureMask" ), r"QtWidgets.QDockWidget.DockWidgetClosable | QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetVerticalTitleBar"],
            [re.escape( r"import resources_rc" ), ""]
        ]
        
        ###############################################################################################################
        #                                                                                                             #
        # ADVANCED SETTINGS                                                                                           #
        #                                                                                                             #
        ###############################################################################################################
        
        # The following settings represent internal workings and generally shouldn't be changed
        
        # System command used to compile resources
        self.resource_command = 'pyrcc5 "{0}" -o "{1}"'
        
        # System command to compile dialogues
        self.ui_command = 'pyuic5 "{0}" -o "{1}"'
        
        # Regular expression used to find the widgets
        self.widget_regex = r"self\.(.*?) = QtWidgets\.(.*?)\("
        
        # Verbose status. This can also be changed via the command line's `--verbose` option.
        self.verbose = False




def __load():
    config = Config()
    
    # TODO
    
    return config


config = __load()
