from screenpy import *
from clockdeco import clock
# from sentence_splitter import split_into_sentences
import json
import pickle
import re
import string
import nltk

# lines are at most 57 characters
RANGE_LEFT = range(18)
RANGE_MID = range(18, 42)
RANGE_RIGHT = range(42,58)


def heading_wrapper(dict_item):
	#[is_master, is_dlg, has_loc, has_subj, has_tod, has_st]
	# if 'modifier' in dict_item.keys():
	# 	print('has modifier:\n ', dict_item)
	seg_attr_dict = {
			'terior': None,
		    'location': None,
		    'shot type': None,
		    'subj': None,
		    'ToD': None}

	if 'terior' in dict_item.keys():
		seg_attr_dict['terior'] = dict_item['terior']
	if 'location' in dict_item.keys():
		if type(dict_item['location']) is pp.ParseResults:
			if 'modifier' in dict_item['location'].keys():
				seg_attr_dict['location'] = [list(dict_item['location']), dict_item['location']['modifier'][1]]
			else:
				seg_attr_dict['location'] = list(dict_item['location'])
		else:
			seg_attr_dict['location'] = list(dict_item['location'])
	if 'shot type' in dict_item.keys():
		if type(dict_item['shot type']) is pp.ParseResults:
			if 'modifier' in dict_item['shot type'].keys():
				seg_attr_dict['shot type'] = [dict_item['shot type']['shot'], dict_item['shot type']['modifier'][1]]
			else:
				seg_attr_dict['shot type'] = dict_item['shot type']['shot']
		else:
			seg_attr_dict['shot type'] = [list(dict_item['shot type'].keys()), dict_item['shot type'][0]]

	has_tod = False
	if 'ToD' in dict_item.keys():
		seg_attr_dict['ToD'] = dict_item[-1]
		# if 'modifier' in dict_item.keys():
		# 	seg_attr_dict['ToD'] = [dict_item['ToD'], dict_item['modifier'][1]]
		has_tod = True
		# else:


	if 'subj' in dict_item.keys():
		if has_tod:
			seg_attr_dict['subj'] = dict_item[-2]
		else:
			seg_attr_dict['subj'] = dict_item[-1]
		# if 'modifier' in dict_item.keys():
		# 	heading = dict_item{'heading'}
		# seg_attr_dict['subj'] = dict_item['subj']

	# elif sum(seg_attr_list[:2]) + sum(seg_attr_list[4:]) == 0:
	# 	# must be subject if it's nothing else
	# 	seg_attr_list[3] = True
	return seg_attr_dict


def seg_to_json(seg, i):
	heading_list = [seg[0].asDict(), [item.asDict() for item in seg[1:]]]
	return heading_list

def clean_tokenization(token_list):
	pattern = re.compile('[{}]'.format(re.escape(string.punctuation)))
	filtered_tokens = filter(None, [pattern.sub('', token) for token in token_list])
	return filtered_tokens

def is_upper(text):
	# tokenize
	tokens = nltk.word_tokenize(text)

	# prune special characters
	filtered_tokens = clean_tokenization(tokens)

	# return False when non caps found
	for token in filtered_tokens:
		if not token.isupper():
			if len(tokens) == 1:
				return False
			try:
				float(token)
			except ValueError:
				return False
	return True


from collections import namedtuple

seg = namedtuple('seg', 'head_type head_text text')


def segmentize(tuple_lines):
	segments = []
	previous = None
	current_seg = None
	for (typ, _, this_text) in tuple_lines:
		if typ in {'heading', 'speaker/title', 'transition'}:
			if current_seg is not None:
				segments.append(current_seg)
			current_seg = seg(typ, this_text, [])
			previous = typ
		elif typ in {'direction', 'dialogue'}:
			# change to new segment when we go direction -> dialogue
			if typ is 'direction' and previous is 'dialogue':
				if current_seg is not None:
					segments.append(current_seg)
				current_seg = seg('heading', '', [])
			if current_seg is None:
				continue
			current_seg.text.append(this_text)
			previous = typ

	if current_seg is not None:
		segments.append(current_seg)
	return segments


# def seg_to_dict(seg):



def master_segmentize(segs):
	master_segs = []
	master_seg = []
	for (head_type, head_text, text_list) in segs:
		# here we'll use pyparsing to extract
		fleshy_text = ' '.join(text_list)

		if head_type is 'heading':
			if head_text is not '':
				try:
					parsed_heading = alpha.parseString(head_text)
					head_dict = heading_wrapper(parsed_heading)
				except pp.ParseException:
					print('parse error: could not parse heading: {}'.format(head_text))
					head_dict = heading_wrapper(dict())
				except TypeError:

					print('type error: could not parse heading: {}'.format(head_text))
					head_dict = heading_wrapper(dict())
					# continue
					# raise ValueError('could not parse heading: {}'.format(head_text))

			else:
				# empty dict, returns keys with None values
				head_dict = heading_wrapper(dict())

			if head_dict['terior'] is not None:
				# dis is a master
				if len(master_seg) > 0:
					master_segs.append(master_seg)
				master_seg = [seg(head_type, head_dict, fleshy_text).__dict__]
			else:
				master_seg.append(seg(head_type, head_dict, fleshy_text).__dict__)

		elif head_type in {'speaker/title', 'transition'}:
			master_seg.append(seg(head_type, {head_type: head_text}, fleshy_text).__dict__)

	if len(master_seg) > 0:
		master_segs.append(master_seg)

	return master_segs


def assemble_lines(text_lines):
	checks_for_sanity = 0
	range_mid = RANGE_MID
	established_dialogue_indent = None
	established_direction_indent = None
	indent_tuples = []
	start_collecting = False
	for i, tl in enumerate(text_lines):

		try:
			leading_indent = spaces.parseString(tl)['indent']
		except:
			leading_indent = 0

		relevant_text = tl[leading_indent:]
		if len(relevant_text)> 57:
			relevant_text = relevant_text[:57].strip()
		is_caps = is_upper(relevant_text)
		# filtered_tokens = clean_tokenization(token_list)

		if not start_collecting:
			if relevant_text in {'FADE IN:', 'FADE IN', 'OVER BLACK', 'FADE UP'}:
				start_collecting = True

			if 'INT. ' in relevant_text or 'EXT. ' in relevant_text:
				start_collecting = True

		if not start_collecting:
			continue

		if leading_indent in RANGE_LEFT:
			# figure out if it's all caps + digits
			if is_caps:


				if len(relevant_text) > 0 and relevant_text[-1] in {'.', ';'}:
					if len(indent_tuples) > 0 and indent_tuples[-1][-1] not in {'.', ';'} and indent_tuples[-1][0] is 'direction':
						# then its probably the end of a sentence
						indent_tuples.append(('direction', leading_indent, relevant_text))
						continue

				rsplit = relevant_text.split()
				if len(rsplit) > 1:
					if rsplit[1] in ['INT.', 'EXT.', 'INT./EXT.', 'EXT./INT.']:
						relevant_text = ' '.join(rsplit[1:])
					else:
						try:
							float(rsplit[0])
							relevant_text = ' '.join(rsplit[1:])
							relevant_text = relevant_text.strip()
						except ValueError:
							pass
				relevant_text = relevant_text.replace(' -- ', ' - ')

				if len(relevant_text) > 0 and relevant_text[0] is '(' and relevant_text[-1] is ')':
					# this is character direction and belongs as dialogue
					indent_tuples.append(('dialogue', leading_indent, relevant_text))
					continue

				indent_tuples.append(('heading', leading_indent, relevant_text))
			else:
				# see if it's actually dialogue
				if established_direction_indent is None and i > 25:
					if leading_indent > 2:
						established_direction_indent = leading_indent
						if leading_indent < 11:
							# change the range to be towards the left
							range_mid = range(leading_indent+4, 42)
					else:
						# requires at least 6 consecutive checks
						if checks_for_sanity == 6:
							established_direction_indent = leading_indent
						checks_for_sanity += 1

				indent_tuples.append(('direction', leading_indent, relevant_text))

		elif leading_indent in range_mid:
			if is_caps:
				if established_dialogue_indent is not None:
					if leading_indent in range(established_dialogue_indent-5, established_dialogue_indent+5):
						# then it's just shouting...
						indent_tuples.append(('dialogue', leading_indent, relevant_text))
						continue
				indent_tuples.append(('speaker/title', leading_indent, relevant_text))
			else:
				indent_tuples.append(('dialogue', leading_indent, relevant_text))
				if established_dialogue_indent is None and i > 50:
					established_dialogue_indent = leading_indent
		else:
			if is_caps:
				indent_tuples.append(('transition', leading_indent, relevant_text))
			else:
				continue
				# raise ValueError('what the fuck is this: {}\n on line: {}'.format(relevant_text, str(i)))
	return indent_tuples


def annotate(screenplay):
	play = screenplay.replace('\t', '        ')
	text_lines = play.split('\n\n')
	line_tups = assemble_lines(text_lines)
	segs = segmentize(line_tups)
	masta = master_segmentize(segs)
	return masta

if __name__ == '__main__':

	# with open('imsdb_raw_nov_2015//Sci-Fi/abyssthe.txt') as fn:
	# 	play = fn.read()

	screenplay = 'indianajonesandtheraidersofthelostark.txt'
	with open(screenplay, 'r') as fn:
		play = fn.read()

	play = play.replace('??!', '\t\t\t')
	play = play.replace('\t', '        ')
	text_lines = play.split('\n\n')
	line_tups = assemble_lines(text_lines)
	segs = segmentize(line_tups)
	masta = master_segmentize(segs)

	with open('test.json', 'w') as fp:
		json.dump(masta, fp, indent=4)

	# pickle.dump(masta, open('ij.pkl', 'wb'))

	with open('indianajonesandtheraidersofthelostark.json', 'w') as fp:
		json.dump(masta, fp, indent=4)


