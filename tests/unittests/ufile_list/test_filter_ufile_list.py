from pathlib import Path




    )

    filtered_list = ufl.filter(
    )
    assert filtered_list == [uf]



    )
    )

    filtered_list = ufl.filter(
        },
    )
    assert filtered_list == [uf_1]


def test_filtering_on_two_files_one_excluding_based_on_additional_filters(
):

    )
    )

    filtered_list = ufl.filter(
        additional_filters={
        },
    )
    assert filtered_list == [uf_2]




    filtered_list = ufl.filter(
        },
    )
    assert filtered_list == []



    )

    filtered_list = ufl.filter(
        },
    )
    assert filtered_list == [uf_1]


    ufiles = [
        ),
        ),
        ),
    ]

    filtered_list = ufl.filter(
    )

    assert len(filtered_list) == 3


    ufiles = [
        ),
        ),
        ),
        ),
        ),
    ]

    filtered_list = ufl.filter(
    )

    assert len(filtered_list) == 5


    ufiles = [
        ),
        ),
        ),
        ),
        ),
    ]

    filtered_list = ufl.filter(
        },
    )
    assert len(filtered_list) == 3


def test_wrapper_defintions_are_met_with_additional_filters_nested_structure(
):
    ufiles = [
        ),
        [
            ),
            ),
        ],
        [
            ),
            ),
        ],
    ]

    filtered_list = ufl.filter(
        },
    )
    assert len(filtered_list) == 3


    ufiles = [
        ),
        ),
        ),
        ),
        ),
    ]


    )