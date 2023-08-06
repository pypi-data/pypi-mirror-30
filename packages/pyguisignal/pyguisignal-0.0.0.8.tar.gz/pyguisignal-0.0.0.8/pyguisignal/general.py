import os
from os import path

from pyguisignal.dialogue_compiler import process_dialogue
from pyguisignal.configuration import config
from pyguisignal.resource_compiler import process_resource


def run_system( command: str ) -> None:
    result = os.system( command )
    
    if result:
        raise ValueError( "Unhappy result '{0}' from '{1}'".format( result, command ) )


def process_unknown( file_name: str ):
    process_function( file_name, config.dialogue_designer, config.dialogue_initialisation, config.dialogue_logic, process_dialogue )
    process_function( file_name, config.resource_designer, config.resource_initialisation, config.resource_logic, process_resource )


def process_function( file_name: str, wildcard_designer: str, wildcard_init: str, wildcard_logic: str, function ):
    file_name = path.abspath( file_name )
    directory, filename_pure = path.split( file_name )
    designer_prefix, designer_suffix = wildcard_designer.split( "*", 1 )
    init_prefix, init_suffix = wildcard_init.split( "*", 1 )
    logic_prefix, logic_suffix = wildcard_logic.split( "*", 1 )
    
    if filename_pure.startswith( designer_prefix ) and filename_pure.endswith( designer_suffix ):
        filename_middle = filename_pure[len( designer_prefix ):-len( designer_suffix )]
        filename_init = path.abspath( path.join( directory, init_prefix + filename_middle + init_suffix ) )
        filename_logic = path.abspath( path.join( directory, logic_prefix + filename_middle + logic_suffix ) )
        
        function( file_name, filename_init, filename_logic )
