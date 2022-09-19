"""
This script checks the text given on the command line for errors with LanguageTool.
"""

import argparse
import logging
from ..languagetool import LanguageToolChecker

logging.basicConfig(
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    parser.add_argument("language")
    parser.add_argument("--dict_name", nargs="*", dest="dicts")
    args = parser.parse_args()

    logger.info("Using dictionaries %s", str(args.dicts))

    checker = LanguageToolChecker()
    matches = checker.check_text(args.text, args.language, dict_names=args.dicts)

    if not matches:
        print("Found no errors!")

    for i, match in enumerate(matches):
        print("=#=", "Error", i, "=#=")
        print(match.message)
        print(match.start, match.end)
        print(match.rule)
        print("Suggestions:", match.replacements)
        print(20 * "=")
