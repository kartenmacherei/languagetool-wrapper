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
    parser.add_argument("--dict_names", nargs="*", dest="dicts")
    parser.add_argument("--enabled_rules", nargs="*")
    parser.add_argument("--disabled_rules", nargs="*")
    parser.add_argument("--enabled_categories", nargs="*")
    parser.add_argument("--disabled_categories", nargs="*")
    parser.add_argument("--enabled_only", action="store_true")
    args = parser.parse_args()

    logger.info("Using dictionaries %s", str(args.dicts))

    checker = LanguageToolChecker()

    kwargs = {}
    if args.enabled_rules:
        kwargs["enabledRules"] = ",".join(args.enabled_rules)
    if args.disabled_rules:
        kwargs["disabledRules"] = ",".join(args.disabled_rules)
    if args.enabled_categories:
        kwargs["enabledCategories"] = ",".join(args.enabled_categories)
    if args.disabled_categories:
        kwargs["disabledCategories"] = ",".join(args.disabled_categories)
    if args.enabled_only:
        kwargs["enabledOnly"] = "true"

    matches = checker.check_text(
        args.text, args.language, dict_names=args.dicts, **kwargs
    )

    if not matches:
        print("Found no errors!")

    for i, match in enumerate(matches):
        print("=#=", "Error", i, "=#=")
        print(match.message)
        print(match.start, match.end)
        print(match.rule)
        print("Suggestions:", match.replacements)
        print(20 * "=")
