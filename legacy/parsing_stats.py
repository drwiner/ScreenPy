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
	stats = [0, 0, 0, 0, 0, 0, 0]
	num_files = 0
	for file in screenplay_files:
		with open(file) as json_file:
			data = json.load(json_file)

		if len(data) == 0:
			continue
		num_files += 1

		num_mastas = len(data)
		num_segs = sum(len(ms) for ms in data)
		num_headings = sum(1 for ms in data for seg in ms if seg['head_type'] == 'heading')
		num_speakers = sum(1 for ms in data for seg in ms if seg['head_type'] == 'speaker/title')

		# num_has_lo = sum(1 for ms in data for seg in ms if seg['head_text']['shot type'] is not None)
		num_has_shot = sum(1 for ms in data for seg in ms if seg['head_type'] == 'heading' and seg['head_text']['shot type'] is not None)
		num_has_subj = sum(1 for ms in data for seg in ms if seg['head_type'] == 'heading' and seg['head_text']['subj'] is not None)
		num_has_tod = sum(1 for ms in data for seg in ms if seg['head_type'] == 'heading' and seg['head_text']['ToD'] is not None)

		stats[0] += num_mastas
		stats[1] += num_segs
		stats[2] += num_headings
		stats[3] += num_speakers
		stats[4] += num_has_shot
		stats[5] += num_has_subj
		stats[6] += num_has_tod

	return ([x / num_files if x > 0 else x for x in stats], num_files)
	# return stats



if __name__ == '__main__':
	folder = 'ParserOutput\\'
	genre_folders = [(f, join(folder, f)) for f in listdir(folder) if not isfile(join(folder, f))]
	genre_stats = {}
	for genre, genre_path in genre_folders:
		screenplay_files = [join(genre_path, f) for f in listdir(genre_path) if isfile(join(genre_path, f)) and f[-5:] == '.json']
		genre_stats[genre] = score_genre(screenplay_files)

		# sums = [sum(stat[i] for stat in genre_stat) for i in range(7)]
		# avgs = [s/len(genre_stat) for s in sums]
		# genre_stats[genre] = (genre_stat, num_fi9les)

	with open('genre_stats_new.txt', 'w') as genre_file:
		for genre, (stat_list, num_screenplays) in genre_stats.items():
			genre_file.write('|' + str(genre) + '\t|\t')
			genre_file.write(str(num_screenplays) + '\t|\t')
			for item in stat_list:
				genre_file.write(str(item) + '\t|\t')
			genre_file.write('\n')