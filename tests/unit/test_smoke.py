"""Teste de fumaça para validação da estrutura hexagonal."""

def test_hexagonal_packages_importable():
    import src.core
    import src.ports
    import src.adapters
    assert src.core is not None
    assert src.ports is not None
    assert src.adapters is not None
