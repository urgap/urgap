
info_collection = []

for cat in UNodeBase.__subclasses__():
    if "test_node" not in str(cat):
        info_collection.append((cat.META_INFO["name"], cat.META_INFO["citation"]))


with open("source/third_party.rst", "w") as f:

Third party tools


    for name, citation in sorted(info_collection):
 * {citation}