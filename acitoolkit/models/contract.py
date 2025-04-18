"""
Contract classes for the ACI Toolkit.
This module contains classes for managing ACI contracts and their components.
"""

from typing import Optional, List, Dict, Any, Type
import logging
from ..core.base import BaseACIObject
from ..acisession import Session
from ..aciTable import Table

log = logging.getLogger(__name__)

class BaseContract(BaseACIObject):
    """
    Base class for all contract types.
    
    This class provides common functionality for all contract types, including
    scope management and filter handling.
    
    Attributes:
        name (str): The name of the contract
        parent (Optional[BaseACIObject]): The parent object (typically a Tenant)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of contract attributes
    """
    
    def __init__(self, contract_name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new contract.
        
        Args:
            contract_name: The name of the contract
            parent: Optional parent object (typically a Tenant)
        """
        super().__init__(contract_name, parent)
        log.info("Created new contract: %s", contract_name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this contract class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['vzBrCP']
    
    def set_scope(self, scope: str) -> None:
        """
        Set the scope of this contract.
        
        Args:
            scope: The scope to set ('context', 'global', 'tenant', 'application-profile')
        """
        self.attributes['scope'] = scope
    
    def get_scope(self) -> str:
        """
        Get the scope of this contract.
        
        Returns:
            The scope of the contract
        """
        return self.attributes.get('scope', 'context')
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the contract.
        
        Returns:
            Dictionary containing the JSON representation of the contract
        """
        return {
            'vzBrCP': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class Contract(BaseContract):
    """
    ACI Contract class.
    
    This class represents a contract in the ACI fabric. A contract defines the
    communication rules between EPGs.
    
    Attributes:
        name (str): The name of the contract
        parent (Optional[BaseACIObject]): The parent object (typically a Tenant)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of contract attributes
    """
    
    def __init__(self, contract_name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new contract.
        
        Args:
            contract_name: The name of the contract
            parent: Optional parent object (typically a Tenant)
        """
        super().__init__(contract_name, parent)
        self.attributes = {
            'scope': 'context'
        }
    
    @staticmethod
    def _get_name_dn_delimiters() -> List[str]:
        """
        Get the delimiters used in the name and DN of this contract.
        
        Returns:
            List of strings containing the delimiters
        """
        return ['brc-']
    
    def _get_instance_subscription_urls(self) -> List[str]:
        """
        Get the subscription URLs for this contract.
        
        Returns:
            List of strings containing the subscription URLs
        """
        return [f'/api/mo/uni/tn-{self.get_parent().name}/brc-{self.name}.json?subscription=yes']
    
    @staticmethod
    def get_table(contracts: List['Contract'], title: str = '') -> Table:
        """
        Get a table of contracts.
        
        Args:
            contracts: List of Contract instances
            title: Optional title for the table
            
        Returns:
            Table instance containing the contract information
        """
        headers = ['Contract', 'Scope', 'Subjects', 'Filters']
        data = []
        for contract in contracts:
            data.append([
                contract.name,
                contract.get_scope(),
                len(contract.get_children('ContractSubject')),
                len(contract.get_children('Filter'))
            ])
        return Table(data, headers, title=title)

class ContractSubject(BaseACIObject):
    """
    ACI Contract Subject class.
    
    This class represents a subject in an ACI contract. A subject defines the
    specific communication rules between EPGs.
    
    Attributes:
        name (str): The name of the contract subject
        parent (Optional[BaseACIObject]): The parent object (typically a Contract)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of contract subject attributes
    """
    
    def __init__(self, subject_name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new contract subject.
        
        Args:
            subject_name: The name of the contract subject
            parent: Optional parent object (typically a Contract)
        """
        super().__init__(subject_name, parent)
        log.info("Created new contract subject: %s", subject_name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this contract subject class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['vzSubj']
    
    def add_filter(self, filter_obj: 'Filter') -> None:
        """
        Add a filter to this contract subject.
        
        Args:
            filter_obj: The filter to add
        """
        self.add_child(filter_obj)
    
    def get_filters(self, deleted: bool = False) -> List['Filter']:
        """
        Get all filters associated with this contract subject.
        
        Args:
            deleted: Whether to include deleted filters
            
        Returns:
            List of Filter instances
        """
        return [child for child in self.get_children('Filter') if not deleted or child.is_deleted()]
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the contract subject.
        
        Returns:
            Dictionary containing the JSON representation of the contract subject
        """
        return {
            'vzSubj': {
                'attributes': {
                    'name': self.name,
                    'status': 'created'
                }
            }
        }

class Filter(BaseACIObject):
    """
    ACI Filter class.
    
    This class represents a filter in the ACI fabric. A filter defines the
    specific traffic patterns that are allowed or denied.
    
    Attributes:
        name (str): The name of the filter
        parent (Optional[BaseACIObject]): The parent object (typically a Tenant)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of filter attributes
    """
    
    def __init__(self, filter_name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new filter.
        
        Args:
            filter_name: The name of the filter
            parent: Optional parent object (typically a Tenant)
        """
        super().__init__(filter_name, parent)
        log.info("Created new filter: %s", filter_name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this filter class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['vzFilter']
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the filter.
        
        Returns:
            Dictionary containing the JSON representation of the filter
        """
        return {
            'vzFilter': {
                'attributes': {
                    'name': self.name,
                    'status': 'created'
                }
            }
        }

class FilterEntry(BaseACIObject):
    """
    ACI Filter Entry class.
    
    This class represents an entry in an ACI filter. A filter entry defines the
    specific traffic pattern that is allowed or denied.
    
    Attributes:
        name (str): The name of the filter entry
        parent (Optional[BaseACIObject]): The parent object (typically a Filter)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of filter entry attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None,
                 applyToFrag: str = '0', arpOpc: str = '0',
                 dFromPort: str = '0', dToPort: str = '0',
                 etherT: str = '0', prot: str = '0',
                 sFromPort: str = '0', sToPort: str = '0',
                 tcpRules: str = '0', stateful: str = '0',
                 icmpv4T: str = 'not-given', icmpv6T: str = 'not-given') -> None:
        """
        Initialize a new filter entry.
        
        Args:
            name: The name of the filter entry
            parent: Optional parent object (typically a Filter)
            applyToFrag: Whether to apply to fragments
            arpOpc: ARP operation code
            dFromPort: Destination port range start
            dToPort: Destination port range end
            etherT: Ethernet type
            prot: Protocol
            sFromPort: Source port range start
            sToPort: Source port range end
            tcpRules: TCP rules
            stateful: Whether the filter is stateful
            icmpv4T: ICMPv4 type
            icmpv6T: ICMPv6 type
        """
        super().__init__(name, parent)
        self.attributes = {
            'applyToFrag': applyToFrag,
            'arpOpc': arpOpc,
            'dFromPort': dFromPort,
            'dToPort': dToPort,
            'etherT': etherT,
            'prot': prot,
            'sFromPort': sFromPort,
            'sToPort': sToPort,
            'tcpRules': tcpRules,
            'stateful': stateful,
            'icmpv4T': icmpv4T,
            'icmpv6T': icmpv6T
        }
        log.info("Created new filter entry: %s", name)
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the filter entry.
        
        Returns:
            Dictionary containing the JSON representation of the filter entry
        """
        return {
            'vzEntry': {
                'attributes': {
                    'name': self.name,
                    'status': 'created',
                    **self.attributes
                }
            }
        }

class Taboo(BaseContract):
    """
    ACI Taboo class.
    
    This class represents a taboo in the ACI fabric. A taboo defines the
    communication rules that are explicitly denied between EPGs.
    
    Attributes:
        name (str): The name of the taboo
        parent (Optional[BaseACIObject]): The parent object (typically a Tenant)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of taboo attributes
    """
    
    def __init__(self, contract_name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new taboo.
        
        Args:
            contract_name: The name of the taboo
            parent: Optional parent object (typically a Tenant)
        """
        super().__init__(contract_name, parent)
        log.info("Created new taboo: %s", contract_name)
    
    @staticmethod
    def _get_name_dn_delimiters() -> List[str]:
        """
        Get the delimiters used in the name and DN of this taboo.
        
        Returns:
            List of strings containing the delimiters
        """
        return ['taboo-']
    
    def _get_instance_subscription_urls(self) -> List[str]:
        """
        Get the subscription URLs for this taboo.
        
        Returns:
            List of strings containing the subscription URLs
        """
        return [f'/api/mo/uni/tn-{self.get_parent().name}/taboo-{self.name}.json?subscription=yes']
    
    @staticmethod
    def get_table(taboos: List['Taboo'], title: str = '') -> Table:
        """
        Get a table of taboos.
        
        Args:
            taboos: List of Taboo instances
            title: Optional title for the table
            
        Returns:
            Table instance containing the taboo information
        """
        headers = ['Taboo', 'Scope', 'Subjects', 'Filters']
        data = []
        for taboo in taboos:
            data.append([
                taboo.name,
                taboo.get_scope(),
                len(taboo.get_children('ContractSubject')),
                len(taboo.get_children('Filter'))
            ])
        return Table(data, headers, title=title) 