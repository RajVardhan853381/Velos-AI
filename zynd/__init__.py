"""
Zynd Protocol Integration Module

Uses the official zyndai-agent SDK (v0.2.2) when available (Python 3.12+),
with a local compatibility shim for older environments.

Exports:
- IdentityManager         — real SDK class or local shim
- AgentCommunicationManager — real SDK class or local shim
- SearchAndDiscoveryManager — real SDK class or local shim
- MQTTMessage             — local dataclass (SDK doesn't export it)
- AgentSearchResponse     — real SDK TypedDict or local TypedDict
- VerifiableCredential    — local W3C VC implementation
- ZyndProtocol            — orchestration wrapper
- zynd_protocol           — singleton instance
- check_official_sdk_available — returns True if SDK is loaded
- get_protocol_instance   — returns the singleton
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
    get_protocol_instance,

    # SDK status flags
    _SDK_AVAILABLE,
    __official_sdk_available__,
    __version__,
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
    'get_protocol_instance',

    # SDK status
    '_SDK_AVAILABLE',
    '__official_sdk_available__',
    '__version__',
]
