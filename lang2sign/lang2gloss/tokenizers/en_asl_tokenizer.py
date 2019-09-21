class EnAslTokenizer(object):

	SUBWORD_TOKENS = [
		"-",
		"'s",
		"n't",
		"'re",
		"'ve",
		"'m",
		"'ll",
		"'d"
	]

	def __init__(self):

		self.vocab_dict = None

	def _tokenize_string(self, text):

		# This will let SpaceTokenizer create hyphen tokens
		# There are no space separated hyphens in our corpus,
		# so there's no information loss
		for subword in self.SUBWORD_TOKENS:
			text = text.replace(subword, " " + subword + " ")

		return text.split()

	def _detokenize_string(self, tokens):

		output = super(
			EnAslTokenizer, self
		)._detokenize_string(tokens)

		# Detokenize custom subwords
		for subword in self.SUBWORD_TOKENS:
			output = output.replace(" - ", "-")

		return " ".join(output)

	def fit_to_files(self, filepaths):
		vocab_dict = dict()
		for filepath in filepaths:
			tokens = self.tokenize_file(filepath)
			for token in tokens:
				if token in vocab_dict:
					vocab_dict[token] += 1
				else:
					vocab_dict[token] = 1

		self.vocab_dict = vocab_dict

	def tokenize_file(self, filepath):

		with open(filepath) as file_obj:
			text = file_obj.read()
			tokens = self._tokenize_string()

		return tokens

	def write_tokenized_file(
		self, from_filepath, to_filepath, sep=" "
	):

		tokens = self.tokenize_file(from_filepath)
		with open(to_filepath, "wb") as file_obj:
			file_obj.write(sep.join(tokens))

def trim_vocab(embedding_filepath, vocab_dict):
	"""
	outputs a new pretrained embedding file with only words
	from vocab dict
	"""

	with open(embedding_filepath) as read_file_obj:
		with open(
			embedding_filepath + "trimmed", "wb"
		) as write_file_obj:
			for line in read_file_obj:
				word = line.split(" ")[0]
				if word in vocab_dict:
					write_file_obj.write(line)

def preprocess_embedding(training_text_filepaths, embedding_filepath):

	tokenizer = EnAslTokenizer()
	tokenizer.fit_to_files(training_text_filepaths)

	trim_vocab(embedding_filepath, tokenizer.vocab_dict)

def if __name__ == "__main__":

	preprocess_embedding(training_text_filepaths, embedding_filepath)
