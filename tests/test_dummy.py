def test_placeholder():
    assert True


def test_vault_import():
    import vault

    assert hasattr(vault, "__file__")
