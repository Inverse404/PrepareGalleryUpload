import json
import os


class pgu_config(object):
	"""description of class"""
	default_config_path				= ".\\config.json"
	default_values = {
		"output_base_directory"	: ".\\",
		"ffmpeg_path"			: ".\\ffmpeg.exe",
		"video_settings"		: "-c:a copy -c:v libx264 -profile:v high -preset slower -tune film -crf 20 -movflags +faststart",
		"thumbnail_settings"	: "-vframes 1 -qscale:v 4"
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
			#write a template config file
			with open(config_path, 'w') as new_config_file:
				json.dump(self.options, new_config_file)
		else:
			#load configuration from specified or default config file
			with open(config_path, "r") as config_file:
				self.options = json.load(config_file)

			#fill in all configuration options that were not specified in the file with defaults
			for option in pgu_config.default_values:
				if not option in self.options:
					self.options[option] = pgu_config.default_values[option]
			pass

