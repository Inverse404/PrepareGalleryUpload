import os
import random
import string

# some useful common use data

common_video_file_extensions = [".mp4", ".avi", ".mpg", ".mpeg", ".wmv", ".webm", ".flv", ".mkv", ".mov", ".m4v"]
file_quality_suffixes = ["-HQ", "-LQ", "-UHD", "-HD", "-SD"]


#some useful common use functions

def get_random_name_bits_from_existing_file( source_raw_name, search_directory, random_name_bit_length ):
	random_name_bit = None

	for dir_entry in os.scandir( search_directory ):
		if dir_entry.is_file():
			name, ext = os.path.splitext( dir_entry.name )
			if name.startswith( source_raw_name ) and (len(name) - random_name_bit_length >= len(source_raw_name)):
				ending_bit = name[-random_name_bit_length:]
				if ending_bit.isalnum():
					random_name_bit = ending_bit

	if random_name_bit == None:
		raise Exception("random name bit not found")
	else:
		return random_name_bit


def chop_off_suffixes( some_string, suffix_list ):
	chop_off_amount = 0

	for suffix in suffix_list:
		if some_string.endswith( suffix ):
			chop_off_amount = max( chop_off_amount, len(suffix) )

	return some_string[:len(some_string) - chop_off_amount]


def get_input_file_paths_filtered_by_file_extension( source_dir_path, allowed_extensions ):
	found_valid_file_paths = []
	allowed_extensions_lower_case = set()

	#this will also remove duplicate extensions given in input, since this goes into a set
	for allowed_extension in allowed_extensions:
		allowed_extensions_lower_case.add( allowed_extension.lower() )

	for dir_entry in os.scandir( source_dir_path ):
		entry_name, entry_extension = os.path.splitext( dir_entry.name )

		for allowed_extension in allowed_extensions_lower_case:
			if entry_extension.lower() == allowed_extension:
				found_valid_file_paths.append( dir_entry.path )

	return found_valid_file_paths


def parent_dir_base_name( source_file_path ):
	return os.path.basename( os.path.dirname( source_file_path ) )


def create_directory_if_non_existant( output_directory ):
	if os.path.exists( output_directory ) == False:
		try:
			os.makedirs( output_directory )
		except:
			raise Exception("directory could not be created")


def prepare_web_output_directory( source_file_path, configuration ):
	output_base_directory		= configuration.options["web_files_base_directory"]
	output_subdirectory			= parent_dir_base_name( source_file_path )
	output_directory			= os.path.join( output_base_directory, output_subdirectory )
	#ensure output directory is created if it does not yet exist
	create_directory_if_non_existant( output_directory )
	return output_directory


def extract_creation_timestamp( source_file_path ):
	year_prefix		= None
	month_prefix	= None
	day_prefix		= None

	raw_file_name, extension	= os.path.splitext( os.path.basename( source_file_path ))
	#try to detect year prefix
	if len(raw_file_name) > 4 and raw_file_name[:4].isdigit():
		potential_year_prefix_value = int(raw_file_name[:4])
		if potential_year_prefix_value > 2000 and potential_year_prefix_value < 3000:
			year_prefix = raw_file_name[:4]
			#now see if there is also a fine grained month-day prefix part
			if len(raw_file_name) > 9 and raw_file_name[5:9].isdigit():
				potential_month_prefix_value	= int(raw_file_name[5:7])
				potential_day_prefix_value		= int(raw_file_name[7:9])
				if potential_month_prefix_value >= 1 and potential_month_prefix_value <= 12:
					month_prefix = raw_file_name[5:7]
				if potential_day_prefix_value >= 1 and potential_day_prefix_value <= 31:
					day_prefix = raw_file_name[7:9]

	creation_timestamp = ""
	if year_prefix != None:
		creation_timestamp += year_prefix
		if month_prefix != None:
			creation_timestamp += "-"
			creation_timestamp += month_prefix
			if day_prefix != None:
				creation_timestamp += day_prefix

	if len(creation_timestamp) == 0:
		creation_timestamp = "_unknown_creation_time"
	return creation_timestamp


def prepare_archive_output_directory( source_file_path, configuration ):
	output_base_directory		= configuration.options["archive_base_directory"]
	output_subdirectory			= extract_creation_timestamp( source_file_path )
	output_directory			= os.path.join( output_base_directory, output_subdirectory )
	#ensure output directory is created if it does not yet exist
	create_directory_if_non_existant( output_directory )
	return output_directory


def construct_output_web_file_name( source_file_path, output_directory ):
	entry_name, entry_extension = os.path.splitext(os.path.basename( source_file_path ))
	source_raw_name				= chop_off_suffixes(entry_name, file_quality_suffixes)

	random_name_bit_length		= 6

	#check output dir if there is any file with random bits that was generated from the same
	#raw file name, so we can  keep the random bits the same and make overwriting easy
	#so that there will not be dulpicate files with just different random name bits
	try:
		random_name_bit				= get_random_name_bits_from_existing_file( source_raw_name, output_directory, random_name_bit_length )
	except:
		random_name_bit				= ''.join(random.choices(string.ascii_uppercase + string.digits, k = random_name_bit_length))

	return source_raw_name + "-HQ", random_name_bit

def check_if_ffmpeg_file_exists( ffmpeg_path ):
	if os.path.isfile( ffmpeg_path ) == False:
		raise Exception("No file found at specified ffmpeg path: " + ffmpeg_path)


def	check_if_source_path_exists( source_path ):
	if (os.path.isdir ( source_path ) == False) and (os.path.isfile( source_path ) == False):
		raise Exception("No file or directory found at specified source path: " + source_path)


def call_ffmpeg( ffmpy_session ):
	try:
		ffmpy_session.run()
	except:
		raise Exception( "an error occurred invoking ffmpeg" )


def is_aec_project_token(source):
	is_token_file = False

	name, ext = os.path.splitext(source)
	if ext.lower() == ".aec":
		is_token_file = True

	return is_token_file