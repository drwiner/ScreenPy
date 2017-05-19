from dateutil.parser import parse as dateparse
from screenpy_vars import *
import sys
DO_TEST = 1
DO_PRINT = 1

def Log(message):
	if DO_PRINT:
		print(message)

if 'sense2vec' not in sys.modules:
	import sense2vec
	print('loading sense2vec')
s2v_model = sense2vec.load()

def loadSpacy():
	import spacy
	print('loading SPACY english')
	nlp = spacy.load('en')
	return nlp


# def loadSense2Vec():
# 	if 'sense2vec' not in sys.modules:
# 		import sense2vec
# 		print('loading sense2vec')
# 	s2v_model = sense2vec.load()
# 	# freq, query_vector = s2v_model["natural_language_processing|NOUN"]
# 	# s2v_model.most_similar(query_vector, n=3)
# 	# s2v_model.data.similarity(s2v_model['thing|TAG'][1], s2v_model['thing|TAG'[1])
# 	return s2v_model


def sense2vec_sim(token1, token2):
	try:
		return s2v_model.data.similarity(s2v_model[token1][1], s2v_model[token2][1])
	except ValueError:
		return 0
	except KeyError:
		return 0


def is_date(s):
	try:
		dateparse(s)
		return True
	except ValueError:
		return False


def is_place(noun_phrase_list):
	# check if noun_phrase is a place
	return False



def check_hardcode(s):
	try:
		enumerated_time_word.parseString(s)
		return True
	except pp.ParseException:
		try:
			stop_words.parseString(s)
			x = min(sense2vec_sim(s + '|NOUN', 'day|NOUN'), sense2vec_sim(s + '|NOUN', 'time|NOUN'))
		except pp.ParseException:
			Log('stop word cannot be used for time expression')
			return 0
	return x


def is_time(s):
	threshold = .55
	s = s.lower()
	# assume s is string, can be multiple words
	Log('is_time({})'.format(s))
	if is_date(s):
		return True

	if type(s) is pp.ParseResults:
		if HYPHEN.parseString(s):
			return False
	elif ' - ' in s:
		return False


	# check if noun_phrase is a temporal expression
	split_tokens = s.split()
	if len(split_tokens) > 1:
		if s == 'continuous action' or s == 'day of the dead':
			return True
		s = split_tokens[-1]
		x = check_hardcode(s)
	else:
		try:
			if is_time(mid_x.parseString(s)[0]):
				return True
		except pp.ParseException:
			x = check_hardcode(s)
		except ValueError:
			x = check_hardcode(s)
		except KeyError:
			x = check_hardcode(s)
	Log(x)
	if x > threshold:
		return True
	return False

# def is_shot(s):
# 	try:
# 		for x in SHOT_TYPES.scanString(s):
# 			return True
# 		return False
# 	except pp.ParseException:
# 		return False

# Opt-H
OPT_H = pp.Optional(HYPHEN)

# MODIFIER
MODIFIER = pp.Combine(LP + pp.OneOrMore(pp.Word(ALL_CHARS)) + RP, joinString=' ', adjacent=False).setResultsName('modifier')
# Opt-M
OPT_M = pp.Optional(MODIFIER)


# ToD
ToD = pp.Combine(pp.Combine(pp.OneOrMore(pp.Word(ALPHANUMS)), joinString=' ', adjacent=False).addCondition(lambda token: is_time(token[0])).setResultsName('ToD') + OPT_M, joinString=', ', adjacent=False)
# Opt-ToD
OPT_ToD = pp.Optional(pp.Combine(pp.Literal('-').suppress() + WH + ToD, joinString=' ', adjacent=False))

if DO_TEST:
	assert(ToD.parseString('3 AM')[0] == '3 AM')
	assert(ToD.parseString('HELLO CHRISTMAS EVE')[0] == 'HELLO CHRISTMAS EVE')
	assert(ToD.parseString('HELLO CHRISTMAS EVE.')[0] == 'HELLO CHRISTMAS EVE')
	try:
		ToD.parseString('WIFE')
		print('bad')
	except pp.ParseException:
		print('good')
	try:
		ToD.parseString('PARK')
		print('bad')
	except pp.ParseException:
		print('good')
	try:
		ToD.parseString('ELEPHANT')
		print('bad')
	except pp.ParseException:
		print('good')
	try:
		ToD.parseString('THIS')
		print('bad')
	except pp.ParseException:
		print('good')
	try:
		ToD.parseString('WIFE AND EVERYONE')
		print('bad')
	except pp.ParseException:
		print('good')


# preposition for camera transitions
prep = pp.oneOf(['ON', 'WITH', 'TO', 'TOWARDS', 'FROM', 'IN', 'UNDER', 'OVER', 'ABOVE', 'AROUND', 'INTO'])
# Opt-P
OPT_P = pp.Combine(OPT_H | prep, joinString=' ', adjacent=False)


# ST
ST = pp.Combine(SHOT_TYPES + OPT_M, joinString=', ', adjacent=False)
if DO_TEST:
	try:
		ST.parseString('HELP ME')
		print('bad')
	except pp.ParseException:
		print('good')

	try:
		ST.parseString('HELP - ME DO THIS')
		print('bad')
	except pp.ParseException:
		print('good')

	try:
		ST.parseString('HELP - WIDE SHOT')
		print('bad')
	except pp.ParseException:
		print('good')
	assert(ST.parseString('HELP WIDE SHOT')[0] == 'HELP WIDE SHOT')
	assert(ST.parseString('WIDE SHOT - WITHOUT MOD')[0] == 'WIDE SHOT')
	assert(ST.parseString('A WIDE SHOT (WITH MOD)')[0] == 'A WIDE SHOT, ( WITH MOD )')
	assert(ST.parseString('THIS WIDE SHOT')[0] == 'THIS WIDE SHOT')


# Subj
# until_time = CAPS.copy().addCondition(lambda tokens: not is_time(' '.join(tokens)))
SUBJ = pp.Combine(pp.Combine(pp.OneOrMore(~HYPHEN + pp.Word(ALPHANUMS), stopOn=pp.FollowedBy(HYPHEN)), joinString=' ', adjacent=False).addCondition(lambda token: not is_time(' '.join(token))) + OPT_M, joinString=', ', adjacent=False).setResultsName('SUBJ')
# SUBJ = pp.OneOrMore(until_time, HYPHEN]))
# SUBJ.parseString('HELP ME - UNDERSTAND')
if DO_TEST:
	# should just get first until HYPHEN
	assert(SUBJ.parseString('HELP - ME UNDERSTAND')[0] == 'HELP')
	assert (SUBJ.parseString('HELP - ME UNDERSTAND')[0] == 'HELP')
	assert (SUBJ.parseString('HELP 3 AM')[0] == 'HELP 3 AM')
	assert(SUBJ.parseString('HELLO (MODIFIER) - 3 AM')[0][0] == 'HELLO, ( MODIFIER )')
	assert (SUBJ.parseString('HELLO ME UNDERSTAND (MODIFIER) - 3 AM')[0][0] == 'HELLO ME UNDERSTAND, ( MODIFIER )')
	assert (SUBJ.parseString('HELLO ME UNDERSTAND (MODIFIER) - ')[0][0] == 'HELLO ME UNDERSTAND, ( MODIFIER )')
	try:
		SUBJ.parseString('3 AM - HELP - ME UNDERSTAND - 3 AM')
		print('bad')
	except pp.ParseException:
		print('good')

# SUB
SUB = SUBJ + OPT_ToD + EOL
if DO_TEST:
	SUB.parseString('HELLO - 3 AM \n')
	SUB.parseString('HELLO - 3 AM\n')
	try:
		SUB.parseString('HELLO GOODBYE - 3 AM - HELLO - 3 AM \n')
		print('bad')
	except pp.ParseException:
		print('good')

# T
TERIOR = pp.oneOf(['INT.', 'EXT.', 'INT./EXT.', 'EXT./INT.'])

# Loc
ONE_LOC = pp.Combine(pp.Combine(pp.OneOrMore(~SHOT_TYPES + pp.Word(ALPHANUMS), stopOn=HYPHEN), joinString=' ', adjacent=False).addCondition(lambda token: not is_time(token[0])) + OPT_M, joinString=', ', adjacent=False)

if DO_TEST:
	assert(ONE_LOC.parseString('HELLO DO I HAUNT YOU - WHAT ABOUT THE LOCATION')[0] == 'HELLO DO I HAUNT YOU')
	assert (ONE_LOC.parseString('HELLO DO I HAUNT YOU - 3 AM - WHAT ABOUT THE LOCATION')[0] == 'HELLO DO I HAUNT YOU')
	assert (ONE_LOC.parseString('HELLO DO I HAUNT YOU - WHAT ABOUT THE LOCATION - 3 AM')[0] == 'HELLO DO I HAUNT YOU')
	pass

LOC = pp.OneOrMore(pp.Or([ONE_LOC, pp.Literal('-').suppress()]))
	#.addCondition(lambda token: not is_time(token[0]))

if DO_TEST:


# setting
SETTING = pp.Combine(TERIOR + LOC, joinString=' - ', adjacent=False).setResultsName('Setting')
# SETTING = pp.Combine(TERIOR + OPT_H + CAPS.copy().addCondition(lambda tokens: not SHOT_TYPES(tokens))
#                      + pp.Optional(LOC), joinString=" ", adjacent=False).setResultsName('Setting')

# Shot
SHOT = pp.Group(ST + OPT_P + SUB)
# Scene
SCENE = pp.Group(SETTING) + pp.Optional(SHOT)

# alpha
alpha = pp.MatchFirst([SCENE | SETTING + SHOT | pp.Group(SHOT_TYPES + OPT_M + OPT_ToD) | SHOT | SUB | ToD])


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

