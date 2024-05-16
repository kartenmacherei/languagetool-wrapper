"""
This script takes a single word on the command line and adds it to the specified dictionary.
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
    parser.add_argument("word")
    parser.add_argument("--dict_name")
    parser.add_argument("--remove", action="store_true")
    args = parser.parse_args()

    dict_name_for_log_msg = "default" if args.dict_name is None else args.dict_name

    if args.remove:
        answer = input(
            "WARNING: "
            + f"You are about to remove the word '{args.word}' "
            + f"from '{dict_name_for_log_msg}' dictionary. "
            "Continue? [y/N] ",
        )
        if answer != "y":
            print("Abort")
            sys.exit()

    lang_tool = LanguageToolDictManager()

    if args.remove:
        faulty_words = lang_tool.delete_dictionary_words(
            [args.word], dict_name=args.dict_name
        )
    else:
        faulty_words = lang_tool.add_dictionary_words(
            [args.word], dict_name=args.dict_name
        )

    if faulty_words:
        print(
            f"ERROR: Word '{args.word}' could not be added to '{dict_name_for_log_msg}' dictionary."
        )
    else:
        print(
            f"Successfully added word '{args.word}' to '{dict_name_for_log_msg}' dictionary"
        )
