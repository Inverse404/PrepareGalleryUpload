import subprocess
import argparse
import os
import json
import string
import random

#CONFIGURE your default directories here
default_output_base_directory = "f:\\_temp\\rexx\\gallery upload"
default_ffmpeg_path = "c:\\Tools\\ffmpeg\\ffmpeg.exe"
default_uploaded_base_url = "http://rexxworld.com/ftp-uploads/galleries/"

#retrieve command line argument to identify from qhich source directory to read for source video files
arguments_parser = argparse.ArgumentParser(description='Prepare web upload gallery files from master videos.')
arguments_parser.add_argument('source_directory')
command_line_arguments = arguments_parser.parse_args()

#verify that ffmpeg can be found at the specified location
if os.path.isfile(default_ffmpeg_path ) == False:
	print( "ERROR: ffmpeg.exe not found at the specified location!" )
	exit(1)

#verify that the source directory exists
if os.path.isdir( command_line_arguments.source_directory ) == False:
	print( "ERROR: Source directory not found!")
	exit(2)

ffmpeg_path = default_ffmpeg_path
source_dir_path		= command_line_arguments.source_directory
source_dir_name		= os.path.basename( source_dir_path )
output_directory	= os.path.join( default_output_base_directory, source_dir_name )

uploaded_gallery_url = default_uploaded_base_url + source_dir_name + "/"

#ensure output directory is created if it does not yet exist
if os.path.exists( output_directory ) == False:
	os.makedirs( output_directory )

for dir_entry in os.scandir( source_dir_path ):
	entry_name, entry_extension = os.path.splitext( dir_entry.name )

	if entry_extension.lower() == ".mp4":
		#we have a video file, so let's go and call the usual external tools to process it

		random_name_bit = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
		output_file_name = entry_name.replace( "-UHD", "-HQ" ) + "-" + random_name_bit
		#create a HQ web video file
		subprocess.run( [	ffmpeg_path,
							"-i",
							dir_entry.path,
							"-c:a", "copy",
							"-c:v", "libx264", "-profile:v", "high", "-crf", "20", "-bf", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
							"-y",
							os.path.join(output_directory, output_file_name + ".mp4" )
						] )

		#create a video thumbnail image
		subprocess.run( [	ffmpeg_path,
							"-i",
							dir_entry.path,
							"-vframes", "1",
							"-y",
							os.path.join(output_directory, output_file_name + ".jpg" )
						] )


		uploaded_video_url = uploaded_gallery_url + output_file_name + ".mp4"
		uploaded_thumb_url = uploaded_gallery_url + output_file_name + ".jpg"

