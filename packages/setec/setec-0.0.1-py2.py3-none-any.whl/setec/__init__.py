# Copyright 2018 by Kurt Griffiths
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from base64 import b64decode, b64encode

import msgpack
import nacl.encoding
import nacl.secret
import nacl.signing
import nacl.utils


class Signer(object):
    """Message signer based on Ed25519 and nacl.signing.

    Arguments:
        key (str): Base64-encoded key obtained from keygen()
    """

    __slots__ = ('_signing_key',)

    def __init__(self, skey):
        self._signing_key = nacl.signing.SigningKey(skey, nacl.encoding.Base64Encoder)

    @staticmethod
    def keygen():
        signing_key = nacl.signing.SigningKey.generate()

        return (
            signing_key.encode(nacl.encoding.Base64Encoder).decode(),
            signing_key.verify_key.encode(nacl.encoding.Base64Encoder).decode(),
        )

    @staticmethod
    def vkey(skey):
        signing_key = nacl.signing.SigningKey(skey, nacl.encoding.Base64Encoder)
        return signing_key.verify_key.encode(nacl.encoding.Base64Encoder)

    def signb(self, message):
        """Sign a binary message with its signature attached.

        Arguments:
            message(bytes): Data to sign.

        Returns:
            bytes: Signed message
        """
        return self._signing_key.sign(message)

    def pack(self, doc):
        return b64encode(self.packb(doc)).decode()

    def packb(self, doc):
        packed = msgpack.packb(doc, encoding='utf-8', use_bin_type=True)
        return self.signb(packed)


class Verifier(object):
    """Signature verifier based on Ed25519 and nacl.signing.

    Arguments:
        key (str): Base64-encoded verify key
    """

    __slots__ = ('_verify_key',)

    def __init__(self, vkey):
        self._verify_key = nacl.signing.VerifyKey(vkey, nacl.encoding.Base64Encoder)

    def verifyb(self, message):
        """Verify a signed binary message.

        Arguments:
            message(bytes): Data to verify.

        Returns:
            bytes: The orignal message, sans signature.
        """
        return self._verify_key.verify(message)

    def unpack(self, packed):
        return self.unpackb(b64decode(packed))

    def unpackb(self, packed):
        packed = self.verifyb(packed)
        return msgpack.unpackb(packed, encoding='utf-8')


class BlackBox(object):
    """Encryption engine based on PyNaCl's SecretBox (Salsa20/Poly1305).

    Warning per the SecretBox docs:

        Once you’ve decrypted the message you’ve demonstrated the ability to
        create arbitrary valid messages, so messages you send are repudiable.
        For non-repudiable messages, sign them after encryption.

        (See also: https://pynacl.readthedocs.io/en/stable/signing)

    Arguments:
        key (str): Base64-encoded key obtained from keygen()
    """

    __slots__ = ('_box',)

    def __init__(self, key):
        self._box = nacl.secret.SecretBox(b64decode(key))

    @staticmethod
    def keygen():
        return b64encode(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)).decode()

    def encrypt(self, doc, signer=None):
        """Serialize and encrypt a document to Base64-encoded ciphertext.

        Arguments:
            doc: The string, dict, array, or other JSON-compatible
                object to serialize and encrypt.

        Keyword Arguments:
            signer: An instance of Signer to use in signing the result. If
                not provided, the ciphertext is not signed.

        Returns:
            str: Ciphertext
        """

        data = msgpack.packb(doc, encoding='utf-8', use_bin_type=True)

        ciphertext = self._box.encrypt(data)
        if signer:
            ciphertext = signer.signb(ciphertext)

        return b64encode(ciphertext).decode()

    def decrypt(self, ciphertext, verifier=None):
        """Unpack Base64-encoded ciphertext.

        Arguments:
            ciphertext (bytes): Ciphertext to decrypt and deserialize.

        Keyword Arguments:
            verifier: An instance of Verifier to use in verifying the
                signed ciphertext. If not provided, the ciphertext is
                assumed to be unsigned.

        Returns:
            doc: Deserialized JSON-compatible object.
        """

        ciphertext = b64decode(ciphertext)
        if verifier:
            ciphertext = verifier.verifyb(ciphertext)

        data = self._box.decrypt(ciphertext)
        return msgpack.unpackb(data, encoding='utf-8')
