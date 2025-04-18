"""
Utility functions for the ACI Toolkit.
This module contains common utility functions used throughout the toolkit.
"""

from typing import Optional, Dict, Any, List, Union, Type, TypeVar
import logging
import re
from datetime import datetime
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network

# Configure logging
log = logging.getLogger(__name__)

T = TypeVar('T')

def validate_ip_address(ip_address: str) -> bool:
    """
    Validate an IP address.
    
    Args:
        ip_address: The IP address to validate
        
    Returns:
        True if the IP address is valid, False otherwise
    """
    try:
        IPv4Address(ip_address)
        return True
    except ValueError:
        try:
            IPv6Address(ip_address)
            return True
        except ValueError:
            return False

def validate_ip_network(network: str) -> bool:
    """
    Validate an IP network.
    
    Args:
        network: The IP network to validate
        
    Returns:
        True if the IP network is valid, False otherwise
    """
    try:
        IPv4Network(network)
        return True
    except ValueError:
        try:
            IPv6Network(network)
            return True
        except ValueError:
            return False

def parse_encap(encap: str) -> tuple[Optional[str], Optional[str]]:
    """
    Parse an encapsulation string.
    
    Args:
        encap: The encapsulation string to parse
        
    Returns:
        Tuple containing (encap_type, encap_id) or (None, None) if parsing failed
    """
    match = re.match(r'^([a-zA-Z0-9]+)-(\d+)$', encap)
    if match:
        return match.groups()
    return None, None

def format_encap(encap_type: str, encap_id: str) -> str:
    """
    Format an encapsulation string.
    
    Args:
        encap_type: The encapsulation type
        encap_id: The encapsulation ID
        
    Returns:
        Formatted encapsulation string
    """
    return f"{encap_type}-{encap_id}"

def get_current_time() -> str:
    """
    Get the current time in ISO format.
    
    Returns:
        Current time as ISO formatted string
    """
    return datetime.now().isoformat()

def validate_mac_address(mac: str) -> bool:
    """
    Validate a MAC address.
    
    Args:
        mac: The MAC address to validate
        
    Returns:
        True if the MAC address is valid, False otherwise
    """
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac))

def format_mac_address(mac: str) -> str:
    """
    Format a MAC address to use colons as separators.
    
    Args:
        mac: The MAC address to format
        
    Returns:
        Formatted MAC address
    """
    # Remove any existing separators
    mac = re.sub(r'[:-]', '', mac)
    # Add colons every 2 characters
    return ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))

def validate_name(name: str) -> bool:
    """
    Validate a name string.
    
    Args:
        name: The name to validate
        
    Returns:
        True if the name is valid, False otherwise
    """
    # Names can only contain letters, numbers, underscores, and hyphens
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, name))

def validate_description(description: str) -> bool:
    """
    Validate a description string.
    
    Args:
        description: The description to validate
        
    Returns:
        True if the description is valid, False otherwise
    """
    # Descriptions can contain any printable characters
    return all(ord(c) < 128 for c in description)

def get_class_name(obj: object) -> str:
    """
    Get the class name of an object.
    
    Args:
        obj: The object to get the class name of
        
    Returns:
        The class name
    """
    return obj.__class__.__name__

def get_module_name(obj: object) -> str:
    """
    Get the module name of an object.
    
    Args:
        obj: The object to get the module name of
        
    Returns:
        The module name
    """
    return obj.__class__.__module__

def get_full_class_name(obj: object) -> str:
    """
    Get the full class name of an object (including module).
    
    Args:
        obj: The object to get the full class name of
        
    Returns:
        The full class name
    """
    return f"{get_module_name(obj)}.{get_class_name(obj)}" 