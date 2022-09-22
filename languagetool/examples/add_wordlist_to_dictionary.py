"""
This script takes a file with one word per line and adds these words to the specified dictionary.
If no dictionary name is specified, the default dictionary is used.
"""

import argparse
import logging
import sys
from ..languagetool import LanguageToolDictManager

logging.basicConfig(
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s", level=logging.INFO
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("word_list_file")
    parser.add_argument("faulty_word_file")
    parser.add_argument("--dict_name")
    parser.add_argument("--remove", action="store_true")
    args = parser.parse_args()

    words = []
    with open(args.word_list_file, encoding="utf8") as input_fp:
        for line in input_fp:
            words.append(line.strip())

    if args.remove:
        dict_name = "default" if args.dict_name is None else args.dict_name
        answer = input(
            f"WARNING: You are about to remove {len(words)} words from '{dict_name}' dictionary."
            " Continue? [y/N] "
        )
        if answer != "y":
            print("Abort")
            sys.exit()

    lang_tool = LanguageToolDictManager()

    if args.remove:
        faulty_words = lang_tool.delete_dictionary_words(
            words, dict_name=args.dict_name
        )
    else:
        faulty_words = lang_tool.add_dictionary_words(words, dict_name=args.dict_name)

    if faulty_words:
        with open(args.faulty_word_file, "w", encoding="utf8") as output_fp:
            for faulty_word in faulty_words:
                print(faulty_word, file=output_fp)
