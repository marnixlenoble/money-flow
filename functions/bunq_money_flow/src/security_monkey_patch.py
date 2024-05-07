import base64

from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey.RSA import RsaKey
from Cryptodome.Signature import PKCS1_v1_5
from bunq.sdk.security.security import _HEADER_SERVER_SIGNATURE
from requests.structures import CaseInsensitiveDict


def is_valid_response_body(
    public_key_server: RsaKey, body_bytes: bytes, headers: CaseInsensitiveDict[str, str]
) -> bool:
    signer = PKCS1_v1_5.new(public_key_server)
    digest = SHA256.new()
    digest.update(body_bytes)

    try:
        signer.verify(digest, base64.b64decode(headers[_HEADER_SERVER_SIGNATURE]))

        return True
    except ValueError:
        return False
