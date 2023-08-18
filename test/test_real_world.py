#!/usr/bin/env python3
import datetime
import pathlib
import pytest
import uuid
import wappstoiot

from typing import Optional

from utils import file_utils

# TODO: Fix this test.
# from wappstoiot.__main__ import _start_session
# from wappstoiot.__main__ import _create_network
# from wappstoiot.__main__ import _claim_network
# from wappstoiot.__main__ import _create_certificaties_files


def pytest_generate_tests(metafunc):
    """Attach the cmd-line args to a test-class that needs them."""
    token = metafunc.config.getoption("token")
    if token and hasattr(metafunc.cls, 'token'):
        metafunc.cls.token = token


class BaseTestClassWithCertificateFiles:
    """Contain the Base functionalities for a test with certificate files."""
    temp: pathlib.Path = pathlib.Path(__file__).parent.parent / pathlib.Path('temp')

    def generate_certificates(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
    ):
        """Generate the needed certificates for a 'real' world test."""
        base_url: str = "qa.wappsto.com"
        if not token:
            session = _start_session(
                base_url=base_url,
                username=username,
                password=password,
            )
        else:
            session = token

        creator = _create_network(
            session=session,
            base_url=base_url,
            dry_run=False
        )
        _claim_network(
            session=session,
            base_url=base_url,
            network_uuid=creator.get('network', {}).get('id'),
            dry_run=False
        )

        self.temp.mkdir(exist_ok=True)

        _create_certificaties_files(self.temp, creator, dry_run=False)


class TestWithOutMocking(BaseTestClassWithCertificateFiles):

    token: Optional[uuid.UUID] = None

    @classmethod
    def setup_class(cls):
        """Setting up all the needed stuff for the test class."""
        if cls.token is None:
            pytest.skip("Token was not given.")
        cls.generate_certificates(cls, token=cls.token)

    @classmethod
    def teardown_class(cls):
        """tearing down all the generated stuff by the setup_class function."""
        file_utils.rm_all(cls.temp)

    @pytest.mark.parametrize(
        "fast_send",
        [
            True,
            False,
        ]
    )
    def test_pytest_usage(self, fast_send: bool):
        # TODO: Hock into the observer, to check for communication error.
        # TODO: Go through the Rest-API to check if value was set.
        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send
            )
            network = wappstoiot.createNetwork("TheNetwork")
            device = network.createDevice("TheDevice")
            value = device.createValue(
                "TheValue",
                permission=wappstoiot.PermissionType.READ,
                value_template=wappstoiot.ValueTemplate.STRING
            )
            value.report(value=5)
            value.report(value=1337, timestamp=datetime.datetime.now())
        finally:
            wappstoiot.close()
