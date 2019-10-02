#!python
# pylint: disable=redefined-outer-name,unexpected-keyword-arg
from lang2sign.lang2gloss.tokenizers.en_asl import EnAslTokenizer

def preprocess_embedding(
    tokenizer, train_text_filepaths,
    embedding_filepath, min_count=None
):

    tokenizer.fit_to_files(train_text_filepaths, min_count)
    tokenizer.trim_vocab(embedding_filepath)

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
