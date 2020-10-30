from cnct.help import DefaultFormatter


def test_print_help(
    mocker,
    apiinfo_factory,
    nsinfo_factory,
    colinfo_factory,
    resinfo_factory,
    actinfo_factory,
    opinfo_factory,
):
    formatter = DefaultFormatter()
    formatter.print_api = mocker.MagicMock(return_value='')
    formatter.print_namespace = mocker.MagicMock(return_value='')
    formatter.print_collection = mocker.MagicMock(return_value='')
    formatter.print_resource = mocker.MagicMock(return_value='')
    formatter.print_operation = mocker.MagicMock(return_value='')
    formatter.print_action = mocker.MagicMock(return_value='')

    api = apiinfo_factory()
    formatter.print_help(api)
    formatter.print_api.assert_called_once_with(api)

    ns = nsinfo_factory()
    formatter.print_help(ns)
    formatter.print_namespace.assert_called_once_with(ns)

    col = colinfo_factory()
    formatter.print_help(col)
    formatter.print_collection.assert_called_once_with(col)

    res = resinfo_factory()
    formatter.print_help(res)
    formatter.print_resource.assert_called_once_with(res)

    act = actinfo_factory()
    formatter.print_help(act)
    formatter.print_action.assert_called_once_with(act)

    op = opinfo_factory()
    formatter.print_help(op)
    formatter.print_operation.assert_called_once_with(op)


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


def test_collection(colinfo_factory, resinfo_factory, opinfo_factory):
    col = colinfo_factory(
        name='resources',
        resource_specs=resinfo_factory(),
        operations=[opinfo_factory()]
    )

    formatter = DefaultFormatter()
    help_ = formatter.print_collection(col)
    assert isinstance(help_, str)


def test_resource(colinfo_factory, resinfo_factory, actinfo_factory, opinfo_factory):
    res = resinfo_factory(
        collections=[colinfo_factory(name='nested')],
        actions=[
            actinfo_factory(info=[opinfo_factory()])
        ],
    )

    formatter = DefaultFormatter()
    help_ = formatter.print_resource(res)
    assert isinstance(help_, str)


def test_action(actinfo_factory, opinfo_factory):
    action = actinfo_factory(info=[opinfo_factory()])
    formatter = DefaultFormatter()
    help_ = formatter.print_action(action)
    assert isinstance(help_, str)


def test_operation(opinfo_factory, opdata_factory):
    opinfo = opinfo_factory(name='search', info=opdata_factory())
    formatter = DefaultFormatter()
    help_ = formatter.print_operation(opinfo)
    assert isinstance(help_, str)
