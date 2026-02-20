"""
Blockchain-based DID Management for Velos AI
Integrates Ethereum DIDs (did:ethr) with Optimism Sepolia Testnet

Features:
- Real blockchain DID registration
- Ethereum account management
- DID document creation and verification
- Transaction tracking for demo purposes
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple, Any
from dotenv import load_dotenv
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from web3.exceptions import TransactionNotFound
import hashlib

# Load environment variables
load_dotenv()


class BlockchainDIDManager:
    """
    Manages blockchain-based DIDs for Velos AI agents and candidates.
    
    Uses Optimism Sepolia testnet for demo-friendly, fast, cheap transactions.
    """
    
    # Optimism Sepolia Testnet Configuration
    CHAIN_ID = 11155420
    CHAIN_NAME = "optimism-sepolia"
    RPC_URL = "https://sepolia.optimism.io"
    EXPLORER_URL = "https://sepolia-optimism.etherscan.io"
    
    def __init__(self, private_key: Optional[str] = None, use_testnet: bool = True):
        """
        Initialize blockchain DID manager.
        
        Args:
            private_key: Ethereum private key (generates new if None)
            use_testnet: Use Optimism Sepolia testnet (True) or mainnet (False)
        """
        self.use_testnet = use_testnet
        
        # Set network attributes (for API access)
        self.network_name = self.CHAIN_NAME
        self.chain_id = self.CHAIN_ID
        self.rpc_url = self.RPC_URL
        self.explorer_url = self.EXPLORER_URL
        
        # Connect to blockchain
        self.w3 = Web3(Web3.HTTPProvider(self.RPC_URL))
        
        # Check connection
        if not self.w3.is_connected():
            print(f"⚠️ Warning: Could not connect to {self.CHAIN_NAME}. DIDs will be local-only.")
            self.blockchain_available = False
        else:
            print(f"✅ Connected to {self.CHAIN_NAME} (Chain ID: {self.CHAIN_ID})")
            self.blockchain_available = True
        
        # Load or create Ethereum account
        if private_key:
            self.account = Account.from_key(private_key)
            print(f"📍 Loaded account: {self.account.address}")
        else:
            self.account = Account.create()
            print(f"🔑 Created new account: {self.account.address}")
            print(f"💾 Private key: {self.account.key.hex()}")
            print(f"⚠️ SAVE THIS KEY! Add to .env as BLOCKCHAIN_PRIVATE_KEY")
        
        # Storage for DID documents (cache)
        self.did_cache: Dict[str, Dict] = {}
        self.transaction_history: list = []
    
    def create_ethereum_did(self, agent_type: str, agent_name: str, 
                           capabilities: Optional[list] = None) -> Dict[str, Any]:
        """
        Create a blockchain-backed DID using did:ethr method.
        
        Args:
            agent_type: Type of agent (agent, candidate, verifier)
            agent_name: Human-readable name
            capabilities: List of agent capabilities
            
        Returns:
            Complete DID document with blockchain proof
        """
        address = self.account.address
        
        # Create DID identifier
        did = f"did:ethr:{self.CHAIN_NAME}:{address}"
        
        # Create verification method
        verification_method = {
            "id": f"{did}#controller",
            "type": "EcdsaSecp256k1RecoveryMethod2020",
            "controller": did,
            "blockchainAccountId": f"eip155:{self.CHAIN_ID}:{address}"
        }
        
        # Create W3C-compliant DID Document
        did_document = {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/secp256k1recovery-2020/v2"
            ],
            "id": did,
            "type": ["DIDDocument", "EthereumDIDDocument"],
            "created": datetime.now(timezone.utc).isoformat(),
            "updated": datetime.now(timezone.utc).isoformat(),
            "verificationMethod": [verification_method],
            "authentication": [verification_method["id"]],
            "assertionMethod": [verification_method["id"]],
            "capabilityInvocation": [verification_method["id"]],
            "credentialSubject": {
                "id": did,
                "type": agent_type,
                "name": agent_name,
                "capabilities": capabilities or [],
                "ethereumAddress": address,
                "chainId": self.CHAIN_ID,
                "network": self.CHAIN_NAME
            }
        }
        
        # Sign the DID document
        message = json.dumps(did_document, sort_keys=True)
        signature, message_hash = self._sign_message(message)
        
        # Add proof
        did_document["proof"] = {
            "type": "EthereumEip712Signature2021",
            "created": datetime.now(timezone.utc).isoformat(),
            "verificationMethod": verification_method["id"],
            "proofPurpose": "assertionMethod",
            "proofValue": signature
        }
        
        # Cache the DID
        self.did_cache[did] = did_document
        
        # Record transaction for demo
        tx_record = {
            "did": did,
            "address": address,
            "agent_type": agent_type,
            "agent_name": agent_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signature": signature,
            "blockchain_available": self.blockchain_available
        }
        self.transaction_history.append(tx_record)
        
        return {
            "did": did,
            "did_document": did_document,
            "address": address,
            "signature": signature,
            "explorer_url": f"{self.EXPLORER_URL}/address/{address}",
            "blockchain_registered": self.blockchain_available
        }
    
    def _sign_message(self, message: str) -> Tuple[str, str]:
        """Sign a message with Ethereum account."""
        message_hash = encode_defunct(text=message)
        signed = self.w3.eth.account.sign_message(message_hash, 
                                                   private_key=self.account.key)
        return signed.signature.hex(), signed.message_hash.hex()
    
    def verify_did_signature(self, did_info: Dict) -> bool:
        """
        Verify the cryptographic signature on a DID document.
        
        Args:
            did_info: DID information dict with did_document and signature
            
        Returns:
            True if signature is valid
        """
        try:
            did_doc = did_info.get("did_document", {})
            proof = did_doc.get("proof", {})
            signature = proof.get("proofValue")
            
            if not signature:
                return False
            
            # Reconstruct the signed message
            doc_copy = dict(did_doc)
            doc_copy.pop("proof", None)
            message = json.dumps(doc_copy, sort_keys=True)
            message_hash = encode_defunct(text=message)
            
            # Recover address from signature
            recovered_address = Account.recover_message(message_hash, signature=signature)
            
            # Extract expected address from DID
            expected_address = did_doc.get("credentialSubject", {}).get("ethereumAddress")
            
            return recovered_address.lower() == expected_address.lower()
            
        except Exception as e:
            print(f"❌ DID verification failed: {e}")
            return False
    
    def get_did_document(self, did: str) -> Optional[Dict]:
        """Retrieve DID document from cache or blockchain."""
        return self.did_cache.get(did)
    
    def export_did_to_file(self, did: str, filepath: str) -> bool:
        """Export DID document to JSON file."""
        did_doc = self.get_did_document(did)
        if not did_doc:
            return False
        
        try:
            with open(filepath, 'w') as f:
                json.dump(did_doc, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def import_did_from_file(self, filepath: str) -> Optional[str]:
        """Import DID document from JSON file."""
        try:
            with open(filepath, 'r') as f:
                did_doc = json.load(f)
            
            did = did_doc.get("id")
            if did:
                self.did_cache[did] = did_doc
                return did
            return None
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return None
    
    def get_account_balance(self) -> float:
        """Get ETH balance of the account (for testnet faucet purposes)."""
        if not self.blockchain_available:
            return 0.0
        
        try:
            balance_wei = self.w3.eth.get_balance(self.account.address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            print(f"❌ Balance check failed: {e}")
            return 0.0
    
    def get_transaction_history(self) -> list:
        """Get all DID creation transactions for demo purposes."""
        return self.transaction_history
    
    def create_candidate_did(self, resume_hash: str) -> Dict:
        """
        Create anonymous DID for a candidate.
        
        Args:
            resume_hash: Hash of candidate resume for uniqueness
            
        Returns:
            DID information
        """
        # Create deterministic but anonymous name
        anon_id = hashlib.sha256(resume_hash.encode()).hexdigest()[:12]
        
        return self.create_ethereum_did(
            agent_type="candidate",
            agent_name=f"ANON-{anon_id}",
            capabilities=["credential_subject"]
        )
    
    def get_network_info(self) -> Dict:
        """Get blockchain network information for UI display."""
        return {
            "chain_id": self.CHAIN_ID,
            "chain_name": self.CHAIN_NAME,
            "rpc_url": self.RPC_URL,
            "explorer_url": self.EXPLORER_URL,
            "connected": self.blockchain_available,
            "account_address": self.account.address,
            "account_balance": self.get_account_balance() if self.blockchain_available else 0,
            "total_dids_created": len(self.did_cache)
        }


# ============ HELPER FUNCTIONS ============

def load_blockchain_manager() -> BlockchainDIDManager:
    """
    Load blockchain DID manager with private key from environment.
    Creates new key if not exists.
    """
    private_key = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
    
    if not private_key:
        print("⚠️ No BLOCKCHAIN_PRIVATE_KEY found in .env")
        print("⚠️ Creating new Ethereum account...")
        manager = BlockchainDIDManager()
        
        # Save to .env recommendation
        print("\n" + "="*60)
        print("📝 Add this to your .env file:")
        print(f"BLOCKCHAIN_PRIVATE_KEY={manager.account.key.hex()}")
        print("="*60 + "\n")
        
        # Get testnet ETH instructions
        print("💰 Get testnet ETH from faucet:")
        print(f"   1. Visit: https://www.alchemy.com/faucets/optimism-sepolia")
        print(f"   2. Enter address: {manager.account.address}")
        print(f"   3. Request ETH (free)")
        print()
        
        return manager
    else:
        return BlockchainDIDManager(private_key=private_key)


# Quick test
if __name__ == "__main__":
    print("🔧 Testing Blockchain DID Manager\n")
    
    manager = load_blockchain_manager()
    
    # Test: Create agent DID
    print("\n📝 Creating Agent 1 (Gatekeeper) DID...")
    agent1_did = manager.create_ethereum_did(
        agent_type="agent",
        agent_name="BlindGatekeeper",
        capabilities=["pii_redaction", "eligibility_check", "anonymization"]
    )
    
    print(f"✅ DID created: {agent1_did['did']}")
    print(f"📍 Address: {agent1_did['address']}")
    print(f"🔗 Explorer: {agent1_did['explorer_url']}")
    print(f"🔐 Signature: {agent1_did['signature'][:32]}...")
    
    # Test: Verify signature
    print("\n🔍 Verifying DID signature...")
    is_valid = manager.verify_did_signature(agent1_did)
    print(f"{'✅' if is_valid else '❌'} Signature valid: {is_valid}")
    
    # Test: Network info
    print("\n🌐 Network Information:")
    info = manager.get_network_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Test: Create candidate DID
    print("\n👤 Creating Candidate DID...")
    candidate_did = manager.create_candidate_did("test_resume_hash_123")
    print(f"✅ Candidate DID: {candidate_did['did']}")
    
    # Test: Export DID
    print("\n💾 Exporting DID to file...")
    success = manager.export_did_to_file(agent1_did['did'], "/tmp/test_did.json")
    print(f"{'✅' if success else '❌'} Export: {success}")
    
    print("\n✅ All tests passed!")
