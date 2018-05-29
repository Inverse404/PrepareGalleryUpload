import subprocess
import argparse
import os
import string
import random
import ffmpy

from pgu_config import pgu_config



def ffmpeg_found( ffmpeg_path ):
	ffmpeg_found = False
	if os.path.isfile( ffmpeg_path ) == True:
		ffmpeg_found = True
	else:
		print( "ERROR: ffmpeg.exe not found at the specified location!" )
	return ffmpeg_found


def source_found( source_path ):
	source_found = False
	if (os.path.isdir ( source_path ) == True) or (os.path.isfile( source_path ) == True):
		source_found = True
	else:
		print( "ERROR: Source directory ot file not found!")
	return source_found


def error_ffmpeg():
	print( "ERROR when invoking ffmpeg.exe!" )


def prepare_one_entry(entry_path, ffmpeg_path, output_directory, video_settings, thumbnail_settings):
	#ensure output directory is created if it does not yet exist
	if os.path.exists( output_directory ) == False:
		os.makedirs( output_directory )

	random_name_bit				= ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
	entry_name, entry_extension = os.path.splitext(os.path.basename( entry_path ))
	output_file_name			= entry_name.replace( "-UHD", "-HQ" ) + "-" + random_name_bit
	output_path_video			= os.path.join(output_directory, output_file_name + ".mp4")
	output_path_thumb			= os.path.join(output_directory, output_file_name + ".jpg")
	input_video_settings		= None
	input_thumbnail_settings	= None

	#create a HQ web video file
	encode_video = ffmpy.FFmpeg(
		executable		= ffmpeg_path,
		global_options	= "-y",
		inputs			= {entry_path:			input_video_settings},
		outputs			= {output_path_video:	video_settings}
		)
	
	try:
		encode_video.run()
	except:
		error_ffmpeg()

	#create a video thumbnail image
	make_thumbnail = ffmpy.FFmpeg(
		executable		= ffmpeg_path,
		global_options	= "-y",
		inputs			= {entry_path:			input_thumbnail_settings},
		outputs			= {output_path_thumb:	thumbnail_settings}
		)
	
	try:
		make_thumbnail.run()
	except:
		error_ffmpeg()


#when run directly start execution here
def main():
	config = pgu_config(None)

	#retrieve command line argument to identify from qhich source directory to read for source video files
	arguments_parser = argparse.ArgumentParser(description='Prepare web upload gallery files from master videos.')
	arguments_parser.add_argument('source')
	command_line_arguments = arguments_parser.parse_args()

	ffmpeg_path						= config.options["ffmpeg_path"]
	default_output_base_directory	= config.options["output_base_directory"]
	video_settings					= config.options["video_settings"]
	thumbnail_settings				= config.options["thumbnail_settings"]
	source							= command_line_arguments.source

	#verify that ffmpeg.exe and the source are valid
	if not ( ffmpeg_found(ffmpeg_path) and source_found(source) ):
		exit(1)

	if os.path.isdir(source):
		output_directory	= os.path.join( default_output_base_directory, os.path.basename(source) )
		for dir_entry in os.scandir( source ):
			entry_name, entry_extension = os.path.splitext( dir_entry.name )

			if entry_extension.lower() == ".mp4":
				#we have a video file, so let's go and call the usual external tools to process it
				prepare_one_entry(dir_entry.path, ffmpeg_path, output_directory, video_settings, thumbnail_settings)

	elif os.path.isfile(source):
		prepare_one_entry(source, ffmpeg_path, default_output_base_directory, video_settings, thumbnail_settings)


if __name__ == "__main__":
    # execute only if run directly not when imported
    main()