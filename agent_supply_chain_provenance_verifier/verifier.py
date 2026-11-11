"""Core Provenance Verifier implementation."""
import hashlib
import hmac
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class SkillAttestation:
    skill_name: str
    version: str
    sha256_digest: str
    maintainer_id: str
    signature: str

class VerificationStatus:
    def __init__(self, verified: bool, reason: str, calculated_hash: str):
        self.verified = verified
        self.reason = reason
        self.calculated_hash = calculated_hash

class ProvenanceVerifier:
    """Verifies that downloaded agent plugins match signed cryptographic attestations."""
    
    def __init__(self):
        # Trusted maintainer public HMAC/symmetric keys (or pubkeys)
        self.trusted_maintainers: Dict[str, str] = {}

    def register_maintainer(self, maintainer_id: str, secret_key: str) -> None:
        self.trusted_maintainers[maintainer_id] = secret_key

    def compute_sha256(self, content_bytes: bytes) -> str:
        return hashlib.sha256(content_bytes).hexdigest()

    def verify_skill(self, content_bytes: bytes, attestation: SkillAttestation) -> VerificationStatus:
        actual_hash = self.compute_sha256(content_bytes)
        
        # 1. Hash match check
        if actual_hash != attestation.sha256_digest:
            return VerificationStatus(False, f"Hash mismatch: actual {actual_hash} != expected {attestation.sha256_digest}", actual_hash)

        # 2. Maintainer trust check
        key = self.trusted_maintainers.get(attestation.maintainer_id)
        if not key:
            return VerificationStatus(False, f"Maintainer '{attestation.maintainer_id}' is not in trusted registry", actual_hash)

        # 3. Signature verification
        target = f"{attestation.skill_name}|{attestation.version}|{attestation.sha256_digest}".encode("utf-8")
        expected_sig = hmac.new(key.encode("utf-8"), target, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_sig, attestation.signature):
            return VerificationStatus(False, "Cryptographic signature verification failed", actual_hash)

        return VerificationStatus(True, "Skill provenance verified successfully", actual_hash)
