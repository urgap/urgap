import pytest



def is_tuple(checker, instance):
    return isinstance(instance, tuple)


TupleValidator = validators.extend(
)
reference_schema = {
    "type": "object",
    "maxItems": 12,
    "required": [
        "name",
        "version",
        "release_date",
        "engine_type",
        "wrapper_version",
        "citation",
        "engine",
    ],
    "properties": {
        "name": {"type": "string"},
        "version": {"type": "string"},
        "release_date": {"type": "string"},
        "engine_type": {"type": "tuple"},
        "wrapper_version": {"type": "object"},
        "citation": {"type": "string"},
        "engine": {"type": "object"},
    },
}
tuple_validator = TupleValidator(schema=reference_schema)


def test_meta_info_is_sane(node_name):