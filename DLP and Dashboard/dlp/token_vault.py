import hashlib
import hmac
import secrets
from config import TOKEN_SECRET

class TokenVault:
    """In-memory reversible token map for a single running service instance.
    Do not persist raw secrets in logs; use a managed secret store in production.
    """
    def __init__(self, secret: str = TOKEN_SECRET):
        self.secret = secret.encode()
        self._tokens = {}

    def _digest(self, value: str) -> str:
        return hmac.new(self.secret, value.encode(), hashlib.sha256).hexdigest()[:16]

    def put(self, value: str) -> str:
        token = f"[LLMGUARD_TOKEN:{self._digest(value)}:{secrets.token_hex(4)}]"
        self._tokens[token] = value
        return token

    def get(self, token: str):
        return self._tokens.get(token)

    def unmask(self, text: str) -> str:
        for token, value in list(self._tokens.items()):
            text = text.replace(token, value)
        return text
