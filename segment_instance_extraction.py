# read in json screenplay, output text file of screenplay segment instances
import json


def ignore_if_none(item):
	if item is None:
		return ''
	else:
		return str(item) + ', '

def ignore_if_doubled(title, is_doubled):
	if is_doubled:
		return ''
	else:
		return str(title) + ', '

class Heading:
	def __init__(self, dict_item):
		self.title = dict_item['heading']
		self.title_doubled = False
		self.time_of_day = None
		self.location = None
		self.setting = None
		self.shot_type = None

		if 'terior' in dict_item.keys():
			self.setting = dict_item['terior']
		if 'location' in dict_item.keys():
			self.location = dict_item['location']
		if 'ToD' in dict_item.keys():
			self.time_of_day = dict_item['ToD']
		if 'shot type' in dict_item.keys():
			self.shot_type = dict_item['shot type']
		if self.title in [self.setting, self.location, self.time_of_day, self.shot_type]:
			self.title_doubled = True
	def __repr__(self):
		return '<' + ignore_if_none(self.setting) + ignore_if_none(self.location) \
		       +  ignore_if_doubled(self.title, self.title_doubled)  + ignore_if_none(self.shot_type)\
		       + ignore_if_none(self.time_of_day) + '>'


if __name__ == '__main__':
	with open('indianajonesandtheraidersofthelostark.json') as ij_file:
		data = json.load(ij_file)

	print("test")
	"""
	data is a list.
		each item in list is a pair
			first item in pair is a dict with heading and stage direction
			second item is list of <speaker, dialgoue> items
	"""

	segments = []
	for (heading_item, dialogue_item) in data:
		heading = Heading(heading_item['result'])
		direction = [drct['raw_text'] for drct in heading_item['direction']]
		speakers = [dlg['result']['heading'] for dlg in dialogue_item]
		segments.append((heading, direction, speakers))

	print('test')