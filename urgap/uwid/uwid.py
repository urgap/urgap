
import secrets


# https://github.com/moby/moby/blob/master/pkg/namesgenerator/names-generator.go
# ^--- too look at ...


class UWIDGenerator:



    All issued WIDs are captured in self.issued_wids and those
    """


        """
        self.nouns = self._read_word_file("nouns.txt")
        self.verbs = self._read_word_file("verbs_3rd_form.txt")
        self.adjectives = self._read_word_file("adjectives.txt")
        self.adverbs = self._read_word_file("adverbs.txt")
        self.prepositions = self._read_word_file("prepositions.txt")
        self.indefinitpronomen = self._read_word_file("indefinitpronomen.txt")
        self.issued_wids = []

        word_file = Path(__file__).parent / f"{word_type}"

    @property
    def n(self) -> int:

        Returns:
        """
        n_nouns = len(self.nouns)
        n_adj = len(self.adjectives)
        n_verbs = len(self.verbs)
        return n_adj * n_nouns * n_verbs * n_adj * n_nouns


        Returns:
        """
        return self


        Returns:
        """
        return self.generate_wid()

    def generate_wid(self) -> str:

        Returns:
        """
        noun_a = secrets.choice(self.nouns)
        noun_b = secrets.choice(self.nouns)
        adjective_a = secrets.choice(self.adjectives)
        adjective_b = secrets.choice(self.adjectives)
        verbs = secrets.choice(self.verbs)
        self.issued_wids.append(new_wid)
        return new_wid