from dateutil.parser import parse
from screenpy_vars import *


def loadSpacy():
	import spacy
	print('loading SPACY english')
	nlp = spacy.load('en')
	return nlp


def loadSense2Vec():
	import sense2vec
	print('loading sense2vec')
	s2v_model = sense2vec.load()
	# freq, query_vector = s2v_model["natural_language_processing|NOUN"]
	# s2v_model.most_similar(query_vector, n=3)
	# s2v_model.data.similarity(s2v_model['thing|TAG'][1], s2v_model['thing|TAG'[1])
	return s2v_model


def is_date(s):
	try:
		parse(s)
		return True
	except ValueError:
		return False


def is_place(noun_phrase_list):
	# check if noun_phrase is a place
	return False


def is_time(noun_phrase_list):
	if is_date:
		return True
	# check if noun_phrase is a temporal expression
	return False

def is_shot(s):

	if len(list(SHOT_TYPES.scanString(s))) == 0:
		return False

	return True

# Opt-H
OPT_H = pp.Optional(HYPHEN)

# MODIFIER
MODIFIER = pp.Combine(LP + pp.OneOrMore(pp.Word(ALL_CHARS)) + RP, joinString=' ', adjacent=False).setResultsName('modifier')
# Opt-M
OPT_M = pp.Optional(MODIFIER)


# ToD
ToD = pp.Combine(pp.OneOrMore(pp.Word(ALPHANUMS)).addCondition(lambda tokens: is_time(tokens)) + OPT_M, joinString=' ', adjacent=False).setResultsName('ToD')
# Opt-ToD
OPT_ToD = pp.Optional(pp.Combine(HYPHEN + ToD, joinString=' ', adjacent=False))


# preposition for camera transitions
prep = pp.oneOf(['ON', 'WITH', 'TO', 'TOWARDS', 'FROM', 'IN', 'UNDER', 'OVER', 'ABOVE', 'AROUND', 'INTO'])
# Opt-P
OPT_P = pp.Combine(OPT_H | prep, joinString=' ', adjacent=False)


# ST
ST = pp.Combine(SHOT_TYPES + OPT_M, joinString=' ', adjacent=False)
# Subj
SUBJ = pp.Combine(pp.OneOrMore(CAPS.copy().addCondition(lambda token: not is_date(token)) + OPT_M,
                     stopOn=EOL | pp.Empty.addCondition(lambda x: is_date(x))), joinString=' ', adjacent=False)
# SUB
SUB = pp.Combine(SUBJ + OPT_ToD, joinString=' ', adjacent=False)


# T
TERIOR = pp.oneOf(['INT.', 'EXT.', 'INT./EXT.'])
# Loc
LOC = pp.Combine(pp.OneOrMore(HYPHEN + CAPS.copy().addCondition(lambda token: not is_shot(token)) + OPT_M),
                 joinString=' ', adjacent=False)
# setting
SETTING = pp.Combine(TERIOR + OPT_H + CAPS.copy().addCondition(lambda tokens: not SHOT_TYPES(tokens))
                     + pp.Optional(LOC), joinString=" ", adjacent=False).setResultsName('Setting')

# Shot
SHOT = pp.Combine(SHOT_TYPES + OPT_P + SUB, joinString=' ', adjacent=False)
# Scene
SCENE = pp.Combine(SETTING + pp.Optional(SHOT), joinString=' ', adjacent=False)

# alpha
alpha = pp.Or(SCENE | SHOT | SUB | pp.Combine(SHOT_TYPES + OPT_M + OPT_ToD, joinString=' ', adjacent=False))


# A class object to host operations currently being constructed
# class Line:
# 	def __init__(self, str_line):
# 		if str_line == '\n':
# 			raise ValueError('Don\'t give me blank lines, doofus')
# 		self._indent = str_line.index(str_line.strip()[0])
# 		self._line = str_line.strip().split()
# 	def __len__(self):
# 		return len(self._line)
# 	def __getitem__(self, item):
# 		return self._line[item]
# 	def __str__(self):
# 		return ' '.join(item for item in self._line)
# 	def __repr__(self):
# 		return 'LINE{}'.format(self._line)


# experimental method for adding Conditions : just returns the exception as a string
def not_one_letter(toks):
	# print('here')
	if len(toks) == 1 and len(toks[0]) == 1:
		return pp.ParseException
	return toks


if __name__ == '__main__':
	screenplay = 'indianajonesandtheraidersofthelostark.txt'
	look_at_lines = []
	with open(screenplay) as fn:
		for line in fn:
			for result, s, e in CAPS.scanString(line):
				look_at_lines.append(result)
			# look_at_lines.append(alpha.parseString(line))
		# doc = split_into_sentences(fn.read())

	# with open('indianajonesandtheraidersofthelostark.txt', 'r') as ij:
	# 	ij.read()
	print("here")

