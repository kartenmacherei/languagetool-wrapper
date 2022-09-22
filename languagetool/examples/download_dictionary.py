"""
This script downloads the content of one or more dictionaries to a file.
If no dictionary name is given, the default dictionary is used.
"""

import argparse
import logging
from ..languagetool import LanguageToolDictManager

logging.basicConfig(
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s", level=logging.INFO
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output_file")
    parser.add_argument("--num_words_per_request", type=int, default=100)
    parser.add_argument("--dict_name", nargs="*", dest="dicts")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    lang_tool = LanguageToolDictManager(api_chunk_size=args.num_words_per_request)
    words = lang_tool.list_dictionary_words(limit=args.limit, dict_names=args.dicts)

    with open(args.output_file, "w", encoding="utf8") as output_fp:
        for word in words:
            print(word, file=output_fp)
