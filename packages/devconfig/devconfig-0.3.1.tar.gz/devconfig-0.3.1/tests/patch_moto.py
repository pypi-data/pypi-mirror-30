import warnings
import moto.kms.models
import moto.kms.responses
import boto.kms
import json
import os
import random
import base64


kms_backends = {}
class KmsResponse(object):
    @property
    def kms_backend(self):
        return kms_backends[self.region]

    def generate_data_key(self):
        key_id = self.parameters.get('KeyId')
        encryption_context = self.parameters.get('EncryptionContext')
        number_of_bytes = self.parameters.get('NumberOfBytes')
        if r'alias/' in str(key_id).lower():
            key_id = self.kms_backend.get_key_id_from_alias(key_id.split('alias/')[1])
        moto.kms.responses._assert_valid_key_id(self.kms_backend.get_key_id(key_id))
        data_key = self.kms_backend.generate_data_key(key_id, encryption_context, number_of_bytes)
        return json.dumps({
                    'Plaintext': data_key.decode('utf-8'),
                    'CiphertextBlob': base64.b64encode(data_key).decode('utf-8'),
                })


class KmsBackend(object):
    def generate_data_key(self, key_id, encryption_context, number_of_bytes):
        return base64.b64encode(os.urandom(number_of_bytes))[:number_of_bytes]


orig_KmsResponse = moto.kms.responses.KmsResponse
class PatchedKmsResponse(KmsResponse, orig_KmsResponse):
    pass

orig_KmsBackend = moto.kms.models.KmsBackend
class PatchedKmsBackend(orig_KmsBackend, KmsBackend):
    pass

def patch_moto_kms():
    for region in boto.kms.regions():
        kms_backends[region.name] = PatchedKmsBackend()    
    moto.kms.responses.KmsResponse = PatchedKmsResponse
    moto.kms.models.KmsBackend = PatchedKmsBackend
    moto.kms.models.kms_backends = {}


for region in boto.kms.regions():
    kms_backends[region.name] = PatchedKmsBackend()

moto.kms.models.kms_backends = kms_backends