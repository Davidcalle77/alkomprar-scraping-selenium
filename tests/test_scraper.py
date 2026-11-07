from scraper.precios import a_numero


def test_a_numero_valido():
    """Verifica que el texto de un precio se convierta correctamente a entero."""
    assert a_numero("$1.079.050") == 1079050
    assert a_numero("$1.499.050") == 1499050


def test_a_numero_nulo():
    """Verifica que valores vacíos o nulos retornen None."""
    assert a_numero(None) is None
    assert a_numero("") is None
