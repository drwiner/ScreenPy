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


if __name__ == '__main__':

	RELOAD = 1
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
	# with open('segments.txt', 'w') as seg_file:
	# 	for seg in segments:
	# 		seg_file.write(json)


