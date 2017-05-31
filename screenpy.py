from dateutil.parser import parse as dateparse
from screenpy_vars import *
import sys
DO_TEST = 0
DO_PRINT = 0


def Log(message):
	if DO_PRINT:
		print(message)


# if 'sense2vec' not in sys.modules:
import sense2vec
print('loading sense2vec')

s2v_model = sense2vec.load()
print('done loading')


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

# TITLE = pp.Combine(pp.Word(ALPHANUMS, exact=1) + pp.Word(lower), joinString='', adjacent=True)

# Opt-H
OPT_H = pp.Optional(HYPHEN)

# MODIFIER
MODIFIER = pp.Group(LP + pp.Combine(pp.OneOrMore(pp.Word(ALPHANUMS)), joinString=' ', adjacent=False) + RP).setResultsName('modifier')
# Opt-M
OPT_M = pp.Optional(MODIFIER)


# ToD
ToD = pp.Combine(pp.Combine(pp.OneOrMore(pp.Word(ALPHANUMS), stopOn=TITLE | one_word_title), joinString=' ', adjacent=False).addCondition(lambda token: is_time(token[0])).setResultsName('ToD') + OPT_M, joinString=', ', adjacent=False)
# Opt-ToD
OPT_ToD = pp.Optional(pp.Combine(pp.Literal('-').suppress() + WH + ToD, joinString=' ', adjacent=False))

if DO_TEST:
	assert(ToD.parseString('3 AM')[0] == '3 AM')
	assert(ToD.parseString('3 AM Ambphibean')[0] == '3 AM')
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

	t99 = 'NIGHT\n\n    A amphibian plane sits in the water beneath a green cliff.'
	assert(ToD.parseString(t99)[0] == 'NIGHT')

# preposition for camera transitions
# Opt-P
OPT_P = pp.Combine(OPT_H | prep, joinString=' ', adjacent=False)


# ST
ST = pp.Combine(SHOT_TYPES + OPT_M, joinString=', ', adjacent=False).setResultsName('shot type')

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
	assert(ST.parseString('HELP WIDE SHOT')[0][0] == 'HELP WIDE SHOT')
	assert(ST.parseString('WIDE SHOT - WITHOUT MOD')[0][0] == 'WIDE SHOT')
	assert(ST.parseString('A WIDE SHOT (WITH MOD)')[0][0] == 'A WIDE SHOT, (WITH MOD)')
	assert(ST.parseString('THIS WIDE SHOT')[0][0] == 'THIS WIDE SHOT')
	assert(ST.parseString('WIDE SHOT WITH EXTRA WORDS')[0][0] == 'WIDE SHOT')
	assert(ST.parseString('WIDE SHOT ANY EXTRA WORDS')[0][0] == 'WIDE SHOT')
	assert (ST.parseString('WIDE SHOT BECAUSE EXTRA WORDS')[0][0] == 'WIDE SHOT')
	assert(ST.parseString('WIDE SHOT Any EXTRA WORDS')[0][0] == 'WIDE SHOT')
	assert(ST.parseString('ANY WIDE SHOT (THE_MOD) \n\nAn CLOSE UP - DUSK\n\nAn CLOSE UP')[0][0] == 'ANY WIDE SHOT, (THE_MOD)')
	assert(ST.parseString('INTERCUT WITH INDY AND JONES')[0][0] == 'INTERCUT')
	assert(ST.parseString("INTERCUTTING INDY AND SIMONE SAYS")[0][0] == 'INTERCUTTING')
	assert(ST.parseString('MONTAGE THE BEES')[0][0] == 'MONTAGE')

def is_single_cap(s):
	return (len(s) == 1 and (s.isupper() or s == ',')) or s == ', I'


# Subj
X = pp.Combine(pp.OneOrMore(~HYPHEN + pp.Word(ALPHANUMS) + (WH | ~pp.Word(lower)), stopOn=pp.FollowedBy(HYPHEN) | one_word_title), joinString=' ', adjacent=False)
SUBJ = pp.Combine(X + OPT_M, joinString=', ', adjacent=False).addCondition(lambda token: not is_time(' '.join(token))).addCondition(lambda token: not is_single_cap(' '.join(token)))
SUBJ.setResultsName('subj')

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
	assert(SUBJ.parseString('ANY WIDE SHOT (THE_MOD) \n\nAn CLOSE UP - DUSK\n\nAn CLOSE UP')[0] == 'ANY WIDE SHOT, (THE_MOD)')
	assert (SUBJ.parseString('ANY WIDE SHOT (THE_MOD) An CLOSE UP - DUSK\n\nAn CLOSE UP')[0] == 'ANY WIDE SHOT, (THE_MOD)')
	assert (SUBJ.parseString('SAMUEL (THE_MOD) An CLOSE UP - DUSK\n\nAn CLOSE UP')[0] == 'SAMUEL, (THE_MOD)')
	assert (SUBJ.parseString('SAMUEL - (THE_MOD) - An CLOSE UP - DUSK\n\nAn CLOSE UP')[0] == 'SAMUEL')
	assert (SUBJ.parseString('SAMUEL Amb (THE_MOD) - An CLOSE UP - DUSK\n\nAn CLOSE UP')[0] == 'SAMUEL')
	assert(SUBJ.parseString('ANY WIDE SHOT (THE_MOD) \n\nAn CLOSE UP - DUSK\n\nAn CLOSE UP')[0] == 'ANY WIDE SHOT, (THE_MOD)')
	assert(SUBJ.parseString('AMD Dn')[0] == 'AMD')
	try:
		SUBJ.parseString('DDDDn')
		print('bad')
	except pp.ParseException:
		print('good')

	t9 = """THE URUBAMBA RIVER\n\n   A amphibian plane sits in the water beneath a green cliff."""
	assert(SUBJ.parseString(t9)[0] == 'THE URUBAMBA RIVER')

# SUB
SUB = (SUBJ + OPT_ToD) | ToD
if DO_TEST:
	SUB.parseString('HELLO - 3 AM \n')
	SUB.parseString('HELLO (MOD) - 3 AM\n 5 AM')
	assert(SUB.parseString('HELLO GOODBYE - 3 AM - HELLO - 3 AM \n')[1] == '3 AM')
	assert (SUB.parseString('HELLO GOODBYE - 3 AM An - HELLO - 3 AM \n')[1] == '3 AM')
	try:
		SUB.parseString('HELLO GOODBYE An - 3 AM An - HELLO - 3 AM \n')[1]
		print('bad')
	except IndexError:
		print('good')
	assert(SUB.parseString('HELLO GOODBYE An - 3 AM An - HELLO - 3 AM \n')[0] == 'HELLO GOODBYE')
	assert (SUB.parseString('SAMUEL L JACKSON (CREEPY) Amb')[0] == 'SAMUEL L JACKSON, (CREEPY)')
	t9 = """THE URUBAMBA RIVER - NIGHT\n\n    An amphibian plane sits in the water beneath a green cliff."""
	assert(len(SUB.parseString(t9)) == 2)
	t9 = """THE URUBAMBA RIVER - NIGHT\n\n    A amphibian plane sits in the water beneath a green cliff."""
	assert(SUB.parseString(t9)[0] == 'THE URUBAMBA RIVER')
	assert(SUB.parseString(t9)[1] == 'NIGHT')

# T
TERIOR = pp.oneOf(['INT.', 'EXT.', 'INT./EXT.', 'EXT./INT.', 'EXT. / INT.', 'INT. / EXT.']).setResultsName('terior')

# ONE_LOC
Y = pp.Combine(pp.OneOrMore(~SHOT_TYPES + pp.Word(ALPHANUMS), stopOn=pp.MatchFirst([HYPHEN | TITLE | one_word_title])), joinString=' ', adjacent=False).addCondition(lambda token: not is_time(token[0]))
ONE_LOC = pp.Combine(Y + OPT_M, joinString=', ', adjacent=False)

if DO_TEST:
	assert(ONE_LOC.parseString('HELLO DO I HAUNT YOU - WHAT ABOUT THE LOCATION')[0] == 'HELLO DO I HAUNT YOU')
	assert (ONE_LOC.parseString('HELLO DO I HAUNT YOU Amphibean - WHAT ABOUT THE LOCATION')[0] == 'HELLO DO I HAUNT YOU')
	assert (ONE_LOC.parseString('HELLO DO I HAUNT YOU - 3 AM - WHAT ABOUT THE LOCATION')[0] == 'HELLO DO I HAUNT YOU')
	assert (ONE_LOC.parseString('HELLO DO I HAUNT YOU - WHAT ABOUT THE LOCATION - 3 AM')[0] == 'HELLO DO I HAUNT YOU')

	assert (ONE_LOC.parseString('HELLO DO I HAUNT YOU (EAST HALLWAY) - WHAT ABOUT THE LOCATION (WEST SIDE OF TOWN)')[0] == 'HELLO DO I HAUNT YOU, (EAST HALLWAY)')
	t7 = """THE URUBAMBA RIVER - DUSK

		           An amphibian plane sits in the water beneath a green cliff."""
	assert (len(ONE_LOC.parseString(t7)) == 1)
	t9 = """THE URUBAMBA RIVER - NOTATIME

			           An amphibian plane sits in the water beneath a green cliff."""
	assert (len(ONE_LOC.parseString(t9)) == 1)
	t9 = """THE URUBAMBA RIVER

			           A amphibian plane sits in the water beneath a green cliff."""


# LOC
LOC = pp.OneOrMore(pp.MatchFirst([ONE_LOC, pp.Literal('-').suppress() + WH]))

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
	t7 = """THE URUBAMBA RIVER - DUSK\n\n     An amphibian plane sits in the water beneath a green cliff."""
	LOC.parseString(t7)
	assert(len(LOC.parseString(t7)) == 1)
	t9 = """THE URUBAMBA RIVER - NOTATIME

			           An amphibian plane sits in the water beneath a green cliff."""
	assert(len(LOC.parseString(t9)) == 2)
	assert(len(LOC.parseString('AN ELEPHANT rumbles')) == 1)
	assert(len(LOC.parseString('AN ELEPHANT Drumbles')) == 1)

# setting
SETTING = TERIOR + pp.Group(LOC).setResultsName('location')

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
	t7 = """EXT. THE URUBAMBA RIVER - DUSK

	           An amphibian plane sits in the water beneath a green cliff."""
	assert(len(SETTING.parseString(t7)[1]) == 1)
	t9 = """EXT. THE URUBAMBA RIVER - NOTEATIME

	           An amphibian plane sits in the water beneath a green cliff."""
	assert(len(SETTING.parseString(t9)[1]) == 2)

# Shot
S1 = ST + pp.Optional((prep | (pp.Literal('-').suppress() + WH)).suppress() + SUB)
S2 = OTHER_SHOT_SUBJ_TRANSITIONS + ~prep + SUB
SHOT = pp.MatchFirst([S2, S1])

if DO_TEST:
	assert(SHOT.parseString('WIDE SHOT (MOD TEST) - CNN CORRESPONDENT')[1] == 'CNN CORRESPONDENT')
	assert(SHOT.parseString('TRACKING SHOT ON CNN CORRESPONDENT - 4 AM \n')[2] == '4 AM')
	assert(SHOT.parseString('CLOSE ANGLE WITH CNN')['shot type'][0] == 'CLOSE ANGLE')
	assert(SHOT.parseString('ZOOM TO CNN')['shot type'][0] == 'ZOOM')
	assert(SHOT.parseString('WIDE SHOT')['shot type'][0] == 'WIDE SHOT')
	assert(SHOT.parseString('WIDE SHOT (SNEAKY)')['shot type'][0] == 'WIDE SHOT, (SNEAKY)')
	assert(SHOT.parseString('WIDE SHOT (SNEAKY) Amb')['shot type'][0] == 'WIDE SHOT, (SNEAKY)')
	assert(SHOT.parseString('WIDE SHOT Amb(SNEAKY) Amb')['shot type'][0] == 'WIDE SHOT')
	assert(SHOT.parseString('CLOSE ANGLE (KINDA) - AND HERE IS THE SUBJECT (SNEAKY RIGHT) Amb')[1] == 'AND HERE IS THE SUBJECT, (SNEAKY RIGHT)')
	assert(SHOT.parseString('CLOSE ANGLE Amb (KINDA) - AND HERE IS THE SUBJECT (SNEAKY RIGHT) Amb')['shot type'][0] == 'CLOSE ANGLE')
	assert(SHOT.parseString('CLOSE ANGLE (KINDA) Amb - AND HERE IS THE SUBJECT (SNEAKY RIGHT) Amb')['shot type'][0] == 'CLOSE ANGLE, (KINDA)')
	assert(SHOT.parseString('CLOSE ANGLE (KINDA) - AND HERE IS THE SUBJECT Amb (SNEAKY RIGHT) Amb')[1] == 'AND HERE IS THE SUBJECT')
	assert(SHOT.parseString('INTERCUTTING INDY')[1] == 'INDY')
	assert(SHOT.parseString('MONTAGE OF INDY AND MONSTERS')[1] == 'INDY AND MONSTERS')
	assert(SHOT.parseString('MONTAGE INDY AND MONSTERS')[1] == 'INDY AND MONSTERS')


# Scene
SCENE = SETTING + pp.MatchFirst([SHOT | ToD | pp.Empty()])

if DO_TEST:
	SCENE.parseString('EXT. THIS IS A LOCATION - MORE SPECIFIC LOCATION')
	assert (len(SCENE.parseString('EXT. RIVER - DUSK')) == 3)
	assert (SCENE.parseString('EXT. THIS IS A LOCATION - MORE SPECIFIC LOCATION - 4 AM')[2] == '4 AM')
	assert (SCENE.parseString('EXT. THIS IS A LOCATION - MORE SPECIFIC LOCATION - 4 AM \nAn ambibean')[2] == '4 AM')
	assert (SCENE.parseString('EXT. THIS IS A LOCATION - MORE SPECIFIC LOCATION - 4 AM - WIDE SHOT')[2] == '4 AM')
	assert (SCENE.parseString('EXT. THIS IS A LOCATION - MORE SPECIFIC LOCATION - 4 AM - WIDE SHOT An ambibean')[2] == '4 AM')
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
	assert (len(SCENE.parseString('EXT. THIS ONE (A MOD HERE) - MORE SPECIFIC LOCATION (A MOD THERE) - WIDE SHOT (THERE\'S A MOD) - SUBJECT (ALMOST) Ambphean - 4 AM (EVERYWHERE) Ambphean')) == 4)
	assert (len(SCENE.parseString(
		'EXT. THIS ONE (A MOD HERE) amb - MORE SPECIFIC LOCATION (A MOD THERE) - WIDE SHOT (THERE\'S A MOD) - SUBJECT (ALMOST) - 4 AM (EVERYWHERE) Ambphean')) == 2)
	assert (len(SCENE.parseString(
		'EXT. THIS ONE (A MOD HERE) - MORE SPECIFIC LOCATION (A MOD THERE) Amb- WIDE SHOT (THERE\'S A MOD) - SUBJECT (ALMOST) - 4 AM (EVERYWHERE) Ambphean')) == 2)
	assert (len(SCENE.parseString(
		'EXT. THIS ONE (A MOD HERE) - MORE SPECIFIC LOCATION (A MOD THERE) - WIDE SHOT (THERE\'S A MOD) - SUBJECT (ALMOST) - 4 AM (EVERYWHERE) Amb')) == 5)
	assert (len(SCENE.parseString(
		'EXT. THIS ONE (A MOD HERE) - MORE SPECIFIC LOCATION (A MOD THERE) - WIDE SHOT (THERE\'S A MOD) - SUBJECT (ALMOST) Ambphean - 4 AM (EVERYWHERE) Ambphean')) == 4)
	assert(len(SCENE.parseString(t7)) == 3)
	assert(len(SCENE.parseString(t9)[1]) == 2)
	t8 = """EXT. THE URUBAMBA RIVER - NOTEATIME - ANY SHOT - DAY

	           An amphibian plane sits in the water beneath a green cliff."""
	assert(len(SCENE.parseString(t8)) == 4)
	assert(len(SCENE.parseString('EXT. THE URUBAMBA RIVER - NOTEATIME - DAY An')) == 3)
	y = """INT. ARAB BAR - NIGHT

               A dark,"""
	assert(SCENE.parseString(y)['ToD'] == 'NIGHT')


# alpha
alpha = pp.MatchFirst([SCENE | SHOT | SUB | ToD]).setResultsName('heading')

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
	assert(len(alpha.parseString(t7)[1]) == 1)
	assert(len(alpha.parseString(t9)[1]) == 2)
	assert(len(alpha.parseString(header)) == 4)
	assert (len(alpha.parseString('EXT. THIS ONE (A MOD HERE) - MORE SPECIFIC LOCATION (A MOD THERE) - WIDE SHOT (THERE\'S A MOD) - SUBJECT (ALMOST) Ambphean - 4 AM (EVERYWHERE) Ambphean')) == 4)
	assert (len(alpha.parseString(
		'EXT. THIS ONE (A MOD HERE) amb - MORE SPECIFIC LOCATION (A MOD THERE) - WIDE SHOT (THERE\'S A MOD) - SUBJECT (ALMOST) - 4 AM (EVERYWHERE) Ambphean')) == 2)
	assert (len(alpha.parseString(
		'EXT. THIS ONE (A MOD HERE) - MORE SPECIFIC LOCATION (A MOD THERE) Amb- WIDE SHOT (THERE\'S A MOD) - SUBJECT (ALMOST) - 4 AM (EVERYWHERE) Ambphean')) == 2)
	assert (len(alpha.parseString(
		'EXT. THIS ONE (A MOD HERE) - MORE SPECIFIC LOCATION (A MOD THERE) - WIDE SHOT (THERE\'S A MOD) - SUBJECT (ALMOST) - 4 AM (EVERYWHERE) Amb')) == 5)
	assert (len(alpha.parseString(
		'EXT. THIS ONE (A MOD HERE) - MORE SPECIFIC LOCATION (A MOD THERE) - WIDE SHOT (THERE\'S A MOD) - SUBJECT (ALMOST) Ambphean - 4 AM (EVERYWHERE) Ambphean')) == 4)
	assert(len(alpha.parseString(t7)) == 3)
	assert(len(alpha.parseString(t9)[1]) == 2)
	t8 = """EXT. THE URUBAMBA RIVER - NOTEATIME - ANY SHOT - DAY

	           An amphibian plane sits in the water beneath a green cliff."""
	assert(len(alpha.parseString(t8)) == 4)
	assert(len(alpha.parseString('EXT. THE URUBAMBA RIVER - NOTEATIME - DAY An')) == 3)
	aquote = """EXT. THE FOOT CHASE - INTERCUTTING INDY AND THE MOVING

               BASKET - DAY"""
	alpha.parseString(aquote)
	x = """THE SANCTUARY\n\n  A large"""


def join_strings(tokens):
	return ' '.join(tokens)

options = pp.Combine(pp.Optional(pp.White(' ', max=1).suppress() + pp.Word(ALPHANUMS, max=1)) + pp.Optional(pp.White(' ', max=1)), joinString='', adjacent=True)
direction = ~pp.Word('.' + ',' + '-', exact=1) + options + pp.Word(lower + '\'' + '.' + '\"' + ',' + '(' + ')', min=1)
no_new_line = pp.OneOrMore(~pp.White('\n') + pp.Or([TITLE, pp.Word(ALPHANUMS)]))
after_caps = pp.Combine(~pp.White('\n', min=1) + pp.OneOrMore(TITLE | pp.Word(ALPHANUMS)), joinString='', adjacent=False)
before_caps = pp.Combine(pp.Optional(no_new_line) + direction, joinString=' ', adjacent=False)
legal = before_caps + pp.Optional(after_caps)
LOWER_CASE = ~pp.Word('.' + '-' + ',', exact=1).suppress() + pp.OneOrMore(legal | TITLE, stopOn=wall).addParseAction(join_strings)

if DO_TEST:
	t8 = """EXT. THE URUBAMBA RIVER - NOTEATIME - ANY SHOT - DAY

		           An amphibian plane sits in the water beneath a green cliff."""
	scan_t8 = list(LOWER_CASE.scanString(t8))[0]
	assert(t8[scan_t8[1]:scan_t8[2]].strip() == 'An amphibian plane sits in the water beneath a green cliff.')

	t11 = """EXT. THE URUBAMBA RIVER - NOTEATIME - ANY SHOT - DAY

			           An amphibian plane sits in the water BENEATH a green cliff."""
	scan_t11 = list(LOWER_CASE.scanString(t11))[0]
	assert(t11[scan_t11[1]:scan_t11[2]].strip() == 'An amphibian plane sits in the water BENEATH a green cliff.')
	list(LOWER_CASE.scanString("  Lawrence Kasdan"))


LC = spaces + LOWER_CASE.setResultsName('text')
HEADINGS = pp.Group(spaces + ~LC + alpha).setResultsName('heading')

if DO_TEST:
	t11 = """  EXT. THE URUBAMBA RIVER - NOTEATIME - ANY SHOT - DAY

				           An amphibian plane sits in the water BENEATH a green cliff."""

	t12 = """                 EXT. THE URUBAMBA RIVER - NOTEATIME - ANY SHOT - DAY

				           An amphibian plane sits in the water BENEATH a green cliff."""
	d = list(HEADINGS.scanString(t11))[0][0].asDict()
	assert(d['heading']['location'][1] == 'NOTEATIME')
	# assert(len(list(HEADINGS.scanString(t11))) == 1)
	t13 = """  other stuff here\n\n               EXT. THE URUBAMBA RIVER - NOTEATIME - ANY SHOT - DAY

					           An amphibian plane sits in the water BENEATH a green cliff."""
	assert(list(HEADINGS.scanString(t13))[0][0].asDict()['heading']['ToD'] == 'DAY')
	t13 = """  other stuff here\n\n               EXT. THE URUBAMBA RIVER - NOTEATIME - ANY SHOT - DAY

						           A amphibian plane sits in the water BENEATH a green cliff."""
	assert (list(HEADINGS.scanString(t13))[0][0].asDict()['heading']['ToD'] == 'DAY')


if __name__ == '__main__':
	pass
# 	screenplay = 'indianajonesandtheraidersofthelostark.txt'
#
# 	look_at_lines = []
# 	print('reading indiana jones')
# 	with open(screenplay) as fn:
# 		# for line in fn:
# 		for result, s, e in alpha.scanString(fn.read()):
# 			look_at_lines.append(result)
#
# 	with open('headings.txt', 'w') as head:
# 		for line in look_at_lines:
# 			head.write('{}\n'.format(line))

