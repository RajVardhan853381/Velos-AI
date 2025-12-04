"""
Zynd Protocol Integration Module
Compatible with official zyndai-agent SDK (v0.1.5)

Implements:
- IdentityManager - DID document management
- AgentCommunicationManager - MQTT-based messaging
- SearchAndDiscoveryManager - Agent discovery by capabilities
- VerifiableCredential - W3C standard credentials
- ZyndProtocol - Main interface combining all features

NOTE: This is a compatibility layer for Python 3.10.
When running on Python 3.12+, install the official package:
    pip install zyndai-agent==0.1.5
"""

from .protocol import (
    # Identity
    IdentityManager,
    
    # Communication
    AgentCommunicationManager,
    MQTTMessage,
    
    # Discovery
    SearchAndDiscoveryManager,
    AgentSearchResponse,
    
    # Credentials
    VerifiableCredential,
    
    # Main Protocol
    ZyndProtocol,
    zynd_protocol,
    
    # Utility
    check_official_sdk_available,
    get_protocol_instance
)

__all__ = [
    # Identity
    'IdentityManager',
    
    # Communication
    'AgentCommunicationManager',
    'MQTTMessage',
    
    # Discovery
    'SearchAndDiscoveryManager',
    'AgentSearchResponse',
    
    # Credentials
    'VerifiableCredential',
    
    # Main Protocol
    'ZyndProtocol',
    'zynd_protocol',
    
    # Utility
    'check_official_sdk_available',
    'get_protocol_instance'
]
