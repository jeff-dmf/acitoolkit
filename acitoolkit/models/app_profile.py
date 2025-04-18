"""
Application Profile classes for the ACI Toolkit.
This module contains classes for managing ACI application profiles and their components.
"""

from typing import Optional, List, Dict, Any, Type
import logging
from ..core.base import BaseACIObject

log = logging.getLogger(__name__)

class AppProfile(BaseACIObject):
    """
    ACI Application Profile class.
    
    This class represents an application profile in the ACI fabric. An application
    profile is a collection of endpoint groups (EPGs) that represent the application
    components.
    
    Attributes:
        name (str): The name of the application profile
        parent (Optional[BaseACIObject]): The parent object (typically a Tenant)
        children (List[BaseACIObject]): List of child objects (EPGs)
        attributes (Dict[str, Any]): Dictionary of application profile attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new application profile.
        
        Args:
            name: The name of the application profile
            parent: Optional parent object (typically a Tenant)
        """
        super().__init__(name, parent)
        log.info("Created new application profile: %s", name)
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the application profile.
        
        Returns:
            Dictionary containing the JSON representation of the application profile
        """
        return {
            'fvAp': {
                'attributes': {
                    'name': self.name,
                    'status': 'created'
                }
            }
        }
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this application profile class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['fvAp']
    
    def add_epg(self, name: str) -> 'EPG':
        """
        Add a new endpoint group to this application profile.
        
        Args:
            name: The name of the endpoint group
            
        Returns:
            The newly created EPG object
        """
        from .epg import EPG
        epg = EPG(name, self)
        self.add_child(epg)
        return epg 