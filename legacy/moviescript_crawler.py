# this script crawls through my local moviescript library to assemble the corpus.


# import os
from os import listdir, makedirs
from os.path import isfile, join, exists
# path = 'D:\\Documents\\NLP corpora\\imsdb_scenes_sep_2012\\imsdb_scenes_clean'
from screenpile import *


if __name__ == '__main__':

	# get this path from arguments in command line
	path = 'D:\\Documents\\python\\screenpy\\imsdb_raw_nov_2015\\'

	# get this boolean tag from argument in command line, default is to not reload (pkl dump headings)
	DUMP_HEADINGS = 0

	# find all folders at input path
	movie_paths = [join(path,f) for f in listdir(path) if not isfile(join(path,f))]

	# for each movie path, for each movie file, save in its genre folder
	for mp in movie_paths:

		# assemble all movie file .txt files
		movie_files = [f for f in listdir(mp) if isfile(join(mp, f))]

		# make folder in current directory if not exists
		directory = 'ParserOutput//' + mp.split('\\')[-1]
		if not exists(directory):
			makedirs(directory)

		# convert each .txt file into a .json, and save in new folder (in current directory)
		for mf in movie_files:

			print(mf)
			try:

				# the full path of the screenplay
				screenplay = join(mp, mf)

				# just the movie path part of the text file name
				just_mf = mf[:-4]
				with open(screenplay, 'r') as screenplay_file:
					play = screenplay_file.read()

				pkl_file_name = directory + "//" +  just_mf + '.pkl'
				if exists(pkl_file_name) and not DUMP_HEADINGS:
					play = open(screenplay, 'r').read()
					headings = pickle.load(open(pkl_file_name, 'rb'))
				else:
					# annotate the play...
					headings = annotate(play)

					# dump for easy reload later
					pickle.dump(headings, open(pkl_file_name, 'wb'))

				# convert to json and dump in new folder in current directory

				json_output_name = directory + "//" + just_mf + '.json'
				if not exists(json_output_name):
					with open(json_output_name, 'w') as mf_json:
						json.dump(headings, mf_json, indent=4)

			except OverflowError:
				continue
