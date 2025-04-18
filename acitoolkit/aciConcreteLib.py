#!/usr/bin/env python
################################################################################
#                                                                              #
################################################################################
#                                                                              #
# Copyright (c) 2015 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
# Licensed under the Apache License, Version 2.0 (the "License"); you may      #
# not use this file except in compliance with the License. You may obtain      #
# a copy of the License at                                                     #
#                                                                              #
# http://www.apache.org/licenses/LICENSE-2.0                                   #
#                                                                              #
# Unless required by applicable law or agreed to in writing, software          #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
################################################################################
"""
This is a library of all the Concrete classes that are on a switch.
"""
import copy
import re
from operator import itemgetter
from typing import Optional, Dict, Any, List, Type, Union, Tuple, Any

from .acibaseobject import BaseACIPhysObject
from .aciphysobject import Node
from .aciSearch import Searchable
from .aciTable import Table
from .acitoolkit import Context, EPG


class CommonConcreteObject(BaseACIPhysObject):
    """
    Intermediate abstract class that provides common methods for physical
    objects storing data in an 'attr' dictionary.
    """

    def __init__(self, parent: Optional[BaseACIPhysObject] = None) -> None:
        """Initialize the CommonConcreteObject.

        Args:
            parent: Optional parent object
        """
        self.attr: Dict[str, str] = {'dn': '', 'name': ''}
        super(CommonConcreteObject, self).__init__(parent=parent)

    def populate_children(self, deep: bool = False, include_concrete: bool = False) -> None:
        """Populates all of the children and then calls populate_children
        of those children if deep is True. This method should be
        overridden by any object that does have children.

        Args:
            deep: Whether to recursively populate children
            include_concrete: Whether to include concrete objects
        """
        pass

    def get_attributes(self, name: Optional[str] = None) -> Union[str, Dict[str, str]]:
        """Get the attributes of the object.

        Args:
            name: Optional name of specific attribute to get

        Returns:
            If name is specified, returns the value of that attribute.
            Otherwise returns the entire attributes dictionary.
        """
        if name is not None:
            return self.attr.get(name, '')
        return self.attr

    @property
    def dn(self) -> str:
        """Get the distinguished name of the object.

        Returns:
            The distinguished name as a string
        """
        return self.attr.get('dn', '')

    @dn.setter
    def dn(self, value: str) -> None:
        """Set the distinguished name of the object.

        Args:
            value: The distinguished name to set
        """
        self.attr['dn'] = value

    @property
    def name(self) -> str:
        """Get the name of the object.

        Returns:
            The name as a string
        """
        return self.attr.get('name', '')

    @name.setter
    def name(self, value: str) -> None:
        """Set the name of the object.

        Args:
            value: The name to set
        """
        self.attr['name'] = value

    def __eq__(self, other: object) -> bool:
        """Check if this object is equal to another object.

        Args:
            other: The object to compare with

        Returns:
            True if the objects are equal, False otherwise
        """
        if not isinstance(other, self.__class__):
            return False
        return self.dn == other.dn

    @staticmethod
    def _parse_dn_pod_node(dn: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse the pod and node from a distinguished name.

        Args:
            dn: The distinguished name to parse

        Returns:
            Tuple of (pod, node) where both are strings or None if not found
        """
        pod = None
        node = None
        if dn:
            match = re.search(r'/pod-(\d+)/', dn)
            if match:
                pod = match.group(1)
            match = re.search(r'/node-(\d+)/', dn)
            if match:
                node = match.group(1)
        return pod, node


class ConcreteArp(CommonConcreteObject):
    """This class defines a concrete ARP object.
    """

    def __init__(self, parent: Optional[BaseACIPhysObject] = None) -> None:
        """Initialize the ConcreteArp object.

        Args:
            parent: Optional parent object
        """
        super(ConcreteArp, self).__init__(parent=parent)
        self.attr['tenant'] = ''
        self.attr['context'] = ''
        self.attr['mac'] = ''
        self.attr['ip'] = ''
        self.attr['physical_interface'] = ''

    @staticmethod
    def _get_parent_class() -> Type[BaseACIPhysObject]:
        """Get the class of the parent object.

        Returns:
            The class of the parent object
        """
        return Node

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Get the parent DN from the child DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The parent DN
        """
        return dn.split('/sys/arp')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Get the instance name from the DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The instance name
        """
        name = dn.split('/sys/arp/inst/dom-')[1].split('/')[0]
        return name

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Get the APIC classes used by this acitoolkit class.

        Returns:
            List of strings containing APIC class names
        """
        resp = ['arpInst', 'arpDom', 'arpAdjEp']
        return resp

    @classmethod
    def get(cls, top: Any, parent: Optional[BaseACIPhysObject] = None) -> List['ConcreteArp']:
        """Get all of the ARP entries from the APIC.

        Args:
            top: The top level json object
            parent: Optional parent object

        Returns:
            List of ARP entries
        """
        cls.check_parent(parent)
        result = []

        arp_data = top.get_class('arpInst')[:]
        arp_data.extend(top.get_class('arpDom')[:])
        arp_data.extend(top.get_class('arpAdjEp')[:])

        for arp_object in arp_data:
            if 'arpAdjEp' in arp_object:
                arp = cls()
                arp._populate_from_attributes(arp_object['arpAdjEp']['attributes'])
                result.append(arp)
                if parent:
                    arp._parent = parent
                    arp._parent.add_child(arp)

        return result

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Populate the object from the APIC attributes.

        Args:
            attributes: Dictionary of attributes
        """
        self.attr['dn'] = str(attributes.get('dn', ''))
        self.attr['mac'] = str(attributes.get('mac', ''))
        self.attr['ip'] = str(attributes.get('ip', ''))
        self.attr['physical_interface'] = str(attributes.get('physIfId', ''))
        self.attr['oper_st'] = str(attributes.get('operSt', ''))

        if 'dom-' in self.attr['dn']:
            self.attr['context'] = self.attr['dn'].split('/dom-')[1].split('/')[0]
        else:
            self.attr['context'] = ''

        if ':' in self.attr['context']:
            self.attr['tenant'] = self.attr['context'].split(':')[0]
            self.attr['context'] = self.attr['context'].split(':')[1]
        else:
            self.attr['tenant'] = ''

    @staticmethod
    def get_table(arps: List['ConcreteArp'], title: str = '') -> List[Table]:
        """Create table of ARP information.

        Args:
            arps: List of ARP instances
            title: Title string for the table

        Returns:
            List of Table objects
        """
        result = []
        headers = ['Tenant',
                  'Context',
                  'MAC Address',
                  'IP Address',
                  'Physical Interface',
                  'Operational State']

        data = []
        for arp in sorted(arps, key=lambda x: (x.attr.get('tenant', ''), x.attr.get('context', ''),
                                              x.attr.get('mac', ''), x.attr.get('ip', ''))):
            data.append([
                arp.attr.get('tenant', ''),
                arp.attr.get('context', ''),
                arp.attr.get('mac', ''),
                arp.attr.get('ip', ''),
                arp.attr.get('physical_interface', ''),
                arp.attr.get('oper_st', '')
            ])

        result.append(Table(data, headers, title=title + 'ARP Entries'))
        return result

    def __str__(self) -> str:
        """Default print string.

        Returns:
            String containing basic object information
        """
        return 'ConcreteArp-' + self.attr.get('ip', '')


class ConcreteArpDomain(CommonConcreteObject):
    """This class defines a concrete ARP domain.
    """

    def __init__(self, parent: Optional[BaseACIPhysObject] = None) -> None:
        """Initialize the ConcreteArpDomain object.

        Args:
            parent: Optional parent object
        """
        super(ConcreteArpDomain, self).__init__(parent=parent)
        self.attr['name'] = ''
        self.attr['encap'] = ''
        self.attr['stats'] = ''

    @staticmethod
    def _get_parent_class() -> Type[BaseACIPhysObject]:
        """Get the class of the parent object.

        Returns:
            The class of the parent object
        """
        return Node

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Get the parent DN from the child DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The parent DN
        """
        return dn.split('/dom-')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Get the instance name from the DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The instance name
        """
        name = dn.split('/dom-')[1].split('/')[0]
        return name

    @staticmethod
    def _get_children_concrete_classes() -> List[Type[BaseACIPhysObject]]:
        """Get the classes of the children concrete objects.

        Returns:
            List of classes of child concrete objects
        """
        return []

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Get the APIC classes used by this acitoolkit class.

        Returns:
            List of strings containing APIC class names
        """
        return ['arpDom']

    @classmethod
    def get(cls, working_data: Dict[str, Any], parent: Optional[BaseACIPhysObject] = None) -> List['ConcreteArpDomain']:
        """Get all of the ARP domains from the APIC.

        Args:
            working_data: The working data containing the ARP information
            parent: Optional parent object

        Returns:
            List of ARP domains
        """
        return cls.get_obj(working_data, cls._get_apic_classes(), parent)

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Populate the object from the attributes.

        Args:
            attributes: Dictionary of attributes
        """
        self.attr['name'] = str(attributes.get('name', ''))
        self.attr['encap'] = str(attributes.get('encap', ''))
        self.attr['stats'] = str(attributes.get('stats', ''))

    @staticmethod
    def get_stats(apic_class: str, dn: str, working_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get the statistics for the ARP domain.

        Args:
            apic_class: The APIC class
            dn: The distinguished name
            working_data: The working data containing the statistics

        Returns:
            Dictionary containing the statistics
        """
        stats = {}
        if apic_class in working_data:
            for obj in working_data[apic_class]:
                if obj['attributes']['dn'] == dn:
                    stats = obj['attributes']
                    break
        return stats


class ConcreteArpEntry(CommonConcreteObject):
    """This class defines a concrete ARP Entry.
    """

    def __init__(self, parent: Optional[BaseACIPhysObject] = None) -> None:
        """Initialize the ConcreteArpEntry object.

        Args:
            parent: Optional parent object
        """
        super(ConcreteArpEntry, self).__init__(parent=parent)
        self.attr['scope'] = ''
        self.attr['context'] = ''
        self.attr['tenant'] = ''
        self.attr['dclass'] = ''
        self.attr['sclass'] = ''
        self.attr['d_epg'] = ''
        self.attr['s_epg'] = ''
        self.attr['priority'] = ''
        self.attr['relative_priority'] = ''
        self.attr['pod'] = ''
        self.attr['node'] = ''

    @staticmethod
    def _get_parent_class() -> Type[BaseACIPhysObject]:
        """Get the class of the parent object.

        Returns:
            The class of the parent object
        """
        return Node

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Get the APIC classes used by this acitoolkit class.

        Returns:
            List of strings containing APIC class names
        """
        resp = ['actrlRule']
        return resp

    @classmethod
    def get(cls, top: Any, parent: Optional[BaseACIPhysObject] = None) -> List['ConcreteArpEntry']:
        """Get all of the ARP entries from the APIC.

        Args:
            top: The top level json object
            parent: Optional parent object

        Returns:
            List of Bridge Domains
        """
        cls.check_parent(parent)
        result = []

        bd_data = top.get_class('l2BD')
        for l2bd in bd_data:
            bd = cls()
            bd._populate_from_attributes(l2bd['l2BD']['attributes'])
            bd._get_context_info(bd.attr['dn'], top)
            result.append(bd)
            if parent:
                bd._parent = parent
                bd._parent.add_child(bd)
        return result

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Populate the object from the APIC attributes.

        Args:
            attributes: Dictionary of attributes
        """
        self.attr['dn'] = str(attributes.get('dn', ''))
        self.attr['oper_st'] = str(attributes.get('operSt', ''))
        self.attr['create_time'] = str(attributes.get('createTs', ''))
        self.attr['admin_state'] = str(attributes.get('adminSt', ''))

    def _get_context_info(self, dname: str, top: Any) -> None:
        """Get the context information for the Bridge Domain.

        Args:
            dname: The distinguished name
            top: The top level json object
        """
        bd_data = top.get_subtree('l3Ctx', dname)
        for ctx in bd_data:
            self.attr['context'] = str(ctx['l3Ctx']['attributes']['name'])
            self.attr['context_dn'] = str(ctx['l3Ctx']['attributes']['dn'])
            self.attr['tenant'] = str(ctx['l3Ctx']['attributes']['name']).split(':')[0]

    @staticmethod
    def get_table(bridge_domains: List['ConcreteBD'], title: str = '') -> List[Table]:
        """Create table of Bridge Domain information.

        Args:
            bridge_domains: List of Bridge Domain instances
            title: Title string for the table

        Returns:
            List of Table objects
        """
        result = []
        headers = ['Tenant',
                  'Context',
                  'Bridge Domain',
                  'Create Time',
                  'Admin State',
                  'Oper State']

        data = []
        for bdomain in sorted(bridge_domains, key=lambda x: (x.attr.get('tenant', ''), x.attr.get('context', ''),
                                                           x.attr.get('dn', ''))):
            data.append([
                bdomain.attr.get('tenant', ''),
                bdomain.attr.get('context', ''),
                bdomain.attr.get('dn', ''),
                bdomain.attr.get('create_time', ''),
                bdomain.attr.get('admin_state', ''),
                bdomain.attr.get('oper_st', '')
            ])

        result.append(Table(data, headers, title=title + 'Bridge Domains'))
        return result

    def __str__(self) -> str:
        """Default print string.

        Returns:
            String containing basic object information
        """
        return 'ConcreteBD-' + self.attr.get('dn', '')


class ConcreteSVI(CommonConcreteObject):
    """This class defines a concrete SVI.
    """

    def __init__(self, parent: Optional[BaseACIPhysObject] = None) -> None:
        """Initialize the ConcreteSVI object.

        Args:
            parent: Optional parent object
        """
        super(ConcreteSVI, self).__init__(parent=parent)
        self.attr['admin_state'] = ''
        self.attr['mac'] = ''
        self.attr['mtu'] = ''
        self.attr['vlan_id'] = ''

    @staticmethod
    def _get_parent_class() -> Type[BaseACIPhysObject]:
        """Get the class of the parent object.

        Returns:
            The class of the parent object
        """
        return Node

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Get the parent DN from the child DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The parent DN
        """
        return dn.split('/svi-')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Get the instance name from the DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The instance name
        """
        name = dn.split('/svi-')[1].split('/')[0]
        return name

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Get the APIC classes used by this acitoolkit class.

        Returns:
            List of strings containing APIC class names
        """
        resp = ['sviIf']
        return resp

    @classmethod
    def get(cls, top: Any, parent: Optional[BaseACIPhysObject] = None) -> List['ConcreteSVI']:
        """Get all of the SVIs from the APIC.

        Args:
            top: The top level json object
            parent: Optional parent object

        Returns:
            List of SVIs
        """
        cls.check_parent(parent)
        result = []

        data = top.get_class('sviIf')
        for obj in data:
            svi = cls()
            svi._populate_from_attributes(obj['sviIf']['attributes'])
            result.append(svi)
            if parent:
                svi._parent = parent
                svi._parent.add_child(svi)
        return result

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Populate the object from the APIC attributes.

        Args:
            attributes: Dictionary of attributes
        """
        self.attr['dn'] = str(attributes.get('dn', ''))
        self.attr['admin_state'] = str(attributes.get('adminSt', ''))
        self.attr['mac'] = str(attributes.get('mac', ''))
        self.attr['mtu'] = str(attributes.get('mtu', ''))
        self.attr['vlan_id'] = str(attributes.get('vlanId', ''))

    @staticmethod
    def get_table(svis: List['ConcreteSVI'], title: str = '') -> List[Table]:
        """Create table of SVI information.

        Args:
            svis: List of SVI instances
            title: Title string for the table

        Returns:
            List of Table objects
        """
        result = []
        headers = ['Name',
                  'Admin State',
                  'MAC',
                  'MTU',
                  'VLAN']

        data = []
        for svi in sorted(svis, key=lambda x: x.attr.get('vlan_id', '')):
            data.append([
                svi.name,
                svi.attr.get('admin_state', ''),
                svi.attr.get('mac', ''),
                svi.attr.get('mtu', ''),
                svi.attr.get('vlan_id', '')
            ])

        result.append(Table(data, headers, title=title + 'SVIs'))
        return result

    def __str__(self) -> str:
        """Default print string.

        Returns:
            String containing basic object information
        """
        return 'ConcreteSVI'

    def __eq__(self, other: object) -> bool:
        """Check if two SVIs are equal.

        Args:
            other: Other object to compare to

        Returns:
            True if equal, False otherwise
        """
        if isinstance(other, self.__class__):
            self_key = (self.get_parent(), self.attr.get('vlan_id', ''))
            other_key = (other.get_parent(), other.attr.get('vlan_id', ''))
            return self_key == other_key
        return NotImplemented


class ConcreteLoopback(CommonConcreteObject):
    """
    This class defines a concrete Loopback interface.
    """

    def __init__(self, parent: Optional[BaseACIPhysObject] = None) -> None:
        """Initialize the ConcreteLoopback object.

        Args:
            parent: Optional parent object
        """
        super(ConcreteLoopback, self).__init__(parent=parent)
        self.attr['id'] = ''
        self.attr['ip'] = ''
        self.attr['mac'] = ''
        self.attr['name'] = ''
        self.attr['status'] = ''
        self.attr['type'] = ''

    @staticmethod
    def _get_parent_class() -> Type[BaseACIPhysObject]:
        """Get the class of the parent object.

        Returns:
            The class of the parent object
        """
        return Node

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Get the parent DN from the child DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The parent DN
        """
        return dn.split('/loopback-')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Get the instance name from the DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The instance name
        """
        name = dn.split('/loopback-')[1].split('/')[0]
        return name

    @staticmethod
    def _get_children_concrete_classes() -> List[Type[BaseACIPhysObject]]:
        """Get the classes of the children concrete objects.

        Returns:
            List of classes of child concrete objects
        """
        return []

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Get the APIC classes used by this acitoolkit class.

        Returns:
            List of strings containing APIC class names
        """
        return ['loopbackIf']

    @classmethod
    def get(cls, top: Any, parent: Optional[BaseACIPhysObject] = None) -> List['ConcreteLoopback']:
        """Get all of the Loopback interfaces from the APIC.

        Args:
            top: The top level json object
            parent: Optional parent object

        Returns:
            List of Loopback interfaces
        """
        return cls.get_obj(top, cls._get_apic_classes(), parent)

    @staticmethod
    def get_table(loopbacks: List['ConcreteLoopback'], title: str = '') -> Table:
        """Create a table of Loopback interfaces.

        Args:
            loopbacks: List of Loopback interfaces
            title: Optional title for the table

        Returns:
            Table object containing the Loopback information
        """
        result = Table()
        result.title = 'Loopback Interfaces'
        if title:
            result.title = title + ' ' + result.title
        result.add_row(['ID', 'IP Address', 'MAC Address', 'Name', 'Status', 'Type'])
        result.add_row(['----', '----------', '-----------', '----', '------', '----'])
        for loopback in sorted(loopbacks, key=itemgetter('id')):
            result.add_row([loopback.attr['id'], loopback.attr['ip'], loopback.attr['mac'],
                          loopback.attr['name'], loopback.attr['status'], loopback.attr['type']])
        return result

    def __str__(self) -> str:
        """Get a string representation of the Loopback interface.

        Returns:
            String representation of the Loopback interface
        """
        return 'Loopback Interface: ID={0}, IP={1}, MAC={2}, Name={3}'.format(
            self.attr['id'], self.attr['ip'], self.attr['mac'], self.attr['name'])


class ConcreteLoopbackEntry(CommonConcreteObject):
    """
    This class defines a concrete Loopback entry.
    """

    def __init__(self, parent: Optional[BaseACIPhysObject] = None) -> None:
        """Initialize the ConcreteLoopbackEntry object.

        Args:
            parent: Optional parent object
        """
        super(ConcreteLoopbackEntry, self).__init__(parent=parent)
        self.attr['id'] = ''
        self.attr['ip'] = ''
        self.attr['mac'] = ''
        self.attr['name'] = ''
        self.attr['status'] = ''
        self.attr['type'] = ''

    @staticmethod
    def _get_parent_class() -> Type[BaseACIPhysObject]:
        """Get the class of the parent object.

        Returns:
            The class of the parent object
        """
        return ConcreteLoopback

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Get the parent DN from the child DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The parent DN
        """
        return dn.split('/entry-')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Get the instance name from the DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The instance name
        """
        name = dn.split('/entry-')[1].split('/')[0]
        return name

    @staticmethod
    def _get_children_concrete_classes() -> List[Type[BaseACIPhysObject]]:
        """Get the classes of the children concrete objects.

        Returns:
            List of classes of child concrete objects
        """
        return []

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Get the APIC classes used by this acitoolkit class.

        Returns:
            List of strings containing APIC class names
        """
        return ['loopbackEntry']

    @classmethod
    def get(cls, top: Any, parent: Optional[BaseACIPhysObject] = None) -> List['ConcreteLoopbackEntry']:
        """Get all of the Loopback entries from the APIC.

        Args:
            top: The top level json object
            parent: Optional parent object

        Returns:
            List of Loopback entries
        """
        return cls.get_obj(top, cls._get_apic_classes(), parent)

    @staticmethod
    def get_table(loopback_entries: List['ConcreteLoopbackEntry'], title: str = '') -> Table:
        """Create a table of Loopback entries.

        Args:
            loopback_entries: List of Loopback entries
            title: Optional title for the table

        Returns:
            Table object containing the Loopback information
        """
        result = Table()
        result.title = 'Loopback Entries'
        if title:
            result.title = title + ' ' + result.title
        result.add_row(['ID', 'IP Address', 'MAC Address', 'Name', 'Status', 'Type'])
        result.add_row(['----', '----------', '-----------', '----', '------', '----'])
        for entry in sorted(loopback_entries, key=itemgetter('id')):
            result.add_row([entry.attr['id'], entry.attr['ip'], entry.attr['mac'],
                          entry.attr['name'], entry.attr['status'], entry.attr['type']])
        return result

    def __str__(self) -> str:
        """Get a string representation of the Loopback entry.

        Returns:
            String representation of the Loopback entry
        """


class ConcreteContext(CommonConcreteObject):
    """This class defines a concrete Context.
    """

    def __init__(self, parent: Optional[BaseACIPhysObject] = None) -> None:
        """Initialize the ConcreteContext object.

        Args:
            parent: Optional parent object
        """
        super(ConcreteContext, self).__init__(parent=parent)
        self.attr['tenant'] = ''
        self.attr['context'] = ''

    @staticmethod
    def _get_parent_class() -> Type[BaseACIPhysObject]:
        """Get the class of the parent object.

        Returns:
            The class of the parent object
        """
        return Node

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Get the parent DN from the child DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The parent DN
        """
        return dn.split('/ctx-')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Get the instance name from the DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The instance name
        """
        name = dn.split('/ctx-[vxlan-')[1].split(']/')[0]
        return name

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Get the APIC classes used by this acitoolkit class.

        Returns:
            List of strings containing APIC class names
        """
        resp = ['l3Ctx']
        return resp

    @classmethod
    def get(cls, top: Any, parent: Optional[BaseACIPhysObject] = None) -> List['ConcreteContext']:
        """Get all of the Contexts from the APIC.

        Args:
            top: The top level json object
            parent: Optional parent object

        Returns:
            List of Contexts
        """
        cls.check_parent(parent)
        result = []

        ctx_data = top.get_class('l3Ctx')
        for ctx in ctx_data:
            context = cls()
            context._populate_from_attributes(ctx['l3Ctx']['attributes'])
            result.append(context)
            if parent:
                context._parent = parent
                context._parent.add_child(context)
        return result

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Populate the object from the APIC attributes.

        Args:
            attributes: Dictionary of attributes
        """
        self.attr['dn'] = str(attributes.get('dn', ''))
        self.attr['name'] = str(attributes.get('name', ''))
        self.attr['scope'] = str(attributes.get('scope', ''))
        self.attr['pcTag'] = str(attributes.get('pcTag', ''))
        self.attr['seg'] = str(attributes.get('seg', ''))
        if ':' in self.attr['name']:
            self.attr['tenant'] = self.attr['name'].split(':')[0]
            self.attr['context'] = self.attr['name'].split(':')[1]
        else:
            self.attr['tenant'] = ''
            self.attr['context'] = self.attr['name']

    @staticmethod
    def get_table(contexts: List['ConcreteContext'], title: str = '') -> List[Table]:
        """Create table of Context information.

        Args:
            contexts: List of Context instances
            title: Title string for the table

        Returns:
            List of Table objects
        """
        result = []
        headers = ['Tenant',
                  'Context',
                  'VNID',
                  'Scope',
                  'pcTag',
                  'Segment ID']

        data = []
        for context in sorted(contexts, key=lambda x: (x.attr.get('tenant', ''), x.attr.get('context', ''))):
            data.append([
                context.attr.get('tenant', ''),
                context.attr.get('context', ''),
                context.attr.get('name', ''),
                context.attr.get('scope', ''),
                context.attr.get('pcTag', ''),
                context.attr.get('seg', '')
            ])

        result.append(Table(data, headers, title=title + 'Contexts'))
        return result

    def __str__(self) -> str:
        """Default print string.

        Returns:
            String containing basic object information
        """
        return 'ConcreteContext-' + self.attr.get('name', '')


class ConcreteOverlay(CommonConcreteObject):
    """This class defines a concrete Overlay.
    """

    def __init__(self, parent: Optional[BaseACIPhysObject] = None) -> None:
        """Initialize the ConcreteOverlay object.

        Args:
            parent: Optional parent object
        """
        super(ConcreteOverlay, self).__init__(parent=parent)
        self.attr['proxy_ip_mac'] = ''
        self.attr['proxy_ip_v4'] = ''
        self.attr['proxy_ip_v6'] = ''
        self.attr['src_tep_ip'] = ''
        self.attr['vpc_tep_ip'] = ''

    @staticmethod
    def _get_parent_class() -> Type[BaseACIPhysObject]:
        """Get the class of the parent object.

        Returns:
            The class of the parent object
        """
        return Node

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Get the parent DN from the child DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The parent DN
        """
        return dn.split('/overlay')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Get the instance name from the DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The instance name
        """
        name = dn.split('/overlay')[1].split('/')[0]
        return name

    @staticmethod
    def _get_children_concrete_classes() -> List[Type[BaseACIPhysObject]]:
        """Get the classes of the children concrete objects.

        Returns:
            List of classes of child concrete objects
        """
        return [ConcreteTunnel]

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Get the APIC classes used by this acitoolkit class.

        Returns:
            List of strings containing APIC class names
        """
        resp = ['topoctrlOverlayBootstrap']
        return resp

    @classmethod
    def get(cls, top: Any, parent: Optional[BaseACIPhysObject] = None) -> List['ConcreteOverlay']:
        """Get all of the Overlays from the APIC.

        Args:
            top: The top level json object
            parent: Optional parent object

        Returns:
            List of Overlays
        """
        cls.check_parent(parent)
        result = []

        data = top.get_class('topoctrlOverlayBootstrap')
        for obj in data:
            overlay = cls()
            overlay._populate_from_attributes(obj['topoctrlOverlayBootstrap']['attributes'])
            result.append(overlay)
            if parent:
                overlay._parent = parent
                overlay._parent.add_child(overlay)
        return result

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Populate the object from the APIC attributes.

        Args:
            attributes: Dictionary of attributes
        """
        self.attr['dn'] = str(attributes.get('dn', ''))
        self.attr['proxy_ip_mac'] = str(attributes.get('proxyIpMac', ''))
        self.attr['proxy_ip_v4'] = str(attributes.get('proxyIpv4', ''))
        self.attr['proxy_ip_v6'] = str(attributes.get('proxyIpv6', ''))
        self.attr['src_tep_ip'] = str(attributes.get('srcTepIp', ''))
        self.attr['vpc_tep_ip'] = str(attributes.get('vpcTepIp', ''))

    @staticmethod
    def get_table(overlays: List['ConcreteOverlay'], title: str = '') -> List[Table]:
        """Create table of Overlay information.

        Args:
            overlays: List of Overlay instances
            title: Title string for the table

        Returns:
            List of Table objects
        """
        result = []
        headers = ['Source TEP IP',
                  'VPC TEP IP',
                  'MAC Proxy IP',
                  'IPv4 Proxy IP',
                  'IPv6 Proxy IP']

        data = []
        for overlay in sorted(overlays, key=lambda x: x.attr.get('src_tep_ip', '')):
            data.append([
                overlay.attr.get('src_tep_ip', ''),
                overlay.attr.get('vpc_tep_ip', ''),
                overlay.attr.get('proxy_ip_mac', ''),
                overlay.attr.get('proxy_ip_v4', ''),
                overlay.attr.get('proxy_ip_v6', '')
            ])

        result.append(Table(data, headers, title=title + 'Overlays'))
        return result

    def __str__(self) -> str:
        """Default print string.

        Returns:
            String containing basic object information
        """
        return 'ConcreteOverlay'

    def __eq__(self, other: object) -> bool:
        """Check if two Overlays are equal.

        Args:
            other: Other object to compare to

        Returns:
            True if equal, False otherwise
        """
        if isinstance(other, self.__class__):
            self_key = self.get_parent()
            other_key = other.get_parent()
            return self_key == other_key
        return NotImplemented


class ConcreteBD(CommonConcreteObject):
    """This class defines a concrete Bridge Domain.
    """

    def __init__(self, parent: Optional[BaseACIPhysObject] = None) -> None:
        """Initialize the ConcreteBD object.

        Args:
            parent: Optional parent object
        """
        super(ConcreteBD, self).__init__(parent=parent)
        self.attr['tenant'] = ''
        self.attr['context'] = ''
        self.attr['name'] = ''
        self.attr['oper_st'] = ''
        self.attr['create_time'] = ''
        self.attr['admin_state'] = ''

    @staticmethod
    def _get_parent_class() -> Type[BaseACIPhysObject]:
        """Get the class of the parent object.

        Returns:
            The class of the parent object
        """
        return Node

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Get the parent DN from the child DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The parent DN
        """
        return dn.split('/bd-')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Get the instance name from the DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The instance name
        """
        name = dn.split('/bd-')[1].split('/')[0]
        return name

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Get the APIC classes used by this acitoolkit class.

        Returns:
            List of strings containing APIC class names
        """
        resp = ['l2BD']
        return resp

    @classmethod
    def get(cls, top: Any, parent: Optional[BaseACIPhysObject] = None) -> List['ConcreteBD']:
        """Get all of the Bridge Domains from the APIC.

        Args:
            top: The top level json object
            parent: Optional parent object

        Returns:
            List of Bridge Domains
        """
        cls.check_parent(parent)
        result = []

        data = top.get_class('l2BD')
        for obj in data:
            bd = cls()
            bd._populate_from_attributes(obj['l2BD']['attributes'])
            result.append(bd)
            if parent:
                bd._parent = parent
                bd._parent.add_child(bd)
        return result

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Populate the object from the APIC attributes.

        Args:
            attributes: Dictionary of attributes
        """
        self.attr['dn'] = str(attributes.get('dn', ''))
        self.attr['name'] = str(attributes.get('name', ''))
        self.attr['oper_st'] = str(attributes.get('operSt', ''))
        self.attr['create_time'] = str(attributes.get('createTs', ''))
        self.attr['admin_state'] = str(attributes.get('adminSt', ''))

    @staticmethod
    def get_table(bridge_domains: List['ConcreteBD'], title: str = '') -> List[Table]:
        """Create table of Bridge Domain information.

        Args:
            bridge_domains: List of Bridge Domain instances
            title: Title string for the table

        Returns:
            List of Table objects
        """
        result = []
        headers = ['Tenant',
                  'Context',
                  'Bridge Domain',
                  'Create Time',
                  'Admin State',
                  'Oper State']

        data = []
        for bdomain in sorted(bridge_domains, key=lambda x: (x.attr.get('tenant', ''), x.attr.get('context', ''),
                                                           x.attr.get('name', ''))):
            data.append([
                bdomain.attr.get('tenant', ''),
                bdomain.attr.get('context', ''),
                bdomain.attr.get('name', ''),
                bdomain.attr.get('create_time', ''),
                bdomain.attr.get('admin_state', ''),
                bdomain.attr.get('oper_st', '')
            ])

        result.append(Table(data, headers, title=title + 'Bridge Domains'))
        return result

    def __str__(self) -> str:
        """Default print string.

        Returns:
            String containing basic object information
        """
        return 'ConcreteBD-' + self.attr.get('name', '')

    def __eq__(self, other: object) -> bool:
        """Check if two Bridge Domains are equal.

        Args:
            other: Other object to compare to

        Returns:
            True if equal, False otherwise
        """
        if isinstance(other, self.__class__):
            self_key = (self.get_parent(), self.attr.get('name', ''))
            other_key = (other.get_parent(), other.attr.get('name', ''))
            return self_key == other_key
        return NotImplemented


class ConcreteTunnel(CommonConcreteObject):
    """This class defines a concrete Tunnel.
    """

    def __init__(self, parent: Optional[BaseACIPhysObject] = None) -> None:
        """Initialize the ConcreteTunnel object.

        Args:
            parent: Optional parent object
        """
        super(ConcreteTunnel, self).__init__(parent=parent)
        self.attr['id'] = ''
        self.attr['type'] = ''
        self.attr['src_tep_ip'] = ''
        self.attr['dest_tep_ip'] = ''
        self.attr['context'] = ''
        self.attr['oper_st'] = ''
        self.attr['oper_st_qual'] = ''

    @staticmethod
    def _get_parent_class() -> Type[BaseACIPhysObject]:
        """Get the class of the parent object.

        Returns:
            The class of the parent object
        """
        return ConcreteOverlay

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Get the parent DN from the child DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The parent DN
        """
        return dn.split('/tunnel-')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Get the instance name from the DN.

        Args:
            dn: The distinguished name URL

        Returns:
            The instance name
        """
        name = dn.split('/tunnel-')[1].split('/')[0]
        return name

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Get the APIC classes used by this acitoolkit class.

        Returns:
            List of strings containing APIC class names
        """
        resp = ['tunnelIf']
        return resp

    @classmethod
    def get(cls, top: Any, parent: Optional[BaseACIPhysObject] = None) -> List['ConcreteTunnel']:
        """Get all of the Tunnels from the APIC.

        Args:
            top: The top level json object
            parent: Optional parent object

        Returns:
            List of Tunnels
        """
        cls.check_parent(parent)
        result = []

        data = top.get_class('tunnelIf')
        for obj in data:
            tunnel = cls()
            tunnel._populate_from_attributes(obj['tunnelIf']['attributes'])
            result.append(tunnel)
            if parent:
                tunnel._parent = parent
                tunnel._parent.add_child(tunnel)
        return result

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Populate the object from the APIC attributes.

        Args:
            attributes: Dictionary of attributes
        """
        self.attr['dn'] = str(attributes.get('dn', ''))
        self.attr['id'] = str(attributes.get('id', ''))
        self.attr['type'] = str(attributes.get('type', ''))
        self.attr['src_tep_ip'] = str(attributes.get('srcTepIp', ''))
        self.attr['dest_tep_ip'] = str(attributes.get('destTepIp', ''))
        self.attr['context'] = str(attributes.get('context', ''))
        self.attr['oper_st'] = str(attributes.get('operSt', ''))
        self.attr['oper_st_qual'] = str(attributes.get('operStQual', ''))

    @staticmethod
    def get_table(tunnels: List['ConcreteTunnel'], title: str = '') -> List[Table]:
        """Create table of Tunnel information.

        Args:
            tunnels: List of Tunnel instances
            title: Title string for the table

        Returns:
            List of Table objects
        """
        result = []
        headers = ['ID',
                  'Type',
                  'Source TEP IP',
                  'Destination TEP IP',
                  'Context',
                  'Oper State',
                  'Oper Qualifier']

        data = []
        for tunnel in sorted(tunnels, key=lambda x: x.attr.get('id', '')):
            data.append([
                tunnel.attr.get('id', ''),
                tunnel.attr.get('type', ''),
                tunnel.attr.get('src_tep_ip', ''),
                tunnel.attr.get('dest_tep_ip', ''),
                tunnel.attr.get('context', ''),
                tunnel.attr.get('oper_st', ''),
                tunnel.attr.get('oper_st_qual', '')
            ])

        result.append(Table(data, headers, title=title + 'Tunnels'))
        return result

    def __str__(self) -> str:
        """Default print string.

        Returns:
            String containing basic object information
        """
        return 'ConcreteTunnel-' + self.attr.get('id', '')

    def __eq__(self, other: object) -> bool:
        """Check if two Tunnels are equal.

        Args:
            other: Other object to compare to

        Returns:
            True if equal, False otherwise
        """
        if isinstance(other, self.__class__):
            self_key = (self.get_parent(), self.attr.get('id', ''))
            other_key = (other.get_parent(), other.attr.get('id', ''))
            return self_key == other_key
        return NotImplemented
