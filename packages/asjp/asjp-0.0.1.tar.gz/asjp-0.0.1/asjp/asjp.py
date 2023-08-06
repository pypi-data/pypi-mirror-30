import os.path
import unicodedata

from ipatok.ipa import is_letter, is_tie_bar, replace_substitutes
from ipatok.tokens import normalise
from ipatok import tokenise as tokenise_ipa



"""
Paths to the asjp/data dir and the chart file located there.
"""
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CHART_FILE = os.path.join(DATA_DIR, 'chart')



class Chart:
	"""
	Object that loads and stores the data from the chart file.
	"""

	def __init__(self):
		"""
		Init the instance's properties: a dict mapping IPA symbols to their
		ASJP counterparts and three dicts for the reverse mapping.
		"""
		self.ipa = {}

		self.asjp_letters = {}
		self.asjp_diacritics = {}
		self.asjp_juxta_letters = {}

	def load(self, path):
		"""
		Populate the instance's properties. The data is expected to be read
		from a file which is parsed as follows:

		- empty lines and lines starting with # are ignored;
		- content lines should consist of tab-separated sub-strings, the first
		  being an IPA symbol, the second its ASJP counterpart, the (optional)
		  third a marker;
		- the marker ✓ indicates that the IPA symbol is also the ASJP's
		  counterpart for the purposes of asjp2ipa conversion;
		- the marker + indicates that the second symbol is an ASJP diacritic;
		- the marker = indicates that the correspondence only applies in the
		  context of an ASJP juxtaposition;
		"""
		with open(path, encoding='utf-8') as f:
			for line in map(lambda x: x.strip(), f):
				if not line or line.startswith('#'):
					continue

				line = line.split('\t')

				if len(line) == 2:
					ipa_symbol, asjp_symbol = line
					flag = ''
				elif len(line) == 3:
					ipa_symbol, asjp_symbol, flag = line
				else:
					continue

				self.ipa[ipa_symbol.replace('ə͡'[1], '')] = asjp_symbol

				if flag == '✓':
					self.asjp_letters[asjp_symbol] = ipa_symbol
				elif flag == '+':
					self.asjp_diacritics[asjp_symbol] = ipa_symbol
				elif flag == '=':
					self.asjp_juxta_letters[asjp_symbol] = ipa_symbol


def convert_ipa_token(token):
	"""
	Convert an IPA token into an ASJP token or raise (Assertion|Index)Error if
	the input does not constitute a valid IPA token.

	Helper for ipa2asjp(ipa_seq).
	"""
	output = []
	has_tie_bar = False

	for char in token:
		if is_letter(char):
			if has_tie_bar:
				affricate = output[-1] + char
				if affricate in chart.ipa:
					output[-1] = chart.ipa[affricate]
				has_tie_bar = False
			else:
				for asjp_char in chart.ipa[char]:
					output.append(asjp_char)

		elif is_tie_bar(char):
			has_tie_bar = True

		elif char == 'n̪'[1] and output[-1] == 'n':
			output[-1] = chart.ipa['n̪']

		elif char in chart.ipa:
			asjp_char = chart.ipa[char]
			if asjp_char in chart.asjp_diacritics:
				output[-1] += asjp_char
			else:
				output.append(asjp_char)

	assert 1 <= len(output) <= 3

	if len(output) != 1:
		output.append('~' if len(output) == 2 else '$')

	return ''.join(output)


def ipa2asjp(ipa_seq):
	"""
	Convert an IPA sequence (string or list) into an ASJP sequence of the same
	type. Raise ValueError if the input is not a valid IPA sequence and raise
	TypeError if it is not a sequence. Usage:

	>>> ipa2asjp('zɛmʲa')
	'zEmy~a'
	>>> ipa2asjp(['z', 'ɛ', 'mʲ', 'a'])
	['z', 'E', 'my~', 'a']

	Part of the package's public API.
	"""
	if isinstance(ipa_seq, str):
		output = []

		for ipa_word in ipa_seq.strip().split():
			try:
				output.append(''.join([
					convert_ipa_token(token)
					for token in tokenise_ipa(ipa_word, replace=True)]))
			except (AssertionError, IndexError):
				raise ValueError('invalid IPA word: {}'.format(ipa_word))

		return ' '.join(output)

	else:
		output = []

		for token in ipa_seq:
			token = replace_substitutes(normalise(token))

			try:
				output.append(convert_ipa_token(token))
			except (AssertionError, IndexError):
				raise ValueError('invalid IPA token: {}'.format(token))

		return output


def convert_asjp_token(token):
	"""
	Convert an ASJP token into an IPA token or raise (Assertion|Key)Error if
	the input does not constitute a valid ASJP token.

	Helper for asjp2ipa(asjp_seq).
	"""
	juxtaposed = False
	output = ''

	if token[-1] in '~$':
		juxtaposed = True
		token = token[:-1]
		token = token.replace('Sx', 'ɧ')

	for char in token:
		if juxtaposed and char in chart.asjp_juxta_letters:
			output += chart.asjp_juxta_letters[char]
		elif char in chart.asjp_diacritics:
			output += chart.asjp_diacritics[char]
		elif char == 'ɧ':
			output += char
		else:
			output += chart.asjp_letters[char]

	return output


def asjp2ipa(asjp_seq):
	"""
	Convert an ASJP sequence (string or list) into an IPA sequence of the same
	type. Raise ValueError if the input is not a valid ASJP sequence and raise
	TypeError if it is not a sequence. Usage:

	>>> asjp2ipa('zEmy~a')
	'zɛmʲa'
	>>> asjp2ipa(tokenise('zEmy~a'))
	['z', 'ɛ', 'mʲ', 'a']

	Part of the package's public API.
	"""
	if isinstance(asjp_seq, str):
		output = []

		for asjp_word in asjp_seq.strip().split():
			try:
				output.append(''.join([
					convert_asjp_token(token) for token in tokenise(asjp_word)]))
			except (AssertionError, KeyError):
				raise ValueError('invalid ASJP word: {}'.format(asjp_word))

		return ' '.join(output)

	else:
		output = []

		for token in asjp_seq:
			try:
				output.append(convert_asjp_token(token))
			except (AssertionError, KeyError):
				raise ValueError('invalid ASJP token: {}'.format(token))

		return output


def tokenise_word(string):
	"""
	Tokenise an ASJP string into a list of tokens or raise ValueError if it
	cannot be unambiguously tokenised. The string is assumed to comprise a
	single word, i.e. it should not contain whitespace chars.

	Helper for tokenise(string).
	"""
	tokens = []

	for ix, char in enumerate(string):
		if char in '~$':
			try:
				for _ in range(1 if char == '~' else 2):
					last_token = tokens.pop()
					tokens[-1] += last_token
				tokens[-1] += char
			except IndexError:
				raise ValueError('ambiguous usage of {} ({})'.format(char, unicodedata.name(char)))

		elif char in '"*':
			try:
				tokens[-1] += char
			except IndexError:
				raise ValueError('word-initial {} ({})'.format(char, unicodedata.name(char)))

		elif char in chart.asjp_letters:
			tokens.append(char)

		else:
			raise ValueError('unknown symbol {} ({})'.format(char, unicodedata.name(char)))

	return tokens


def tokenise(string):
	"""
	Tokenise an ASJP string into a list of tokens. Raise ValueError if it
	cannot be unambiguously tokenised and raise TypeError if it is not a
	string. The input may consist of several words, i.e. whitespace-separated
	sub-strings. Usage:

	>>> tokenise('nova zEmy~a')
	['n', 'o', 'v', 'a', 'z', 'E', 'my~', 'a']

	Part of the package's public API.
	"""
	if not isinstance(string, str):
		raise TypeError('string expected')

	words = string.split()
	output = []

	for word in words:
		try:
			output.extend(tokenise_word(word))
		except ValueError as err:
			raise ValueError('cannot tokenise {}: {!s}'.format(word, err))

	return output


"""
Provide for the alternative spelling.
"""
tokenize = tokenise


"""
Load the chart
"""
chart = Chart()
chart.load(CHART_FILE)
