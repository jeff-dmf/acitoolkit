"""
Monitoring classes for the ACI Toolkit.
This module contains classes for managing ACI monitoring components like faults,
health scores, and statistics.
"""

from typing import Optional, List, Dict, Any, Type
import logging
from datetime import datetime
from ..core.base import BaseACIObject
from ..acisession import Session
from ..aciTable import Table

log = logging.getLogger(__name__)

class Fault(BaseACIObject):
    """
    ACI Fault class.
    
    This class represents a fault in the ACI fabric. A fault is an event that
    indicates a problem or potential problem in the fabric.
    
    Attributes:
        name (str): The name of the fault
        parent (Optional[BaseACIObject]): The parent object
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of fault attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new fault.
        
        Args:
            name: The name of the fault
            parent: Optional parent object
        """
        super().__init__(name, parent)
        self.attributes = {
            'code': 'F0000',
            'severity': 'warning',
            'description': '',
            'occurred': datetime.now().isoformat(),
            'status': 'active'
        }
        log.info("Created new fault: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this fault class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['fault:Inst']
    
    def set_code(self, code: str) -> None:
        """
        Set the code for this fault.
        
        Args:
            code: The fault code
        """
        self.attributes['code'] = code
    
    def get_code(self) -> str:
        """
        Get the code for this fault.
        
        Returns:
            The fault code
        """
        return self.attributes.get('code', 'F0000')
    
    def set_severity(self, severity: str) -> None:
        """
        Set the severity for this fault.
        
        Args:
            severity: The severity ('critical', 'major', 'minor', 'warning')
        """
        self.attributes['severity'] = severity
    
    def get_severity(self) -> str:
        """
        Get the severity for this fault.
        
        Returns:
            The severity
        """
        return self.attributes.get('severity', 'warning')
    
    def set_description(self, description: str) -> None:
        """
        Set the description for this fault.
        
        Args:
            description: The fault description
        """
        self.attributes['description'] = description
    
    def get_description(self) -> str:
        """
        Get the description for this fault.
        
        Returns:
            The fault description
        """
        return self.attributes.get('description', '')
    
    def set_occurred(self, occurred: str) -> None:
        """
        Set the occurrence time for this fault.
        
        Args:
            occurred: The ISO format timestamp
        """
        self.attributes['occurred'] = occurred
    
    def get_occurred(self) -> str:
        """
        Get the occurrence time for this fault.
        
        Returns:
            The ISO format timestamp
        """
        return self.attributes.get('occurred', datetime.now().isoformat())
    
    def set_status(self, status: str) -> None:
        """
        Set the status for this fault.
        
        Args:
            status: The status ('active', 'cleared')
        """
        self.attributes['status'] = status
    
    def get_status(self) -> str:
        """
        Get the status for this fault.
        
        Returns:
            The status
        """
        return self.attributes.get('status', 'active')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the fault.
        
        Returns:
            Dictionary containing the JSON representation of the fault
        """
        return {
            'fault:Inst': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class HealthScore(BaseACIObject):
    """
    ACI Health Score class.
    
    This class represents a health score in the ACI fabric. A health score is
    a numerical value that indicates the overall health of a component.
    
    Attributes:
        name (str): The name of the health score
        parent (Optional[BaseACIObject]): The parent object
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of health score attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new health score.
        
        Args:
            name: The name of the health score
            parent: Optional parent object
        """
        super().__init__(name, parent)
        self.attributes = {
            'score': 100,
            'max_score': 100,
            'min_score': 0,
            'last_updated': datetime.now().isoformat()
        }
        log.info("Created new health score: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this health score class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['health:Inst']
    
    def set_score(self, score: int) -> None:
        """
        Set the score for this health score.
        
        Args:
            score: The health score (0-100)
        """
        self.attributes['score'] = max(self.attributes['min_score'],
                                     min(self.attributes['max_score'], score))
    
    def get_score(self) -> int:
        """
        Get the score for this health score.
        
        Returns:
            The health score
        """
        return self.attributes.get('score', 100)
    
    def set_max_score(self, max_score: int) -> None:
        """
        Set the maximum score for this health score.
        
        Args:
            max_score: The maximum health score
        """
        self.attributes['max_score'] = max_score
    
    def get_max_score(self) -> int:
        """
        Get the maximum score for this health score.
        
        Returns:
            The maximum health score
        """
        return self.attributes.get('max_score', 100)
    
    def set_min_score(self, min_score: int) -> None:
        """
        Set the minimum score for this health score.
        
        Args:
            min_score: The minimum health score
        """
        self.attributes['min_score'] = min_score
    
    def get_min_score(self) -> int:
        """
        Get the minimum score for this health score.
        
        Returns:
            The minimum health score
        """
        return self.attributes.get('min_score', 0)
    
    def set_last_updated(self, last_updated: str) -> None:
        """
        Set the last update time for this health score.
        
        Args:
            last_updated: The ISO format timestamp
        """
        self.attributes['last_updated'] = last_updated
    
    def get_last_updated(self) -> str:
        """
        Get the last update time for this health score.
        
        Returns:
            The ISO format timestamp
        """
        return self.attributes.get('last_updated', datetime.now().isoformat())
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the health score.
        
        Returns:
            Dictionary containing the JSON representation of the health score
        """
        return {
            'health:Inst': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class Statistics(BaseACIObject):
    """
    ACI Statistics class.
    
    This class represents statistics in the ACI fabric. Statistics are numerical
    values that track various aspects of the fabric's operation.
    
    Attributes:
        name (str): The name of the statistics
        parent (Optional[BaseACIObject]): The parent object
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of statistics attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new statistics object.
        
        Args:
            name: The name of the statistics
            parent: Optional parent object
        """
        super().__init__(name, parent)
        self.attributes = {
            'type': 'interface',
            'interval': 300,
            'last_updated': datetime.now().isoformat(),
            'values': {}
        }
        log.info("Created new statistics: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this statistics class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['stats:Inst']
    
    def set_type(self, stats_type: str) -> None:
        """
        Set the type for this statistics.
        
        Args:
            stats_type: The statistics type ('interface', 'endpoint', 'fabric')
        """
        self.attributes['type'] = stats_type
    
    def get_type(self) -> str:
        """
        Get the type for this statistics.
        
        Returns:
            The statistics type
        """
        return self.attributes.get('type', 'interface')
    
    def set_interval(self, interval: int) -> None:
        """
        Set the collection interval for this statistics.
        
        Args:
            interval: The interval in seconds
        """
        self.attributes['interval'] = interval
    
    def get_interval(self) -> int:
        """
        Get the collection interval for this statistics.
        
        Returns:
            The interval in seconds
        """
        return self.attributes.get('interval', 300)
    
    def set_last_updated(self, last_updated: str) -> None:
        """
        Set the last update time for this statistics.
        
        Args:
            last_updated: The ISO format timestamp
        """
        self.attributes['last_updated'] = last_updated
    
    def get_last_updated(self) -> str:
        """
        Get the last update time for this statistics.
        
        Returns:
            The ISO format timestamp
        """
        return self.attributes.get('last_updated', datetime.now().isoformat())
    
    def set_value(self, key: str, value: Any) -> None:
        """
        Set a value for this statistics.
        
        Args:
            key: The value key
            value: The value
        """
        self.attributes['values'][key] = value
    
    def get_value(self, key: str) -> Any:
        """
        Get a value for this statistics.
        
        Args:
            key: The value key
            
        Returns:
            The value
        """
        return self.attributes['values'].get(key)
    
    def get_values(self) -> Dict[str, Any]:
        """
        Get all values for this statistics.
        
        Returns:
            Dictionary of values
        """
        return self.attributes.get('values', {})
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the statistics.
        
        Returns:
            Dictionary containing the JSON representation of the statistics
        """
        return {
            'stats:Inst': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        } 