"""
Network classes for the ACI Toolkit.
This module contains classes for managing ACI network components like bridge domains,
subnets, and contexts.
"""

from typing import Optional, List, Dict, Any, Type
import logging
from ..core.base import BaseACIObject
from ..acisession import Session
from ..aciTable import Table

log = logging.getLogger(__name__)

class BridgeDomain(BaseACIObject):
    """
    ACI Bridge Domain class.
    
    This class represents a bridge domain in the ACI fabric. A bridge domain
    is a Layer 2 forwarding construct that defines a broadcast domain.
    
    Attributes:
        name (str): The name of the bridge domain
        parent (Optional[BaseACIObject]): The parent object (typically a Tenant)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of bridge domain attributes
    """
    
    def __init__(self, bd_name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new bridge domain.
        
        Args:
            bd_name: The name of the bridge domain
            parent: Optional parent object (typically a Tenant)
        """
        super().__init__(bd_name, parent)
        self.attributes = {
            'arpFlood': 'no',
            'unicastRoute': 'yes',
            'unkMacUcastAct': 'proxy',
            'unkMcastAct': 'flood'
        }
        log.info("Created new bridge domain: %s", bd_name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this bridge domain class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['fvBD']
    
    def set_unknown_mac_unicast(self, unicast: str) -> None:
        """
        Set the unknown unicast forwarding behavior.
        
        Args:
            unicast: The forwarding behavior ('flood', 'proxy', 'drop')
        """
        self.attributes['unkMacUcastAct'] = unicast
    
    def get_unknown_mac_unicast(self) -> str:
        """
        Get the unknown unicast forwarding behavior.
        
        Returns:
            The forwarding behavior
        """
        return self.attributes.get('unkMacUcastAct', 'proxy')
    
    def set_unknown_multicast(self, multicast: str) -> None:
        """
        Set the unknown multicast forwarding behavior.
        
        Args:
            multicast: The forwarding behavior ('flood', 'drop')
        """
        self.attributes['unkMcastAct'] = multicast
    
    def get_unknown_multicast(self) -> str:
        """
        Get the unknown multicast forwarding behavior.
        
        Returns:
            The forwarding behavior
        """
        return self.attributes.get('unkMcastAct', 'flood')
    
    def set_arp_flood(self, arp_value: str) -> None:
        """
        Set the ARP flooding behavior.
        
        Args:
            arp_value: Whether to enable ARP flooding ('yes', 'no')
        """
        self.attributes['arpFlood'] = arp_value
    
    def is_arp_flood(self) -> bool:
        """
        Check if ARP flooding is enabled.
        
        Returns:
            True if ARP flooding is enabled, False otherwise
        """
        return self.attributes.get('arpFlood', 'no') == 'yes'
    
    def set_unicast_route(self, route: str) -> None:
        """
        Set the unicast routing behavior.
        
        Args:
            route: Whether to enable unicast routing ('yes', 'no')
        """
        self.attributes['unicastRoute'] = route
    
    def is_unicast_route(self) -> bool:
        """
        Check if unicast routing is enabled.
        
        Returns:
            True if unicast routing is enabled, False otherwise
        """
        return self.attributes.get('unicastRoute', 'yes') == 'yes'
    
    def add_context(self, context: 'Context') -> None:
        """
        Add a context to this bridge domain.
        
        Args:
            context: The context to add
        """
        self.add_child(context)
    
    def remove_context(self) -> None:
        """
        Remove the context from this bridge domain.
        """
        contexts = self.get_children('Context')
        if contexts:
            self.remove_child(contexts[0])
    
    def get_context(self) -> Optional['Context']:
        """
        Get the context associated with this bridge domain.
        
        Returns:
            Context instance or None if no context is associated
        """
        contexts = self.get_children('Context')
        return contexts[0] if contexts else None
    
    def has_context(self) -> bool:
        """
        Check if this bridge domain has a context.
        
        Returns:
            True if a context is associated, False otherwise
        """
        return bool(self.get_context())
    
    def add_subnet(self, subnet: 'Subnet') -> None:
        """
        Add a subnet to this bridge domain.
        
        Args:
            subnet: The subnet to add
        """
        self.add_child(subnet)
    
    def remove_subnet(self, subnet: 'Subnet') -> None:
        """
        Remove a subnet from this bridge domain.
        
        Args:
            subnet: The subnet to remove
        """
        self.remove_child(subnet)
    
    def get_subnets(self) -> List['Subnet']:
        """
        Get all subnets associated with this bridge domain.
        
        Returns:
            List of Subnet instances
        """
        return self.get_children('Subnet')
    
    def has_subnet(self, subnet: 'Subnet') -> bool:
        """
        Check if this bridge domain has a specific subnet.
        
        Args:
            subnet: The subnet to check for
            
        Returns:
            True if the subnet is associated, False otherwise
        """
        return subnet in self.get_subnets()
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the bridge domain.
        
        Returns:
            Dictionary containing the JSON representation of the bridge domain
        """
        return {
            'fvBD': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }
    
    @staticmethod
    def get_table(bridge_domains: List['BridgeDomain'], title: str = '') -> Table:
        """
        Get a table of bridge domains.
        
        Args:
            bridge_domains: List of BridgeDomain instances
            title: Optional title for the table
            
        Returns:
            Table instance containing the bridge domain information
        """
        headers = ['Bridge Domain', 'Context', 'Subnets', 'EPGs']
        data = []
        for bd in bridge_domains:
            data.append([
                bd.name,
                bd.get_context().name if bd.get_context() else '',
                len(bd.get_subnets()),
                len(bd.get_children('EPG'))
            ])
        return Table(data, headers, title=title)

class BaseSubnet(BaseACIObject):
    """
    Base class for all subnet types.
    
    This class provides common functionality for all subnet types, including
    IP address management and scope handling.
    
    Attributes:
        name (str): The name of the subnet
        parent (Optional[BaseACIObject]): The parent object (typically a BridgeDomain)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of subnet attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None, address: Optional[str] = None) -> None:
        """
        Initialize a new subnet.
        
        Args:
            name: The name of the subnet
            parent: Optional parent object (typically a BridgeDomain)
            address: Optional IP address for the subnet
        """
        super().__init__(name, parent)
        if address:
            self.set_addr(address)
        log.info("Created new subnet: %s", name)
    
    @property
    def ip(self) -> str:
        """
        Get the IP address of this subnet.
        
        Returns:
            The IP address
        """
        return self.attributes.get('ip', '')
    
    @ip.setter
    def ip(self, x: str) -> None:
        """
        Set the IP address of this subnet.
        
        Args:
            x: The IP address to set
        """
        self.attributes['ip'] = x
    
    def get_addr(self) -> str:
        """
        Get the IP address of this subnet.
        
        Returns:
            The IP address
        """
        return self.attributes.get('ip', '')
    
    def set_addr(self, addr: str) -> None:
        """
        Set the IP address of this subnet.
        
        Args:
            addr: The IP address to set
        """
        self.attributes['ip'] = addr
    
    def get_scope(self) -> str:
        """
        Get the scope of this subnet.
        
        Returns:
            The scope
        """
        return self.attributes.get('scope', 'private')
    
    def set_scope(self, scope: str) -> None:
        """
        Set the scope of this subnet.
        
        Args:
            scope: The scope to set ('public', 'private', 'shared')
        """
        self.attributes['scope'] = scope

class Subnet(BaseSubnet):
    """
    ACI Subnet class.
    
    This class represents a subnet in the ACI fabric. A subnet is a Layer 3
    network segment that is associated with a bridge domain.
    
    Attributes:
        name (str): The name of the subnet
        parent (Optional[BaseACIObject]): The parent object (typically a BridgeDomain)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of subnet attributes
    """
    
    def __init__(self, subnet_name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new subnet.
        
        Args:
            subnet_name: The name of the subnet
            parent: Optional parent object (typically a BridgeDomain)
        """
        super().__init__(subnet_name, parent)
        log.info("Created new subnet: %s", subnet_name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this subnet class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['fvSubnet']
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the subnet.
        
        Returns:
            Dictionary containing the JSON representation of the subnet
        """
        return {
            'fvSubnet': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    'ip': self.get_addr(),
                    'scope': self.get_scope()
                }
            }
        }

class OutsideNetwork(BaseSubnet):
    """
    ACI Outside Network class.
    
    This class represents an outside network in the ACI fabric. An outside network
    is a Layer 3 network segment that is outside the fabric.
    
    Attributes:
        name (str): The name of the outside network
        parent (Optional[BaseACIObject]): The parent object (typically an OutsideL3)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of outside network attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None, address: Optional[str] = None) -> None:
        """
        Initialize a new outside network.
        
        Args:
            name: The name of the outside network
            parent: Optional parent object (typically an OutsideL3)
            address: Optional IP address for the outside network
        """
        super().__init__(name, parent, address)
        log.info("Created new outside network: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this outside network class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['l3extSubnet']
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the outside network.
        
        Returns:
            Dictionary containing the JSON representation of the outside network
        """
        return {
            'l3extSubnet': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    'ip': self.get_addr(),
                    'scope': self.get_scope()
                }
            }
        }

class Context(BaseACIObject):
    """
    ACI Context class.
    
    This class represents a context in the ACI fabric. A context is a Layer 3
    forwarding construct that defines a routing domain.
    
    Attributes:
        name (str): The name of the context
        parent (Optional[BaseACIObject]): The parent object (typically a Tenant)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of context attributes
    """
    
    def __init__(self, context_name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new context.
        
        Args:
            context_name: The name of the context
            parent: Optional parent object (typically a Tenant)
        """
        super().__init__(context_name, parent)
        self.attributes = {
            'allowAll': 'no'
        }
        log.info("Created new context: %s", context_name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this context class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['fvCtx']
    
    def set_allow_all(self, value: bool = True) -> None:
        """
        Set whether to allow all traffic.
        
        Args:
            value: Whether to allow all traffic
        """
        self.attributes['allowAll'] = 'yes' if value else 'no'
    
    def get_allow_all(self) -> bool:
        """
        Check if all traffic is allowed.
        
        Returns:
            True if all traffic is allowed, False otherwise
        """
        return self.attributes.get('allowAll', 'no') == 'yes'
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the context.
        
        Returns:
            Dictionary containing the JSON representation of the context
        """
        return {
            'fvCtx': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }
    
    @staticmethod
    def get_table(contexts: List['Context'], title: str = '') -> Table:
        """
        Get a table of contexts.
        
        Args:
            contexts: List of Context instances
            title: Optional title for the table
            
        Returns:
            Table instance containing the context information
        """
        headers = ['Context', 'Allow All', 'Bridge Domains']
        data = []
        for context in contexts:
            data.append([
                context.name,
                context.get_allow_all(),
                len(context.get_children('BridgeDomain'))
            ])
        return Table(data, headers, title=title) 