"""
Domain classes for the ACI Toolkit.
This module contains classes for managing ACI domain components like physical domains,
VMM domains, and L2/L3 domains.
"""

from typing import Optional, List, Dict, Any, Type
import logging
from ..core.base import BaseACIObject
from ..acisession import Session
from ..aciTable import Table

log = logging.getLogger(__name__)

class Domain(BaseACIObject):
    """
    Base ACI Domain class.
    
    This class serves as the base for all domain types in the ACI fabric.
    A domain is a logical grouping of resources with common policies.
    
    Attributes:
        name (str): The name of the domain
        parent (Optional[BaseACIObject]): The parent object
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of domain attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new domain.
        
        Args:
            name: The name of the domain
            parent: Optional parent object
        """
        super().__init__(name, parent)
        self.attributes = {
            'type': 'physical',
            'status': 'active'
        }
        log.info("Created new domain: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this domain class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['phys:DomP']
    
    def set_type(self, domain_type: str) -> None:
        """
        Set the type for this domain.
        
        Args:
            domain_type: The domain type ('physical', 'vmm', 'l2', 'l3')
        """
        self.attributes['type'] = domain_type
    
    def get_type(self) -> str:
        """
        Get the type for this domain.
        
        Returns:
            The domain type
        """
        return self.attributes.get('type', 'physical')
    
    def set_status(self, status: str) -> None:
        """
        Set the status for this domain.
        
        Args:
            status: The status ('active', 'inactive')
        """
        self.attributes['status'] = status
    
    def get_status(self) -> str:
        """
        Get the status for this domain.
        
        Returns:
            The status
        """
        return self.attributes.get('status', 'active')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the domain.
        
        Returns:
            Dictionary containing the JSON representation of the domain
        """
        return {
            'phys:DomP': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class PhysicalDomain(Domain):
    """
    ACI Physical Domain class.
    
    This class represents a physical domain in the ACI fabric. A physical domain
    is used to group physical resources like switches and interfaces.
    
    Attributes:
        name (str): The name of the physical domain
        parent (Optional[BaseACIObject]): The parent object
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of physical domain attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new physical domain.
        
        Args:
            name: The name of the physical domain
            parent: Optional parent object
        """
        super().__init__(name, parent)
        self.attributes['type'] = 'physical'
        log.info("Created new physical domain: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this physical domain class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['phys:DomP']

class VMMDomain(Domain):
    """
    ACI VMM Domain class.
    
    This class represents a Virtual Machine Manager (VMM) domain in the ACI fabric.
    A VMM domain is used to group virtual resources like VMs and hypervisors.
    
    Attributes:
        name (str): The name of the VMM domain
        parent (Optional[BaseACIObject]): The parent object
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of VMM domain attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new VMM domain.
        
        Args:
            name: The name of the VMM domain
            parent: Optional parent object
        """
        super().__init__(name, parent)
        self.attributes.update({
            'type': 'vmm',
            'provider': 'VMware',
            'controller': 'vcenter'
        })
        log.info("Created new VMM domain: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this VMM domain class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['vmm:DomP']
    
    def set_provider(self, provider: str) -> None:
        """
        Set the provider for this VMM domain.
        
        Args:
            provider: The provider ('VMware', 'Microsoft', 'OpenStack')
        """
        self.attributes['provider'] = provider
    
    def get_provider(self) -> str:
        """
        Get the provider for this VMM domain.
        
        Returns:
            The provider
        """
        return self.attributes.get('provider', 'VMware')
    
    def set_controller(self, controller: str) -> None:
        """
        Set the controller for this VMM domain.
        
        Args:
            controller: The controller name
        """
        self.attributes['controller'] = controller
    
    def get_controller(self) -> str:
        """
        Get the controller for this VMM domain.
        
        Returns:
            The controller name
        """
        return self.attributes.get('controller', 'vcenter')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the VMM domain.
        
        Returns:
            Dictionary containing the JSON representation of the VMM domain
        """
        return {
            'vmm:DomP': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class L2Domain(Domain):
    """
    ACI L2 Domain class.
    
    This class represents an L2 domain in the ACI fabric. An L2 domain is used
    to group resources that share the same Layer 2 policies.
    
    Attributes:
        name (str): The name of the L2 domain
        parent (Optional[BaseACIObject]): The parent object
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of L2 domain attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new L2 domain.
        
        Args:
            name: The name of the L2 domain
            parent: Optional parent object
        """
        super().__init__(name, parent)
        self.attributes['type'] = 'l2'
        log.info("Created new L2 domain: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this L2 domain class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['l2ext:DomP']

class L3Domain(Domain):
    """
    ACI L3 Domain class.
    
    This class represents an L3 domain in the ACI fabric. An L3 domain is used
    to group resources that share the same Layer 3 policies.
    
    Attributes:
        name (str): The name of the L3 domain
        parent (Optional[BaseACIObject]): The parent object
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of L3 domain attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new L3 domain.
        
        Args:
            name: The name of the L3 domain
            parent: Optional parent object
        """
        super().__init__(name, parent)
        self.attributes['type'] = 'l3'
        log.info("Created new L3 domain: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this L3 domain class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['l3ext:DomP'] 