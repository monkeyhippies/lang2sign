#!python
# pylint: disable=redefined-outer-name,unexpected-keyword-arg
from lang2sign.lang2gloss.tokenizers.en_asl import EnAslTokenizer

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Preprocess corpus files and embeddings'
    )

    parser.add_argument(
        '--input-file',
        dest="input_file",
        type=str,
        help="filepath of text to be detokenized"
    )

    args = parser.parse_args()
    output_filepath = args.input_file + ".detok"
    tokenizer = EnAslTokenizer()

    print(
        "Writing detokenized file to {}".format(
            output_filepath
        )
    )
    tokenizer.write_detokenized_file(
        args.input_file,
        output_filepath
    )
