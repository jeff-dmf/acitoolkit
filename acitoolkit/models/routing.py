"""
Routing classes for the ACI Toolkit.
This module contains classes for managing ACI routing components like L3 interfaces,
OSPF policies, and BGP sessions.
"""

from typing import Optional, List, Dict, Any, Type
import logging
from ..core.base import BaseACIObject
from ..acisession import Session
from ..aciTable import Table

log = logging.getLogger(__name__)

class L3Interface(BaseACIObject):
    """
    ACI Layer 3 Interface class.
    
    This class represents a Layer 3 interface in the ACI fabric. A Layer 3 interface
    is used for routing between bridge domains and external networks.
    
    Attributes:
        name (str): The name of the L3 interface
        parent (Optional[BaseACIObject]): The parent object (typically a Node)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of L3 interface attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new L3 interface.
        
        Args:
            name: The name of the L3 interface
            parent: Optional parent object (typically a Node)
        """
        super().__init__(name, parent)
        self.attributes = {
            'encap': 'vlan-1',
            'mode': 'regular'
        }
        log.info("Created new L3 interface: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this L3 interface class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['l3EncRtdIf']
    
    def set_encap(self, encap: str) -> None:
        """
        Set the encapsulation for this L3 interface.
        
        Args:
            encap: The encapsulation (e.g., 'vlan-1')
        """
        self.attributes['encap'] = encap
    
    def get_encap(self) -> str:
        """
        Get the encapsulation for this L3 interface.
        
        Returns:
            The encapsulation
        """
        return self.attributes.get('encap', 'vlan-1')
    
    def set_mode(self, mode: str) -> None:
        """
        Set the mode for this L3 interface.
        
        Args:
            mode: The mode ('regular', 'native', 'untagged')
        """
        self.attributes['mode'] = mode
    
    def get_mode(self) -> str:
        """
        Get the mode for this L3 interface.
        
        Returns:
            The mode
        """
        return self.attributes.get('mode', 'regular')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the L3 interface.
        
        Returns:
            Dictionary containing the JSON representation of the L3 interface
        """
        return {
            'l3EncRtdIf': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class OSPFInterfacePolicy(BaseACIObject):
    """
    ACI OSPF Interface Policy class.
    
    This class represents an OSPF interface policy in the ACI fabric. An OSPF
    interface policy defines the OSPF parameters for an interface.
    
    Attributes:
        name (str): The name of the OSPF interface policy
        parent (Optional[BaseACIObject]): The parent object
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of OSPF interface policy attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new OSPF interface policy.
        
        Args:
            name: The name of the OSPF interface policy
            parent: Optional parent object
        """
        super().__init__(name, parent)
        self.attributes = {
            'helloIntvl': '10',
            'deadIntvl': '40',
            'cost': '1',
            'priority': '1',
            'networkType': 'bcast'
        }
        log.info("Created new OSPF interface policy: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this OSPF interface policy class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['ospfIfPol']
    
    def set_hello_interval(self, interval: str) -> None:
        """
        Set the OSPF hello interval.
        
        Args:
            interval: The hello interval in seconds
        """
        self.attributes['helloIntvl'] = interval
    
    def get_hello_interval(self) -> str:
        """
        Get the OSPF hello interval.
        
        Returns:
            The hello interval in seconds
        """
        return self.attributes.get('helloIntvl', '10')
    
    def set_dead_interval(self, interval: str) -> None:
        """
        Set the OSPF dead interval.
        
        Args:
            interval: The dead interval in seconds
        """
        self.attributes['deadIntvl'] = interval
    
    def get_dead_interval(self) -> str:
        """
        Get the OSPF dead interval.
        
        Returns:
            The dead interval in seconds
        """
        return self.attributes.get('deadIntvl', '40')
    
    def set_cost(self, cost: str) -> None:
        """
        Set the OSPF interface cost.
        
        Args:
            cost: The interface cost
        """
        self.attributes['cost'] = cost
    
    def get_cost(self) -> str:
        """
        Get the OSPF interface cost.
        
        Returns:
            The interface cost
        """
        return self.attributes.get('cost', '1')
    
    def set_priority(self, priority: str) -> None:
        """
        Set the OSPF interface priority.
        
        Args:
            priority: The interface priority
        """
        self.attributes['priority'] = priority
    
    def get_priority(self) -> str:
        """
        Get the OSPF interface priority.
        
        Returns:
            The interface priority
        """
        return self.attributes.get('priority', '1')
    
    def set_network_type(self, network_type: str) -> None:
        """
        Set the OSPF network type.
        
        Args:
            network_type: The network type ('bcast', 'p2p', 'nbma')
        """
        self.attributes['networkType'] = network_type
    
    def get_network_type(self) -> str:
        """
        Get the OSPF network type.
        
        Returns:
            The network type
        """
        return self.attributes.get('networkType', 'bcast')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the OSPF interface policy.
        
        Returns:
            Dictionary containing the JSON representation of the OSPF interface policy
        """
        return {
            'ospfIfPol': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class OSPFRouter(BaseACIObject):
    """
    ACI OSPF Router class.
    
    This class represents an OSPF router in the ACI fabric. An OSPF router
    is used to configure OSPF routing.
    
    Attributes:
        name (str): The name of the OSPF router
        parent (Optional[BaseACIObject]): The parent object (typically a Tenant)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of OSPF router attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new OSPF router.
        
        Args:
            name: The name of the OSPF router
            parent: Optional parent object (typically a Tenant)
        """
        super().__init__(name, parent)
        self.attributes = {
            'routerId': '0.0.0.0',
            'areaId': '0.0.0.0'
        }
        log.info("Created new OSPF router: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this OSPF router class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['ospfRtPol']
    
    def set_router_id(self, router_id: str) -> None:
        """
        Set the OSPF router ID.
        
        Args:
            router_id: The router ID in IP address format
        """
        self.attributes['routerId'] = router_id
    
    def get_router_id(self) -> str:
        """
        Get the OSPF router ID.
        
        Returns:
            The router ID
        """
        return self.attributes.get('routerId', '0.0.0.0')
    
    def set_area_id(self, area_id: str) -> None:
        """
        Set the OSPF area ID.
        
        Args:
            area_id: The area ID in IP address format
        """
        self.attributes['areaId'] = area_id
    
    def get_area_id(self) -> str:
        """
        Get the OSPF area ID.
        
        Returns:
            The area ID
        """
        return self.attributes.get('areaId', '0.0.0.0')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the OSPF router.
        
        Returns:
            Dictionary containing the JSON representation of the OSPF router
        """
        return {
            'ospfRtPol': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class OSPFInterface(BaseACIObject):
    """
    ACI OSPF Interface class.
    
    This class represents an OSPF interface in the ACI fabric. An OSPF interface
    is used to configure OSPF on a specific interface.
    
    Attributes:
        name (str): The name of the OSPF interface
        parent (Optional[BaseACIObject]): The parent object (typically an L3Interface)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of OSPF interface attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new OSPF interface.
        
        Args:
            name: The name of the OSPF interface
            parent: Optional parent object (typically an L3Interface)
        """
        super().__init__(name, parent)
        self.attributes = {
            'areaId': '0.0.0.0',
            'areaType': 'regular'
        }
        log.info("Created new OSPF interface: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this OSPF interface class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['ospfIf']
    
    def set_area_id(self, area_id: str) -> None:
        """
        Set the OSPF area ID.
        
        Args:
            area_id: The area ID in IP address format
        """
        self.attributes['areaId'] = area_id
    
    def get_area_id(self) -> str:
        """
        Get the OSPF area ID.
        
        Returns:
            The area ID
        """
        return self.attributes.get('areaId', '0.0.0.0')
    
    def set_area_type(self, area_type: str) -> None:
        """
        Set the OSPF area type.
        
        Args:
            area_type: The area type ('regular', 'stub', 'nssa')
        """
        self.attributes['areaType'] = area_type
    
    def get_area_type(self) -> str:
        """
        Get the OSPF area type.
        
        Returns:
            The area type
        """
        return self.attributes.get('areaType', 'regular')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the OSPF interface.
        
        Returns:
            Dictionary containing the JSON representation of the OSPF interface
        """
        return {
            'ospfIf': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class BGPSession(BaseACIObject):
    """
    ACI BGP Session class.
    
    This class represents a BGP session in the ACI fabric. A BGP session
    is used to configure BGP routing.
    
    Attributes:
        name (str): The name of the BGP session
        parent (Optional[BaseACIObject]): The parent object (typically a Tenant)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of BGP session attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new BGP session.
        
        Args:
            name: The name of the BGP session
            parent: Optional parent object (typically a Tenant)
        """
        super().__init__(name, parent)
        self.attributes = {
            'routerId': '0.0.0.0',
            'localAs': '0',
            'remoteAs': '0',
            'peerAddr': '0.0.0.0'
        }
        log.info("Created new BGP session: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this BGP session class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['bgpPeerP']
    
    def set_router_id(self, router_id: str) -> None:
        """
        Set the BGP router ID.
        
        Args:
            router_id: The router ID in IP address format
        """
        self.attributes['routerId'] = router_id
    
    def get_router_id(self) -> str:
        """
        Get the BGP router ID.
        
        Returns:
            The router ID
        """
        return self.attributes.get('routerId', '0.0.0.0')
    
    def set_local_as(self, local_as: str) -> None:
        """
        Set the local AS number.
        
        Args:
            local_as: The local AS number
        """
        self.attributes['localAs'] = local_as
    
    def get_local_as(self) -> str:
        """
        Get the local AS number.
        
        Returns:
            The local AS number
        """
        return self.attributes.get('localAs', '0')
    
    def set_remote_as(self, remote_as: str) -> None:
        """
        Set the remote AS number.
        
        Args:
            remote_as: The remote AS number
        """
        self.attributes['remoteAs'] = remote_as
    
    def get_remote_as(self) -> str:
        """
        Get the remote AS number.
        
        Returns:
            The remote AS number
        """
        return self.attributes.get('remoteAs', '0')
    
    def set_peer_addr(self, peer_addr: str) -> None:
        """
        Set the BGP peer address.
        
        Args:
            peer_addr: The peer address in IP address format
        """
        self.attributes['peerAddr'] = peer_addr
    
    def get_peer_addr(self) -> str:
        """
        Get the BGP peer address.
        
        Returns:
            The peer address
        """
        return self.attributes.get('peerAddr', '0.0.0.0')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the BGP session.
        
        Returns:
            Dictionary containing the JSON representation of the BGP session
        """
        return {
            'bgpPeerP': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        } 