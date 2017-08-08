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

from collections import namedtuple

seg = namedtuple('seg', 'head_type head_text text')

def heading_wrapper(dict_item):
	seg_attr_dict = {
			'terior': None,
		    'location': None,
		    'shot type': None,
		    'subj': None,
		    'ToD': None}

	# T - INT./EXT.
	if 'terior' in dict_item.keys():
		seg_attr_dict['terior'] = dict_item['terior']

	# Loc - location
	if 'location' in dict_item.keys():
		if type(dict_item['location']) is pp.ParseResults:
			if 'modifier' in dict_item['location'].keys():
				seg_attr_dict['location'] = [list(dict_item['location']), dict_item['location']['modifier'][1]]
			else:
				seg_attr_dict['location'] = list(dict_item['location'])
		else:
			seg_attr_dict['location'] = list(dict_item['location'])

	# ST - shot type
	if 'shot type' in dict_item.keys():
		if type(dict_item['shot type']) is pp.ParseResults:
			if 'modifier' in dict_item['shot type'].keys():
				seg_attr_dict['shot type'] = [dict_item['shot type']['shot'], dict_item['shot type']['modifier'][1]]
			else:
				seg_attr_dict['shot type'] = dict_item['shot type']['shot']
		else:
			seg_attr_dict['shot type'] = [list(dict_item['shot type'].keys()), dict_item['shot type'][0]]

	# ToD - time of day
	has_tod = False
	if 'ToD' in dict_item.keys():
		seg_attr_dict['ToD'] = dict_item[-1]
		has_tod = True

	# Subj - subject
	if 'subj' in dict_item.keys():
		if has_tod:
			seg_attr_dict['subj'] = dict_item[-2]
		else:
			seg_attr_dict['subj'] = dict_item[-1]


	return seg_attr_dict


# filter tokens from punctuation
def clean_tokenization(token_list):
	pattern = re.compile('[{}]'.format(re.escape(string.punctuation)))
	filtered_tokens = filter(None, [pattern.sub('', token) for token in token_list])
	return filtered_tokens


# check if text is either caps and Fail if just a number
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


# segment tuples of the form (type of line, leading white space, text in the line)
# create "segs" with heading and subsequent text, or speaker and dialogue, or transition
def segmentize(tuple_lines):
	segments = []
	previous = None
	current_seg = None
	for (typ, _, this_text) in tuple_lines:
		if typ in {'heading', 'speaker/title', 'transition'}:

			# save ongoing seg if its non empty
			if current_seg is not None:
				segments.append(current_seg)

			# create new seg starting with this heading
			current_seg = seg(typ, this_text, [])
			previous = typ

		elif typ in {'direction', 'dialogue'}:
			# change to new segment when we go direction -> dialogue
			if typ is 'direction' and previous is 'dialogue':

				# save the ongoing seg if it's non empty
				if current_seg is not None:
					segments.append(current_seg)

				# an empty heading is created if direction follows dialogue without a heading
				current_seg = seg('heading', '', [])

			# don't add text until we've seen at least one heading
			if current_seg is None:
				continue
			current_seg.text.append(this_text)
			previous = typ

	# save last ongoing seg if document ends with text
	if current_seg is not None:
		segments.append(current_seg)

	return segments


# created nested list of segs where first seg is a "master shot"
def master_segmentize(segs):
	master_segs = []
	master_seg = []
	for (head_type, head_text, text_list) in segs:

		# flesh out text into single item
		fleshy_text = ' '.join(text_list)

		if head_type == 'heading':

			# use pyparsing to parse shot headings
			if head_text != '':
				try:
					parsed_heading = alpha.parseString(head_text)
					head_dict = heading_wrapper(parsed_heading)

				# an error is OK - just put in an empty heading
				except pp.ParseException:
					print('parse error: could not parse heading: {}'.format(head_text))
					head_dict = heading_wrapper(dict())
			else:
				# empty dict, returns keys with None values
				head_dict = heading_wrapper(dict())

			# if it IS a master shot
			if head_dict['terior'] is not None:
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


# iterate through lines of screenplay, label the type of line
def assemble_lines(text_lines):
	checks_for_sanity = 0
	range_mid = RANGE_MID
	established_dialogue_indent = None
	established_direction_indent = None
	indent_tuples = []
	start_collecting = False
	for i, tl in enumerate(text_lines):

		# get leading indent
		try:
			leading_indent = spaces.parseString(tl)['indent']
		except pp.ParseException:
			leading_indent = 0

		# prune leading indent
		relevant_text = tl[leading_indent:]
		if len(relevant_text)> 57:
			relevant_text = relevant_text[:57].strip()

		# check if all capitalized
		is_caps = is_upper(relevant_text)

		# don't start collecting until we've met one of two criteria:
		if not start_collecting:
			# 1
			if relevant_text in {'FADE IN:', 'FADE IN', 'OVER BLACK', 'FADE UP'}:
				start_collecting = True
			# 2
			if 'INT. ' in relevant_text or 'EXT. ' in relevant_text:
				start_collecting = True

		# if none of the 2 criteria have been met yet, get lost kid
		if not start_collecting:
			continue

		# left side o fpage
		if leading_indent in RANGE_LEFT:

			if is_caps:
				if len(relevant_text) > 0 and relevant_text[-1] in {'.', ';'}:
					if len(indent_tuples) > 0 and indent_tuples[-1][-1] not in {'.', ';'} and indent_tuples[-1][0] is 'direction':
						# then its probably the end of a sentence
						indent_tuples.append(('direction', leading_indent, relevant_text))
						continue

				# time to deal with turbulence
				rsplit = relevant_text.split()
				if len(rsplit) > 1:
					# we've got extra shit in the front, fogetta boutit
					if rsplit[1] in ['INT.', 'EXT.', 'INT./EXT.', 'EXT./INT.']:
						relevant_text = ' '.join(rsplit[1:])
					else:
						# if we're leading with a number, fogetta boutit!
						try:
							float(rsplit[0])
							relevant_text = ' '.join(rsplit[1:])
							relevant_text = relevant_text.strip()
						except ValueError:
							pass
				# if we've got dub hyphens, FOGETTA BOUTIT!
				relevant_text = relevant_text.replace(' -- ', ' - ')

				# If we're in parentheses, fogeeeet... it's just character direction...
				if len(relevant_text) > 0 and relevant_text[0] == '(' and relevant_text[-1] == ')':
					# this is character direction and belongs as dialogue
					indent_tuples.append(('dialogue', leading_indent, relevant_text))
					continue

				# it's a real live heading
				indent_tuples.append(('heading', leading_indent, relevant_text))
			else:
				# see if it's actually dialogue, 25 is ARBITRARY
				if established_direction_indent is None and i > 25:
					if leading_indent > 2:
						established_direction_indent = leading_indent
						if leading_indent < 11:
							# change the range to be towards the left
							range_mid = range(leading_indent+4, 42)
					else:
						# requires at least 6 consecutive checks (ARBITRARY)
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


# the annotation pipeline
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

	# screenplay = 'indianajonesandtheraidersofthelostark.txt'
	screenplay = 'imsdb_raw_nov_2015/Western/truegrit.txt'
	with open(screenplay, 'r') as fn:
		play = fn.read()

	play = play.replace('??!', '\t\t\t')
	play = play.replace('\t', '        ')
	text_lines = play.split('\n\n')
	line_tups = assemble_lines(text_lines)
	segs = segmentize(line_tups)
	masta = master_segmentize(segs)

	# with open('test.json', 'w') as fp:
	# 	json.dump(masta, fp, indent=4)

	# pickle.dump(masta, open('ij.pkl', 'wb'))

	# with open('indianajonesandtheraidersofthelostark.json', 'w') as fp:
	with open('truegrit.json', 'w') as fp:
		json.dump(masta, fp, indent=4)


