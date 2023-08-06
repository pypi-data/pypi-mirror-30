import re
from os import path

from mhelper import file_helper
from pyguisignal.configuration import config
from pyguisignal import general


class SignalDefinition:
    def __init__( self, widget_name, widget_type, signal_name, signal_params ):
        self.widget_name = widget_name
        self.widget_type = widget_type
        self.signal_name = signal_name
        self.signal_params = signal_params
        self.signal_function = config.function_format.format( self.widget_name, self.widget_type, self.signal_name, self.signal_params )
        
        if self.signal_params:
            self.formatted_params = "self, " + self.signal_params
        else:
            self.formatted_params = "self"
        
        self.signal_command = config.command_format.format( self.widget_name, self.widget_type, self.signal_name, self.signal_params, self.signal_function, self.formatted_params )
    
    
    @staticmethod
    def append( widget_name, widget_type ):
        if widget_type in config.handlers and not widget_name.endswith( "_" ):
            signals = config.handlers[widget_type]
            
            for signal in signals:
                yield SignalDefinition( widget_name, widget_type, signal[0], signal[1] )


def process_dialogue( designer_filename: str, init_filename: str, logic_filename: str ) -> None:
    """
    Processes a dialogue file
    :param designer_filename:   Dialogue designer file, _designer.UI, input 
    :param init_filename:       Generated dialogue file, _designer.PY, output 
    :param logic_filename:      Logic file, ../.PY, input/output 
    :return: 
    """
    #
    # Debugging information
    #
    print( "PROCESS DIALOGUE: " + file_helper.get_filename( designer_filename ) )
    
    if config.verbose:
        print( "---- DESIGNER FILE            : " + designer_filename )
        print( "---- INITIALISATION FILE      : " + init_filename )
        print( "---- LOGIC FILE               : " + logic_filename )
    
    #
    # Compile .UI --> .PY
    #
    command = config.ui_command.format( designer_filename, init_filename )
    
    general.run_system( command )
    
    if not path.isfile( init_filename ):
        raise FileNotFoundError( "The initialisation file '{0}' does not exist.".format( init_filename ) )
    
    #
    # Read files
    #
    with open( init_filename, "r" ) as f:
        original_initialisation_content = f.read()
        initialisation_content = original_initialisation_content
    
    if path.isfile( logic_filename ):
        with open( logic_filename, "r" ) as f:
            original_logic_content = f.read()
            logic_content = original_logic_content
    else:
        logic_content = ""
        original_logic_content = None
    
    #
    # Initialisation file: Garbage removal
    #
    for find, replace in config.garbage_regex:
        initialisation_content = re.sub( find, replace, initialisation_content )
    
    #
    # Initialisation file: Find widgets
    #
    signals = [signal for match in re.finditer( config.widget_regex, initialisation_content ) for signal in SignalDefinition.append( match.group( 1 ), match.group( 2 ) )]
    widget_names = set( signal.widget_name for signal in signals )
    
    #
    # Logic file: Find existing signals
    #
    new_handlers = []
    last_match = -1
    
    for signal in signals:
        index = logic_content.find( "def " + signal.signal_function )
        found = index != -1
        
        if found:
            last_match = index
        else:
            print( "---- HANDLER: " + signal.signal_command )
            new_handlers.append( signal.signal_command )
    
    # Our last match is at "last_match", so use the indentation of this
    start_index = last_match
    
    if start_index != -1:
        while True:
            start_index -= 1
            if start_index == -1 or (start_index < len( logic_content ) and logic_content[start_index] != " "):
                break
    
    indentation = last_match - start_index - 1
    
    # Indent our handlers
    for index, value in enumerate( new_handlers ):
        new_handlers[index] = " " * indentation + value
    
    # Insert after our last function in the code (this is easiest)
    
    # We need to READ forward until we have a line with <= indentation to "indentation"
    
    index = last_match
    current_indent = 9999
    NEW_LINE = 1
    TEXT_CONTENT = 2
    stage = 0  # 1 = new line
    
    while True:
        index += 1
        
        if index == len( logic_content ):
            break
        
        c = logic_content[index]
        
        if c == "\n":
            stage = NEW_LINE
            # print( c + " is NEW LINE" )
            current_indent = 0
        elif stage == NEW_LINE:
            if c == " ":
                current_indent += 1
                # print( c + " INDENT " + str( current_indent ) )
            elif c == "#":
                stage = TEXT_CONTENT
                # print( c + " COMMENT " + str( current_indent ) )
            else:
                stage = TEXT_CONTENT
                # print( c + " CONTENT! " + str( current_indent ) )
                if current_indent <= indentation:
                    # We have our line but we now need to move back to the start of it
                    # print( "EXITING WITH " + str( current_indent ) )
                    while logic_content[index] != "\n":
                        index -= 1
                    break
    
    new_code = "\n".join( new_handlers )
    
    logic_content = logic_content[:index] + new_code + logic_content[index:]
    
    # Find rubbish in the code
    next_line = False
    find_handler_regex = re.compile( "on_(.*)_.*\\(" )
    lines = logic_content.split( "\n" )
    
    for line in lines:
        if next_line:
            widget_name = find_handler_regex.findall( line )
            
            if len( widget_name ) != 0:
                widget_name = widget_name[0]
                if widget_name not in widget_names:
                    print( "WARNING: Bad handler - {}".format( line.strip() ) )
                    
                    if "BAD_HANDLER" not in line:
                        logic_content = logic_content.replace( line, line + " #TODO: BAD_HANDLER - The widget '{}' does not appear in the designer file.".format( widget_name ) )
            
            next_line = False
        elif "exqtSlot" in line or "pyqtSlot" in line:
            next_line = True
    
    if original_logic_content != logic_content:
        print( "--------Logic file: {} new handlers.".format( len( new_handlers ) ) )
        
        # Write our new code
        with open( logic_filename, "w" ) as f:
            f.write( logic_content )
    
    if original_initialisation_content != initialisation_content:
        # Write our new window
        with open( init_filename, "w" ) as f:
            f.write( initialisation_content )
