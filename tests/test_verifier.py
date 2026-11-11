"""Unit tests for agent-supply-chain-provenance-verifier."""
import hashlib
import hmac
import unittest
from agent_supply_chain_provenance_verifier.verifier import ProvenanceVerifier, SkillAttestation

class TestProvenanceVerifier(unittest.TestCase):
    def setUp(self):
        self.verifier = ProvenanceVerifier()
        self.verifier.register_maintainer("auth_user", "sec123")

    def test_valid_attestation(self):
        data = b"my_skill_code"
        dhash = hashlib.sha256(data).hexdigest()
        sig = hmac.new(b"sec123", f"test_skill|0.1.0|{dhash}".encode(), hashlib.sha256).hexdigest()
        att = SkillAttestation("test_skill", "0.1.0", dhash, "auth_user", sig)
        res = self.verifier.verify_skill(data, att)
        self.assertTrue(res.verified)

    def test_tampered_payload_rejected(self):
        data = b"clean_code"
        dhash = hashlib.sha256(data).hexdigest()
        sig = hmac.new(b"sec123", f"test_skill|0.1.0|{dhash}".encode(), hashlib.sha256).hexdigest()
        att = SkillAttestation("test_skill", "0.1.0", dhash, "auth_user", sig)
        
        # Tamper payload
        res = self.verifier.verify_skill(b"tampered_code", att)
        self.assertFalse(res.verified)
        self.assertIn("Hash mismatch", res.reason)
