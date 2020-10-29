from cnct.help import DefaultFormatter


def test_api_info(apiinfo_factory):
    api = apiinfo_factory()
    formatter = DefaultFormatter()
    help_ = formatter.print_api(api)
    assert isinstance(help_, str)
