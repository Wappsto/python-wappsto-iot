import uuid


def pytest_addoption(parser):
    parser.addoption(
        "--token",
        type=uuid.UUID,
        default=None,
        help="The QA-token used to make the 'real world' test."
    )
