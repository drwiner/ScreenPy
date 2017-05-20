import pyparsing as pp

# basic vars

EOL = pp.Or(pp.LineEnd().suppress(), pp.Literal('\n'))
caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lower = caps.lower()
digits = "0123456789"
ALPHANUMS = caps + digits + '\'' + ',' + '\"' + '_'
ALL_CHARS = ALPHANUMS + lower
WH = pp.White().suppress()
HYPHEN = WH + pp.Literal('-').suppress() + WH
LP = pp.Literal('(')
RP = pp.Literal(')')
BASIC_VARS = [HYPHEN, EOL, caps, lower, digits, ALPHANUMS, WH, LP, RP]


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
CRANE = pp.Literal('CRANE')
TILT = pp.Literal('TILT')
PAN = pp.Literal('PAN')
ZOOM = pp.Literal('ZOOM')
MOVING_SHOT = pp.Or([ZOOM, PAN, CRANE, TILT, MOVING_CAM, PAN])

# POV
WHATXSEES = pp.Combine(pp.Literal('WHAT') + pp.Word(ALPHANUMS) + pp.Literal('SEES'), joinString=' ', adjacent=False)
XPOV = pp.Combine(pp.Word(ALPHANUMS) + pp.Literal('\'s POV'), joinString='', adjacent=False)
POV = pp.Or([pp.Literal('POV'), pp.Literal('MYSTERY POV'), pp.Literal('ANONYMOUS POV'), pp.Literal('THROUGH SNIPER SCOPE'), pp.Literal('POV SHOT'), pp.Literal('BINOCULAR POV'), pp.Literal('MICROSCOPIC POV'), pp.Literal('UPSIDE-DOWN POV'), pp.Literal('WATCHER\'s POV'), pp.Literal('SUBJECTIVE CAMERA'), WHATXSEES, XPOV]).setResultsName('pov')


prep = pp.oneOf(['ON', 'WITH', 'TO', 'TOWARDS', 'FROM', 'IN', 'UNDER', 'OVER', 'ABOVE', 'AROUND', 'INTO'])

# misc
INSERT = pp.Literal('INSERT').setResultsName('insert')
BTS = pp.Literal('BACK TO SCENE').setResultsName('back-to-scene')
INLINE = pp.Or([pp.Literal('FROM BEHIND'), pp.Literal('THROUGH WINDOW')]).setResultsName('in-line')
HANDHELD = pp.Or([pp.Literal('HANDHELD SHOT'), pp.Literal('(HANDHELD)')]).setResultsName('handheld')
AERIAL = pp.Literal('AERIAL SHOT').setResultsName('aerial')
UNDERWATER = pp.Literal('UNDERWATER SHOT').setResultsName('underwater')
IS_SHOT = pp.ZeroOrMore(pp.Word(ALPHANUMS), stopOn=pp.Literal('SHOT')) + pp.OneOrMore(pp.Word(ALPHANUMS), stopOn=prep | EOL | HYPHEN)
MISC = pp.Combine(pp.Or([BTS, INLINE, HANDHELD, AERIAL, UNDERWATER, INSERT, IS_SHOT]).setResultsName('misc'), joinString=' ', adjacent=False)


# segment of caps
in_caps = pp.OneOrMore(pp.Word(ALPHANUMS), stopOn=pp.Or(HYPHEN, EOL))
in_caps_w_condition = in_caps.addCondition(lambda toks: len(toks) > 1 or len(toks[0]) > 1)
CAPS = pp.Combine(in_caps_w_condition, joinString=" ", adjacent=False)

# A shot is one of these, but group together
SHOT_TYPES = pp.Or([CLOSE, XCLOSE, WIDE, MED, MOVING_SHOT, TWOSHOT, THREESHOT, EST, MOVING_CAM, ANGLE, REV, POV, MISC]).setResultsName('shot')
SHOT_TYPES = pp.ZeroOrMore(pp.Word(ALPHANUMS), stopOn=SHOT_TYPES) + SHOT_TYPES

# Transition
CUT = pp.Literal('CUT')
DISSOLVE = pp.Literal('DISSOLVE')
FADE = pp.Literal('FADE')
WIPE = pp.Literal('WIPE')
MISC_TRANS = pp.oneOf('LATER', 'SAME SCENE')
TRANSITIONS = pp.Combine(pp.Optional(CAPS) + pp.Or([CUT, DISSOLVE, FADE, WIPE, MISC_TRANS]) + pp.Optional(pp.Word(ALPHANUMS)) + pp.Optional(pp.Literal(':').suppress()), joinString=' ', adjacent=False).setResultsName('transition')


#misc
mid_x = pp.Literal('mid').suppress() + pp.Word(pp.alphanums)
continuous_action = pp.Literal('continuous action')

enumerated_time_word = pp.oneOf(['sunrise', 'sunset', 'present', 'later', 'before', 'breakfast', 'lunch', 'dinner', 'past', 'spring', 'summer', 'fall', 'winter', 'easter', 'christmas', 'passover', 'eve', 'dusk', 'ramadan', 'birthday', 'purim', 'holi', 'equinox', 'kwanzaa', 'recent', 'annual', 'sundown', 'sun-down', 'sun-up', 'tonight']) + ~(~WH + pp.Word(pp.alphanums))

stop_words = ~pp.oneOf(['is', 'this', 'that', 'there', 'are', 'were', 'be', 'for', 'with', 'was', 'won\'t', 'aren\'t', 'ain\'t', 'isn\'t', 'not', 'on', 'above', 'into', 'around', 'over', 'in', 'number', 'another', 'third', 'fourth', 'anything', 'hear', 'wife', 'run', 'me', 'case', 'everyone'])


