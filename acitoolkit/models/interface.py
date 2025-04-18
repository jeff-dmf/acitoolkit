"""
Interface classes for the ACI Toolkit.
This module contains classes for managing ACI interface components like L2 interfaces,
port channels, FEX interfaces, and tunnel interfaces.
"""

from typing import Optional, List, Dict, Any, Type
import logging
from ..core.base import BaseACIObject
from ..acisession import Session
from ..aciTable import Table

log = logging.getLogger(__name__)

class L2Interface(BaseACIObject):
    """
    ACI Layer 2 Interface class.
    
    This class represents a Layer 2 interface in the ACI fabric. A Layer 2 interface
    is used for connecting endpoints and external devices to the fabric.
    
    Attributes:
        name (str): The name of the L2 interface
        parent (Optional[BaseACIObject]): The parent object (typically a Node)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of L2 interface attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new L2 interface.
        
        Args:
            name: The name of the L2 interface
            parent: Optional parent object (typically a Node)
        """
        super().__init__(name, parent)
        self.attributes = {
            'encap': 'vlan-1',
            'mode': 'regular'
        }
        log.info("Created new L2 interface: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this L2 interface class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['l2EncRtdIf']
    
    def set_encap(self, encap: str) -> None:
        """
        Set the encapsulation for this L2 interface.
        
        Args:
            encap: The encapsulation (e.g., 'vlan-1')
        """
        self.attributes['encap'] = encap
    
    def get_encap(self) -> str:
        """
        Get the encapsulation for this L2 interface.
        
        Returns:
            The encapsulation
        """
        return self.attributes.get('encap', 'vlan-1')
    
    def set_mode(self, mode: str) -> None:
        """
        Set the mode for this L2 interface.
        
        Args:
            mode: The mode ('regular', 'native', 'untagged')
        """
        self.attributes['mode'] = mode
    
    def get_mode(self) -> str:
        """
        Get the mode for this L2 interface.
        
        Returns:
            The mode
        """
        return self.attributes.get('mode', 'regular')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the L2 interface.
        
        Returns:
            Dictionary containing the JSON representation of the L2 interface
        """
        return {
            'l2EncRtdIf': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class PortChannel(BaseACIObject):
    """
    ACI Port Channel class.
    
    This class represents a port channel in the ACI fabric. A port channel
    is a logical interface that bundles multiple physical interfaces.
    
    Attributes:
        name (str): The name of the port channel
        parent (Optional[BaseACIObject]): The parent object (typically a Node)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of port channel attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new port channel.
        
        Args:
            name: The name of the port channel
            parent: Optional parent object (typically a Node)
        """
        super().__init__(name, parent)
        self.attributes = {
            'lagT': 'link',
            'mode': 'active'
        }
        log.info("Created new port channel: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this port channel class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['fabric:LagPol']
    
    def set_lag_type(self, lag_type: str) -> None:
        """
        Set the LAG type for this port channel.
        
        Args:
            lag_type: The LAG type ('link', 'node')
        """
        self.attributes['lagT'] = lag_type
    
    def get_lag_type(self) -> str:
        """
        Get the LAG type for this port channel.
        
        Returns:
            The LAG type
        """
        return self.attributes.get('lagT', 'link')
    
    def set_mode(self, mode: str) -> None:
        """
        Set the mode for this port channel.
        
        Args:
            mode: The mode ('active', 'passive', 'on')
        """
        self.attributes['mode'] = mode
    
    def get_mode(self) -> str:
        """
        Get the mode for this port channel.
        
        Returns:
            The mode
        """
        return self.attributes.get('mode', 'active')
    
    def add_member(self, interface: 'L2Interface') -> None:
        """
        Add a member interface to this port channel.
        
        Args:
            interface: The interface to add as a member
        """
        self.add_child(interface)
    
    def remove_member(self, interface: 'L2Interface') -> None:
        """
        Remove a member interface from this port channel.
        
        Args:
            interface: The interface to remove
        """
        self.remove_child(interface)
    
    def get_members(self) -> List['L2Interface']:
        """
        Get all member interfaces of this port channel.
        
        Returns:
            List of L2Interface instances
        """
        return self.get_children('L2Interface')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the port channel.
        
        Returns:
            Dictionary containing the JSON representation of the port channel
        """
        return {
            'fabric:LagPol': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class FexInterface(BaseACIObject):
    """
    ACI FEX Interface class.
    
    This class represents a Fabric Extender (FEX) interface in the ACI fabric.
    A FEX interface is used to connect FEX devices to the fabric.
    
    Attributes:
        name (str): The name of the FEX interface
        parent (Optional[BaseACIObject]): The parent object (typically a Node)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of FEX interface attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new FEX interface.
        
        Args:
            name: The name of the FEX interface
            parent: Optional parent object (typically a Node)
        """
        super().__init__(name, parent)
        self.attributes = {
            'fexId': '101',
            'type': 'leaf'
        }
        log.info("Created new FEX interface: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this FEX interface class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['fabric:FexP']
    
    def set_fex_id(self, fex_id: str) -> None:
        """
        Set the FEX ID for this interface.
        
        Args:
            fex_id: The FEX ID
        """
        self.attributes['fexId'] = fex_id
    
    def get_fex_id(self) -> str:
        """
        Get the FEX ID for this interface.
        
        Returns:
            The FEX ID
        """
        return self.attributes.get('fexId', '101')
    
    def set_type(self, fex_type: str) -> None:
        """
        Set the FEX type for this interface.
        
        Args:
            fex_type: The FEX type ('leaf', 'spine')
        """
        self.attributes['type'] = fex_type
    
    def get_type(self) -> str:
        """
        Get the FEX type for this interface.
        
        Returns:
            The FEX type
        """
        return self.attributes.get('type', 'leaf')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the FEX interface.
        
        Returns:
            Dictionary containing the JSON representation of the FEX interface
        """
        return {
            'fabric:FexP': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class TunnelInterface(BaseACIObject):
    """
    ACI Tunnel Interface class.
    
    This class represents a tunnel interface in the ACI fabric. A tunnel interface
    is used for overlay networking and encapsulation.
    
    Attributes:
        name (str): The name of the tunnel interface
        parent (Optional[BaseACIObject]): The parent object (typically a Node)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of tunnel interface attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new tunnel interface.
        
        Args:
            name: The name of the tunnel interface
            parent: Optional parent object (typically a Node)
        """
        super().__init__(name, parent)
        self.attributes = {
            'type': 'vxlan',
            'source': '0.0.0.0',
            'destination': '0.0.0.0'
        }
        log.info("Created new tunnel interface: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this tunnel interface class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['tunnelIf']
    
    def set_type(self, tunnel_type: str) -> None:
        """
        Set the tunnel type for this interface.
        
        Args:
            tunnel_type: The tunnel type ('vxlan', 'gre', 'ipsec')
        """
        self.attributes['type'] = tunnel_type
    
    def get_type(self) -> str:
        """
        Get the tunnel type for this interface.
        
        Returns:
            The tunnel type
        """
        return self.attributes.get('type', 'vxlan')
    
    def set_source(self, source: str) -> None:
        """
        Set the source address for this tunnel interface.
        
        Args:
            source: The source IP address
        """
        self.attributes['source'] = source
    
    def get_source(self) -> str:
        """
        Get the source address for this tunnel interface.
        
        Returns:
            The source IP address
        """
        return self.attributes.get('source', '0.0.0.0')
    
    def set_destination(self, destination: str) -> None:
        """
        Set the destination address for this tunnel interface.
        
        Args:
            destination: The destination IP address
        """
        self.attributes['destination'] = destination
    
    def get_destination(self) -> str:
        """
        Get the destination address for this tunnel interface.
        
        Returns:
            The destination IP address
        """
        return self.attributes.get('destination', '0.0.0.0')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the tunnel interface.
        
        Returns:
            Dictionary containing the JSON representation of the tunnel interface
        """
        return {
            'tunnelIf': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        } 