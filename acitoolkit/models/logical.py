"""
Logical model classes for the ACI Toolkit.
This module contains classes for managing ACI logical components like policies,
profiles, and other configuration objects.
"""

from typing import Optional, List, Dict, Any, Type, Union
import logging
from ..core.base import BaseACIObject
from ..acisession import Session
from ..aciTable import Table

log = logging.getLogger(__name__)

class Policy(BaseACIObject):
    """
    Base ACI Policy class.
    
    This class serves as the base for all policy types in the ACI fabric.
    A policy defines a set of rules or configurations that can be applied
    to various components.
    
    Attributes:
        name (str): The name of the policy
        parent (Optional[BaseACIObject]): The parent object
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of policy attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new policy.
        
        Args:
            name: The name of the policy
            parent: Optional parent object
        """
        super().__init__(name, parent)
        self.attributes = {
            'type': 'policy',
            'status': 'active'
        }
        log.info("Created new policy: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this policy class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['pol:Uni']
    
    def set_type(self, policy_type: str) -> None:
        """
        Set the type for this policy.
        
        Args:
            policy_type: The policy type
        """
        self.attributes['type'] = policy_type
    
    def get_type(self) -> str:
        """
        Get the type for this policy.
        
        Returns:
            The policy type
        """
        return self.attributes.get('type', 'policy')
    
    def set_status(self, status: str) -> None:
        """
        Set the status for this policy.
        
        Args:
            status: The status ('active', 'inactive')
        """
        self.attributes['status'] = status
    
    def get_status(self) -> str:
        """
        Get the status for this policy.
        
        Returns:
            The status
        """
        return self.attributes.get('status', 'active')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the policy.
        
        Returns:
            Dictionary containing the JSON representation of the policy
        """
        return {
            'pol:Uni': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class Profile(BaseACIObject):
    """
    Base ACI Profile class.
    
    This class serves as the base for all profile types in the ACI fabric.
    A profile defines a set of configurations that can be applied to various
    components.
    
    Attributes:
        name (str): The name of the profile
        parent (Optional[BaseACIObject]): The parent object
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of profile attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new profile.
        
        Args:
            name: The name of the profile
            parent: Optional parent object
        """
        super().__init__(name, parent)
        self.attributes = {
            'type': 'profile',
            'status': 'active'
        }
        log.info("Created new profile: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this profile class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['infra:Infra']
    
    def set_type(self, profile_type: str) -> None:
        """
        Set the type for this profile.
        
        Args:
            profile_type: The profile type
        """
        self.attributes['type'] = profile_type
    
    def get_type(self) -> str:
        """
        Get the type for this profile.
        
        Returns:
            The profile type
        """
        return self.attributes.get('type', 'profile')
    
    def set_status(self, status: str) -> None:
        """
        Set the status for this profile.
        
        Args:
            status: The status ('active', 'inactive')
        """
        self.attributes['status'] = status
    
    def get_status(self) -> str:
        """
        Get the status for this profile.
        
        Returns:
            The status
        """
        return self.attributes.get('status', 'active')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the profile.
        
        Returns:
            Dictionary containing the JSON representation of the profile
        """
        return {
            'infra:Infra': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class LogicalModel(BaseACIObject):
    """
    ACI Logical Model class.
    
    This class represents the logical model of the ACI fabric. It provides
    methods for managing logical components and their relationships.
    
    Attributes:
        name (str): The name of the logical model
        parent (Optional[BaseACIObject]): The parent object
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of logical model attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new logical model.
        
        Args:
            name: The name of the logical model
            parent: Optional parent object
        """
        super().__init__(name, parent)
        self.attributes = {
            'type': 'logical',
            'status': 'active'
        }
        log.info("Created new logical model: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this logical model class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['fabric:LogicalModel']
    
    def set_type(self, model_type: str) -> None:
        """
        Set the type for this logical model.
        
        Args:
            model_type: The model type
        """
        self.attributes['type'] = model_type
    
    def get_type(self) -> str:
        """
        Get the type for this logical model.
        
        Returns:
            The model type
        """
        return self.attributes.get('type', 'logical')
    
    def set_status(self, status: str) -> None:
        """
        Set the status for this logical model.
        
        Args:
            status: The status ('active', 'inactive')
        """
        self.attributes['status'] = status
    
    def get_status(self) -> str:
        """
        Get the status for this logical model.
        
        Returns:
            The status
        """
        return self.attributes.get('status', 'active')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the logical model.
        
        Returns:
            Dictionary containing the JSON representation of the logical model
        """
        return {
            'fabric:LogicalModel': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class LogicalInterface(BaseACIObject):
    """
    ACI Logical Interface class.
    
    This class represents a logical interface in the ACI fabric. It provides
    methods for managing logical interface configurations.
    
    Attributes:
        name (str): The name of the logical interface
        parent (Optional[BaseACIObject]): The parent object
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of logical interface attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new logical interface.
        
        Args:
            name: The name of the logical interface
            parent: Optional parent object
        """
        super().__init__(name, parent)
        self.attributes = {
            'type': 'logical',
            'status': 'active',
            'encap': 'vlan-1',
            'mode': 'regular'
        }
        log.info("Created new logical interface: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this logical interface class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['l1:PhysIf']
    
    def set_type(self, interface_type: str) -> None:
        """
        Set the type for this logical interface.
        
        Args:
            interface_type: The interface type
        """
        self.attributes['type'] = interface_type
    
    def get_type(self) -> str:
        """
        Get the type for this logical interface.
        
        Returns:
            The interface type
        """
        return self.attributes.get('type', 'logical')
    
    def set_status(self, status: str) -> None:
        """
        Set the status for this logical interface.
        
        Args:
            status: The status ('active', 'inactive')
        """
        self.attributes['status'] = status
    
    def get_status(self) -> str:
        """
        Get the status for this logical interface.
        
        Returns:
            The status
        """
        return self.attributes.get('status', 'active')
    
    def set_encap(self, encap: str) -> None:
        """
        Set the encapsulation for this logical interface.
        
        Args:
            encap: The encapsulation (e.g., 'vlan-1')
        """
        self.attributes['encap'] = encap
    
    def get_encap(self) -> str:
        """
        Get the encapsulation for this logical interface.
        
        Returns:
            The encapsulation
        """
        return self.attributes.get('encap', 'vlan-1')
    
    def set_mode(self, mode: str) -> None:
        """
        Set the mode for this logical interface.
        
        Args:
            mode: The mode ('regular', 'native', 'untagged')
        """
        self.attributes['mode'] = mode
    
    def get_mode(self) -> str:
        """
        Get the mode for this logical interface.
        
        Returns:
            The mode
        """
        return self.attributes.get('mode', 'regular')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the logical interface.
        
        Returns:
            Dictionary containing the JSON representation of the logical interface
        """
        return {
            'l1:PhysIf': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        } 