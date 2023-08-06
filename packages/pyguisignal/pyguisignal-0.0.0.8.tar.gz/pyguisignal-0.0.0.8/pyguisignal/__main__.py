import sys
from os import path
from mhelper import file_helper

from pyguisignal.configuration import config
from pyguisignal import general


def main() -> None:
    commands = sys.argv[1:]
    
    print( commands )
    
    # Print help if we don't have everything
    if not commands:
        print( "pyguisignal <path>" )
        print( "    <path> one or more paths to \".ui\" files or folders." )
        print( "    If folders are selected they will be recursively searched for '.ui' and '.qrc' files." )
        raise SystemExit()
    
    # Parse the commands
    for command in commands:
        if config.verbose:
            print( "command: [" + command + "]" )
        
        if command == "--verbose":
            print( "SET VERBOSE" )
            config.verbose = True
        elif path.isdir( command ):
            command = path.abspath( command ).strip()
            print( "PROCESS DIRECTORY: " + command )
            
            for file in file_helper.list_dir( command , recurse = True):
                general.process_unknown( file )
        elif path.isfile( command ):
            print( "PROCESS FILE: " + command )
            print( "file" )
            general.process_unknown( command )
        else:
            print( "Argument «{}» rejected".format( command ) )


if __name__ == "__main__":
    main()
