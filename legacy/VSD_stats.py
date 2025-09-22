"""
David R. Winer

This craws through ParsedOutput_VSD folder, whose segments contain senseProfiles of the form...

	sp = [verb, [frame.name, frame.ID], [str(syns) for syns in synsets], arg_frames]

and it builds a dictionary of frame_names used and synsets used.

Should do this for each genre!
"""


from os import listdir, makedirs
from os.path import isfile, join, exists
# path = 'D:\\Documents\\NLP corpora\\imsdb_scenes_sep_2012\\imsdb_scenes_clean'

import json
from collections import defaultdict

def score_stats(screenplay_files):

	verb_dict = defaultdict(list)
	verb_num_dict = defaultdict(int)
	frame_num_dict = defaultdict(int)
	frame_verb_dict = defaultdict(set)
	frame_syns_dict = defaultdict(set)

	num_files = 0

	total_segs = 0
	total_msegs = 0
	for file in screenplay_files:
		with open(file) as json_file:
			data = json.load(json_file)

		if len(data) == 0:
			continue
		num_files += 1
		total_msegs += len(data)
		total_segs += sum(1 for mseg in data for seg in mseg)

		for mseg in data:
			for seg in mseg:
				if 'sense_profile' not in seg.keys():
					continue

				sps = seg['sense_profile']
				if sps is None or sps == '' or sps == 'none' or sps == []:
					continue

				for sp in sps:
					if sp is None or sp == '' or sp == 'none' or sp == []:
						continue

					verb, frame, synsets, _ = sp
					verb_dict[verb].append(frame[0])
					verb_num_dict[verb] += 1
					frame_num_dict[frame[0]] += 1
					frame_verb_dict[frame[0]].add(verb)
					frame_syns_dict[frame[0]].update(set(synsets))


	# avg_mseg = mseg_avg_frame/len(data)
	# avg_seg = mseg_avg_frame /len
	# genre_avg_syns = sum(syns_num_dict.values()) / len(screenplay_files)
	genre_avg_frames = sum(frame_num_dict.values()) / len(screenplay_files)
	seg_avg_frames = sum(frame_num_dict.values()) / total_segs
	mseg_avg_frames = sum(frame_num_dict.values()) / total_msegs

	return (genre_avg_frames, seg_avg_frames, mseg_avg_frames, frame_num_dict, frame_verb_dict, frame_syns_dict)

def output_genre_stats(genre_stats, filename):
	with open(filename, 'w') as genre_file:
		for genre, (genre_avg_frames, seg_avg_frames, mseg_avg_frames, frame_num_dict, frame_verb_Dict, frame_syns_dict) in genre_stats.items():
			# genre_file.write('|' + str(genre) + '\t|\t')
			genre_file.write(str(genre) + '\t')
			# genre_file.write(str(genre_avg_frames) + '\t|\t')
			genre_file.write(str(genre_avg_frames) + '\t')
			genre_file.write(str(mseg_avg_frames) + '\t')
			genre_file.write(str(seg_avg_frames) + '\t')

			# for item in stat_list:
			# 	genre_file.write(str(item) + '\t|\t')
			genre_file.write('\n')

			with open('VSD_genre//VSD_frame_dict_by_genre_' + genre + '.txt', 'w') as vsdf:
				vsdf.write(str(genre) + '\n')
				for frame, num in frame_num_dict.items():
					vsdf.write('{}\t{}\t'.format(str(frame), str(num)))
					vsdf.write(str(frame_verb_Dict[frame]))
					vsdf.write('\t')
					vsdf.write(str(frame_syns_dict[frame]))
					vsdf.write('\n')


def just_westerns(screenplay_files):

		for file in screenplay_files:
			with open(file) as json_file:
				data = json.load(json_file)

			if len(data) == 0:
				continue

			print(file)
			the_count = 0

			for mseg in data:
				for seg in mseg:
					if 'sense_profile' not in seg.keys():
						continue

					sps = seg['sense_profile']
					if sps is None or sps == '' or sps == 'none' or sps == []:
						continue

					for sp in sps:
						if sp is None or sp == '' or sp == 'none' or sp == []:
							continue

						the_count += 1
			print(len(data))
			print(str(sum(1 for mseg in data for seg in mseg)))
			print(the_count)
			print('\n')


if __name__ == '__main__':

	# get this path from arguments in command line
	path = 'D:\\Documents\\python\\screenpy\\ParserOutput_VSD\\'

	genre_folders = [(f, join(path, f)) for f in listdir(path) if not isfile(join(path, f))]
	genre_stats = {}
	for genre, genre_path in genre_folders:


		# if genre == 'Western':
		screenplay_files = [join(genre_path, f) for f in listdir(genre_path) if
		                    isfile(join(genre_path, f)) and f[-5:] == '.json']

		# just_westerns(screenplay_files)


		genre_stats[genre] = score_stats(screenplay_files)

	output_genre_stats(genre_stats, filename='VSD_genre//VSD_genre_stats.txt')
			# break
