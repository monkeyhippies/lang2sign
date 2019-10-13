#!python
# pylint: disable=redefined-outer-name,unexpected-keyword-arg
"""Script to detokenize text file""" 
from lang2sign.lang2gloss.tokenizers.en_asl import EnAslTokenizer

def clean_text(text):
    # WOULD LIKE -> WANT
    removed_words = set([".", ",", "?", "BE", "TO", "MR"]) # These arent ASL gloss terms

    # There are some ASL gloss convention mismatches between ASLLVD and ASLG-PC12
    replacement_mapping = {
        "X-I": "IX-1p",
        "X-WE": "IX-1p-pl-arc",
        "X-IT": "IX:i",
        "X-HE": "IX:i",
        "X-YOU": "IX-2p",
        "X-Y": "IX-2p", # X-Y is you in the general sense so this might not be good
        "THIS": "IX:i",
        "EU": "ns-EUROPE",
        "EUROPE": "ns-EUROPE",
        "EUROPEAN": "ns-EUROPE",# This might not be right to assume
        "WILL": "FUTURE",
        "NEED": "SHOULD",
        "DESC-NOT": "NOT",
        "DESC-ALSO": "ALSO"
    }

    # Remopve all DESC- from terms
    words = text.split()
    words = [word for word in words if word not in removed_words]
    words = [word if word not in replacement_mapping else replacement_mapping[word] for word in words]
    words = [word if not word.startswith("DESC-") else word[5:] for word in words]

    return " ".join(words)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean gloss output of transformer"
    )

    parser.add_argument(
        "--input-file",
        dest="input_file",
        type=str,
        help="filepath of text to be detokenized"
    )

    parser.add_argument(
        "--output-file",
        dest="output_file",
        type=str,
        help="filepath of text to be detokenized"
    )


    args = parser.parse_args()
    tokenizer = EnAslTokenizer()

    text = tokenizer.detokenize_file(
        args.input_file,
    )

    text = clean_text(text)

    with open(args.output_file, "w") as file_obj:
        file_obj.write(text)
