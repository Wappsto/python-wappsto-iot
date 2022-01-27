#! /usr/bin/env python3

from pathlib import Path

import pytest

import wappstoiot


class TestConnection:
    """
    TestJsonLoadClass instance.

    Tests loading json files in wappsto.

    """

    @classmethod
    def setup_class(self):
        """
        Sets up the class.

        Sets locations to be used in test.

        """
        wappstoiot._DEBUG = True
        wappstoiot.config(
            config_folder=Path("./certificates/"),
        )

        