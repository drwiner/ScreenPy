from nltk.corpus import wordnet as wn
from nltk.corpus import framenet as fn


# given verb, return dict of form {synset: frames}
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


if __name__ == '__main__':
	verbs = ['load', 'fire', 'sail', 'eat', 'wish', 'look']
	for verb in verbs:
		synframes = verb_to_frames(verb)
		for syn, frames in synframes.items():
			print('syn: {}\n'.format(syn))
			
			print('frames:')
			for f in frames:
				print(f.name)
			print('\n\n')
		
		#print(verb_to_frames(verb))
		print('\n')
		
			