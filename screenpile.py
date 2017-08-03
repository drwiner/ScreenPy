from screenpy import *
from clockdeco import clock
# from sentence_splitter import split_into_sentences
import json
import pickle

class Heading:
	def __init__(self, name_, result_, start_, stop_, indent_=None):
		self.name = name_
		self.result = result_
		self.start = start_
		self.stop = stop_
		self.indent = indent_
		# self.raw_text = raw_text
		self.in_lines = []
		self.transition = None
		self.dialogue = []
		self.direction = []

	def asDict(self):
		if self.result is not None:
			self.result = self.result.asDict()

		if self.transition is not None:
			self.transition = self.transition.asDict()

		for i, inline in enumerate(list(self.in_lines)):
			self.in_lines[i] = inline.asDict()

		for i, dlg in enumerate(list(self.dialogue)):
			self.dialogue[i] = dlg.asDict()

		for i, drct in enumerate(list(self.direction)):
			self.direction[i] = drct.asDict()

		return self.__dict__

	def __repr__(self):
		if self.result is None:
			return self.name
		return str(self.result)


class TextSeg:
	def __init__(self, name_, start_, stop_, raw_text):
		self.name = name_
		self.start = start_
		self.stop = stop_
		self.raw_text = ' '.join([line.strip() for line in raw_text.split('\n\n')])


	def asDict(self):
		return self.__dict__

	def __repr__(self):
		return '{}[{}:{}]'.format(self.name, str(self.start), str(self.stop))


def find_stop(raw_txt):
	for r, s, t in spaces.scanString(raw_txt):
		indent_ = r['indent']
		if indent_ > 18 or indent_ == 1:
			continue
		return t
	return None


def separate_into_segs(headings):
	# just get the first real heading
	first_seg = 0
	for i, heading in enumerate(headings):
		if heading.name == 'heading':
			first_seg = i
			break

	# split headings into scene segments
	segs = []
	seg = []
	# seg = [headings[first_seg]]
	for i, heading in enumerate(headings[first_seg:]):

		if heading.name == 'heading':
			# if seg has items, save them before reloading
			if seg != []:
				segs.append(seg)
			seg = [heading]

		elif heading.name == 'in_line':
			try:
				seg[-1].in_lines.append(heading)
			except:
				# this means there's a problem, ignore for now
				continue
				# print('here too')
			# headings[i-1].append_inline(heading)

		elif heading.name == 'transition':
			if seg == []:
				# 2 consecutive transitions
				continue
			# 	raise ValueError('2 consecutive transitions at {}:{}'.format(heading.start, heading.stop))
			# seg[0].transition = heading
			seg.append(heading)
			# save ended seg and refresh seg
			segs.append(seg)
			seg = []

		else:
			seg.append(heading)
	return segs


@clock
def screenpile_algorithm(headings, screenplay):
	# separate into segs also compiles away non-headings, that's why its used here
	segs = separate_into_segs(headings)

	# flatten the headings into single list
	flat_heads = [head for seg in segs for head in seg]

	# pair segs off into start, stop tuples
	interseg_pairs = [(flat_heads[i-1], flat_heads[i]) for i in range(1, len(flat_heads))]

	# interseg_pairs = [(segs[i-1][0].stop, segs[i][0].start) for i in range(1, len(segs))]
	try:
		last_heading = flat_heads[0]
	except:
		print('possibly no spaces on screenplay')
		return None
	for i, (head_s, head_t) in enumerate(interseg_pairs):

		if head_s.name == 'speaker':
			all_dialogue = True
			# determine if first line is actually dialogue
			try:
				first_spaces = list(min_2_spaces.scanString(screenplay[head_s.start:head_s.stop]))[-1]
			except:
				print('here')
			indent_ = first_spaces[0]['indent']
			if indent_ > 5 and indent_ < 20:
				# first line is direction
				drct = TextSeg('direction', head_s.stop, head_t.start, screenplay[head_s.stop: head_t.start].strip())
				last_heading.direction.append(drct)
				# and the head_s isn't really a speaker
				head_s.name = 'title'
			else:
				# first evaluate first line cuz it sometimes doesn't show up
				# starts with dialogue, but may stop midway
				for result in min_2_spaces.scanString(indent_*' ' + screenplay[head_s.stop: head_t.start]):
					item = result[0]
					if item['indent'] > 5 and item['indent'] < 20:
						local_stop = head_s.stop + result[1] - indent_
						dlg = TextSeg('dialogue', head_s.stop, local_stop, screenplay[head_s.stop: local_stop].strip())
						head_s.dialogue.append(dlg)

						local_start = head_s.stop + result[2] - indent_
						drct = TextSeg('direction', local_start, head_t.start, screenplay[local_start: head_t.start].strip())
						last_heading.direction.append(drct)

						all_dialogue = False
						break

				if all_dialogue:
					dlg = TextSeg('dialogue', head_s.stop, head_t.start, screenplay[head_s.stop: head_t.start].strip())
					head_s.dialogue.append(dlg)
				# head_dlg = extract_text_seg(screenplay, 'dialogue', head_s.stop, head_t.start, speaker=head_s.result)
				# flat_heads.append(head_dlg)

		else:
			if head_s.name == 'heading':
				last_heading = head_s
			# assume direction
			drct = TextSeg('direction', head_s.stop, head_t.start, screenplay[head_s.stop: head_t.start].strip())
			last_heading.direction.append(drct)
			# head_drct = extract_text_seg(screenplay, 'direction', head_s.stop, head_t.start)
			# flat_heads.append(head_drct)

	# flat_heads.sort(key=lambda z: z.start)
	# final_segs = separate_into_segs(flat_heads)
	return flat_heads


def seg_to_json(seg, i):
	heading_list = [seg[0].asDict(), [item.asDict() for item in seg[1:]]]
	# heading_dict.update({'sub_heading': [item.asDict() for item in seg[1:]]})
	# heading_dict.update(seg[0].\)
	# heading_dict.update({'seg ' + str(i): {[item.asDict() for item in seg[1:]], })
	# common roof over head
	# json_dict = heading_dict
	return heading_list
	# json.dumps(json_dict)
	# return None


# def tokenize_text(text):
	# word_tokens = [nltk.word_tokenize(text)]

import re
import string
import nltk

# lines are at most 57 characters
RANGE_LEFT = range(18)
RANGE_MID = range(18, 50)
RANGE_RIGHT = range(50,58)

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
			current_seg.text.append(this_text)
			previous = typ

	segments.append(current_seg)
	return segments


def master_segmentize(segs):
	master_segs = []
	master_seg = []
	for (head_type, head_text, text_list) in segs:
		# here we'll use pyparsing to extract
		fleshy_text = '\n'.join(text_list)

		if head_type is 'heading':
			if head_text is not '':
				try:
					parsed_heading = alpha.parseString(head_text)
				except ValueError('could not parse heading: {}'.format(head_text)):
					raise
			else:
				parsed_heading = {} # empty dict

			if 'terior' in parsed_heading.keys():
				# dis is a master
				if len(master_seg) > 0:
					master_segs.append(master_seg)
				master_seg = [seg(head_type, parsed_heading, fleshy_text)]
			else:
				master_seg.append(seg(head_type, parsed_heading, fleshy_text))

		elif head_type in {'speaker/title', 'transition'}:
			master_seg.append(seg(head_type, head_text, fleshy_text))

	if len(master_seg) > 0:
		master_segs.append(master_seg)

	return master_segs



def assemble_lines(text):
	established_dialogue_indent = None
	# established_speaker_indent = None
	indent_tuples = []
	start_collecting = False
	for i, tl in enumerate(text_lines):
		try:
			leading_indent = spaces.parseString(tl)['indent']
		except:
			leading_indent = 0

		relevant_text = tl[leading_indent:]
		is_caps = is_upper(relevant_text)
		# filtered_tokens = clean_tokenization(token_list)

		if not start_collecting:
			if relevant_text in {'FADE IN:', 'FADE IN'}:
				start_collecting = True

			if 'INT. ' in relevant_text or 'EXT. ' in relevant_text:
				start_collecting = True

		if not start_collecting:
			continue

		if leading_indent in RANGE_LEFT:
			# figure out if it's all caps + digits
			if is_caps:
				indent_tuples.append(('heading', leading_indent, relevant_text))
			else:
				indent_tuples.append(('direction', leading_indent, relevant_text))

		elif leading_indent in RANGE_MID:
			if is_caps:
				if established_dialogue_indent is not None:
					if leading_indent in range(established_dialogue_indent-5, established_dialogue_indent+5):
						# then it's just shouting...
						indent_tuples.append(('dialogue', leading_indent, relevant_text))
						continue
				indent_tuples.append(('speaker/title', leading_indent, relevant_text))
			else:
				indent_tuples.append(('dialogue', leading_indent, relevant_text))
				if established_dialogue_indent is None and i > 100:
					established_dialogue_indent = leading_indent
		else:
			if is_caps:
				indent_tuples.append(('transition', leading_indent, relevant_text))
			else:
				raise ValueError('what the fuck is this: {}\n on line: {}'.format(relevant_text, str(i)))
	return indent_tuples

if __name__ == '__main__':



	# from nltk.stem import WordNetLemmatizer
	# wordnet_lemmatizer = WordNetLemmatizer()

	RELOAD = 0
	DO = 0
	screenplay = 'indianajonesandtheraidersofthelostark.txt'
	with open(screenplay, 'r') as fn:
		play = fn.read()

	text_lines = play.split('\n\n')
	line_tups = assemble_lines(text_lines)
	segs = segmentize(line_tups)
	masta = master_segmentize(segs)
	print('here')


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

	if DO:
		segments = screenpile_algorithm(heads, play)
		hsegs = separate_into_segs(segments)
		print('ok')
		with open('indianajonesandtheraidersofthelostark.json', 'w') as fp:
			json.dump([seg_to_json(seg, i) for i, seg in enumerate(hsegs)], fp, indent=4)


