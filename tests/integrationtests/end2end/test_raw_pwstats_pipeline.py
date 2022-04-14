#!/usr/bin/env python
import pytest


@pytest.mark.slow
def test_raw_to_pwstats_pipeline():

    # do we need a bigger raw file