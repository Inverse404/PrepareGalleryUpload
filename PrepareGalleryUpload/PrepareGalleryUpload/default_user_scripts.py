import os
import random
import string

import ffmpy

import pgu_util



#create a HQ web video file
def transcode_to_hq_webvideo( input_path, output_path, configuration ):
	input_video_settings	= None

	encode_video = ffmpy.FFmpeg(
		executable		= configuration.options["ffmpeg_path"],
		global_options	= "-y",
		inputs			= {input_path:	input_video_settings},
		outputs			= {output_path:	configuration.options["video_settings_hd"]}
		)

	pgu_util.call_ffmpeg( encode_video )


#create a video thumbnail image
def create_thumbnail( input_path, output_path, configuration ):
	input_thumbnail_settings	= None

	make_thumbnail = ffmpy.FFmpeg(
		executable		= configuration.options["ffmpeg_path"],
		global_options	= "-y",
		inputs			= {input_path:	input_thumbnail_settings},
		outputs			= {output_path:	configuration.options["thumbnail_settings"]}
		)

	pgu_util.call_ffmpeg( make_thumbnail )


#create a video thumbnail image
def create_poster( input_path, output_path, configuration ):
	input_thumbnail_settings	= None

	make_thumbnail = ffmpy.FFmpeg(
		executable		= configuration.options["ffmpeg_path"],
		global_options	= "-y",
		inputs			= {input_path:	input_thumbnail_settings},
		outputs			= {output_path:	configuration.options["poster_settings"]}
		)

	pgu_util.call_ffmpeg( make_thumbnail )


#create a suitable set of files as needed for publishing on the web
def generate_web_files( source_file_path, configuration ):
	output_directory				= pgu_util.prepare_output_directory( source_file_path, configuration )
	output_file_name, random_bit	= pgu_util.construct_output_web_file_name( source_file_path, output_directory )

	output_path_video			= os.path.join(output_directory, output_file_name + random_bit								+ ".mp4")
	output_path_poster			= os.path.join(output_directory, output_file_name + "-poster"		+ "-"	+ random_bit	+ ".jpg")
	output_path_thumbnail		= os.path.join(output_directory, output_file_name + "-thumbnail"	+ "-"	+ random_bit	+ ".jpg")

	transcode_to_hq_webvideo( source_file_path, output_path_video, configuration )
	create_poster( source_file_path, output_path_poster, configuration )
	create_thumbnail( source_file_path, output_path_thumbnail, configuration )



#
# these get called depending on which type of input was supplied
#

def on_input_image_sequence( source_dir, sequence_base_name ):
	#generate master archive video
	#generate web files
	#cleanup
	pass


def on_input_archive_video( source_video_file_path, configuration_options ):
	try:
		generate_web_files( source_video_file_path, configuration_options )
	except Exception as error_reason:
		raise Exception("web files not successfully generated because ", error_reason.args )
		

def on_input_archive_directory( source_dir_path, configuration_options ):
	#get the full path names of all the files in this directory that have a useful video file type extension
	input_file_paths	= pgu_util.get_input_file_paths_filtered_by_file_extension( source_dir_path, pgu_util.common_video_file_extensions )

	for file_path in input_file_paths:
		#we supposedly have some video files, so let's process each one at a time
		try:
			on_input_archive_video( file_path, configuration_options )
		except Exception as processing_error:
			print( "Error when processing " + file_path )
			print( processing_error )
