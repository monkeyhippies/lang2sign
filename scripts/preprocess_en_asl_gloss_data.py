#!python
# pylint: disable=redefined-outer-name,unexpected-keyword-arg
import os

class EnAslTokenizer(object):
    """
    Tokenizer for en-asl translation task
    """
    SUBWORD_TOKENS = [
        "'s",
        "n't",
        "'re",
        "'ve",
        "'m",
        "'ll",
        "'d"
    ]

    WORD_REPLACEMENTS = {
        " refore ": " therefore ",
        " toger ": " together ",
        " strengn ": " strengthen ",
        " russium ": " russia "
    }

    def __init__(self, sep=" ", case_sensitive=False):
        self.case_sensitive = case_sensitive
        self.sep = sep
        self.vocab_dict = None

    def _tokenize_string(self, text):
        """
        This will let SpaceTokenizer create hyphen tokens
        There are no space separated hyphens in our corpus,
        so there's no information loss
        """
        text = text.replace("-", " - ")
        for subword in self.SUBWORD_TOKENS:
            text = text.replace(subword, " " + subword)

        for from_word, to_word in self.WORD_REPLACEMENTS.items():
            text = text.replace(from_word, to_word)

        return text.split(self.sep)

    def _detokenize_string(self, tokens):
        """
        detokenizes tokens
        """
        for from_word, to_word in self.WORD_REPLACEMENTS.items():
            tokens = tokens.replace(to_word, from_word)

        # Detokenize custom subwords
        for subword in self.SUBWORD_TOKENS:
            tokens = tokens.replace(" " + subword, subword)

        tokens = tokens.replace(" - ", "-")

        return self.sep.join(tokens)

    def fit_to_files(self, filepaths, min_count=None):
        """
        Creates vocab_dict from text files specified by @filepaths
        """
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

        if min_count:
            self.vocab_dict = {
                key: value for key, value in \
                vocab_dict.items() if value >= min_count
            }

        else:
            self.vocab_dict = vocab_dict

    def tokenize_file(self, filepath):
        tokens = []
        with open(filepath) as file_obj:
            lines = file_obj.readlines()
            for line in lines:
                if not self.case_sensitive:
                    line = line.lower()
                tokens.append(self._tokenize_string(line))

        return tokens

    def write_tokenized_file(
        self, from_filepath, to_filepath):

        os.makedirs(
			os.path.dirname(to_filepath),
			exist_ok=True
		)

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
        with open(embedding_filepath + ".trimmed.vocab", "w") as vocab_file_obj:
            with open(embedding_filepath + ".trimmed", "w") as write_file_obj:
                for line in read_file_obj:
                    word = line.split(" ")[0]
                    if not tokenizer.case_sensitive:
                        word = word.lower()
                    if word in tokenizer.vocab_dict:
                        write_file_obj.write(line)
                        vocab_file_obj.write(word + "\n")

def preprocess_embedding(
    tokenizer, train_text_filepaths,
    embedding_filepath, min_count=None
):

    tokenizer.fit_to_files(train_text_filepaths, min_count)
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
    def list_str(arguments):
        return arguments.split(",")

    parser = argparse.ArgumentParser(
        description='Preprocess corpus files and embeddings'
    )

    parser.add_argument(
        '--min_vocab_count',
        dest="min_count",
        type=int,
        help="count cutoff for word to be added to vocab"
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
        args.embedding_file,
        args.min_count
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
