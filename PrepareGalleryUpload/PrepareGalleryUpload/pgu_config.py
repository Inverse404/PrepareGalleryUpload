import json
import os


class pgu_config(object):
	"""description of class"""
	default_config_path				= ".\\config.json"
	default_values = {
		"ffmpeg_path"				: ".\\ffmpeg.exe",
		"video_settings"			: "-c:a copy -c:v libx264 -profile:v high -preset slower -tune film -crf 20 -movflags +faststart",
		"thumbnail_settings"		: "-frames:v 1 -s 640x360 -qscale:v 4",
		"poster_settings"			: "-frames:v 1 -qscale:v 4",
		"archive_base_direcory"		: ".\\archive",
		"web_files_base_directory"	: ".\\web",
		"video_settings_uhd"		: "-c:a copy -c:v libx264 -profile:v high -preset slower -tune film -crf 16 -movflags +faststart",
		"video_settings_hd"			: "-c:a copy -c:v libx264 -profile:v high -preset slow -tune film -crf 20 -movflags +faststart",
		"video_settings_sd"			: "-c:a copy -c:v libx264 -profile:v high -preset slow -tune film -crf 22 -movflags +faststart",
		"image_sequence_settings"	: "-framerate 30",
		"deprecated_settings"		: { "output_base_directory"		: ".\\"}
		}

	def __init__(self, custom_config_path):
		self.options = {}
		#search default config file in current working directory if not specified
		if custom_config_path == None:
			config_path = pgu_config.default_config_path
		else:
			config_path = custom_config_path

		if os.path.isfile( config_path ) == False:
			#if config file was not found use all default values
			for option in pgu_config.default_values:
				self.options[option] = pgu_config.default_values[option]
		else:
			#load configuration from specified or default config file
			try:
				with open(config_path, "r") as config_file:
						self.options = json.load(config_file)
			except:
				#loading from the config file encountered and error
				print( "ERROR reading existing config file!" )
				try:
					os.rename( config_path, config_path + ".defective" );
					print( "Renamed defective config file to "+ config_path, config_path + ".defective" )
					print( "New template config file will be generated under its name instead." )
				except:
					print( "ERROR Could not rename defective config file." )	

			#fill in all configuration options that were not specified in the file with defaults
			for option in pgu_config.default_values:
				if not option in self.options:
					self.options[option] = pgu_config.default_values[option]

		#move aside any deprecated values so the user will be aware of it
		for setting in self.options["deprecated_settings"]:
			if setting in self.options:
				self.options["deprecated_settings"][setting] = self.options.pop( setting, None )

		#write back the established config
		#this will either be new template default config or
		#an existing config will be replaced with one extended
		#by all unused options filled in with defaults
		#so the user will be made aware of all additional
		#options that are available
		with open(config_path, 'w') as new_config_file:
			try:
				json.dump(self.options, new_config_file, indent=4)
				print( "Updated config file " + config_path )
			except:
				print( "ERROR Unable to write to config file." )

