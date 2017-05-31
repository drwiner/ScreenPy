from screenpy import *


class Heading:
	def __init__(self, name_, result_, start_, stop_, indent_=None, raw_text=None):
		self.name = name_
		self.result = result_
		self.start = start_
		self.stop = stop_
		self.indent = indent_
		self.raw_text = raw_text

	def __repr__(self):
		return str(self.result)


def find_stop(raw_txt):
	for r, s, t in spaces.scanString(raw_txt):
		indent = r['indent']
		if indent > 18 or r['indent'] == 1:
			continue
		return t-1
	return None

# compile HILT into single timeline
def screenpile_algorithm(headings, screenplay):

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
	for heading in headings[first_seg:]:
		if heading.name == 'heading':
			if seg is not None:
				segs.append(seg)
			seg = [heading]
		else:
			seg.append(heading)

	# find direction and dialogue for elements of scene segment
	final_segs = []
	directions = []
	dialogues = []
	is_dialogue = False
	for seg in segs:
		start = seg[0].stop
		for heading in seg[1:]:
			if heading.name == 'in_line':
				continue
			if heading.name == 'speaker':
				stop = heading.start-1
				if is_dialogue:
					txt = screenplay[start:stop]
					poss_stop = find_stop(txt)
					if poss_stop is None:
						t_seg = Heading('dialogue', seg.result, start, stop, raw_text=txt)
						dialogues.append(t_seg)
					else:
						t_seg = Heading('dialogue', seg.result, start, poss_stop-1, raw_text=screenplay[start:poss_stop-1])
						dialogues.append(t_seg)
						o_seg = Heading('direction', None, poss_stop+1, stop, raw_text=screenplay[poss_stop+1:stop])
						directions.append(o_seg)
				else:
					t_seg = Heading('direction', None, start, stop, raw_text=screenplay[start:stop])
					directions.append(t_seg)
		#insert dialogues and directions as elements of segment
		new_seg = seg + dialogues + directions
		new_seg.sort(lambda z: z.start)
		final_segs.append(seg_to_json(new_seg))
	return final_segs


def seg_to_json(seg):
	heading_dict = {'heading': seg[0].asDict()}
	heading_dict.update({item.name: item for item in seg[1:]})
	# common roof over head
	json_dict = {'seg': heading_dict}
	return json_dict


if __name__ == '__main__':

	heads = []
	screenplay = 'indianajonesandtheraidersofthelostark.txt'
	with open(screenplay, 'r') as fn:
		play = fn.read()
		for result, s, t in HEADINGS.scanString(play):
			indent = result[0]['indent']
			if indent < 13:
				heads.append(Heading('in_line', result[0], s, t, indent))
			elif indent > 50:
				heads.append(Heading('transition', result[0], s, t, indent))
			elif indent < 18:
				heads.append(Heading('heading', result[0], s, t, indent))
			else:
				heads.append(Heading('speaker', result[0], s, t, indent))

	heads.sort(key=lambda y: y.start, reverse=False)
	segments = screenpile_algorithm(heads, play)


