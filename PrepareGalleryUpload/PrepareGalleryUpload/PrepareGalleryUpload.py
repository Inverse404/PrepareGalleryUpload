import subprocess
import argparse
import os
import json

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

#create envira gallery import file
envira_gallery = {}
#WARNING: the actual implication of this gallery ID on import in undocumented
# check if this overwrites galleries before production use
envira_gallery["id"] = 9045
envira_gallery["gallery"] = {}
envira_gallery["config"] = {}
envira_gallery["in_gallery"] = []

gallery_entry_id = 0
for dir_entry in os.scandir( source_dir_path ):
	entry_name, entry_extension = os.path.splitext( dir_entry.name )

	if entry_extension.lower() == ".mp4":
		#we have a video file, so let's go and call the usual external tools to process it
		gallery_entry_id += 1
		gallery_entry_id_str = str(gallery_entry_id)

		output_file_name = entry_name.replace( "-UHD", "-HQ" )
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

		#create an entry in the envira gallery import json file
		envira_gallery["gallery"][gallery_entry_id_str]={}
		envira_gallery["gallery"][gallery_entry_id_str]["status"] = "active"
		envira_gallery["gallery"][gallery_entry_id_str]["src"] = ""
		envira_gallery["gallery"][gallery_entry_id_str]["title"] = output_file_name
		envira_gallery["gallery"][gallery_entry_id_str]["link"] = uploaded_video_url
		envira_gallery["gallery"][gallery_entry_id_str]["alt"] = ""
		envira_gallery["gallery"][gallery_entry_id_str]["caption"] = ""
		envira_gallery["gallery"][gallery_entry_id_str]["thumb"] = uploaded_thumb_url
		envira_gallery["gallery"][gallery_entry_id_str]["tags"] = []
		envira_gallery["gallery"][gallery_entry_id_str]["schedule_meta"] = 0
		envira_gallery["gallery"][gallery_entry_id_str]["schedule_meta_start"] = ""
		envira_gallery["gallery"][gallery_entry_id_str]["schedule_meta_end"] = ""
		envira_gallery["gallery"][gallery_entry_id_str]["schedule_meta_ignore_date"] = 0
		envira_gallery["gallery"][gallery_entry_id_str]["schedule_meta_ignore_year"] = 0
		envira_gallery["gallery"][gallery_entry_id_str]["video_aspect_ratio"] = ""
		envira_gallery["gallery"][gallery_entry_id_str]["video_width"] = ""
		envira_gallery["gallery"][gallery_entry_id_str]["video_height"] = ""
		envira_gallery["gallery"][gallery_entry_id_str]["video_in_gallery"] = ""

		envira_gallery["in_gallery"].append( gallery_entry_id )

envira_gallery_import_file_path = os.path.join(default_output_base_directory, source_dir_name + ".json")
envira_gallery_import_file = open( envira_gallery_import_file_path, 'w+' )
json.dump( envira_gallery, envira_gallery_import_file )
envira_gallery_import_file.close()
