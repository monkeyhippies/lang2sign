#!python
# pylint: disable=redefined-outer-name,unexpected-keyword-arg
"""Script to tokenize text file"""
from lang2sign.lang2gloss.tokenizers.en_asl import EnAslTokenizer

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Detokenize text files"
    )

    parser.add_argument(
        "--input-file",
        dest="input_file",
        type=str,
        help="filepath of text to be detokenized"
    )

    args = parser.parse_args()
    output_filepath = args.input_file + ".tok"
    tokenizer = EnAslTokenizer()

    print(
        "Writing detokenized file to {}".format(
            output_filepath
        )
    )
    tokenizer.write_tokenized_file(
        args.input_file,
        output_filepath
    )
