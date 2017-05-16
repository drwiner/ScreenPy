# this script crawls through my local moviescript library to assemble a single file.


# import os
from os import listdir
from os.path import isfile, join
path = 'D:\\Documents\\NLP corpora\\imsdb_scenes_sep_2012\\imsdb_scenes_clean'

def joinMovies(movie_paths, combo_name):
	print('joining movies')
	num_movies = 0
	with open(combo_name, 'w') as cn:
		for mp in movie_paths:
			# get all file contents
			movies = [f for f in listdir(mp) if isfile(join(mp, f))]
			for movie in movies:
				num_movies += 1
				# print('reading ' + movie)
				with open(join(mp,movie)) as mn:
					for line in mn:
						if line == '\n':
							continue
						cn.write(line)
					cn.write('\n')
	print(num_movies)


if __name__ == '__main__':
	movie_cats = listdir(path)
	movie_paths = [join(path,f) for f in movie_cats if not isfile(join(path,f))]
	combo_name = 'movie_combo.txt'
	joinMovies(movie_paths, combo_name)
