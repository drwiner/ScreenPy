"""
David R. Winer

This is the verb-sense disambiguation code. Gets dependency parse for raw tet and sends to...
Semafor, the frame-semantic parser
The output is used to prune the set of WordNet synsets.

"""

from clockdeco import clock
from collections import defaultdict
from nltk.corpus import framenet as fn
from nltk.corpus import wordnet as wn
from verb_sense.semafor_api import semafor, semafor_util
from verb_sense.dep_conll_api import setup_parser as corenlp

# from verb_sense.clausie_api import clausie, clause_to_synsets, prepare_raw_text
# from nltk.stem import WordNetLemmatizer
# wordnet_lemmatizer = WordNetLemmatizer()
"""
	No longer using Clausie, based on results from development. A different synset-pruning strategy is employed.
"""
nlp = corenlp()


# unusued
# def clausIE(raw_text):
# 	sents = clausie(prepare_raw_text(raw_text))
# 	verb_synset_dict = [{clause.dict['V'].split('_')[0]: clause_to_synsets(clause) for clause in sent.clauses}
# 	                    for sent in sents]
#
# 	# for each verb in sent, clause_to_synsets
# 	return verb_synset_dict

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
def verb_to_frames(verb):
	syn_frame_dict = {}
	wnsynsets = wn.synsets(verb, wn.VERB)
	for syn in wnsynsets:
		lemmas = syn.lemma_names()
		frames = []
		for lem in lemmas:
			# just collect frame ID
			fids = [frame.ID for frame in fn.frames_by_lemma(r'(?i)' + lem)]
			frames.extend(fids)
		syn_frame_dict[syn] = frames
	return syn_frame_dict


# narrows the set of synsets based on the frame and the lex units associated with that frame
# @clock
def narrow_synsets(synset_frame_dict, frame):
	lex_units = [unit[:-2] for unit in list(frame.lexUnit.keys())]
	synsets = []
	for synset, frames in synset_frame_dict.items():
		if frame.ID in frames:
			synset_name = synset._name.split(".")[0]
			if synset_name in lex_units:
				synsets.append(synset)

	return synsets


@clock
def sense_profile(raw_text):
	# no longer reducing with clausie
	# verb_to_synsets_dict = clausIE(raw_text)

	# get conllu (dependency parse)
	var_dict = nlp(text=raw_text, property=['conllu', 'json'])
	conllu = var_dict['conllu']

	# get frames for verbs and noun chunks
	sem_output = semafor(sock=None, text=conllu, reconnect=1)
	frame_list_dict = semafor_util(sem_output)

	# as set of verbs for each sentence
	sent_verb_dict = conll_to_verb_map(conllu)

	action_senses = []

	# frame_dict is {frame text: targetFrame(target_frame=name, descendants=[framedText(text, name),...,]}
	for sent_num, frame_dict in enumerate(frame_list_dict):

		# the verbs found in this sentence
		verbs = sent_verb_dict[sent_num]

		for verb in verbs:
			# ignore verbs for which no frame is identified
			if verb not in frame_dict.keys():
				continue

			# create dictionary of form {synset: frames} for each synset of verb
			synset_frameid_dict = verb_to_frames(verb)

			# get the frame of the verb given output from Semafor
			try:
				frame = fn.frame_by_name(frame_dict[verb].target_frame)
			except:
				print('did not have this frame:')
				print(verb)
				print(frame_dict[verb].target_frame)
				continue

			# narrow the set of synsets to just those whose associated frames include the one we got as output
			synsets = narrow_synsets(synset_frameid_dict, frame)

			# given frame_dict[verb].descendants, collect the args and their frames
			arg_frames = [[ft.text, ft.frame] for ft in frame_dict[verb].descendants]

			# compile sense profile
			sp = [verb, [frame.name, frame.ID], [str(synset) for synset in synsets], arg_frames]

			action_senses.append(sp)

	return action_senses



if __name__ == '__main__':

	text = "He lowers the torch to the floor of the landing. " \
	       "The landing is carpeted with human skeletons, one on top of another, all squashed flat as cardboard. " \
	       "Satipo gasps. " \
	       "Indy looks up at the ceiling of the landing, then he steps onto skeletons, which make a cracking noise under his feet. "

	action_senses = sense_profile(text)
	import json
	with open('actionsense_test.json', 'w') as lightyears:
		json.dump(action_senses, lightyears, indent=4)
	with open('verb_sense_output_VSD.txt', 'w') as vso:
		for verb, frame, synsets, args in action_senses:
			vso.write('verb:\t' + str(verb) + '\n')
			vso.write('frame:\t' + str(frame) + '\n')
			vso.write('args:\n\t' + '\n\t'.join(str(arg) for arg in args))
			vso.write('\nsynsets:\n')
			vso.write('\t' + '\n\t'.join(str(syn) for syn in synsets) + '\n')
			vso.write('\n\n')
	print(action_senses)