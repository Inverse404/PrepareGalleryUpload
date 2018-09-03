import os
import shutil

from collections import defaultdict
from collections import namedtuple

from pgu_config import pgu_config
import pgu_util
import default_user_scripts


configuration = pgu_config(None)

UWF_file_info = namedtuple( 'UWF_file_info', ['path', 'file_name', 'relative_path', 'stripped_name'] )

archive_base_directory			= configuration.options["archive_base_directory"]
removed_web_files_directory		= configuration.options["removed_web_files_base_directory"]
web_files_base_directory		= configuration.options["web_files_base_directory"]
new_web_files_base_directory	= configuration.options["new_files_web_files_base_directory"]

pgu_util.create_directory_if_non_existant( removed_web_files_directory )
pgu_util.create_directory_if_non_existant( web_files_base_directory )


def scan_archive_tree( base_dir ):
	archive_files = {}
	for dirpath, subdirs, files in os.walk( base_dir ):
		for file_name in files:
			qualified_file_path = os.path.join( dirpath, file_name )
			relative_path		= os.path.relpath( dirpath, base_dir )
			pure_name, ext		= os.path.splitext( file_name )
			stripped_name		= pgu_util.chop_off_suffixes( pure_name, pgu_util.file_quality_suffixes )

			file_info			= UWF_file_info( qualified_file_path, file_name, relative_path, stripped_name )

			if ext in pgu_util.common_video_file_extensions:
				archive_files[qualified_file_path] = file_info

	return archive_files


def scan_web_files_tree( base_dir ):
	web_vid_files = {}
	web_thumb_files = {}
	for dirpath, subdirs, files in os.walk( base_dir ):
		for file_name in files:
			qualified_file_path = os.path.join( dirpath, file_name )
			relative_path		= os.path.relpath( dirpath, base_dir )
			pure_name, ext		= os.path.splitext( file_name )
			stripped_name		= pgu_util.chop_off_suffixes( pgu_util.chop_off_random_name_bits( pure_name ), pgu_util.file_quality_suffixes )

			file_info			= UWF_file_info( qualified_file_path, file_name, relative_path, stripped_name )

			if ext in pgu_util.common_video_file_extensions:
				web_vid_files[qualified_file_path] = file_info
			if ext in ['.jpg', '.jpeg']:
				web_thumb_files[qualified_file_path] = file_info

	return web_vid_files, web_thumb_files


def index_files_by_stripped_name( files ):
	web_files_by_raw_name = defaultdict(defaultdict)

	for	qualified_file_path, file_info in files.items():
		web_files_by_raw_name[file_info.stripped_name][file_info.relative_path] = file_info

	return web_files_by_raw_name


def move_orphaned_web_files_to_removed_dir( files ):
	for qualified_path, file_info in files.items():
		shutil.move( qualified_path, os.path.join( removed_web_files_directory, file_info.file_name ) )


def pop_matching_web_file( archive_file_info, web_files_by_url, web_files_by_stripped_name ):
	file_match = None

	if archive_file_info.stripped_name in web_files_by_stripped_name:
		if archive_file_info.relative_path in web_files_by_stripped_name[archive_file_info.stripped_name]:
			#matching file at correct location found, prefer this one
			file_match = web_files_by_stripped_name[archive_file_info.stripped_name][archive_file_info.relative_path]
			del web_files_by_stripped_name[archive_file_info.stripped_name][archive_file_info.relative_path]
		else:
			#just pick the first one viable
			subdir_key, file_match = web_files_by_stripped_name[archive_file_info.stripped_name].popitem()

		if file_match.path in web_files_by_url:
			del web_files_by_url[file_match.path]

	return file_match


def synch_web_file_placement( archive_file_info, matching_web_file, target_web_files_base_directory ):
	destination_dir			= os.path.join( target_web_files_base_directory, archive_file_info.relative_path )
	destination_file_url	= os.path.join( destination_dir, matching_web_file.file_name )
	pgu_util.create_directory_if_non_existant( os.path.join( target_web_files_base_directory, archive_file_info.relative_path) )
	shutil.move( matching_web_file.path, destination_file_url )


archive_files_by_url									= scan_archive_tree( archive_base_directory )
archive_files_by_stripped_name							= index_files_by_stripped_name( archive_files_by_url )

web_vid_files_by_url, web_thumb_files_by_url			= scan_web_files_tree( web_files_base_directory )
web_vid_files_by_stripped_name							= index_files_by_stripped_name( web_vid_files_by_url )
web_thumb_files_by_stripped_name						= index_files_by_stripped_name( web_thumb_files_by_url )

new_web_vid_files_by_url, new_web_thumb_files_by_url	= scan_web_files_tree( new_web_files_base_directory )
new_web_vid_files_by_stripped_name						= index_files_by_stripped_name( new_web_vid_files_by_url )
new_web_thumb_files_by_stripped_name					= index_files_by_stripped_name( new_web_thumb_files_by_url )


for archive_file_url, archive_file_info in archive_files_by_url.items():
	#check latest generated files for a match
	random_bit = None
	matching_web_vid_file = pop_matching_web_file( archive_file_info, new_web_vid_files_by_url, new_web_vid_files_by_stripped_name )

	#check older generated files for a match
	if matching_web_vid_file == None:
		matching_web_vid_file = pop_matching_web_file( archive_file_info, web_vid_files_by_url, web_vid_files_by_stripped_name )

	if matching_web_vid_file != None:
		synch_web_file_placement( archive_file_info, matching_web_vid_file, web_files_base_directory )
		random_bit = pgu_util.get_random_name_bits( matching_web_vid_file.file_name )
	else:
		#generate_missing_web_video_file()
		output_web_directory			= os.path.os.path.join( web_files_base_directory, archive_file_info.relative_path )
		pgu_util.create_directory_if_non_existant( output_web_directory )
		output_file_name, random_bit	= pgu_util.construct_output_web_file_name( archive_file_info.path, output_web_directory )
		output_path_video				= os.path.join(output_web_directory, output_file_name + "-"	+ random_bit + ".mp4")

		if pgu_util.is_crap_gif_input( archive_file_info.path ):
			default_user_scripts.recover_what_can_be_saved_from_gif_crap( archive_file_info.path, output_path_video, configuration )
		else:
			default_user_scripts.transcode_to_hq_webvideo( archive_file_info.path, output_path_video, configuration )

	#same for thumbnails
	#check latest generated files for a match
	matching_web_thumb_file = pop_matching_web_file( archive_file_info, new_web_thumb_files_by_url, new_web_thumb_files_by_stripped_name )

	#check older generated files for a match
	if matching_web_thumb_file == None:
		matching_web_thumb_file = pop_matching_web_file( archive_file_info, web_thumb_files_by_url, web_thumb_files_by_stripped_name )

	if matching_web_thumb_file != None:
		synch_web_file_placement( archive_file_info, matching_web_thumb_file, web_files_base_directory )
	else:
		#generate_missing_web_thumb_file()
		output_web_directory			= os.path.os.path.join( web_files_base_directory, archive_file_info.relative_path )
		pgu_util.create_directory_if_non_existant( output_web_directory )
		output_file_name, random_bit	= pgu_util.construct_output_web_file_name( archive_file_info.path, output_web_directory )
		output_path_poster				= os.path.join(output_web_directory, output_file_name + "-"	+ random_bit + ".jpg")

		default_user_scripts.create_poster( archive_file_info.path, output_path_poster, configuration )
#	create_gif_preview( source_file_path, output_path_gif, configuration )


move_orphaned_web_files_to_removed_dir( web_vid_files_by_url )
move_orphaned_web_files_to_removed_dir( web_thumb_files_by_url )
move_orphaned_web_files_to_removed_dir( new_web_vid_files_by_url )
move_orphaned_web_files_to_removed_dir( new_web_thumb_files_by_url )


