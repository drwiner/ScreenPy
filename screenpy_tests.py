from screenpy import *

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

t = [t1,t2,t3,t4,t5,t6,t7]

# Test MODIFIER
# MODIFIER = pp.Combine(LP + pp.OneOrMore(pp.Word(ALL_CHARS)) + RP, joinString=' ', adjacent=False).setResultsName('modifier')
print('testing \"find MODIFIER\"')
test_text = 'THIS IS A PARSABLE STRING (in 1985), and there\'s more (that meets the eye)'
print('\t{}'.format(test_text))
for result, start, end in MODIFIER.scanString(test_text):
	print("\tFound \"{}\" at [{}:{}]".format(result, start, end))
	print('\tresult[\'paren\'][\'words\']: {}'.format(result['paren']['words']))

# Test Time of Day
# ToD = pp.Combine(pp.OneOrMore(pp.Word(ALPHANUMS)).addCondition(lambda tokens: is_time(tokens)) + OPT_M, joinString=' ', adjacent=False).setResultsName('ToD')
for i, ti in enumerate(t):
	# print(ti)
	print('\tt{}'.format(str(i + 1)))
	for result, start, end in ToD.scanString(ti):
		print("\t\tFound \"{}\" at [{}:{}]".format(result, start, end))

# test SUBJ
# ST = SHOT_TYPES + OPT_M
# SUBJ = pp.OneOrMore(CAPS.copy().addCondition(lambda token: not is_date(token)) + OPT_M,
#                      stopOn=EOL | pp.Empty.addCondition(lambda x: is_date(x))
# SUB = SUBJ + OPT_ToD
for i, ti in enumerate(t):
	# print(ti)
	print('\tt{}'.format(str(i + 1)))
	for result, start, end in SUBJ.scanString(ti):
		print("\t\tFound \"{}\" at [{}:{}]".format(result, start, end))


# test SHOT
# SHOT = SHOT_TYPES + OPT_P + SUB
for i, ti in enumerate(t):
	# print(ti)
	print('\tt{}'.format(str(i + 1)))
	for result, start, end in SUBJ.scanString(ti):
		print("\t\tFound \"{}\" at [{}:{}]".format(result, start, end))


# test setting
# old SEG
# SEG = HYPHEN + pp.Combine(pp.OneOrMore(~EOL + pp.Word(ALPHANUMS), stopOn=HYPHEN | EOL), joinString=' ', adjacent=False)
setting = TERIOR + CAPS + pp.ZeroOrMore(pp.Optional(HYPHEN + CAPS))

for i, ti in enumerate(t):
	# print(ti)
	print('\tt{}'.format(str(i+1)))
	for result, start, end in setting.scanString(ti):
		print("\t\tFound \"{}\" at [{}:{}]".format(result, start, end))

# test SETTING
# LOC = pp.OneOrMore(HYPHEN + CAPS.copy().addCondition(lambda tokens: is_place(tokens))) + OPT_M
# SETTING = pp.Combine(TERIOR + OPT_H + CAPS.copy().addCondition(lambda tokens: is_place(tokens))
#                      + pp.Optional(LOC), joinString=" ", adjacent=False).setResultsName('Setting')
for i, ti in enumerate(t):
	# print(ti)
	print('\tt{}'.format(str(i + 1)))
	for result, start, end in SETTING.scanString(ti):
		print("\t\tFound \"{}\" at [{}:{}]".format(result, start, end))


# alpha = pp.Or(SCENE | SHOT | SUB | (SHOT_TYPES + OPT_M + OPT_ToD))
for i, ti in enumerate(t):
	# print(ti)
	print('\tt{}'.format(str(i + 1)))
	for result, start, end in alpha.scanString(ti):
		print("\t\tFound \"{}\" at [{}:{}]".format(result, start, end))
