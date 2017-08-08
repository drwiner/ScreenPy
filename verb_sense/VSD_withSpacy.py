from clockdeco import clock

from collections import defaultdict

from nltk.corpus import framenet as fn
from nltk.corpus import wordnet as wn


from verb_sense.semafor_api import semafor, semafor_util

import spacy
print('loading spaCy')
nlp = spacy.load('en')
print('finished loading')

# @clock
def conll_to_verb_map(conll):
	verb_map = defaultdict(list)
	sent = 0
	for line in conll.split('\n'):
		if line == '':
			sent += 1
			continue

		conll_line = line.split('\t')

		# look for verbs
		if len(conll_line[4]) > 1 and conll_line[4][:2] == 'VB':
			verb_map[sent].append(conll_line[2])

	return verb_map

# @clock
def get_verb_synsets(verb):
	return wn.synsets(verb, wn.VERB)


# @clock
def get_lemma_frames(lemm):

	print(lemm)
	fs = fn.frames_by_lemma(lemm)
	for f in fs:
		lunits = [lunit.split('.')[0] for lunit in f['lexUnit']]
		if lemm in lunits:
			print(True)
		else:
			print(False)

	return fn.frames_by_lemma(lemm)
	# return fn.lus(r'(?i)' + lemm).frame


# def get_lus(lemm):
# 	return fn.lus(r'(?i)' + lemm).fra


# @clock
# def verb_to_frames(verb):
	# syn_frame_dict = {}
	# return get_verb_synsets(verb)
	# for syn in wnsynsets:
	# 	lemmas = syn.lemma_names()
	# 	frames = []
	# 	for lem in lemmas:
	# 		# just collect frame ID
	#
	# 		fids = [f.ID for f in get_lemma_frames(lem)]
	# 		frames.extend(fids)
	# 	syn_frame_dict[syn] = frames
	# return syn_frame_dict


# narrows the set of synsets based on the frame and the lex units associated with that frame
def narrow_synsets(synsets, frame):
	lex_units = [unit[:-2] for unit in list(frame.lexUnit.keys())]
	narrowed_synsets = []
	for synset in synsets:
		lemms = synset.lemma_names()
		if len(set(lemms).intersection(set(lex_units))) > 0:
			narrowed_synsets.append(synset)
		# if frame.ID in frames:
		# 	synset_name = synset._name.split(".")[0]
		# 	if synset_name in lex_units:
		# 		synsets.append(synset)

	return narrowed_synsets


spacy_map = {
	'HYPH': ':',

}

# @clock
def spacy_sents_to_conll(raw_text):


	docs = nlp(raw_text)

	# for sent in sents:

	conll = ''

	for sent in docs.sents:
		s = nlp(sent.orth_)
		for token in s:
			# if token.orth_.strip() == '':
			# 	print('here')
			if token.head is token:
				head_idx = 0
				dep = 'root'
			else:
				head_idx = token.head.i+1
				dep = token.dep_
			if token.tag_ in spacy_map.keys():
				tag = spacy_map[token.tag_]
			else:
				tag = token.tag_
			conll += str(token.i+1) + '\t' + \
			         token.orth_ + '\t' + \
			         token.lemma_ + \
			         '\t_\t' + \
			         tag + \
			         '\t_\t' + \
			         str(head_idx) + '\t' + \
			         dep + \
			         '\t_\t_\n'
		if len(s) > 0:
			conll += '\n'

	return conll



# def compile_framenet_starters():
print('loading dub frames')
dub_frames = [full_frame.name for full_frame in fn.frames() if len(full_frame.name.split('_')) > 1]
FDD = defaultdict(list)
for dub_frame in dub_frames:
	FDD[dub_frame.split('_')[0]].append(dub_frame)
	# return fdd


# @clock
def get_frame_from_name(frame_name):
	try:
		frame = fn.frame_by_name(frame_name)
	except:
		if len(FDD[frame_name]) == 1:
			frame = fn.frame_by_name(FDD[frame_name][0])
		elif len(FDD[frame_name]) > 1:
			print('this frame has more den one extensions: {}'.format(frame_name))
			found = False
			for fname in FDD[frame_name]:
				if fname.split('_')[-1] != 'activity':
					frame = fn.frame_by_name(fname)
					found = True
					print('resolved')
					break
			if not found:
				print('just chose first item: {}'.format(FDD[frame_name][0]))
				frame = fn.frame_by_name(FDD[frame_name][0])
		else:
			print('did not have frame {}'.format(frame_name))
			return False
	return frame


# @clock
def compile_profile(fld, svd):
	action_senses = []

	# frame_dict is {frame text: targetFrame(target_frame=name, descendants=[framedText(text, name),...,]}
	for sent_num, frame_dict in enumerate(fld):

		# the verbs found in this sentence
		verbs = svd[sent_num]

		for verb in verbs:
			# ignore verbs for which no frame is identified
			if verb not in frame_dict.keys():
				continue

			# create dictionary of form {synset: frames} for each synset of verb
			synsets_list = get_verb_synsets(verb)

			# get the frame of the verb given output from Semafor
			frame_name = frame_dict[verb].target_frame
			frame = get_frame_from_name(frame_name)
			if not frame:
				continue

			# narrow the set of synsets to just those whose associated frames include the one we got as output
			synsets = narrow_synsets(synsets_list, frame)

			# given frame_dict[verb].descendants, collect the args and their frames
			arg_frames = [[ft.text, ft.frame] for ft in frame_dict[verb].descendants]

			# compile sense profile
			sp = [verb, [frame.name, frame.ID], [str(syns) for syns in synsets], arg_frames]

			action_senses.append(sp)
	return action_senses


# @clock
def sense_profile(raw_text):
	# no longer reducing with clausie
	# verb_to_synsets_dict = clausIE(raw_text)

	# get conllu (dependency parse)
	conllu = spacy_sents_to_conll(raw_text)

	# get frames for verbs and noun chunks
	sem_output = semafor(sock=None, text=conllu, reconnect=1)
	frame_list_dict = semafor_util(sem_output)

	# as set of verbs for each sentence
	sent_verb_dict = conll_to_verb_map(conllu)

	return compile_profile(frame_list_dict, sent_verb_dict)



def simple_test():
	text = "He lowers the torch to the floor of the landing. " \
	       "The landing is carpeted with human skeletons, one on top of another, all squashed flat as cardboard. " \
	       "Satipo gasps. " \
	       "Indy looks up at the ceiling of the landing, then steps onto skeletons, which make a cracking noise under his feet. "

	action_senses = sense_profile(text)
	with open('VSD_simple_test.txt', 'w') as vso:
		for verb, frame, synsets, args in action_senses:
			vso.write('verb:\t' + str(verb) + '\n')
			vso.write('frame:\t' + str(frame) + '\n')
			vso.write('args:\n\t' + '\n\t'.join(str(arg) for arg in args))
			vso.write('\nsynsets:\n')
			vso.write('\t' + '\n\t'.join(str(syn) for syn in synsets) + '\n')
			vso.write('\n\n')
	print(action_senses)


def full_json_test(json_name):
	import json
	with open(json_name) as play:
		text = json.load(play)

	for mseg in text:
		for seg in mseg:
			if seg['head_type'] != 'heading':
				continue

			text = ' '.join(seg['text'].split())
			if text == '':
				continue
			action_senses = sense_profile(text)

	print(action_senses)

if __name__ == '__main__':
	simple_test()
	full_json_test('../ParserOutput//Action//badboys.json')