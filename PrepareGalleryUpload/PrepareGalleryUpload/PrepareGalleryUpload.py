import subprocess
import argparse
import os
import json
import string
import random

#CONFIGURE your default directories here
default_output_base_directory = "f:\\_temp\\rexx\\gallery upload"
default_ffmpeg_path = "c:\\Tools\\ffmpeg\\ffmpeg.exe"


def prepare_one_entry(entry_path, ffmpeg_path, output_directory):
	#ensure output directory is created if it does not yet exist
	if os.path.exists( output_directory ) == False:
		os.makedirs( output_directory )

	random_name_bit		= ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
	entry_name			= os.path.basename( entry_path )
	output_file_name	= entry_name.replace( "-UHD", "-HQ" ) + "-" + random_name_bit
	#create a HQ web video file
	subprocess.run( [	ffmpeg_path,
						"-i",
						entry_path,
						"-c:a", "copy",
						"-c:v", "libx264", "-profile:v", "high", "-crf", "20", "-bf", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
						"-y",
						os.path.join(output_directory, output_file_name + ".mp4" )
					] )

	#create a video thumbnail image
	subprocess.run( [	ffmpeg_path,
						"-i",
						entry_path,
						"-vframes", "1",
						"-y",
						os.path.join(output_directory, output_file_name + ".jpg" )
					] )


#retrieve command line argument to identify from qhich source directory to read for source video files
arguments_parser = argparse.ArgumentParser(description='Prepare web upload gallery files from master videos.')
arguments_parser.add_argument('source')
command_line_arguments = arguments_parser.parse_args()

#verify that ffmpeg can be found at the specified location
if os.path.isfile(default_ffmpeg_path ) == False:
	print( "ERROR: ffmpeg.exe not found at the specified location!" )
	exit(1)

#verify that the source directory exists
if (os.path.isdir (command_line_arguments.source ) == False) and (os.path.isfile( command_line_arguments.source ) == False):
	print( "ERROR: Source directory ot file not found!")
	exit(2)

ffmpeg_path			= default_ffmpeg_path
source				= command_line_arguments.source

if os.path.isdir(source):
	output_directory	= os.path.join( default_output_base_directory, os.path.basename(source) )
	for dir_entry in os.scandir( source ):
		entry_name, entry_extension = os.path.splitext( dir_entry.name )

		if entry_extension.lower() == ".mp4":
			#we have a video file, so let's go and call the usual external tools to process it
			prepare_one_entry(dir_entry.path, ffmpeg_path, output_directory)

elif os.path.isfile(source):
	prepare_one_entry(source, ffmpeg_path,default_output_base_directory)

