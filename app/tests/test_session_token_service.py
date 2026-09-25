from auth.session_token_service import SessionTokenService


def test_generateToken_returnsUrlSafeString():
    service = SessionTokenService()
    token = service.generateToken()

    assert isinstance(token, str)
    assert len(token) > 0


def test_generateToken_returnsDistinctValues():
    service = SessionTokenService()

    assert service.generateToken() != service.generateToken()


def test_hashToken_isDeterministicSha256Hex():
    service = SessionTokenService()
    token = "example-token"

    first = service.hashToken(token)
    second = service.hashToken(token)

    assert first == second
    assert len(first) == 64
    assert all(character in "0123456789abcdef" for character in first)


def test_hashToken_differsForDifferentTokens():
    service = SessionTokenService()

    assert service.hashToken("a") != service.hashToken("b")
