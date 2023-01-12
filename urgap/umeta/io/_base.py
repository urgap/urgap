from copy import deepcopy


class UMetaIOBase:
    """UMetaIO Base Class.

    """



        Args:

        Note:

        Returns:
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            setattr(result, k, deepcopy(v, memo))
        return result






        Args:

        Returns:
        """


        Args:

        Returns:
        """
