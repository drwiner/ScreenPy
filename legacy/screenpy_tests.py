from screenpy import *

print('testing SETTING')
t1 = '               EXT. THE JUNGLE - INDY\'S RUN - CLOSE ANGLE - DAY'
t2 = '               Indy disappears into the foliage. PAN TO an instant later, the leaves '
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

for i, ti in enumerate(t):
	print('\tt{}'.format(str(i + 1)))
	for result, start, end in alpha.scanString(ti):
		print("\t\tFound \"{}\" at [{}:{}]".format(result, start, end))
