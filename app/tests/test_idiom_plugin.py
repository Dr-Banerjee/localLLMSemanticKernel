from plugins.idiom_plugin import IdiomPlugin


def test_getIdiomHint_knownIdiom():
    plugin = IdiomPlugin()

    result = plugin.getIdiomHint("Piece Of Cake")

    assert 'Idiom: "piece of cake"' in result
    assert "Meaning:" in result
    assert "Why:" in result
    assert "Example:" in result


def test_getIdiomHint_unknownIdiom():
    plugin = IdiomPlugin()

    result = plugin.getIdiomHint("unknown idiom")

    assert "I don't have information about the idiom 'unknown idiom'." == result
