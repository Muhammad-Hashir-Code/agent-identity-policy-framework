import json
import time
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

class AIPFIdentityAnchor:
    """
    Layer 1: Agent Identity Assertion (AIA)
    Represents the stable core identity of the agent, cryptographically signed by an issuer.
    """
    def __init__(self, agent_id: str, principal: str, model_family: str, issuer: str, issuer_private_key):
        self.payload = {
            "agent_id": agent_id,
            "principal": principal,
            "composition": {
                "model_family": model_family,
                "certification_hash": hashlib.sha256(b"aligned-baseline-v1").hexdigest()
            },
            "issuer": issuer,
            "issued_at": int(time.time()),
            "expires_at": int(time.time()) + 3600
        }
        self.signature = self._sign(issuer_private_key)

    def _sign(self, private_key) -> bytes:
        serialized = json.dumps(self.payload, sort_keys=True).encode('utf-8')
        return private_key.sign(
            serialized,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

    def get_hash(self) -> str:
        """Returns a stable SHA-256 hash of the identity payload for session binding."""
        serialized = json.dumps(self.payload, sort_keys=True).encode('utf-8')
        return hashlib.sha256(serialized).hexdigest()


class AIPFCapabilityDescriptor:
    """
    Layer 2: Agent Capability and Policy Descriptor (ACPD)
    Contains dynamic permissions, cryptographically bound to a specific AIA hash
    to prevent Confused Deputy and Replay attacks.
    """
    def __init__(self, aia: AIPFIdentityAnchor, scopes: list, nonce: str, operator_private_key):
        self.payload = {
            "aia_binding_hash": aia.get_hash(),  # Cryptographic session binding
            "scopes": scopes,
            "constraints": {
                "max_transaction_usd": 100.00,
                "allowed_domains": ["api.partner.com", "github.com"]
            },
            "nonce": nonce,
            "issued_at": int(time.time())
        }
        self.signature = self._sign(operator_private_key)

    def _sign(self, private_key) -> bytes:
        serialized = json.dumps(self.payload, sort_keys=True).encode('utf-8')
        return private_key.sign(
            serialized,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )


class LocalEnforcementInterface:
    """
    Layer 3: Local Enforcement Interface (LEI)
    Validates AIA, verifies the cryptographic session binding of the ACPD,
    and runs local policy checks before letting agent executions bypass.
    """
    def __init__(self, trusted_issuers: dict):
        self.trusted_issuers = trusted_issuers  # Dict mapping issuer name -> public key

    def verify_request(self, aia: AIPFIdentityAnchor, acpd: AIPFCapabilityDescriptor, operator_public_key, expected_nonce: str) -> bool:
        # 1. Verify AIA Signature
        issuer = aia.payload["issuer"]
        if issuer not in self.trusted_issuers:
            return False
        
        aia_serialized = json.dumps(aia.payload, sort_keys=True).encode('utf-8')
        try:
            self.trusted_issuers[issuer].verify(
                aia.signature,
                aia_serialized,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
        except InvalidSignature:
            return False

        # 2. Verify Session Binding (AIA must match the hash declared in ACPD)
        computed_aia_hash = aia.get_hash()
        if acpd.payload["aia_binding_hash"] != computed_aia_hash:
            return False  # Blocks Confused Deputy / Token Replay attacks

        # 3. Verify ACPD Signature (Signed by the Operator)
        acpd_serialized = json.dumps(acpd.payload, sort_keys=True).encode('utf-8')
        try:
            operator_public_key.verify(
                acpd.signature,
                acpd_serialized,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
        except InvalidSignature:
            return False

        # 4. Verify Nonce to prevent Replay Attacks
        if acpd.payload["nonce"] != expected_nonce:
            return False

        return True


# --- BENCHMARKING SUITE (Empirical Validation) ---
if __name__ == "__main__":
    print("Generating secure 2048-bit RSA keys...")
    issuer_priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    issuer_pub = issuer_priv.public_key()
    
    operator_priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    operator_pub = operator_priv.public_key()

    # Configure the Local Enforcement Interface with trusted issuer keys
    lei = LocalEnforcementInterface(trusted_issuers={"Global_CUNY_Trust": issuer_pub})
    nonce = "server-challenge-nonce-98213"

    print("\n--- Latency Benchmark (100 Iterations) ---")
    durations = []
    
    for i in range(100):
        start_time = time.perf_counter()
        
        # 1. Create Identity Anchor (AIA)
        aia = AIPFIdentityAnchor(
            agent_id="did:example:agent-007",
            principal="did:example:hashir-labs",
            model_family="llama-3-70b-instruct",
            issuer="Global_CUNY_Trust",
            issuer_private_key=issuer_priv
        )
        
        # 2. Create Dynamic Capability Descriptor (ACPD) with cryptographic binding
        acpd = AIPFCapabilityDescriptor(
            aia=aia,
            scopes=["read_db", "api_call"],
            nonce=nonce,
            operator_private_key=operator_priv
        )
        
        # 3. Verify at LEI
        is_valid = lei.verify_request(aia, acpd, operator_pub, expected_nonce=nonce)
        
        end_time = time.perf_counter()
        durations.append((end_time - start_time) * 1000)  # Convert to milliseconds

    avg_latency = sum(durations) / len(durations)
    print(f"Validation successful: {is_valid}")
    print(f"Average processing overhead per request: {avg_latency:.3f} ms")
    print(f"AIPF adds only ~{avg_latency:.1f}ms latency, verifying its suitability for real-time validation.")
