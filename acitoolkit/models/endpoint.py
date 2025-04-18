"""
Endpoint classes for the ACI Toolkit.
This module contains classes for managing ACI endpoint components like endpoints,
static bindings, and endpoint groups.
"""

from typing import Optional, List, Dict, Any, Type
import logging
from ..core.base import BaseACIObject
from ..acisession import Session
from ..aciTable import Table

log = logging.getLogger(__name__)

class Endpoint(BaseACIObject):
    """
    ACI Endpoint class.
    
    This class represents an endpoint in the ACI fabric. An endpoint is a device
    or virtual machine that is connected to the fabric.
    
    Attributes:
        name (str): The name of the endpoint
        parent (Optional[BaseACIObject]): The parent object (typically an EPG)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of endpoint attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new endpoint.
        
        Args:
            name: The name of the endpoint
            parent: Optional parent object (typically an EPG)
        """
        super().__init__(name, parent)
        self.attributes = {
            'mac': '00:00:00:00:00:00',
            'ip': '0.0.0.0',
            'encap': 'vlan-1',
            'status': 'active'
        }
        log.info("Created new endpoint: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this endpoint class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['fv:CEp']
    
    def set_mac(self, mac: str) -> None:
        """
        Set the MAC address for this endpoint.
        
        Args:
            mac: The MAC address
        """
        self.attributes['mac'] = mac
    
    def get_mac(self) -> str:
        """
        Get the MAC address for this endpoint.
        
        Returns:
            The MAC address
        """
        return self.attributes.get('mac', '00:00:00:00:00:00')
    
    def set_ip(self, ip: str) -> None:
        """
        Set the IP address for this endpoint.
        
        Args:
            ip: The IP address
        """
        self.attributes['ip'] = ip
    
    def get_ip(self) -> str:
        """
        Get the IP address for this endpoint.
        
        Returns:
            The IP address
        """
        return self.attributes.get('ip', '0.0.0.0')
    
    def set_encap(self, encap: str) -> None:
        """
        Set the encapsulation for this endpoint.
        
        Args:
            encap: The encapsulation (e.g., 'vlan-1')
        """
        self.attributes['encap'] = encap
    
    def get_encap(self) -> str:
        """
        Get the encapsulation for this endpoint.
        
        Returns:
            The encapsulation
        """
        return self.attributes.get('encap', 'vlan-1')
    
    def set_status(self, status: str) -> None:
        """
        Set the status for this endpoint.
        
        Args:
            status: The status ('active', 'inactive')
        """
        self.attributes['status'] = status
    
    def get_status(self) -> str:
        """
        Get the status for this endpoint.
        
        Returns:
            The status
        """
        return self.attributes.get('status', 'active')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the endpoint.
        
        Returns:
            Dictionary containing the JSON representation of the endpoint
        """
        return {
            'fv:CEp': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class StaticBinding(BaseACIObject):
    """
    ACI Static Binding class.
    
    This class represents a static binding in the ACI fabric. A static binding
    is used to associate an endpoint with a specific interface and VLAN.
    
    Attributes:
        name (str): The name of the static binding
        parent (Optional[BaseACIObject]): The parent object (typically an EPG)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of static binding attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new static binding.
        
        Args:
            name: The name of the static binding
            parent: Optional parent object (typically an EPG)
        """
        super().__init__(name, parent)
        self.attributes = {
            'encap': 'vlan-1',
            'mode': 'regular',
            'interface': 'eth1/1'
        }
        log.info("Created new static binding: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this static binding class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['fv:RsPathAtt']
    
    def set_encap(self, encap: str) -> None:
        """
        Set the encapsulation for this static binding.
        
        Args:
            encap: The encapsulation (e.g., 'vlan-1')
        """
        self.attributes['encap'] = encap
    
    def get_encap(self) -> str:
        """
        Get the encapsulation for this static binding.
        
        Returns:
            The encapsulation
        """
        return self.attributes.get('encap', 'vlan-1')
    
    def set_mode(self, mode: str) -> None:
        """
        Set the mode for this static binding.
        
        Args:
            mode: The mode ('regular', 'native', 'untagged')
        """
        self.attributes['mode'] = mode
    
    def get_mode(self) -> str:
        """
        Get the mode for this static binding.
        
        Returns:
            The mode
        """
        return self.attributes.get('mode', 'regular')
    
    def set_interface(self, interface: str) -> None:
        """
        Set the interface for this static binding.
        
        Args:
            interface: The interface name (e.g., 'eth1/1')
        """
        self.attributes['interface'] = interface
    
    def get_interface(self) -> str:
        """
        Get the interface for this static binding.
        
        Returns:
            The interface name
        """
        return self.attributes.get('interface', 'eth1/1')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the static binding.
        
        Returns:
            Dictionary containing the JSON representation of the static binding
        """
        return {
            'fv:RsPathAtt': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        } 