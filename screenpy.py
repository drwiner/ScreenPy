import pyparsing as pp


DO_TEST = 1

def loadSpacy():
	import spacy
	print('loading SPACY english')
	return spacy.load('en')



HYPHEN = pp.Literal('-').suppress()
EOL = pp.Or(pp.LineEnd().suppress(), pp.Literal('\n'))
caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lower = caps.lower()
digits = "0123456789"
ALPHANUMS = caps + digits +'\''

# just once:
AFTER_SHOT = pp.Or([HYPHEN, pp.Literal('ON'), pp.Literal('WITH')])
# "ON" can be a shot for ANGLE ON

# Classic Shot Types
CLOSE = pp.Combine(pp.oneOf(['CLOSE', 'CLOSE SHOT', 'CLOSEUP', 'CLOSE ANGLE']).setResultsName('CU'), joinString=' ', adjacent=False)
XCLOSE = pp.oneOf(['EXTREME CLOSEUP', 'TIGHT CLOSE']).setResultsName('ECU')
WIDE = pp.oneOf(['WIDE', 'WIDE SHOT', 'WIDE ANGLE']).setResultsName('wide')
MED = pp.Literal('MED. SHOT').setResultsName('medium')
TWOSHOT = pp.Literal('TWO SHOT').setResultsName('2shot')
THREESHOT = pp.Literal('THREE SHOT').setResultsName('3shot')
EST = pp.oneOf(['ESTABLISHING SHOT', 'ESTABLISHING', '(ESTABLISHING)', 'TO ESTABLISH']).setResultsName('est')
MOVING_CAM = pp.Or([pp.Literal('TRACKING SHOT'), pp.Literal('TRACKING'), pp.Literal('MOVING'), pp.Literal('MOVING SHOT')]).setResultsName('moving-shot')
ANGLE = pp.Or([pp.Literal('NEW ANGLE'), pp.Literal('ANGLE'), pp.Literal('UP ANGLE'), pp.Literal('DOWN ANGLE'), pp.Literal('HIGH ANGLE'), pp.Literal('LOW ANGLE')]).setResultsName('angle')
REV = pp.Literal('REVERSE ANGLE').setResultsName('rev-shot')

# POV
WHATXSEES = pp.Combine(pp.Literal('WHAT') + pp.Word(pp.alphas) + pp.Literal('SEES'), joinString=' ', adjacent=False)
XPOV = pp.Combine(pp.Word(pp.alphas) + pp.Literal('\'s POV'), joinString='', adjacent=False)
POV = pp.Or([pp.Literal('POV'), pp.Literal('MYSTERY POV'), pp.Literal('ANONYMOUS POV'), pp.Literal('THROUGH SNIPER SCOPE'), pp.Literal('POV SHOT'), pp.Literal('BINOCULAR POV'), pp.Literal('MICROSCOPIC POV'), pp.Literal('UPSIDE-DOWN POV'), pp.Literal('WATCHER\'s POV'), pp.Literal('SUBJECTIVE CAMERA'), WHATXSEES, XPOV]).setResultsName('pov')

# misc
INSERT = pp.Literal('INSERT').setResultsName('insert')
BTS = pp.Literal('BACK TO SCENE').setResultsName('back-to-scene')
INLINE = pp.Or([pp.Literal('FROM BEHIND'), pp.Literal('THROUGH WINDOW')]).setResultsName('in-line')
HANDHELD = pp.Or([pp.Literal('HANDHELD SHOT'), pp.Literal('(HANDHELD)')]).setResultsName('handheld')
AERIAL = pp.Literal('AERIAL SHOT').setResultsName('aerial')
UNDERWATER = pp.Literal('UNDERWATER SHOT').setResultsName('underwater')
IS_SHOT = pp.ZeroOrMore(pp.Word(ALPHANUMS), stopOn=pp.Literal('SHOT')) + pp.Word(ALPHANUMS) + pp.ZeroOrMore(pp.Word(ALPHANUMS), stopOn=EOL | HYPHEN)
MISC = pp.Combine(pp.Or([BTS, INLINE, HANDHELD, AERIAL, UNDERWATER, INSERT, IS_SHOT]).setResultsName('misc'), joinString=' ', adjacent=False)



# A shot is one of these, but group together
SHOT_TYPES = pp.Group(pp.Or([CLOSE, XCLOSE, WIDE, MED, TWOSHOT, THREESHOT, EST, MOVING_CAM, ANGLE, REV, POV, MISC])).setResultsName('shot')

# Types of Shot Headers
# 1) Begins with SETTING
# 2) (Master Shot Heading): Begins with SHOT_TYPES
# 3) Subject Shot : Begins with Subject
# 4) Transition (may end with Colon)
# Each may end with Time of Day, each may include descriptions associated with each category
# May also be CAMERA actions in Direction

# pp.oneOf(SETTING, MASTER, SUBjECT, TRANSITION)



if DO_TEST:
	LP = pp.Literal('(').suppress()
	RP = pp.Literal(')').suppress()
	name = pp.OneOrMore(pp.Word(pp.alphanums)).setResultsName('words')
	PAREN = pp.Combine(LP + name + RP, joinString=' ', adjacent=False).setResultsName('paren')

	print('testing \"find Parenthesis\"')
	test_text = 'THIS IS A PARSABLE STRING (in 1985), and there\'s more (that meets the eye)'
	print('\t{}'.format(test_text))
	for result, start, end in PAREN.scanString(test_text):
		print("\tFound \"{}\" at [{}:{}]".format(result, start, end))
		print('\tresult[\'paren\'][\'words\']: {}'.format(result['paren']['words']))


# Transitions
FADE = ['FADE']
CUT = ['CUT']
DISSOLVE = ['DISSOLVE']


if DO_TEST:
	print('testing SETTING')
	t1 = '               EXT. THE JUNGLE - INDY\'S RUN - CLOSE ANGLE - DAY'
	t2 = '               Indy disappears into the foliage. An instant later, the leaves '
	t3 = '               EXT. THE URUBAMBA RIVER - DUSK'
	t4 = """               An amphibian plane sits in the water beneath a green cliff.

               Sitting on the wing is JOCK, the British pilot. Indy breaks

               out of some distant brush and runs along the path at the top

               of the cliff."""
	t5 = """               AT THE EDGE OF THE CLEARING

               Indy disappears into the foliage. An instant later, the leaves

               are peppered with a rain of poison darts and spears.

               EXT. THE JUNGLE - INDY'S RUN - VARIOUS SHOTS - DAY

               Indy runs like hell through steadily falling terrain. And

               always close behind, a swift gang of angry Hovitos.

               Occasionally they get close enough to send a dart or spear

               whizzing past Indy's head.

               EXT. THE URUBAMBA RIVER - DUSK

               An amphibian plane sits in the water beneath a green cliff.

               Sitting on the wing is JOCK, the British pilot. Indy breaks

               out of some distant brush and runs along the path at the top

               of the cliff."""

	t6 = 'DUSK                \n\n An amphibian plane sits in the water beneath a green cliff'
	t7 = """EXT. THE URUBAMBA RIVER - DUSK

               An amphibian plane sits in the water beneath a green cliff."""
	# test_new_line = pp.Word(pp.alphas) + pp.LineEnd().suppress()
	# test_new_line.parseString(t6)
	# SETTING (terior + locations(s))

	TERIOR = pp.oneOf(['INT.', 'EXT.', 'INT./EXT.'])

	SEG = HYPHEN + pp.Combine(pp.OneOrMore(~EOL + pp.Word(ALPHANUMS), stopOn=HYPHEN | EOL), joinString=' ', adjacent=False)
	first_loc = pp.Combine(pp.OneOrMore(~EOL + pp.Word(ALPHANUMS)), joinString=' ', adjacent=False)
	setting = pp.Group(TERIOR).setResultsName('terior') + first_loc + pp.ZeroOrMore(SEG)
	heading = pp.Group(setting) + pp.Group(pp.Optional(SHOT_TYPES))
	t = [t1,t2,t3,t4,t5,t6,t7]
	for i, ti in enumerate(t):
		# print(ti)
		print('\tt{}'.format(str(i+1)))
		for result, start, end in setting.scanString(ti):
			print("\t\tFound \"{}\" at [{}:{}]".format(result, start, end))

# Sub tasks - determine whether noun is person or place by looking at head (noun_list[-1]) and categorize as person or place, or proper noun. How can we figure this out by using it's distributional similarity to persons or places?

class Line:
	def __init__(self, str_line):
		if str_line == '\n':
			raise ValueError('Don\'t give me blank lines, doofus')
		self._indent = str_line.index(str_line.strip()[0])
		self._line = str_line.strip().split()
	def __len__(self):
		return len(self._line)
	def __getitem__(self, item):
		return self._line[item]
	def __str__(self):
		return ' '.join(item for item in self._line)
	def __repr__(self):
		return 'LINE{}'.format(self._line)


if __name__ == '__main__':
	screenplay = 'indianajonesandtheraidersofthelostark.txt'
	look_at_lines = []
	with open(screenplay) as fn:
		for line in fn:
			look_at_lines.append(line)
		# doc = split_into_sentences(fn.read())

	# with open('indianajonesandtheraidersofthelostark.txt', 'r') as ij:
	# 	ij.read()
	print("here")

