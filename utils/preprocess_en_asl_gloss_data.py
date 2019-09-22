#!python
import os, errno

class EnAslTokenizer(object):

	SUBWORD_TOKENS = [
		"'s",
		"n't",
		"'re",
		"'ve",
		"'m",
		"'ll",
		"'d"
	]

	def __init__(self, sep=" ", case_sensitive=False):

		self.case_sensitive = case_sensitive
		self.sep = sep
		self.vocab_dict = None

	def _tokenize_string(self, text):

		# This will let SpaceTokenizer create hyphen tokens
		# There are no space separated hyphens in our corpus,
		# so there's no information loss
		text = text.replace("-", " - ")
		for subword in self.SUBWORD_TOKENS:
			text = text.replace(subword, " " + subword)

		return text.split(self.sep)

	def _detokenize_string(self, tokens):

		# Detokenize custom subwords
		for subword in self.SUBWORD_TOKENS:
			output = output.replace(" " + subword, subword)

		text = text.replace(" - ", "-")

		return self.sep.join(output)

	def fit_to_files(self, filepaths):
		vocab_dict = dict()
		for filepath in filepaths:
			tokens = self.tokenize_file(filepath)
			for sentence in tokens:
				for word in sentence:
					if not self.case_sensitive:
						word = word.lower()
						if word in vocab_dict:
							vocab_dict[word] += 1
						else:
							vocab_dict[word] = 1

		self.vocab_dict = vocab_dict

	def tokenize_file(self, filepath):
		tokens = []
		with open(filepath) as file_obj:
			lines = file_obj.readlines()
			for line in lines:
				tokens.append(self._tokenize_string(line))

		return tokens

	def write_tokenized_file(
		self, from_filepath, to_filepath):

		try:
			os.makedirs(os.path.dirname(to_filepath))
		except FileExistsError:
			# directory already exists
			pass

		tokens = self.tokenize_file(from_filepath)
		with open(to_filepath, "w") as file_obj:
			for token in tokens:
				file_obj.write(self.sep.join(token))

def trim_vocab(embedding_filepath, tokenizer):
	"""
	outputs a new pretrained embedding file with only words
	from vocab dict
	"""

	with open(embedding_filepath) as read_file_obj:
		with open(
			embedding_filepath + ".trimmed", "w"
		) as write_file_obj:
			for line in read_file_obj:
				word = line.split(" ")[0]
				if not tokenizer.case_sensitive:
					word = word.lower()
				if word in tokenizer.vocab_dict:
					write_file_obj.write(line)

def preprocess_embedding(
	tokenizer, train_text_filepaths, embedding_filepath
):

	tokenizer.fit_to_files(train_text_filepaths)
	trim_vocab(embedding_filepath, tokenizer)

def preprocess_text_files(
	tokenizer,
	from_filepaths,
	to_filepaths
):

	for from_filepath, to_filepath in zip(
		from_filepaths, to_filepaths):

		tokenizer.write_tokenized_file(
			from_filepath,
			to_filepath
		)

if __name__ == "__main__":
	import argparse

	def list_str(args):

		return args.split(",")

	parser = argparse.ArgumentParser(
		description='Preprocess corpus files and embeddings'
	)

	parser.add_argument(
		'--embedding_file',
		dest="embedding_file",
		type=str,
		help="filepath of pretrained embedding"
	)

	parser.add_argument(
		'--train_files',
		dest="train_files",
		type=list_str,
		nargs='+',
		help='list of text training files'
	)

	parser.add_argument(
		'--dev_files',
		dest="dev_files",
		type=list_str,
		nargs='+',
		help='list of text dev files'
	)

	parser.add_argument(
		'--test_files',
		dest="test_files",
		type=list_str,
		nargs='+',
		help='list of text test files'
	)
	args = parser.parse_args()
	tokenizer = EnAslTokenizer()
	preprocess_embedding(
		tokenizer,
		args.train_files[0],
		args.embedding_file
	)
	from_filepaths = \
		args.train_files[0] + \
		args.dev_files[0] + \
		args.test_files[0]

	to_filepaths = [
		f.replace("/raw/", "/preprocessed/")
		for f in from_filepaths
	]

	preprocess_text_files(
		tokenizer,
		from_filepaths,
		to_filepaths
	)
