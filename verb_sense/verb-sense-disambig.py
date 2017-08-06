from functools import partial
from subprocess import Popen, PIPE
import socket

from clockdeco import clock
from nltk.corpus import framenet as fn
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
wordnet_lemmatizer = WordNetLemmatizer()

from clausie_api import clausie, clause_to_synsets, prepare_raw_text
from semafor_api import semafor, semafor_util
from dep_conll_api import setup_parser as corenlp
nlp = corenlp()


class senseProfile:
	"""
	sense profile for a particular verb
	"""
	def __init__(self, verb_lemma, synsets, arg_list, verb_frame, arg_frames, corefs=None):
		self.verb = verb_lemma
		self.synsets = synsets
		self.arg_list = arg_list
		self.verb_frame = verb_frame
		self.arg_frames = arg_frames
		self.corefs = corefs

	def __repr__(self):
		return self.verb + '\n'.join(str(synset) for synset in self.synsets) + '\n'.join(self.arg_list) + '\n' + str(self.verb_frame) + '\n'.join(str(arg) for arg in self.arg_frames)

@clock
def clausIE(raw_text):
	sents = clausie(prepare_raw_text(raw_text))

	triple_list = [sent.triples for sent in sents]

	verb_synset_dict = [{clause.dict['V'].split('_')[0]:
		                     (clause_to_synsets(clause), match_triples_to_clause(clause.dict, triple_list))
	                                for clause in sent.clauses}  for sent in sents]

	# for each verb in sent, clause_to_synsets
	return verb_synset_dict

@clock
def narrow_synsets(synsets, lex_units):
	"""

	:param synsets:
	:param lex_units:
	:return: only those synsets such that there exists a lex unit with matching name
			(typically, there are more lex units than synsets, so more comprehensive)
	"""
	narrowed_list = []
	for lex_unit in lex_units:
		# ignore the pos
		lu = lex_unit[:-2]
		for synset in synsets:
			synset_name = synset._name.split(".")[0]
			if lu == synset_name:
				# then this synset is OK
				narrowed_list.append(synset)
	return narrowed_list


# arg_list output of method: "match_triples_to_clause"
def arg_list_to_dict(list_with_arg_tups):
	return {tup[0] + str(i): list(tup)[1:] for i, tup in enumerate(list_with_arg_tups)}


def lemmatize(word):
	# if word is possessive pronoun, get lemma from corenlp
	if word in {'our', 'your', 'their', 'ours', 'yours', 'theirs', 'my', 'your', 'his', 'her', 'its', 'mine', 'hers'}:
		var_dict = nlp(text=text, property='json')
		return var_dict['sentences'][0]['tokens'][0]['lemma']
	else:
		return wordnet_lemmatizer.lemmatize(word)

def match_triples_to_clause(clause_dict, triples):
	# first, find the triple containing the verb
	verb = clause_dict['V'].split("_")[0]
	verb_lemma = wordnet_lemmatizer.lemmatize(verb)
	trips = [trip for trip in triples for arg in trip if verb_lemma in arg]

	cdict = {key: lemmatize(val.split('_')[0].lower()) for key, val in clause_dict.items()}

	arg_list = []
	for key, val in cdict.items():
		for trip in trips:
			for arg in trip:
				if arg[-1] == '\n':
					continue
				if val in ' '.join(arg[1:-1]).split():
					arg_list.append((key, val, arg[1:-1]))
					# arg_map[key] = (val, arg[1:-1])

	return arg_list

#
# def match_frames_to_args(frame_items_per_sent, arg_lists):
# 	# triples in triple_list are cndts for
# 	for target_frame_text, (target_frame_name, descendants) in frame_items_per_sent.items():
# 		if target_frame_text
#
# 	{arg: fi for arg in alist for fn, fi in frame_dict.items() if fn in arg or arg in fn}

@clock
def sense_profile(raw_text):
	verb_to_synsets = clausIE(text)

	# get conllu and corefs
	var_dict = nlp(text=text, property=['conllu', 'json'])
	conllu = var_dict['conllu']
	corefs = list(var_dict['json']['corefs'].values())

	sentnums_with_coref = [[item['sentNum'] for item in corefs] for corefs in corefs]

	# get frames for verbs and noun chunks
	sem_output = semafor(sock=None, text=conllu, reconnect=1)
	frame_list_dict = semafor_util(sem_output)

	sent_eval = zip(verb_to_synsets, frame_list_dict)
	action_senses = []
	# synset_dict is list of verb_dicts for each sentence
	# frame_dict is {frame text: targetFrame(target_frame=name, descendants=[framedText(text, name),...,]}
	for sent_num, (synset_dict, frame_dict) in enumerate(sent_eval):
		#synset_dict.values():  (clause_to_synsets(clause), match_triples_to_clause(clause.dict, triple_list))
		for verb, (synset_list, arg_list) in synset_dict.items():
			verb_lemma = lemmatize(verb)
			if verb_lemma not in frame_dict.keys():
				continue

			# verb part
			frame = fn.frame_by_name(frame_dict[verb_lemma].target_frame)
			synsets = narrow_synsets(synset_list, list(frame.lexUnit.keys()))

			# arg_frames = []

			arg_frames = [frame for _, arg, arg_phrase in arg_list for frame_text, frame in frame_dict.items()
			              if arg in frame_text or frame_text in arg_phrase]
			verb_frame = None
			for frame_text, frame in frame_dict.items():
				if frame_text in verb or verb in frame_text:
					verb_frame = frame
					break

			# add corefs
			#for coref_item in sentnums_with_coref:
			# for k, sent_nums in enumerate(sentnums_with_coref):
			# 	if sent_num not in sent_nums:
			# 		continue
			# 	corefs[k]
			# 	]
			#coref_zip = zip(corefs, sentnums_with_coref)
			#coref_items_ = [corefs for corefs, sentnums in coref_zip if sent_num in sentnums]
			               # k in range(corefs) if sent_num in u[k]] for u,t in enumerate(sentnums_with_coref)]

			sp = senseProfile(verb_lemma, synsets, arg_list, verb_frame, arg_frames)

			action_senses.append(sp)


	return action_senses


	# for each sentence,Indy looks up at the ceiling of the landing, then steps onto skeletons, which make a cracking noise under his feet.
	# print('play from here')


if __name__ == '__main__':

	text = "He lowers the torch to the floor of the landing. " \
	       "The landing is carpeted with human skeletons, one on top of another, all squashed flat as cardboard. " \
	       "Satipo gasps. " \
	       "Indy looks up at the ceiling of the landing, then steps onto skeletons, which make a cracking noise under his feet. "

	action_senses = sense_profile(text)
	with open('verb_sense_output.txt', 'w') as vso:
		for act_sense in action_senses:
			vso.write(str(act_sense))
			vso.write('\n\n')
	print(action_senses)