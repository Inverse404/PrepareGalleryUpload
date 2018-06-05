import os
import argparse

from pgu_config import pgu_config
import default_user_scripts


config = pgu_config(None)

#retrieve command line argument to identify from which source path to read from
arguments_parser = argparse.ArgumentParser(description='Prepare many video gallery subdirectories for upload.')
arguments_parser.add_argument('source')
command_line_arguments = arguments_parser.parse_args()

source = command_line_arguments.source

for dir_entry in os.scandir( source ):
	if dir_entry.is_dir() == True:
		default_user_scripts.on_input_archive_directory( dir_entry.path, config )
