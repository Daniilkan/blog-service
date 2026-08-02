import logging

from ninja.security import APIKeyHeader

from .models import AuthToken

logger = logging.getLogger("blog")


class TokenAuth(APIKeyHeader):
    """
    Authenticates requests using the custom 256-char token.

    The token is expected in the `Authorization` header as:
        Authorization: Token <256-char-token>

    As a fallback (per spec: "in the header or body"), the token may also be
    supplied in the JSON body as `token`, which is handled in `authenticate`
    by inspecting the raw request if the header is absent.
    """

    param_name = "Authorization"

    def authenticate(self, request, key):
        token_value = None

        if key:
            # Support both "Token <value>" and a raw token value.
            token_value = key.split(" ")[-1] if key.startswith("Token ") else key

        if not token_value:
            # Fallback: look for a "token" field in the JSON body.
            try:
                import json

                body = json.loads(request.body or b"{}")
                token_value = body.get("token")
            except Exception:
                token_value = None

        if not token_value:
            return None

        try:
            auth_token = AuthToken.objects.select_related("user").get(key=token_value)
        except AuthToken.DoesNotExist:
            logger.warning("Auth failed: invalid token used from %s", request.META.get("REMOTE_ADDR"))
            return None

        if not auth_token.user.is_active:
            logger.warning("Auth failed: inactive user '%s' attempted access", auth_token.user.username)
            return None

        request.auth_user = auth_token.user
        return auth_token.user


token_auth = TokenAuth()
