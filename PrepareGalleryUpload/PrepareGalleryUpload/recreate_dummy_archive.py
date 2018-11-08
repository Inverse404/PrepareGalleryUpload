import os
import pgu_util
import shu

with open("rexx-archive-list.txt") as tree_listing:
	lines = [line.rstrip('\n') for line in tree_listing]

current_directory = "."
file_list = []

for line in lines:
	tokens = line.split()
	if tokens and len(tokens) >= 3:
		if tokens[0] == "Directory":
			current_directory = " ".join(tokens[2:])

		elif tokens[0] != "Volume" and tokens[1] != "File(s)" and tokens[1] != "Dir(s)" and len(tokens) >= 5:
			if tokens[3] != "<DIR>":
				file_list.append( current_directory + "\\" + (" ".join(tokens[4:])) )

print("Found {0} files".format( len(file_list)) )

with open("rexx_file_list.txt", "w") as list_output:
	for file_name in file_list:
		list_output.writelines([file_name, "\n"])
		dummy_name = "." + file_name[2:]
		pgu_util.create_directory_if_non_existant( os.path.dirname(dummy_name) )
		with open( dummy_name, "w" ) as dummy_file:
			dummy_file.write("DUMMY FILE")