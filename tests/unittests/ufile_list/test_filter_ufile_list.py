from pathlib import Path



    )
    assert filtered_list == [uf]




    )
    assert filtered_list == [uf_1]


def test_filtering_on_two_files_one_excluding_based_on_additional_filters(
):


        additional_filters={
        },
    )
    assert filtered_list == [uf_2]




    )
    assert filtered_list == []


    ufiles = [
        ),
        ),
        ),
    ]

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

    assert len(filtered_list) == 5


    ufiles = [
        ),
        ),
        ),
        ),
        ),
    ]

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