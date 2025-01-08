import pytest
from jsonschema import validators



def is_tuple(checker, instance):
    return isinstance(instance, tuple)


def is_uftype_specification(checker, instance):
    if isinstance(instance, dict) is False:
        return False
    for uftype, spec in instance.items():
        if isinstance(uftype, str) is False:
            return False
        if {"min", "max"} != spec.keys():
            return False
    return True


type_checker = validators.Draft7Validator.TYPE_CHECKER.redefine_many(
)
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
        "input_uftypes",
        "output_uftypes",
        "citation",
        "engine",
    ],
    "properties": {
        "name": {"type": "string"},
        "version": {"type": "string"},
        "release_date": {"type": "string"},
        "engine_type": {"type": "tuple"},
        "wrapper_version": {"type": "object"},
        "input_uftypes": {"type": "uftype_spec"},
        "output_uftypes": {"type": "uftype_spec"},
        "citation": {"type": "string"},
        "requires": {"type": "object"},
        "engine": {"type": "object"},
    },
}
tuple_validator = TupleValidator(schema=reference_schema)


@pytest.mark.parametrize(
)
def test_meta_info_is_sane(node_name):
        assert tuple_validator.validate(instance=node.META_INFO) is None
    # TODO: create schema for u3