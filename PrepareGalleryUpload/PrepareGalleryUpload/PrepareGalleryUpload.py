import subprocess
import argparse
import os

from pgu_config import pgu_config
import pgu_util

import default_user_scripts


#when run directly start execution here
def main():
	config = pgu_config(None)
	user_scripts = default_user_scripts

	#retrieve command line argument to identify from which source path to read from
	arguments_parser = argparse.ArgumentParser(description='Prepare video gallery files for upload.')
	arguments_parser.add_argument('source')
	command_line_arguments = arguments_parser.parse_args()

	source = command_line_arguments.source

	#verify that ffmpeg.exe and the source are valid paths
	try:
		pgu_util.check_if_ffmpeg_file_exists( config.options["ffmpeg_path"] )
		pgu_util.check_if_source_path_exists( source )
	except Exception as error:
		print(error.args)
		exit(1)

	if os.path.isdir(source):
		user_scripts.on_input_archive_directory( source, config )

	elif os.path.isfile(source):
		user_scripts.on_input_archive_video( source, config )


if __name__ == "__main__":
    # execute only if run directly not when imported
    main()