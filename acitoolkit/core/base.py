"""
Base classes for the ACI Toolkit.
This module contains the fundamental classes used throughout the toolkit.
"""

from typing import Optional, List, Dict, Any, Union, Type, TypeVar
import logging
from abc import ABC, abstractmethod

# Configure logging
log = logging.getLogger(__name__)

T = TypeVar('T', bound='BaseACIObject')

class BaseACIObject(ABC):
    """
    Base class for all ACI objects.
    
    This class provides the fundamental functionality for all ACI objects,
    including JSON serialization, APIC communication, and object relationships.
    
    Attributes:
        name (str): The name of the object
        parent (Optional[BaseACIObject]): The parent object in the object hierarchy
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of object attributes
    """
    
    def __init__(self, name: str, parent: Optional['BaseACIObject'] = None) -> None:
        """
        Initialize a new ACI object.
        
        Args:
            name: The name of the object
            parent: Optional parent object in the object hierarchy
        """
        self.name = name
        self.parent = parent
        self.children: List[BaseACIObject] = []
        self.attributes: Dict[str, Any] = {}
        self._deleted = False
        
        if parent is not None:
            parent.add_child(self)
            
        log.debug("Created %s with name %s", self.__class__.__name__, name)
    
    def add_child(self, child: 'BaseACIObject') -> None:
        """
        Add a child object to this object.
        
        Args:
            child: The child object to add
        """
        if child not in self.children:
            self.children.append(child)
            log.debug("Added child %s to %s", child.name, self.name)
    
    def remove_child(self, child: 'BaseACIObject') -> None:
        """
        Remove a child object from this object.
        
        Args:
            child: The child object to remove
        """
        if child in self.children:
            self.children.remove(child)
            log.debug("Removed child %s from %s", child.name, self.name)
    
    @abstractmethod
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of this object.
        
        Returns:
            Dictionary containing the JSON representation
        """
        pass
    
    @classmethod
    @abstractmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this acitoolkit class.
        
        Returns:
            List of strings containing APIC class names
        """
        pass
    
    def _validate_input(self, value: Any, expected_type: Type, field_name: str) -> None:
        """
        Validate input parameters.
        
        Args:
            value: The value to validate
            expected_type: The expected type of the value
            field_name: The name of the field being validated
            
        Raises:
            TypeError: If the value is not of the expected type
        """
        if not isinstance(value, expected_type):
            raise TypeError(f"{field_name} must be of type {expected_type.__name__}, got {type(value).__name__}")
    
    def mark_deleted(self) -> None:
        """
        Mark this object as deleted.
        """
        self._deleted = True
        log.debug("Marked %s as deleted", self.name)
    
    def is_deleted(self) -> bool:
        """
        Check if this object is marked as deleted.
        
        Returns:
            True if the object is marked as deleted, False otherwise
        """
        return self._deleted

class BaseInterface(BaseACIObject):
    """
    Base class for all interface objects.
    
    This class extends BaseACIObject with interface-specific functionality.
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new interface object.
        
        Args:
            name: The name of the interface
            parent: Optional parent object in the object hierarchy
        """
        super().__init__(name, parent)
        self._interface_type: Optional[str] = None
        self._encap_type: Optional[str] = None
        self._encap_id: Optional[str] = None
    
    def is_interface(self) -> bool:
        """
        Check if this object is an interface.
        
        Returns:
            True if this object is an interface, False otherwise
        """
        return True
    
    def get_interface_type(self) -> Optional[str]:
        """
        Get the type of this interface.
        
        Returns:
            The interface type or None if not set
        """
        return self._interface_type
    
    def set_interface_type(self, interface_type: str) -> None:
        """
        Set the type of this interface.
        
        Args:
            interface_type: The interface type to set
        """
        self._validate_input(interface_type, str, "interface_type")
        self._interface_type = interface_type
        log.debug("Set interface type to %s for %s", interface_type, self.name) 