"""
LedgerManager: Cryptographic Proof of Decision Integrity

Creates immutable "digital fingerprints" of hiring decisions.
If anyone tampers with scores or results later, the hash won't match.

Uses SHA-256 hashing with canonical JSON serialization.
"""

import hashlib
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Tuple


class LedgerManager:
    """
    Creates and verifies cryptographic proofs of hiring decisions.
    
    Features:
    - Canonical JSON serialization (sorted keys)
    - SHA-256 hashing for tamper detection
    - Block structure with timestamps and signatures
    - Integrity verification
    """
    
    def __init__(self, agent_id: str = "Velos-v1"):
        """
        Initialize the ledger manager.
        
        Args:
            agent_id: Identifier for the signing agent (for audit trail)
        """
        self.agent_id = agent_id
        self.blocks: Dict[str, Dict] = {}  # In-memory block storage
    
    def _canonicalize(self, data: Any) -> str:
        """
        Convert data to canonical JSON string.
        Keys are sorted alphabetically to ensure consistent hashing.
        
        {b:2, a:1} and {a:1, b:2} will produce the same hash.
        """
        return json.dumps(data, sort_keys=True, separators=(',', ':'), default=str)
    
    def _compute_hash(self, data: Any) -> str:
        """
        Compute SHA-256 hash of the canonical JSON representation.
        
        Returns:
            64-character hex string (256 bits)
        """
        canonical = self._canonicalize(data)
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    
    def create_block(self, candidate_id: str, decision_data: Dict[str, Any],
                     previous_block_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Create an immutable block containing the decision fingerprint.
        
        Args:
            candidate_id: The candidate this decision is for
            decision_data: The full result from the pipeline (Agent 3 output)
            previous_block_hash: Hash of previous block (for chaining)
            
        Returns:
            Block dictionary:
            {
                "block_id": "uuid",
                "timestamp": "ISO timestamp",
                "candidate_id": "...",
                "data_hash": "SHA-256 fingerprint",
                "previous_hash": "...",
                "signature": "Agent signature",
                "metadata": {...}
            }
        """
        
        # Generate unique block ID
        block_id = str(uuid.uuid4())
        
        # Current timestamp
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Compute the data hash (the "fingerprint")
        data_hash = self._compute_hash(decision_data)
        
        # Create the block
        block = {
            "block_id": block_id,
            "timestamp": timestamp,
            "candidate_id": candidate_id,
            "data_hash": data_hash,
            "previous_hash": previous_block_hash or "GENESIS",
            "signature": self._sign_block(block_id, data_hash, timestamp),
            "metadata": {
                "agent_id": self.agent_id,
                "algorithm": "SHA-256",
                "version": "1.0"
            }
        }
        
        # Store the block
        self.blocks[block_id] = {
            "block": block,
            "original_data": decision_data
        }
        
        return block
    
    def _sign_block(self, block_id: str, data_hash: str, timestamp: str) -> str:
        """
        Create a digital signature for the block.
        
        In production, this would use asymmetric cryptography (RSA/ECDSA).
        For this implementation, we create an HMAC-like signature.
        """
        
        # Combine block elements for signature
        sign_data = f"{block_id}:{data_hash}:{timestamp}:{self.agent_id}"
        
        # Create signature hash
        signature = hashlib.sha256(sign_data.encode('utf-8')).hexdigest()[:32]
        
        return f"SIG-{self.agent_id}-{signature}"
    
    def verify_integrity(self, block: Dict[str, Any], 
                        current_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verify that the data hasn't been tampered with.
        
        Args:
            block: The block containing the original hash
            current_data: The current data from the database
            
        Returns:
            (is_valid, message)
            - True if hash matches (data unchanged)
            - False if hash doesn't match (TAMPERING DETECTED!)
        """
        
        original_hash = block.get("data_hash", "")
        current_hash = self._compute_hash(current_data)
        
        if original_hash == current_hash:
            return True, "✅ VERIFIED: Data integrity confirmed. No tampering detected."
        else:
            return False, f"🚨 TAMPERING DETECTED! Hash mismatch.\nOriginal: {original_hash[:16]}...\nCurrent:  {current_hash[:16]}..."
    
    def get_block(self, block_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a block by ID."""
        stored = self.blocks.get(block_id)
        return stored["block"] if stored else None
    
    def get_verification_report(self, block: Dict[str, Any],
                                current_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a detailed verification report.
        
        Returns:
            {
                "verified": bool,
                "message": str,
                "block_id": str,
                "candidate_id": str,
                "created_at": str,
                "original_hash": str,
                "current_hash": str,
                "hashes_match": bool,
                "signature_valid": bool
            }
        """
        
        is_valid, message = self.verify_integrity(block, current_data)
        current_hash = self._compute_hash(current_data)
        
        # Verify signature
        expected_signature = self._sign_block(
            block.get("block_id", ""),
            block.get("data_hash", ""),
            block.get("timestamp", "")
        )
        signature_valid = block.get("signature") == expected_signature
        
        return {
            "verified": is_valid,
            "message": message,
            "block_id": block.get("block_id"),
            "candidate_id": block.get("candidate_id"),
            "created_at": block.get("timestamp"),
            "original_hash": block.get("data_hash"),
            "current_hash": current_hash,
            "hashes_match": is_valid,
            "signature_valid": signature_valid,
            "algorithm": "SHA-256",
            "agent_id": block.get("metadata", {}).get("agent_id")
        }
    
    def create_audit_chain(self, blocks: list) -> Dict[str, Any]:
        """
        Verify an entire chain of blocks for a candidate.
        
        Returns chain validation status.
        """
        
        if not blocks:
            return {"valid": True, "message": "Empty chain", "blocks": 0}
        
        # Sort by timestamp
        sorted_blocks = sorted(blocks, key=lambda b: b.get("timestamp", ""))
        
        chain_valid = True
        issues = []
        
        for i, block in enumerate(sorted_blocks):
            if i == 0:
                # First block should have GENESIS as previous
                if block.get("previous_hash") != "GENESIS":
                    issues.append(f"Block {i}: Invalid genesis")
                    chain_valid = False
            else:
                # Check chain linkage
                expected_prev = sorted_blocks[i-1].get("data_hash")
                actual_prev = block.get("previous_hash")
                if expected_prev != actual_prev:
                    issues.append(f"Block {i}: Chain broken")
                    chain_valid = False
        
        return {
            "valid": chain_valid,
            "message": "Chain verified" if chain_valid else "Chain broken",
            "blocks": len(blocks),
            "issues": issues
        }


# Quick test
if __name__ == "__main__":
    ledger = LedgerManager(agent_id="Velos-Test")
    
    # Simulate a pipeline result
    decision_data = {
        "candidate_id": "CAND-12345",
        "final_status": "APPROVED",
        "agent_1_status": "PASS",
        "agent_2_status": "PASS",
        "agent_2_score": 85,
        "agent_3_status": "PASS",
        "authenticity_score": 92.5,
        "timestamp": "2025-01-15T10:30:00Z"
    }
    
    print("="*60)
    print("LEDGER MANAGER TEST")
    print("="*60)
    
    # Create a block
    block = ledger.create_block("CAND-12345", decision_data)
    
    print(f"\n📦 Block Created:")
    print(f"   Block ID: {block['block_id']}")
    print(f"   Timestamp: {block['timestamp']}")
    print(f"   Data Hash: {block['data_hash'][:32]}...")
    print(f"   Signature: {block['signature']}")
    
    # Verify unchanged data
    print(f"\n✅ Test 1: Verify unchanged data")
    is_valid, msg = ledger.verify_integrity(block, decision_data)
    print(f"   Result: {msg}")
    
    # Simulate tampering
    print(f"\n🚨 Test 2: Simulate tampering (change score from 85 to 90)")
    tampered_data = decision_data.copy()
    tampered_data["agent_2_score"] = 90
    
    is_valid, msg = ledger.verify_integrity(block, tampered_data)
    print(f"   Result: {msg}")
    
    # Full verification report
    print(f"\n📋 Full Verification Report:")
    report = ledger.get_verification_report(block, decision_data)
    for key, value in report.items():
        if key not in ["original_hash", "current_hash"]:
            print(f"   {key}: {value}")
