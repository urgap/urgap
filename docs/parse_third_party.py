from urgap import UNodeBase

info_collection = []

for cat in UNodeBase.__subclasses__():
    if "test_node" not in str(cat):
        info_collection.append((cat.META_INFO["name"], cat.META_INFO["citation"]))


with open("source/third_party.rst", "w") as f:
    f.write(
        """.. _third party tools:

Third party tools
#################

Here is a list of all tools that are integrated into Urgap2 with proper citations:

"""
    )
    for name, citation in sorted(info_collection):
        f.write(
            f"""{name}
 * {citation}
"""
        )