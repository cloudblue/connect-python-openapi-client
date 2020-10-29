from cnct.help import DefaultFormatter


def test_api_info(apiinfo_factory, nsinfo_factory, colinfo_factory, resinfo_factory):
    api = apiinfo_factory(
        collections=[colinfo_factory(name='resources', resource_specs=resinfo_factory())],
        namespaces=[
            nsinfo_factory(
                collections=[
                    colinfo_factory(
                        name='namespaced-resources',
                        resource_specs=resinfo_factory()
                    )
                ],
            )
        ],
    )
    formatter = DefaultFormatter()
    help_ = formatter.print_api(api)
    assert isinstance(help_, str)


def test_ns(nsinfo_factory, colinfo_factory, resinfo_factory):
    ns = nsinfo_factory(
        collections=[
            colinfo_factory(
                name='namespaced-resources',
                resource_specs=resinfo_factory()
            )
        ],
    )
    formatter = DefaultFormatter()
    help_ = formatter.print_namespace(ns)
    assert isinstance(help_, str)


def test_collection(colinfo_factory, resinfo_factory):
    col = colinfo_factory(
        name='resources',
        resource_specs=resinfo_factory()
    )

    formatter = DefaultFormatter()
    help_ = formatter.print_collection(col)
    assert isinstance(help_, str)