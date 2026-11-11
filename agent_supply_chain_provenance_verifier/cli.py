"""CLI for agent-supply-chain-provenance-verifier."""
import sys
import argparse
import hashlib
import hmac
from .verifier import ProvenanceVerifier, SkillAttestation

def main():
    parser = argparse.ArgumentParser(description="Agent Supply Chain Provenance Verifier CLI")
    parser.add_argument("--demo", action="store_true", help="Demonstrate provenance verification")
    args = parser.parse_args()

    if args.demo:
        verifier = ProvenanceVerifier()
        verifier.register_maintainer("ejajmahmud", "signing_secret_99")
        content = b"print('Safe Tool v1.0')"
        chash = hashlib.sha256(content).hexdigest()
        sig = hmac.new(b"signing_secret_99", f"safe-tool|1.0.0|{chash}".encode(), hashlib.sha256).hexdigest()

        att = SkillAttestation("safe-tool", "1.0.0", chash, "ejajmahmud", sig)
        status = verifier.verify_skill(content, att)
        print(f"Verified: {status.verified}, Reason: {status.reason}")
    else:
        parser.print_help()
    sys.exit(0)

if __name__ == "__main__":
    main()
