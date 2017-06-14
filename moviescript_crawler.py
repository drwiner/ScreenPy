# this script crawls through my local moviescript library to assemble a single file.


# import os
from os import listdir, makedirs
from os.path import isfile, join, exists
# path = 'D:\\Documents\\NLP corpora\\imsdb_scenes_sep_2012\\imsdb_scenes_clean'
from screenpile import *


def extract_headings(play):
	heads = []
	for result, s, t in HEADINGS.scanString(play):
		indent = result[0]['indent']

		# if indent is a weird screenplay number at random spacing...
		# don't extract this for now
		if indent < 13:
			heading_type = 'in_line'
		elif indent > 50:
			heading_type = 'transition'
		elif indent < 18:
			heading_type = 'heading'
		else:
			heading_type = 'speaker'

		heads.append(Heading(heading_type, result[0], s, t, indent))
	return heads


if __name__ == '__main__':
	# get this path from arguments in command line
	path = 'D:\\Documents\\python\\screenpy\\imsdb_raw_nov_2015\\'

	# find all folders at input path
	movie_paths = [join(path,f) for f in listdir(path) if not isfile(join(path,f))]

	# for each movie path, for each movie file, save in its genre folder
	for mp in movie_paths:

		# assemble all movie file .txt files
		movie_files = [f for f in listdir(mp) if isfile(join(mp, f))]

		# make folder in current directory if not exists
		directory = mp.split('\\')[-1]
		if not exists(directory):
			makedirs(directory)

		# convert each .txt file into a .json, and save in new folder (in current directory)
		for mf in movie_files:

			# the full path of the screenplay
			screenplay = join(mp, mf)

			# just the movie path part of the text file name
			just_mf = mf[:-4]

			screenplay_folder = screenplay[:-4]
			with open(directory + just_mf + '.json', 'w') as mfjson:
				play = mfjson.read()
				headings = extract_headings(play)


	RELOAD = 0
	screenplay = 'indianajonesandtheraidersofthelostark.txt'
	if RELOAD:
		heads = []
		with open(screenplay, 'r') as fn:
			play = fn.read()
			for result, s, t in HEADINGS.scanString(play):
				indent = result[0]['indent']

				# if indent is a weird screenplay number at random spacing...
				# don't extract this for now
				if indent < 13:
					heading_type = 'in_line'
				elif indent > 50:
					heading_type = 'transition'
				elif indent < 18:
					heading_type = 'heading'
				else:
					heading_type = 'speaker'

				heads.append(Heading(heading_type, result[0], s, t, indent))

		heads.sort(key=lambda y: y.start, reverse=False)
		pickle.dump(heads, open('pickle_heads.pkl', 'wb'))
	else:
		play = open(screenplay, 'r').read()
		heads = pickle.load(open('pickle_heads.pkl', 'rb'))

	segments = screenpile_algorithm(heads, play)
	hsegs = separate_into_segs(segments)
	print('ok')
	with open('indianajonesandtheraidersofthelostark.json', 'w') as fp:
		json.dump([seg_to_json(seg, i) for i, seg in enumerate(hsegs)], fp, indent=4)
