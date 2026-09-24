from token_vault import TokenVault

def test_token_roundtrip():
    v=TokenVault("test-secret")
    token=v.put("alice@example.com")
    assert token != "alice@example.com"
    assert v.unmask(token) == "alice@example.com"
