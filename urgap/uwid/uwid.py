"""UWIDGenerator class of urgap."""

import secrets

from collections.abc import Iterator
from pathlib import Path

# https://github.com/moby/moby/blob/master/pkg/namesgenerator/names-generator.go
# ^--- too look at ...


class UWIDGenerator:
    """Urgap workflow ID (WID) generator.

    Workflow IDs or WIDs are a central theme in urgap to register
    nodes that were executed as part of one pipeline.

    Scratch folders for UFiles are based on WIDs.

    All issued WIDs are captured in self.issued_wids and those
    folders are removed after interpreter exits.
    """

    def __init__(self) -> None:
        """Initialize a new WIDGenerator object using knowledgebase word lists.

        Word lists are loaded for different types (nouns, verbs, adjectives, etc.)
        and used to generate memorable workflow IDs.

        Already used WIDs are stored in the 'issued_wids' attribute.
        """
        self.nouns = self._read_word_file("nouns.txt")
        self.verbs = self._read_word_file("verbs_3rd_form.txt")
        self.adjectives = self._read_word_file("adjectives.txt")
        self.adverbs = self._read_word_file("adverbs.txt")
        self.prepositions = self._read_word_file("prepositions.txt")
        self.indefinitpronomen = self._read_word_file("indefinitpronomen.txt")
        self.issued_wids = []

    def _read_word_file(self, word_type: str) -> list:
        """Read a word list from a file.

        Args:
            word_type: Name of the word type file (e.g., "nouns.txt").

        Returns:
            List of words (str) from the file.
        """
        word_file = Path(__file__).parent / f"{word_type}"
        with word_file.open() as wf:
            return [line.strip() for line in wf]

    @property
    def n(self) -> int:
        """Get the number of possible unique WID combinations.

        Returns:
            Number of possible combinations as an integer.
        """
        n_nouns = len(self.nouns)
        n_adj = len(self.adjectives)
        n_verbs = len(self.verbs)
        return n_adj * n_nouns * n_verbs * n_adj * n_nouns

    def __iter__(self) -> Iterator[str]:
        """Return self as an iterator for generating WIDs.

        Returns:
            Iterator over WID strings.
        """
        return self

    def __next__(self) -> str:
        """Generate a new WID when iterating.

        Returns:
            New WID string.
        """
        return self.generate_wid()

    def generate_wid(self) -> str:
        """Generate a new WID using the loaded word lists.

        Returns:
            Generated WID string in the format:
            "u_<adjective>_<noun>_<verb>_<adjective>_<noun>"
        """
        noun_a = secrets.choice(self.nouns)
        noun_b = secrets.choice(self.nouns)
        adjective_a = secrets.choice(self.adjectives)
        adjective_b = secrets.choice(self.adjectives)
        verbs = secrets.choice(self.verbs)
        new_wid = f"u_{adjective_a}_{noun_a}_{verbs}_{adjective_b}_{noun_b}"
        self.issued_wids.append(new_wid)
        return new_wid
