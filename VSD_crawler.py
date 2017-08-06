"""
David R. Winer

This craws through ParsedOutput folder, whose output is a singly nested list whose units have a 'text' attribute.
The text field should be raw text, and this runs VSD (verb-sense disambiguation) to create sense profile, the sense
of the meaning of the verbs in the text (FrameNet frame + list of WordNet synsets).

"""


from os import listdir, makedirs
from os.path import isfile, join, exists
# path = 'D:\\Documents\\NLP corpora\\imsdb_scenes_sep_2012\\imsdb_scenes_clean'
from verb_sense.VSD_withSpacy import sense_profile
import json

from shutil import copyfile

if __name__ == '__main__':

	# get this path from arguments in command line
	path = 'D:\\Documents\\python\\screenpy\\ParserOutput\\'

	# find all folders at input path
	movie_paths = [join(path,f) for f in listdir(path) if not isfile(join(path,f))]

	# keep track of file_names and point to their folders
	file_folder_dict = {}

	# first, assemble all existing json files:
	output_path = 'D:\\Documents\\python\\screenpy\\ParserOutput_VSD\\'
	output_paths = [join(output_path,f) for f in listdir(output_path) if not isfile(join(output_path,f))]
	for mp in output_paths:

		movie_files = [f for f in listdir(mp) if isfile(join(mp, f)) and f[-5:] == '.json']
		genre = mp.split('\\')[-1]
		for file in movie_files:
			file_folder_dict[file] = 'ParserOutput_VSD//' + genre + '//' + file

	# for each movie path, for each movie file, save in its genre folder
	for mp in movie_paths:

		# assemble all movie file .txt files
		movie_files = [f for f in listdir(mp) if isfile(join(mp, f)) and f[-5:] == '.json']

		# make folder in current directory if not exists
		directory = 'ParserOutput_VSD//' + mp.split('\\')[-1]
		if not exists(directory):
			makedirs(directory)


		for mf in movie_files:

			print(mf)

			json_output_name = directory + "//" + mf

			if exists(json_output_name):
				print('already parsed')
				if json_output_name not in file_folder_dict[mf]:
					file_folder_dict[mf] = json_output_name
				continue

			if mf in file_folder_dict.keys():
				# then just copy that folder and move here.
				copyfile(file_folder_dict[mf], json_output_name)
				print('screenplay {} found in folder {}'.format(mf, json_output_name))
				continue

			# the full path of the screenplay
			screenplay = join(mp, mf)

			# just the movie path part of the text file name
			# just_mf = mf[:-4]
			with open(screenplay) as json_file:
				data = json.load(json_file)

			if len(data) == 0:
				continue

			for ms in data:
				for seg in ms:
					if seg['head_type'] != 'heading':
						continue
					raw_text = seg['text']
					if raw_text == '':
						continue
					text = ' '.join(seg['text'].split())
					if text == '':
						continue
					try:
						sp = sense_profile(text)
					except KeyError:
						print('something wrong with this text? \n{}'.format(text))
						continue
					seg['sense_profile'] = sp

			with open(json_output_name, 'w') as mf_json:
				json.dump(data, mf_json, indent=4)

			# keep track of the folders that files are located
			file_folder_dict[mf] = json_output_name