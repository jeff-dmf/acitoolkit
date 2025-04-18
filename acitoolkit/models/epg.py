"""
Endpoint Group (EPG) classes for the ACI Toolkit.
This module contains classes for managing ACI endpoint groups and their components.
"""

from typing import Optional, List, Dict, Any, Type, Union
import logging
from ..core.base import BaseACIObject
from ..acisession import Session
from ..aciTable import Table

log = logging.getLogger(__name__)

class CommonEPG(BaseACIObject):
    """
    Base class for all EPG types.
    
    This class provides common functionality for all EPG types, including
    contract management and interface handling.
    
    Attributes:
        name (str): The name of the endpoint group
        parent (Optional[BaseACIObject]): The parent object (typically an AppProfile)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of EPG attributes
    """
    
    def __init__(self, epg_name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new endpoint group.
        
        Args:
            epg_name: The name of the endpoint group
            parent: Optional parent object (typically an AppProfile)
        """
        super().__init__(epg_name, parent)
        log.info("Created new endpoint group: %s", epg_name)
    
    def provide(self, contract: 'Contract') -> None:
        """
        Add a contract that this EPG provides.
        
        Args:
            contract: The contract to add
        """
        self.add_child(contract)
    
    def consume(self, contract: 'Contract') -> None:
        """
        Add a contract that this EPG consumes.
        
        Args:
            contract: The contract to add
        """
        contract.add_child(self)
    
    def get_interfaces(self, status: str = 'attached') -> List['Interface']:
        """
        Get all interfaces attached to this EPG.
        
        Args:
            status: Filter interfaces by status ('attached' or 'detached')
            
        Returns:
            List of Interface instances
        """
        from ..aciphysobject import Interface
        return [child for child in self.get_children(Interface) if child.status == status]

class EPG(CommonEPG):
    """
    ACI Endpoint Group (EPG) class.
    
    This class represents an endpoint group in the ACI fabric. An EPG is a collection
    of endpoints that share common characteristics and policies.
    
    Attributes:
        name (str): The name of the endpoint group
        parent (Optional[BaseACIObject]): The parent object (typically an AppProfile)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of EPG attributes
    """
    
    def __init__(self, epg_name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new endpoint group.
        
        Args:
            epg_name: The name of the endpoint group
            parent: Optional parent object (typically an AppProfile)
        """
        super().__init__(epg_name, parent)
        self.attributes = {
            'isAttrBasedEPg': 'no',
            'pcEnfPref': 'unenforced',
            'prefGrMemb': 'exclude'
        }
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this EPG class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['fvAEPg']
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the EPG.
        
        Returns:
            Dictionary containing the JSON representation of the EPG
        """
        return {
            'fvAEPg': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }
    
    def add_bd(self, bridge_domain: 'BridgeDomain') -> None:
        """
        Add a bridge domain to this EPG.
        
        Args:
            bridge_domain: The bridge domain to add
        """
        self.add_child(bridge_domain)
    
    def get_bd(self) -> Optional['BridgeDomain']:
        """
        Get the bridge domain associated with this EPG.
        
        Returns:
            BridgeDomain instance or None if no bridge domain is associated
        """
        from .network import BridgeDomain
        bds = self.get_children(BridgeDomain)
        return bds[0] if bds else None
    
    @staticmethod
    def get_table(epgs: List['EPG'], title: str = '') -> Table:
        """
        Get a table of EPGs.
        
        Args:
            epgs: List of EPG instances
            title: Optional title for the table
            
        Returns:
            Table instance containing the EPG information
        """
        headers = ['EPG', 'Bridge Domain', 'Contracts', 'Interfaces']
        data = []
        for epg in epgs:
            data.append([
                epg.name,
                epg.get_bd().name if epg.get_bd() else '',
                len(epg.get_children('Contract')),
                len(epg.get_interfaces())
            ])
        return Table(data, headers, title=title)

class OutsideEPG(CommonEPG):
    """
    ACI Outside EPG class.
    
    This class represents an outside endpoint group in the ACI fabric. An outside EPG
    is used to represent endpoints that are outside the fabric.
    
    Attributes:
        name (str): The name of the outside endpoint group
        parent (Optional[BaseACIObject]): The parent object (typically an OutsideL3)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of outside EPG attributes
    """
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this outside EPG class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['l3extInstP']
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the outside EPG.
        
        Returns:
            Dictionary containing the JSON representation of the outside EPG
        """
        return {
            'l3extInstP': {
                'attributes': {
                    'name': self.name,
                    'status': 'created'
                }
            }
        }

class AnyEPG(CommonEPG):
    """
    ACI Any EPG class.
    
    This class represents an "any" endpoint group in the ACI fabric. An any EPG
    is used to represent any endpoint in the fabric.
    
    Attributes:
        name (str): The name of the any endpoint group
        parent (Optional[BaseACIObject]): The parent object (typically an AppProfile)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of any EPG attributes
    """
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this any EPG class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['fvAny']
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the any EPG.
        
        Returns:
            Dictionary containing the JSON representation of the any EPG
        """
        return {
            'fvAny': {
                'attributes': {
                    'name': self.name,
                    'status': 'created'
                }
            }
        }

class OutsideL2EPG(CommonEPG):
    """
    ACI Outside L2 EPG class.
    
    This class represents an outside L2 endpoint group in the ACI fabric. An outside L2 EPG
    is used to represent L2 endpoints that are outside the fabric.
    
    Attributes:
        name (str): The name of the outside L2 endpoint group
        parent (Optional[BaseACIObject]): The parent object (typically an OutsideL2)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of outside L2 EPG attributes
    """
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this outside L2 EPG class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['l2extInstP']
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the outside L2 EPG.
        
        Returns:
            Dictionary containing the JSON representation of the outside L2 EPG
        """
        return {
            'l2extInstP': {
                'attributes': {
                    'name': self.name,
                    'status': 'created'
                }
            }
        } 