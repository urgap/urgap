from pathlib import Path

import pytest



def test_folder_has_uparam_signature():
    folder_with_md5 = Path("./prefix_9e124250617146fdf18f38070f6d4440/")

    nonsense = Path("./prefix_random_32372936127fasdf3/")


def test_folder_has_uparam_signature_not_md5(change_hash_algorithm):
    _ = change_hash_algorithm
    folder_with_argon2 = Path("./prefix_874b8bb7d98ec8b277c51c711902da5c/")
    with pytest.raises(NotImplementedError):