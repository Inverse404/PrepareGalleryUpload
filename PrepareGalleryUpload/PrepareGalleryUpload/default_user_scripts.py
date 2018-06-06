import os
import random
import string

import ffmpy

import pgu_util



#create the big ugly GIF legacy compatibility file
def create_gif_preview( input_path, output_path, configuration ):
	gif_settings = {
		"palette_gen"	: configuration.options["gif_color_palette_gen"],
		"image_gen"		: configuration.options["gif_image_gen"]
		}

	for option in gif_settings:
		gif_settings[option] = gif_settings[option].replace("GIF_HEIGHT", configuration.options["gif_height"])
		gif_settings[option] = gif_settings[option].replace("GIF_WIDTH", configuration.options["gif_width"])

	gif_palette_file_name	= "_gif_palette_temp.png"

	create_gif_colour_palette = ffmpy.FFmpeg(
		executable		= configuration.options["ffmpeg_path"],
		global_options	= "-y",
		inputs			= {input_path:				None},
		outputs			= {gif_palette_file_name:	gif_settings["palette_gen"]}
		)

	pgu_util.call_ffmpeg( create_gif_colour_palette )

	create_gif_image = ffmpy.FFmpeg(
		executable		= configuration.options["ffmpeg_path"],
		global_options	= "-y",
		inputs			= {	input_path:				None,
							gif_palette_file_name:	None},
		outputs			= {output_path:				gif_settings["image_gen"]}
		)

	pgu_util.call_ffmpeg( create_gif_image )

	os.remove( gif_palette_file_name )


#create the lossless master archive video file from an image sequence
def encode_lossless_video_from_image_sequence( input_path, output_path, configuration ):
	input_sequence_settings	= configuration.options["image_sequence_settings"]

	encode_video = ffmpy.FFmpeg(
		executable		= configuration.options["ffmpeg_path"],
		global_options	= "-y",
		inputs			= {input_path:	input_sequence_settings},
		outputs			= {output_path:	configuration.options["video_settings_lossless"]}
		)

	pgu_util.call_ffmpeg( encode_video )


#create the master high quality archive video file from an image sequence
def encode_master_video_from_image_sequence( input_path, output_path, configuration ):
	input_sequence_settings	= configuration.options["image_sequence_settings"]

	encode_video = ffmpy.FFmpeg(
		executable		= configuration.options["ffmpeg_path"],
		global_options	= "-y",
		inputs			= {input_path:	input_sequence_settings},
		outputs			= {output_path:	configuration.options["video_settings_uhd"]}
		)

	pgu_util.call_ffmpeg( encode_video )


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


#create a HQ web video file
def recover_what_can_be_saved_from_gif_crap( input_path, output_path, configuration ):
	input_video_settings	= None

	encode_video = ffmpy.FFmpeg(
		executable		= configuration.options["ffmpeg_path"],
		global_options	= "-y",
		inputs			= {input_path:	input_video_settings},
		outputs			= {output_path:	configuration.options["video_from_gif_settings"]}
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
	output_web_directory			= pgu_util.prepare_web_output_directory( source_file_path, configuration )
	output_gifs_directory			= pgu_util.prepare_gifs_output_directory( source_file_path, configuration )
	output_file_name, random_bit	= pgu_util.construct_output_web_file_name( source_file_path, output_gifs_directory )

	output_path_video			= os.path.join(output_web_directory, output_file_name 					+ "-"	+ random_bit	+ ".mp4")
	output_path_poster			= os.path.join(output_web_directory, output_file_name					+ "-"	+ random_bit	+ ".jpg")
	output_path_thumbnail		= os.path.join(output_web_directory, output_file_name + "-thumbnail"	+ "-"	+ random_bit	+ ".jpg")
	output_path_gif				= os.path.join(output_gifs_directory, output_file_name					+ "-"	+ random_bit	+ ".gif")

	if pgu_util.is_crap_gif_input( source_file_path ):
		recover_what_can_be_saved_from_gif_crap( source_file_path, output_path_video, configuration )
	else:
		transcode_to_hq_webvideo( source_file_path, output_path_video, configuration )

	create_poster( source_file_path, output_path_poster, configuration )
	create_gif_preview( source_file_path, output_path_gif, configuration )
#	create_thumbnail( source_file_path, output_path_thumbnail, configuration )


#create a new master video file in a suitable subdir in the master archive
def generate_master_archive_file( token_file_path, configuration ):
	output_directory					= pgu_util.prepare_archive_output_directory( token_file_path, configuration )
	token_file_name, token_extension	= os.path.splitext( os.path.basename(token_file_path) )
	input_directory						= os.path.dirname( token_file_path )

	output_path_video			= os.path.join(output_directory,	token_file_name	+ "-UHD"		+ ".mp4")
	output_path_lossless_video	= os.path.join(output_directory,	token_file_name	+ "-LOSSLESS"	+ ".mkv")
	input_path_sequence			= os.path.join(input_directory,		token_file_name	+ "%04d"		+ ".png")

	for requested_master_file_type in configuration.options["archive_master_file_types"]:
		if requested_master_file_type == "LOSSLESS":
			encode_lossless_video_from_image_sequence( input_path_sequence, output_path_lossless_video, configuration )
		if requested_master_file_type == "UHD":
			encode_master_video_from_image_sequence( input_path_sequence, output_path_video, configuration )

	return output_path_video



#
# these get called depending on which type of input was supplied
#

def on_input_image_sequence( token_file_path, configuration_options ):
	#generate master archive video
	try:
		new_master_archive_video_file_path = generate_master_archive_file( token_file_path, configuration_options )
	except Exception as error_reason:
		raise Exception("master archive file not successfully generated because ", error_reason.args )
	
	#generate web files
	try:
		generate_web_files( new_master_archive_video_file_path, configuration_options )
	except Exception as error_reason:
		raise Exception("web files not successfully generated because ", error_reason.args )
	
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
