# this script crawls through my local moviescript library to assemble a single file.


# import os
from os import listdir
from os.path import isfile, join
# path = 'D:\\Documents\\NLP corpora\\imsdb_scenes_sep_2012\\imsdb_scenes_clean'
path = 'D:\\Documents\\python\\screenpy\\imsdb_raw_nov_2015\\'
from screenpile import *

if __name__ == '__main__':
	movie_cats = listdir(path)
	movie_paths = [join(path,f) for f in movie_cats if not isfile(join(path,f))]

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
