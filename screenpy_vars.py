import pyparsing as pp

# basic vars

EOL = pp.Or(pp.LineEnd().suppress(), pp.Literal('\n'))
caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lower = caps.lower()
digits = "0123456789"
ALPHANUMS = caps + digits + '\'' + '\\' + '/' + '\"' + '\'' + '_' + ',' + '-' + '.'
ALL_CHARS = ALPHANUMS + lower
WH = pp.White().suppress()
HYPHEN = WH + pp.Literal('-').suppress() + WH
OHYPHEN = pp.Literal('-').suppress() + WH
LP = pp.Literal('(')
RP = pp.Literal(')')
BASIC_VARS = [HYPHEN, EOL, caps, lower, digits, ALPHANUMS, WH, LP, RP]


# Classic Shot Types
CLOSE = pp.Combine(pp.Or([pp.Literal('CLOSE'), pp.Literal('CLOSE SHOT'), pp.Literal('CLOSEUP'), pp.Literal('CLOSE ANGLE')]).setResultsName('CU'), joinString=' ', adjacent=False)
XCLOSE = pp.Or([pp.Literal('EXTREME CLOSEUP'), pp.Literal('TIGHT CLOSE')]).setResultsName('ECU')
WIDE = pp.Or([pp.Literal('WIDE'), pp.Literal('WIDE SHOT'), pp.Literal('WIDE ANGLE')]).setResultsName('wide')
MED = pp.Literal('MED. SHOT').setResultsName('medium')
TWOSHOT = pp.Or([pp.Literal('TWO SHOT'), pp.Literal('2 SHOT')]).setResultsName('2shot')
THREESHOT = pp.Or(pp.Literal('THREE SHOT'), pp.Literal('3 SHOT')).setResultsName('3shot')
EST = pp.Or([pp.Literal('ESTABLISHING SHOT'), pp.Literal('ESTABLISHING'), pp.Literal('(ESTABLISHING)'), pp.Literal('TO ESTABLISH')]).setResultsName('est')
MOVING_CAM = pp.Or([pp.Literal('TRACKING SHOT'), pp.Literal('TRACKING'), pp.Literal('MOVING'), pp.Literal('MOVING SHOT')]).setResultsName('moving-shot')
ANGLE = pp.Or([pp.Literal('NEW ANGLE'), pp.Literal('ANGLE'), pp.Literal('UP ANGLE'), pp.Literal('DOWN ANGLE'), pp.Literal('HIGH ANGLE'), pp.Literal('LOW ANGLE')]).setResultsName('angle')
REV = pp.Literal('REVERSE ANGLE').setResultsName('rev-shot')
CRANE = pp.Literal('CRANE')
TILT = pp.Literal('TILT')
PAN = pp.Literal('PAN')
ZOOM = pp.Literal('ZOOM')
MOVING_SHOT = pp.Or([ZOOM, PAN, CRANE, TILT, MOVING_CAM, PAN])

# POV
WHATXSEES = pp.Combine(pp.Literal('WHAT') + pp.Word(ALPHANUMS) + pp.Literal('SEES'), joinString=' ', adjacent=False)
XPOV = pp.Combine(pp.Word(ALPHANUMS) + pp.Literal('\'s POV'), joinString='', adjacent=False)
POV = pp.Or([pp.Literal('P.O.V.'), pp.Literal('POV'), pp.Literal('MYSTERY POV'), pp.Literal('ANONYMOUS POV'), pp.Literal('THROUGH SNIPER SCOPE'), pp.Literal('POV SHOT'), pp.Literal('BINOCULAR POV'), pp.Literal('MICROSCOPIC POV'), pp.Literal('UPSIDE-DOWN POV'), pp.Literal('WATCHER\'s POV'), pp.Literal('SUBJECTIVE CAMERA'), WHATXSEES, XPOV]).setResultsName('pov')


basic_prep = pp.oneOf(['ON', 'OF', 'WITH', 'TO', 'TOWARDS', 'FROM', 'IN', 'UNDER', 'OVER', 'ABOVE', 'AROUND', 'INTO'])
prep = basic_prep + WH
OTHER_SHOT_SUBJ_TRANSITIONS = pp.oneOf(['TRACKING', 'INTERCUTTING', 'INTERCUT', 'CUTTING', 'CUTS', 'MONTAGE'])

# misc
INTERCUT = pp.Or([pp.Literal('INTERCUTTING'), pp.Literal('INTERCUT'), pp.Literal('CUTTING'), pp.Literal('CUTS'), pp.Literal('MONTAGE'), pp.Literal('VARIOUS SHOTS')])
INSERT = pp.Or([pp.Literal('INSERT SHOT'), pp.Literal('INSERT')]).setResultsName('insert')
INLINE = pp.Or([pp.Literal('FROM BEHIND'), pp.Literal('THROUGH WINDOW')]).setResultsName('in-line')
HANDHELD = pp.Or([pp.Literal('HANDHELD SHOT'), pp.Literal('(HANDHELD)')]).setResultsName('handheld')
AERIAL = pp.Or([pp.Literal('AERIAL'), pp.Literal('AERIAL SHOT')]).setResultsName('aerial')
UNDERWATER = pp.Or([pp.Literal('UNDERWATER'), pp.Literal('UNDERWATER SHOT')]).setResultsName('underwater')
TITLE = pp.Combine(pp.Word(ALPHANUMS, exact=1) + pp.Word(lower), joinString='', adjacent=True)
# INTER_SHOT_WORDS = pp.oneOf(['SHOT', 'TRACKING', 'MOVING', 'INTERCUTTING', 'INTERCUT', 'CUTTING', 'CUTS', 'MONTAGE'])
IS_SHOT = pp.Word(ALPHANUMS, min=3) + pp.Literal('SHOT')
# IS_ALSO_SHOT = pp.Optional(pp.Word(ALPHANUMS, min=3)) + pp.Combine(pp.oneOf(['SHOT', 'TRACKING', 'INTERCUTTING', 'AERIAL']) + pp.OneOrMore(pp.Word(ALPHANUMS), stopOn=pp.MatchFirst([TITLE, prep, HYPHEN])), joinString=' ', adjacent=False)
MISC = pp.Combine(pp.Or([INLINE, HANDHELD, AERIAL, UNDERWATER, INSERT, IS_SHOT, INTERCUT]).setResultsName('misc'), joinString=' ', adjacent=False)


# segment of caps
in_caps = pp.OneOrMore(pp.Word(ALPHANUMS), stopOn=pp.Or(HYPHEN, EOL))
in_caps_w_condition = in_caps.addCondition(lambda toks: len(toks) > 1 or len(toks[0]) > 1)
CAPS = pp.Combine(in_caps_w_condition, joinString=" ", adjacent=False)

not_prep_nor_title_nor_hyphen = ~pp.Group(HYPHEN | TITLE | basic_prep)

# A shot is one of these, but group together
SHOT_TYPES = pp.Or([CLOSE, XCLOSE, WIDE, MED, MOVING_SHOT, TWOSHOT, THREESHOT, EST, MOVING_CAM, ANGLE, REV, POV, MISC]).setResultsName('shot')
# SHOT_TYPES = pp.Combine(pp.ZeroOrMore(pp.Word(ALPHANUMS), stopOn=SHOT_TYPES) + SHOT_TYPES + pp.ZeroOrMore(~not_prep_nor_title_nor_hyphen + pp.Word(ALPHANUMS, min=3)), joinString=" ", adjacent=False)
SHOT_TYPES = pp.Combine(pp.ZeroOrMore(~OHYPHEN + pp.Word(ALPHANUMS), stopOn=SHOT_TYPES) + SHOT_TYPES, joinString=" ", adjacent=False)
# Transition
CUT = pp.Literal('CUT')
DISSOLVE = pp.Literal('DISSOLVE')
FADE = pp.Literal('FADE')
WIPE = pp.Literal('WIPE')
MISC_TRANS = pp.oneOf('LATER', 'SAME SCENE', 'BACK TO SCENE')
FLASHBACK = pp.oneOf(['FLASHBACK', 'FLASHFORWARD'])
TRANSITIONS = pp.Combine(pp.Optional(CAPS) + pp.Or([CUT, DISSOLVE, FADE, WIPE, MISC_TRANS, FLASHBACK]) + pp.Optional(pp.Word(ALPHANUMS)) + pp.Optional(pp.Literal(':').suppress()), joinString=' ', adjacent=False).setResultsName('transition')

# Sound and Visual WORDS
# consider not using, because could be character's name or place?
# SVW = pp.oneOf('FLASH', "ROAR", 'CRACK', 'KNOCK', 'SMACK', 'THUMP', 'ROMP', 'SCREECH', 'PLOP', 'SPLASH', 'BEEP', 'BANG', 'SQUISH', 'FIZZ', 'OINK', 'TICK', 'TOCK', 'ZAP', 'VROOM', 'PING', 'HONK', 'FLUTTER', 'AWOOGA', 'OOM-PAH', 'CLANK', 'BAM', 'BOP')


#misc
mid_x = pp.Literal('mid').suppress() + pp.Word(pp.alphanums)
continuous_action = pp.Or(pp.Literal('CONTINUOUS ACTION'), pp.Literal('continuous action'))

enumerated_time_word = pp.oneOf(['sunrise', 'sunset', 'present', 'later', 'before', 'breakfast', 'lunch', 'dinner', 'past', 'spring', 'summer', 'fall', 'winter', 'easter', 'christmas', 'passover', 'eve', 'dusk', 'ramadan', 'birthday', 'purim', 'holi', 'equinox', 'kwanzaa', 'recent', 'annual', 'sundown', 'sun-down', 'sun-up', 'tonight', 'dawn']) + ~(~WH + pp.Word(pp.alphanums))

stop_words = ~pp.oneOf(['is', 'home', 'this', 'that', 'there', 'are', 'were', 'be', 'for', 'with', 'was', 'won\'t', 'aren\'t', 'ain\'t', 'isn\'t', 'not', 'on', 'above', 'into', 'around', 'over', 'in', 'number', 'another', 'third', 'fourth', 'anything', 'hear', 'wife', 'run', 'me', 'case', 'everyone', 'friends'])


def num_spaces(tokens):
	return len(tokens[0])

spaces = pp.OneOrMore(pp.White(ws=' ', min=1)).addParseAction(num_spaces).setResultsName('indent')
min_2_spaces = pp.OneOrMore(pp.White(ws=' ', min=2)).addParseAction(num_spaces).setResultsName('indent')
w = pp.OneOrMore(pp.White(ws='\t\r\n', min=1, max=0, exact=0))
wall = w + spaces


one_word_title = pp.Word(ALPHANUMS, max=1) & pp.FollowedBy(pp.Word(lower))