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

# Opt-H
OPT_H = pp.Optional(HYPHEN)

# MODIFIER
MODIFIER = pp.Group(LP + pp.Combine(pp.OneOrMore(pp.Word(ALL_CHARS)), joinString=' ', adjacent=False) + RP).setResultsName('modifier')
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
	assert(ToD.parseString('CHRISTMAS EVE (1942)')[0] == 'CHRISTMAS EVE, (1942)')
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
# prep = pp.oneOf(['ON', 'WITH', 'TO', 'TOWARDS', 'FROM', 'IN', 'UNDER', 'OVER', 'ABOVE', 'AROUND', 'INTO'])
# Opt-P
OPT_P = pp.Combine(OPT_H | prep, joinString=' ', adjacent=False)


# ST
ST = pp.Combine(SHOT_TYPES + OPT_M, joinString=', ', adjacent=False)
     # + (EOL | WH | ~pp.Word(lower)).suppress()
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
	# assert(ST.parseString("CLOSEUP (WITH MOD)")
	assert(ST.parseString('HELP WIDE SHOT')[0] == 'HELP WIDE SHOT')
	assert(ST.parseString('WIDE SHOT - WITHOUT MOD')[0] == 'WIDE SHOT')
	assert(ST.parseString('A WIDE SHOT (WITH MOD)')[0] == 'A WIDE SHOT, (WITH MOD)')
	assert(ST.parseString('THIS WIDE SHOT')[0] == 'THIS WIDE SHOT')
	ST.parseString('WIDE SHOT WITH EXTRA WORDS')
	assert(ST.parseString('ANY WIDE SHOT (THE_MOD) \n\nAn CLOSE UP - DUSK\n\nAn CLOSE UP')[0] == 'ANY WIDE SHOT, (THE_MOD)')

# Subj
# until_time = CAPS.copy().addCondition(lambda tokens: not is_time(' '.join(tokens)))
X = pp.Combine(pp.OneOrMore(~HYPHEN + pp.Word(ALPHANUMS) + (WH | ~pp.Word(lower)), stopOn=pp.FollowedBy(HYPHEN)), joinString=' ', adjacent=False)
SUBJ = pp.Combine(X + OPT_M, joinString=', ', adjacent=False).addCondition(lambda token: not is_time(' '.join(token)))
# SUBJ = pp.OneOrMore(until_time, HYPHEN]))
# SUBJ.parseString('HELP ME - UNDERSTAND')
if DO_TEST:
	# should just get first until HYPHEN
	assert(SUBJ.parseString('HELP - ME UNDERSTAND')[0] == 'HELP')
	assert (SUBJ.parseString('HELP - ME UNDERSTAND')[0] == 'HELP')
	assert (SUBJ.parseString('HELP 3 AM')[0] == 'HELP 3 AM')
	assert(SUBJ.parseString('HELLO (MODIFIER) - 3 AM')[0] == 'HELLO, (MODIFIER)')
	assert (SUBJ.parseString('HELLO ME UNDERSTAND (MODIFIER) - 3 AM')[0] == 'HELLO ME UNDERSTAND, (MODIFIER)')
	assert (SUBJ.parseString('HELLO ME UNDERSTAND (MODIFIER) - ')[0] == 'HELLO ME UNDERSTAND, (MODIFIER)')
	try:
		SUBJ.parseString('3 AM - HELP - ME UNDERSTAND - 3 AM')
		print('bad')
	except pp.ParseException:
		print('good')

	try:
		SUBJ.parseString('DUSK An amphibian plane sits in the water beneath a green cliff.')
		print('bad')
	except pp.ParseException:
		print('good')

	assert(SUBJ.parseString('ANYWORD An amphibian plane sits in the water beneath a green cliff.')[0] == 'ANYWORD')
	SUBJ.parseString('ANY WIDE SHOT (THE_MOD) \n\nAn CLOSE UP - DUSK\n\nAn CLOSE UP')

	assert(SUBJ.parseString('ANY WIDE SHOT (THE_MOD) \n\nAn CLOSE UP - DUSK\n\nAn CLOSE UP')[0] == 'ANY WIDE SHOT, (THE_MOD)')

# SUB
SUB = (SUBJ + OPT_ToD + EOL) | ToD
if DO_TEST:
	SUB.parseString('HELLO - 3 AM \n')
	SUB.parseString('HELLO (MOD) - 3 AM\n 5 AM')
	try:
		SUB.parseString('HELLO GOODBYE - 3 AM - HELLO - 3 AM \n')
		print('bad')
	except pp.ParseException:
		print('good')

# T
TERIOR = pp.oneOf(['INT.', 'EXT.', 'INT./EXT.', 'EXT./INT.'])

# Loc
Y = pp.Combine(pp.OneOrMore(~SHOT_TYPES + pp.Word(ALPHANUMS), stopOn=HYPHEN), joinString=' ', adjacent=False).addCondition(lambda token: not is_time(token[0]))
ONE_LOC = pp.Combine(Y + OPT_M, joinString=', ', adjacent=False)

if DO_TEST:
	assert(ONE_LOC.parseString('HELLO DO I HAUNT YOU - WHAT ABOUT THE LOCATION')[0] == 'HELLO DO I HAUNT YOU')
	assert (ONE_LOC.parseString('HELLO DO I HAUNT YOU - 3 AM - WHAT ABOUT THE LOCATION')[0] == 'HELLO DO I HAUNT YOU')
	assert (ONE_LOC.parseString('HELLO DO I HAUNT YOU - WHAT ABOUT THE LOCATION - 3 AM')[0] == 'HELLO DO I HAUNT YOU')

	assert (ONE_LOC.parseString('HELLO DO I HAUNT YOU (EAST HALLWAY) - WHAT ABOUT THE LOCATION (WEST SIDE OF TOWN)')[0] == 'HELLO DO I HAUNT YOU, (EAST HALLWAY')
LOC = pp.OneOrMore(pp.Or([ONE_LOC, pp.Literal('-').suppress() + WH]))
	#.addCondition(lambda token: not is_time(token[0]))

if DO_TEST:
	assert (LOC.parseString('HELLO DO I HAUNT YOU - WHAT ABOUT THE LOCATION')[0] == 'HELLO DO I HAUNT YOU')
	assert (LOC.parseString('HELLO DO I HAUNT YOU - WHAT ABOUT THE LOCATION')[1] == 'WHAT ABOUT THE LOCATION')
	assert (LOC.parseString('HELLO DO I HAUNT YOU - 3 AM - WHAT ABOUT THE LOCATION')[0] == 'HELLO DO I HAUNT YOU')
	try:
		LOC.parseString('HELLO DO I HAUNT YOU - 3 AM - WHAT ABOUT THE LOCATION')[1]
		print('bad')
	except IndexError:
		print('good')

	assert (LOC.parseString('HELLO DO I HAUNT YOU - WHAT ABOUT THE LOCATION - 3 AM')[0] == 'HELLO DO I HAUNT YOU')
	assert (LOC.parseString('HELLO DO I HAUNT YOU - SPECIFIC LOCATION - WHAT ABOUT THE LOCATION 3 AM')[1] == 'SPECIFIC LOCATION')
	assert(LOC.parseString('HELLO DO I HAUNT YOU - SPECIFIC LOCATION - WHAT ABOUT THE LOCATION 3 AM')[2] == 'WHAT ABOUT THE LOCATION 3 AM')

	assert (LOC.parseString('HELLO DO I HAUNT YOU (EAST HALLWAY) - WHAT ABOUT THE LOCATION (WEST SIDE OF TOWN)')[1] == 'WHAT ABOUT THE LOCATION, (WEST SIDE OF TOWN)')

# setting
SETTING = TERIOR + pp.Group(LOC)
# SETTING = pp.Combine(TERIOR + OPT_H + CAPS.copy().addCondition(lambda tokens: not SHOT_TYPES(tokens))
#                      + pp.Optional(LOC), joinString=" ", adjacent=False).setResultsName('Setting')

if DO_TEST:
	assert(SETTING.parseString('INT. WHERE SHOULD I GO NOTTIME')[1][0] == 'WHERE SHOULD I GO NOTTIME')
	try:
		SETTING.parseString('INT. WHERE SHOULD I GO NIGHT')
		print('bad')
	except pp.ParseException:
		print('good')
	assert(SETTING.parseString('EXT./INT. WHERE SHOULD - I GO')[1][1] == 'I GO')
	try:
		SETTING.parseString('EXT./INT. WHERE SHOULD - I GO - NIGHT')[1][2]
		print('bad')
	except IndexError:
		print('good')
	SETTING.parseString('EXT. FIRST LOCATION (AND ITS MOD) - SECOND LOCATION (AND ITS ALSO MOD) - 1 AM')

# Shot
SHOT = ST + pp.Optional((prep | (pp.Literal('-').suppress() + WH)).suppress() + SUB)

if DO_TEST:
	assert(SHOT.parseString('WIDE SHOT (MOD TEST) - CNN CORRESPONDENT')[1] == 'CNN CORRESPONDENT')
	assert(SHOT.parseString('TRACKING SHOT ON CNN CORRESPONDENT - 4 AM \n')[2] == '4 AM')
	assert(SHOT.parseString('CLOSE ANGLE WITH CNN')[0] == 'CLOSE ANGLE')
	assert(SHOT.parseString('ZOOM TO CNN')[0] == 'ZOOM')
	assert(SHOT.parseString('WIDE SHOT')[0] == 'WIDE SHOT')
	assert(SHOT.parseString('WIDE SHOT (SNEAKY)')[0] == 'WIDE SHOT, (SNEAKY)')

# Scene
SCENE = SETTING + (OPT_M + SHOT | ToD | pp.Empty())

if DO_TEST:
	SCENE.parseString('EXT. THIS IS A LOCATION - MORE SPECIFIC LOCATION')
	assert (SCENE.parseString('EXT. THIS IS A LOCATION - MORE SPECIFIC LOCATION - 4 AM')[2] == '4 AM')
	assert (SCENE.parseString('EXT. THIS IS A LOCATION - MORE SPECIFIC LOCATION - 4 AM - WIDE SHOT')[2] == '4 AM')
	assert(len(SCENE.parseString('EXT. THIS IS A LOCATION - MORE SPECIFIC LOCATION - 4 AM - WIDE SHOT')) == 3)
	assert (len(SCENE.parseString('EXT. THIS IS A LOCATION - MORE SPECIFIC LOCATION - WIDE SHOT - SUBJECT - 4 AM')) == 5)
	assert (len(SCENE.parseString('EXT. THIS ONE - MORE SPECIFIC LOCATION - WIDE SHOT - SUBJECT (ALMOST) - 4 AM (EVERYWHERE)')) == 5)
	assert (len(SCENE.parseString('EXT. THIS ONE (WORK HERE) - MORE LOCATION - WIDE SHOT - SUBJECT (ALMOST) - 4 AM (EVERYWHERE)')) == 5)
	assert (len(SCENE.parseString('EXT. THIS ONE - MORE LOCATION (WORK HERE) - WIDE SHOT - SUBJECT (ALMOST) - 4 AM (EVERYWHERE)')) == 5)
	assert (len(SCENE.parseString('EXT. THIS ONE (A MOD HERE) - MORE SPECIFIC LOCATION (A MOD THERE) - WIDE SHOT (THERE\'S A MOD) - SUBJECT (ALMOST) - 4 AM (EVERYWHERE)')) == 5)
	try:
		SCENE.parseString('EXT. WIDE SHOT')
		print('bad')
	except pp.ParseException:
		print('good')
	header = 'EXT. THE JUNGLE - INDY\'S RUN - VARIOUS SHOTS - DAY'
	assert(len(SCENE.parseString(header)) == 4)

# alpha
alpha = pp.MatchFirst([SCENE | SHOT | SUB | ToD])

if DO_TEST:
	assert(len(alpha.parseString('CNN - 4 AM')) == 2)
	assert(len(alpha.parseString('CNN')) == 1)
	assert(len(alpha.parseString('EXT. THIS IS A LOCATION - MORE SPECIFIC LOCATION - 4 AM')) == 3)
	assert(len(alpha.parseString('4 AM')) == 1)
	assert(len(alpha.parseString('EXT. THIS IS A LOCATION - MORE SPECIFIC LOCATION')) == 2)
	assert(len(alpha.parseString('EXT. THIS IS A LOCATION - MORE SPECIFIC LOCATION - WIDE SHOT - SUBJECT - 4 AM')) == 5)
	# throw in some new line noise
	assert(len(alpha.parseString('EXT. THIS IS A \nLOCATION - MORE SPECIFIC  \n LOCATION - WIDE SHOT - \n SUBJECT - 4 AM')) == 5)
	assert(len(alpha.parseString('EXT. THE JUNGLE - INDY\'S RUN - VARIOUS SHOTS - DAY')) == 4)

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

