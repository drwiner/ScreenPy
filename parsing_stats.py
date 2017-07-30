"""
Use this script to read json objects from ParserOutput folder and deliver stats about each genre.
"""
from os import listdir
from os.path import isfile, join

import json

def get_heading(dict_item):
	#[is_master, is_dlg, has_loc, has_subj, has_tod, has_st]
	seg_attr_list = [0,0,0,0,0,0]

	if 'terior' in dict_item.keys():
		seg_attr_list[0] = True
	if 'location' in dict_item.keys():
		seg_attr_list[2] = True
	if 'ToD' in dict_item.keys():
		seg_attr_list[4] = True
	if 'shot type' in dict_item.keys():
		seg_attr_list[5] = True
	if 'subj' in dict_item.keys():
		seg_attr_list[3] = True
	elif sum(seg_attr_list[:2]) + sum(seg_attr_list[4:]) == 0:
		# must be subject if it's nothing else
		seg_attr_list[3] = True
	return seg_attr_list


def append_seg_to_stats(stat, seg):
	# seg = [is_master, is_dlg, has_loc, has_subj, has_tod, has_st]
	# stat = ['num_segs num_master num_dlg_segs num_has_loc num_has_subj num_has_tod num_has_st']
	stat[0] += 1
	for i, seg_item in enumerate(seg):
		stat[i+1] += seg_item
	# stat[1:] = [stat[i+1] + seg[i] for i in range(seg)]
	return stat


def score_genre(screenplay_files):
	stats = []
	for file in screenplay_files:
		with open(file) as json_file:
			data = json.load(json_file)

		dlg_seg = [0,1,0,0,0,0]
		segments = []
		for (heading_item, dialogue_item) in data:
			seg = get_heading(heading_item['result'])
			segments.append(seg)
			segments.extend([dlg_seg for i in range(len(dialogue_item))])
		stat = [0,0,0,0,0,0,0]
		for seg in segments:
			append_seg_to_stats(stat, seg)
		stats.append(stat)
	return stats



if __name__ == '__main__':
	folder = 'ParserOutput\\'
	genre_folders = [(f, join(folder, f)) for f in listdir(folder) if not isfile(join(folder, f))]
	genre_stats = {}
	for genre, genre_path in genre_folders:
		screenplay_files = [join(genre_path, f) for f in listdir(genre_path) if isfile(join(genre_path, f)) and f[-5:] == '.json']
		genre_stat = score_genre(screenplay_files)

		sums = [sum(stat[i] for stat in genre_stat) for i in range(7)]
		avgs = [s/len(genre_stat) for s in sums]
		genre_stats[genre] = (len(genre_stat), avgs)

	with open('genre_stats.txt', 'w') as genre_file:
		for genre, (num_screenplays, avgs) in genre_stats.items():
			genre_file.write(str(genre) + '\t')
			genre_file.write(str(num_screenplays) + '\t')
			for item in avgs:
				genre_file.write(str(item) + '\t')
			genre_file.write('\n')