"""This module holds the python code wrapped around the LanguageTool API."""

from typing import Any, Iterable, Mapping, Optional, Sequence
import requests
import urllib.parse
import os
import logging
import posixpath

from languagetool.data import LTContext, LTMatch, LTRule


logger = logging.getLogger(__name__)

HTTP_POST_METHOD = "POST"
HTTP_GET_METHOD = "GET"


def _send_to_api(method: str, api_url: str, data: Mapping[str, Any]) -> Any:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    req = requests.Request(method=method, url=api_url, headers=headers, data=data)
    prepared = req.prepare()

    session = requests.Session()
    response = session.send(prepared)

    if response.status_code != 200:
        logger.error(
            "Language Tool Error: Response Code %s / Message %s",
            response.status_code,
            response.text,
        )
        raise ValueError(
            f"Unsuccessful LT API Call {response.status_code}: {response.text}"
        )
    return response.json()


def _get_optional_arg_value(
    arg: Optional[str],
    env_var_name: str,
    all_none_msg: Optional[str] = None,
    env_var_msg: Optional[str] = None,
) -> Optional[str]:
    res = arg
    if res is None:
        res = os.environ.get(env_var_name, default=None)
        if res is None:
            if all_none_msg:
                logger.info(all_none_msg)
        else:
            if env_var_msg:
                logger.info(env_var_msg)
    return res


class LanguageToolAbstract:
    """
    This class contains the code common to all interactions with the LanguageTool API.
    """

    NO_PREMIUM_MSG = "Calling LanguageTool API without premium key"

    # API key names
    OFFSET_KEY = "offset"
    USERNAME_KEY = "username"
    APIKEY_KEY = "apiKey"
    DICTS_KEY = "dicts"

    def __init__(
        self,
        username: Optional[str] = None,
        api_key: Optional[str] = None,
        basic_url: Optional[str] = None,
    ) -> None:
        self.username = _get_optional_arg_value(
            username,
            "LT_USERNAME",
            env_var_msg="Using LanguageTool username from environment variable",
        )
        self.api_key = _get_optional_arg_value(
            api_key,
            "LT_API_KEY",
            env_var_msg="Using API key from environment variable",
        )
        self.basic_url = (
            "https://api.languagetoolplus.com/v2/" if basic_url is None else basic_url
        )

        self.use_premium = not (self.username is None or self.api_key is None)
        if not self.use_premium:
            logger.info(self.NO_PREMIUM_MSG)

    def _make_data_premium(self, data_dict: dict[str, Any]):
        if self.use_premium:
            data_dict[self.USERNAME_KEY] = self.username
            data_dict[self.APIKEY_KEY] = self.api_key


class LanguageToolDictManager(LanguageToolAbstract):
    """
    This class handles the interaction with LanguageTool dictionaries.
    """

    # API keys
    LIMIT_KEY = "limit"
    DICT_KEY = "dict"
    WORD_KEY = "word"
    WORDS_KEY = "words"
    IS_ADDED_KEY = "added"
    IS_DELETED_KEY = "deleted"

    def __init__(
        self,
        username: Optional[str] = None,
        api_key: Optional[str] = None,
        basic_url: Optional[str] = None,
        api_chunk_size: int = 100,
    ) -> None:
        super().__init__(username=username, api_key=api_key, basic_url=basic_url)
        self.api_chunk_size = api_chunk_size

        self.get_words_url = posixpath.join(self.basic_url, "words")
        self.add_words_url = posixpath.join(self.get_words_url, "add")
        self.delete_words_url = posixpath.join(self.get_words_url, "delete")

    def _dict_words_helper(
        self, offset: int, limit: int, dict_names: Optional[Sequence[str]] = None
    ) -> list[str]:
        data: dict[str, Any] = {
            self.OFFSET_KEY: offset,
            self.LIMIT_KEY: limit,
        }
        self._make_data_premium(data)
        if dict_names:
            data[self.DICTS_KEY] = ",".join(dict_names)

        encoded_data = urllib.parse.urlencode(data)
        json_response = _send_to_api(
            HTTP_GET_METHOD, self.get_words_url + "?" + encoded_data, {}
        )
        return json_response[self.WORDS_KEY]

    def list_dictionary_words(
        self, limit: Optional[int] = None, dict_names: Optional[Sequence[str]] = None
    ) -> list[str]:
        """
        Downloads up to `limit` words from the given dictionaries.
        Without a limit, everything is downloaded.
        If no dictionary names are given, the special default dictionary is used.
        """

        res: list[str] = []
        offset = 0
        logger.info("Start downloading dictionary words from %s", str(dict_names))
        while limit is None or offset < limit:
            new_words = self._dict_words_helper(offset, self.api_chunk_size, dict_names)
            offset += len(new_words)
            logger.info("Downloaded %i words in total", offset)
            res.extend(new_words)
            if len(new_words) < self.api_chunk_size:
                break
        logger.info("Finished downloading")
        return res

    def _single_word_helper(
        self, is_add_action: bool, word: str, dict_name: Optional[str] = None
    ) -> bool:
        url = self.add_words_url if is_add_action else self.delete_words_url
        result_key = self.IS_ADDED_KEY if is_add_action else self.IS_DELETED_KEY

        data = {self.WORD_KEY: word}
        self._make_data_premium(data)
        if dict_name:
            data[self.DICT_KEY] = dict_name

        json_response = _send_to_api(HTTP_POST_METHOD, url, data)
        return json_response[result_key]

    def _multiple_words_helper(
        self, is_add_action: bool, words: Iterable[str], dict_name: Optional[str]
    ) -> list[str]:
        words_that_could_not_be_processed: list[str] = []
        dict_name_for_logging = "default dictionary" if dict_name is None else dict_name
        action_for_logging = "added to" if is_add_action else "removed from"
        for i, word in enumerate(words, start=1):
            is_successful = self._single_word_helper(
                is_add_action, word, dict_name=dict_name
            )
            if not is_successful:
                words_that_could_not_be_processed.append(word)
                logger.warning(
                    "Word %s could not be %s %s",
                    word,
                    action_for_logging,
                    dict_name_for_logging,
                )
            else:
                logger.info(
                    "#%i : Word %s was %s %s",
                    i,
                    word,
                    action_for_logging,
                    dict_name_for_logging,
                )
        return words_that_could_not_be_processed

    def delete_dictionary_words(
        self, words: Iterable[str], dict_name: Optional[str]
    ) -> list[str]:
        """
        Deletes `words` from the given dictionary (`dict_name`).
        Returns the list of words that could not be deleted, i.e.,
        an empty list means everything went fine.
        If no dictionary is given, the words will be deleted from
        the special default dictionary.
        """
        return self._multiple_words_helper(False, words, dict_name=dict_name)

    def add_dictionary_words(
        self, words: Iterable[str], dict_name: Optional[str]
    ) -> list[str]:
        """
        Adds `words` to the given dictionary (`dict_name`).
        Returns the list of words that could not be added, i.e.,
        an empty list means everything went fine.
        If no dictionary is given, the words will be added to the special
        default dictionary.
        """
        return self._multiple_words_helper(True, words, dict_name=dict_name)


class LanguageToolChecker(LanguageToolAbstract):
    """
    This class handles LanguageTool API interactions concerning text check.
    """

    # API keys
    TEXT_KEY = "text"
    LANGUAGE_KEY = "language"
    MATCHES_KEY = "matches"
    RULE_KEY = "rule"
    ID_KEY = "id"
    DESCRIPTION_KEY = "description"
    VALUE_KEY = "value"
    ISSUE_TYPE_KEY = "issueType"
    CATEGORY_KEY = "category"
    NAME_KEY = "name"
    LENGTH_KEY = "length"
    REPLACEMENTS_KEY = "replacements"
    MESSAGE_KEY = "message"
    SHORT_MESSAGE_KEY = "shortMessage"
    CONTEXT_KEY = "context"

    def __init__(
        self,
        username: Optional[str] = None,
        api_key: Optional[str] = None,
        basic_url: Optional[str] = None,
    ) -> None:
        super().__init__(username, api_key, basic_url)
        self.check_text_url = posixpath.join(self.basic_url, "check")

    def check_text(
        self,
        text: str,
        language: str,
        dict_names: Optional[Sequence[str]] = None,
        **kwargs,
    ) -> list[LTMatch]:
        data = {self.TEXT_KEY: text, self.LANGUAGE_KEY: language}
        self._make_data_premium(data)
        if dict_names:
            data[self.DICTS_KEY] = ",".join(dict_names)
        data.update(kwargs)

        json_response = _send_to_api(HTTP_POST_METHOD, self.check_text_url, data)
        matches = []
        for json_match in json_response[self.MATCHES_KEY]:
            json_rule = json_match[self.RULE_KEY]
            rule = LTRule(
                json_rule[self.ID_KEY],
                json_rule[self.DESCRIPTION_KEY],
                json_rule[self.ISSUE_TYPE_KEY],
                (
                    json_rule[self.CATEGORY_KEY][self.ID_KEY],
                    json_rule[self.CATEGORY_KEY][self.NAME_KEY],
                ),
            )
            context = LTContext(
                json_match[self.CONTEXT_KEY][self.TEXT_KEY],
                json_match[self.CONTEXT_KEY][self.OFFSET_KEY],
                json_match[self.CONTEXT_KEY][self.LENGTH_KEY],
            )

            match = LTMatch(
                rule,
                json_match[self.OFFSET_KEY],
                json_match[self.OFFSET_KEY] + json_match[self.LENGTH_KEY],
                tuple(
                    json_repl[self.VALUE_KEY]
                    for json_repl in json_match[self.REPLACEMENTS_KEY]
                ),
                json_match[self.MESSAGE_KEY],
                json_match[self.SHORT_MESSAGE_KEY],
                context,
            )
            matches.append(match)
        return matches
