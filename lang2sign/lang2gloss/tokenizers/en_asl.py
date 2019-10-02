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
        @tokens is a string of tokens
        detokenizes tokens and outputs as a string
        """
        for from_word, to_word in self.WORD_REPLACEMENTS.items():
            tokens = tokens.replace(to_word, from_word)

        # Detokenize custom subwords
        for subword in self.SUBWORD_TOKENS:
            tokens = tokens.replace(" " + subword, subword)

        tokens = tokens.replace(" - ", "-")

        return tokens

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

    def write_detokenized_file(
        self, from_filepath, to_filepath):

        os.makedirs(
            os.path.dirname(to_filepath),
            exist_ok=True
        )

        lines = self.detokenize_file(from_filepath)
        with open(to_filepath, "w") as file_obj:
            for line in lines:
                file_obj.write(line)


    def detokenize_file(self, filepath, capitalize=True):
        """
        detokenize a file line by line. Output is a list
        where each element is a string representation of line
        """
        output_lines = []
        with open(filepath) as file_obj:
            lines = file_obj.readlines()
            for line in lines:
                line = self._detokenize_string(line)
                if capitalize:
                    line = line.upper()
                output_lines.append(line)

        return output_lines

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

    def trim_vocab(self, embedding_filepath):
        """
        outputs a new pretrained embedding file with only words
        from vocab dict
        """

        with open(embedding_filepath) as read_file_obj:
            with open(embedding_filepath + ".trimmed.vocab", "w") as vocab_file_obj:
                with open(embedding_filepath + ".trimmed", "w") as write_file_obj:
                    for line in read_file_obj:
                        word = line.split(" ")[0]
                        if not self.case_sensitive:
                            word = word.lower()
                        if word in self.vocab_dict:
                            write_file_obj.write(line)
                            vocab_file_obj.write(word + "\n")
