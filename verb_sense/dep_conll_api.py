from functools import partial
from pycorenlp import StanfordCoreNLP

"""
	Setup stanford corenlp parser to listen at local\9000
"""

def NLP(parser, text, property=None):
	if property is None:
		property = 'conllu'
	elif type(property) is list:
		output_dict = {
			item: parser.annotate(text, properties={'outputFormat': item}) for item in property
		}
		return output_dict
	return parser.annotate(text, properties={'outputFormat': property})

def setup_parser():

	nlp = StanfordCoreNLP('http://localhost:9000')
	return partial(NLP, parser=nlp)

"""
user: import setup_parser and keep in hand. then run on text as in __main__ to receive annotated result
"""

if __name__ == '__main__':
	test_string = 'This is a test of the emergency broadcast system.'
	test2 = "John hits the pan. Then he has a drumstick."
	nlp_parser = setup_parser()
	annotated_result = nlp_parser(text=test2, property=['json', 'conllu'])
	print(annotated_result['conllu'])
	print(annotated_result['json']['corefs'])