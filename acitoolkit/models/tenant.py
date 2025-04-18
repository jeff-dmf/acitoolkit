"""
Tenant and Application Profile classes for the ACI Toolkit.
This module contains classes for managing ACI tenants and application profiles.
"""

from typing import Optional, List, Dict, Any, Type
import logging
from ..core.base import BaseACIObject
from ..aciphysobject import Fabric
from ..acisession import Session
from ..aciTable import Table

log = logging.getLogger(__name__)

class Tenant(BaseACIObject):
    """
    ACI Tenant class.
    
    This class represents a tenant in the ACI fabric. A tenant is a logical container
    for application policies that enable an application to be deployed.
    
    Attributes:
        name (str): The name of the tenant
        parent (Optional[BaseACIObject]): The parent object (typically a Fabric)
        children (List[BaseACIObject]): List of child objects
        attributes (Dict[str, Any]): Dictionary of tenant attributes
    """
    
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Initialize a new tenant.
        
        Args:
            name: The name of the tenant
            parent: Optional parent object (typically a Fabric)
        """
        if parent is not None and not isinstance(parent, Fabric):
            raise TypeError('Parent must be None or an instance of Fabric class')
        super().__init__(name, parent)
        log.info("Created new tenant: %s", name)
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this tenant class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['fvTenant']
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the tenant.
        
        Returns:
            Dictionary containing the JSON representation of the tenant
        """
        return {
            'fvTenant': {
                'attributes': {
                    'name': self.name,
                    'status': 'created'
                }
            }
        }
    
    @classmethod
    def get(cls, session: Session, parent: Optional[BaseACIObject] = None) -> List['Tenant']:
        """
        Get all tenants from the APIC.
        
        Args:
            session: The Session instance used to communicate with the APIC
            parent: Optional parent object to limit the query scope
            
        Returns:
            List of Tenant instances
        """
        return cls.get_deep(session, names=(), limit_to=(), subtree='full', config_only=False, parent=parent)
    
    @staticmethod
    def get_table(tenants: List['Tenant'], title: str = '') -> Table:
        """
        Get a table of tenants.
        
        Args:
            tenants: List of Tenant instances
            title: Optional title for the table
            
        Returns:
            Table instance containing the tenant information
        """
        headers = ['Tenant', 'App Profiles', 'EPGs', 'Bridge Domains', 'Contracts']
        data = []
        for tenant in tenants:
            data.append([
                tenant.name,
                len(tenant.get_children(AppProfile)),
                len(tenant.get_children(EPG)),
                len(tenant.get_children(BridgeDomain)),
                len(tenant.get_children(Contract))
            ])
        return Table(data, headers, title=title)

class AppProfile(BaseACIObject):
    """
    ACI Application Profile class.
    
    This class represents an application profile in the ACI fabric. An application
    profile is a collection of endpoint groups (EPGs) and their associated policies.
    
    Attributes:
        name (str): The name of the application profile
        parent (Optional[BaseACIObject]): The parent object (typically a Tenant)
        children (List[BaseACIObject]): List of child objects
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
    
    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by this application profile class.
        
        Returns:
            List of strings containing APIC class names
        """
        return ['fvAp']
    
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
    def get(cls, session: Session, tenant: Optional[Tenant] = None) -> List['AppProfile']:
        """
        Get all application profiles from the APIC.
        
        Args:
            session: The Session instance used to communicate with the APIC
            tenant: Optional Tenant instance to limit the query scope
            
        Returns:
            List of AppProfile instances
        """
        if tenant is None:
            return cls.get_deep(session, names=(), limit_to=(), subtree='full', config_only=False)
        return cls.get_deep(session, names=(), limit_to=(), subtree='full', config_only=False, parent=tenant)
    
    @staticmethod
    def get_table(app_profiles: List['AppProfile'], title: str = '') -> Table:
        """
        Get a table of application profiles.
        
        Args:
            app_profiles: List of AppProfile instances
            title: Optional title for the table
            
        Returns:
            Table instance containing the application profile information
        """
        headers = ['App Profile', 'EPGs', 'Bridge Domains', 'Contracts']
        data = []
        for app_profile in app_profiles:
            data.append([
                app_profile.name,
                len(app_profile.get_children(EPG)),
                len(app_profile.get_children(BridgeDomain)),
                len(app_profile.get_children(Contract))
            ])
        return Table(data, headers, title=title)

    def add_app_profile(self, name: str) -> 'AppProfile':
        """
        Add a new application profile to this tenant.
        
        Args:
            name: The name of the application profile
            
        Returns:
            The newly created AppProfile object
        """
        from .app_profile import AppProfile
        app_profile = AppProfile(name, self)
        self.add_child(app_profile)
        return app_profile

    def add_bridge_domain(self, name: str) -> 'BridgeDomain':
        """
        Add a new bridge domain to this tenant.
        
        Args:
            name: The name of the bridge domain
            
        Returns:
            The newly created BridgeDomain object
        """
        from .network import BridgeDomain
        bridge_domain = BridgeDomain(name, self)
        self.add_child(bridge_domain)
        return bridge_domain

    def add_context(self, name: str) -> 'Context':
        """
        Add a new context to this tenant.
        
        Args:
            name: The name of the context
            
        Returns:
            The newly created Context object
        """
        from .network import Context
        context = Context(name, self)
        self.add_child(context)
        return context

    def add_filter(self, name: str) -> 'Filter':
        """
        Add a new filter to this tenant.
        
        Args:
            name: The name of the filter
            
        Returns:
            The newly created Filter object
        """
        from .contract import Filter
        filter_obj = Filter(name, self)
        self.add_child(filter_obj)
        return filter_obj

    def add_contract(self, name: str) -> 'Contract':
        """
        Add a new contract to this tenant.
        
        Args:
            name: The name of the contract
            
        Returns:
            The newly created Contract object
        """
        from .contract import Contract
        contract = Contract(name, self)
        self.add_child(contract)
        return contract 