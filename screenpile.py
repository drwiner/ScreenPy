from screenpy import *
from clockdeco import clock
# from sentence_splitter import split_into_sentences
import json

class Heading:
	def __init__(self, name_, result_, start_, stop_, indent_=None, raw_text=None):
		self.name = name_
		self.result = result_
		self.start = start_
		self.stop = stop_
		self.indent = indent_
		self.raw_text = raw_text
		self.in_lines = []
		self.transition = None
		self.dialogue = []
		self.direction = []

	def __repr__(self):
		if self.result is None:
			return self.name
		return str(self.result)


class TextSeg:
	def __init__(self, name_, start_, stop_, raw_text):
		self.name = name_
		self.start = start_
		self.stop = stop_
		self.raw_text = raw_text

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
			seg[-1].in_lines.append(heading)
			# headings[i-1].append_inline(heading)

		elif heading.name == 'transition':
			if seg == []:
				raise ValueError('2 consecutive transitions at {}:{}'.format(heading.start, heading.stop))
			# seg[0].transition = heading
			seg.append(heading)
			# save ended seg and refresh seg
			segs.append(seg)
			seg = []

		else:
			seg.append(heading)
	return segs


# @clock
# def extract_text_segs(start, stop, speaker, dialogues, directions):
# 	# how to handle text since last heading
# 	txt = screenplay[start:stop]
# 	if speaker:
# 		poss_stop = find_stop(txt)
# 		if poss_stop is None:
# 			t_seg = Heading('dialogue', speaker, start, stop, raw_text=txt)
# 			dialogues.append(t_seg)
# 		else:
# 			t_seg = Heading('dialogue', speaker, start, start + poss_stop,
# 			                raw_text=screenplay[start:start + poss_stop])
# 			dialogues.append(t_seg)
# 			o_seg = Heading('direction', None, start + poss_stop, stop,
# 			                raw_text=screenplay[start + poss_stop: stop])
# 			directions.append(o_seg)
# 	else:
# 		stop = heading.start - 1
# 		t_seg = Heading('direction', None, start, stop, raw_text=screenplay[start:stop])
# 		directions.append(t_seg)

def extract_text_seg(txt, name, str_start, str_stop, speaker=None):
	text_seg = txt[str_start: str_stop]
	return Heading(name, speaker, str_start, str_stop, raw_text=text_seg)


@clock
def screenpile_algorithm(headings, screenplay):
	# separate into segs also compiles away non-headings, that's why its used here
	segs = separate_into_segs(headings)

	# flatten the headings into single list
	flat_heads = [head for seg in segs for head in seg]

	# pair segs off into start, stop tuples
	interseg_pairs = [(flat_heads[i-1], flat_heads[i]) for i in range(1, len(segs))]

	# interseg_pairs = [(segs[i-1][0].stop, segs[i][0].start) for i in range(1, len(segs))]
	last_heading = flat_heads[0]
	for head_s, head_t in interseg_pairs:

		if head_s.name == 'speaker':
			all_dialogue = True
			# determine if first line is actually dialogue
			first_spaces = list(spaces.scanString(screenplay[head_s.start:head_s.stop]))[-1]
			indent_ = first_spaces[0]['indent']
			if indent_ > 5 and indent_ < 20:
				# first line is direction
				drct = TextSeg('direction', head_s.stop, head_t.start, screenplay[head_s.stop: head_t.start])
				last_heading.direction.append(drct)
				# and the head_s isn't really a speaker
				head_s.name = 'title'
			else:
				# starts with dialogue, but may stop midway
				for result in spaces.scanString(screenplay[head_s.stop: head_t.start]):
					item = result[0]
					if item['indent'] > 5 and item['indent'] < 20:
						local_stop = head_s.stop + result[1]
						dlg = TextSeg('dialogue', head_s.stop, local_stop, screenplay[head_s.stop: local_stop])
						head_s.dialogue.append(dlg)

						local_start = head_s.stop + result[2]
						drct = TextSeg('direction', local_start, head_t.start, screenplay[local_start: head_t.start])
						last_heading.direction.append(drct)

						all_dialogue = False
						continue

				if all_dialogue:
					dlg = TextSeg('dialogue', head_s.stop, head_t.start, screenplay[head_s.stop: head_t.start])
					head_s.dialogue.append(dlg)
				# head_dlg = extract_text_seg(screenplay, 'dialogue', head_s.stop, head_t.start, speaker=head_s.result)
				# flat_heads.append(head_dlg)

		else:
			if head_s.name == 'heading':
				last_heading = head_s
			# assume direction
			drct = TextSeg('direction', head_s.stop, head_t.start, screenplay[head_s.stop: head_t.start])
			last_heading.direction.append(drct)
			# head_drct = extract_text_seg(screenplay, 'direction', head_s.stop, head_t.start)
			# flat_heads.append(head_drct)

	# flat_heads.sort(key=lambda z: z.start)
	# final_segs = separate_into_segs(flat_heads)
	return flat_heads


def seg_to_json(seg):

	heading_dict = seg[0].result.asDict()
	heading_dict.update({item.name: item for item in seg[1:]})
	# common roof over head
	json_dict = {'seg': heading_dict}
	json.dumps(json_dict)
	return json_dict


if __name__ == '__main__':

	heads = []
	screenplay = 'indianajonesandtheraidersofthelostark.txt'
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
	segments = screenpile_algorithm(heads, play)


