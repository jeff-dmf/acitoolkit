################################################################################
#                                  _    ____ ___                               #
#                                 / \  / ___|_ _|                              #
#                                / _ \| |    | |                               #
#                               / ___ \ |___ | |                               #
#                         _____/_/   \_\____|___|_ _                           #
#                        |_   _|__   ___ | | | _(_) |_                         #
#                          | |/ _ \ / _ \| | |/ / | __|                        #
#                          | | (_) | (_) | |   <| | |_                         #
#                          |_|\___/ \___/|_|_|\_\_|\__|                        #
#                                                                              #
################################################################################
#                                                                              #
# Copyright (c) 2015 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
#    Licensed under the Apache License, Version 2.0 (the "License"); you may   #
#    not use this file except in compliance with the License. You may obtain   #
#    a copy of the License at                                                  #
#                                                                              #
#         http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                              #
#    Unless required by applicable law or agreed to in writing, software       #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
################################################################################
"""ACI Toolkit module for physical objects
"""
import copy
import logging
from operator import attrgetter, itemgetter
import re
from typing import Optional, Dict, Any, List, Union, Tuple, Type, TypeVar, Callable

from .acibaseobject import (
    BaseACIObject, BaseACIPhysModule, BaseACIPhysObject, BaseInterface
)
from .acicounters import AtomicCountersOnGoing, InterfaceStats
from .aciSearch import Searchable
from .acisession import Session
from .aciTable import Table
# TODO: resolve circular dependency and import only LogicalModel
import acitoolkit as ACI
from acitoolkit import Node


log = logging.getLogger(__name__)

T = TypeVar('T')

class Systemcontroller(BaseACIPhysModule):
    """This class defines a system controller module of a node.
    """

    def __init__(self, pod: str, node: str, slot: str, parent: Optional[BaseACIObject] = None) -> None:
        """Initialize the basic object.  This should be called by the
           init routines of inheriting subclasses.

        Args:
            pod: Pod ID
            node: Node ID
            slot: Slot ID
            parent: Optional parent object
        """
        self.pod: str = pod
        self.node: str = node
        self.slot: str = slot
        self.type: str = 'systemctrlcard'
        self.dn: str = 'topology/pod-{0}/node-{1}/sys/ch/bslot/board-{2}'.format(pod, node, slot)
        self.descr: str = ''
        self.status: str = ''
        self.hardware_version: str = ''
        self.hardware_vendor: str = ''
        self.serial: str = ''
        self.model: str = ''
        self.name: str = 'SysC-' + slot
        super(Systemcontroller, self).__init__(pod, node, slot, parent)

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Gets the APIC classes used by this acitoolkit class.

        Returns:
            list of strings containing APIC class names
        """
        return ['eqptBoard']

    @staticmethod
    def _get_parent_class() -> Type[BaseACIObject]:
        """Gets the class of the parent object

        Returns:
            class of parent object
        """
        return Node

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Gets the parent DN from the child DN

        Args:
            dn: string containing the distinguished name URL

        Returns:
            string containing the parent DN
        """
        return dn.split('/bslot')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Gets the instance name from the DN

        Args:
            dn: string containing the distinguished name URL

        Returns:
            string containing the instance name
        """
        name = dn.split('/board-')[1].split('/')[0]
        return name

    @classmethod
    def get(cls, session: Session, parent: Optional[BaseACIObject] = None) -> List['Systemcontroller']:
        """Gets all of the system controller modules from the APIC.
           If parent is specified, it will only get system controllers that are children of the parent.

        Args:
            session: Session instance used to communicate with the APIC
            parent: Parent instance to limit system controllers to a specific parent

        Returns:
            list of system controller modules
        """
        return cls.get_obj(session, cls._get_apic_classes(), parent)

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Fills in an object with the desired attributes.
           Overridden by inheriting classes to provide the specific attributes
           when getting objects from the APIC.

        Args:
            attributes: Dictionary containing the attributes to fill in
        """
        self.serial = str(attributes.get('ser', ''))
        self.model = str(attributes.get('model', ''))
        self.dn = str(attributes.get('dn', ''))
        self.descr = str(attributes.get('descr', ''))
        self.status = str(attributes.get('status', ''))
        self.hardware_version = str(attributes.get('hwVer', ''))
        self.hardware_vendor = str(attributes.get('vendor', ''))

    def __eq__(self, other: object) -> bool:
        """Checks equality between two Systemcontroller instances.

        Args:
            other: Instance to compare to

        Returns:
            True if equal, False if not equal
        """
        if isinstance(other, self.__class__):
            key_attrs = attrgetter('pod', 'node', 'slot')
            return key_attrs(self) == key_attrs(other)
        return NotImplemented


class Cluster(BaseACIObject):
    """
    Represents the global settings of the Cluster
    """
    def __init__(self, name: str, parent: Optional[BaseACIObject] = None) -> None:
        """
        Args:
            name: String containing the name of this Cluster object.
            parent: Optional parent object
        """
        super(Cluster, self).__init__(name, parent)
        self.name: str = name
        self.config_size: Optional[int] = None
        self.cluster_size: Optional[int] = None
        self.apics: List[str] = []

    @classmethod
    def get(cls, session: Session, parent: Optional[BaseACIObject] = None) -> 'Cluster':
        """Gets all of the Clusters from the APIC.

        Args:
            session: APIC session
            parent: Optional parent object

        Returns:
            Instance of Cluster class.
        """
        # start at top
        infra_query_url = '/api/node/class/infraCont.json'
        ret = session.get(infra_query_url)
        cluster_info = ret.json()['imdata']
        infra_cluster_url = '/api/node/class/infraClusterPol.json'
        ret = session.get(infra_cluster_url)
        ret_cluster = ret.json()['imdata']
        cluster = cls('apic-cluster', parent=parent)
        cluster.config_size = int(ret_cluster[0]['infraClusterPol']['attributes']['size'])
        for apic in cluster_info:
            cluster.apics.append(apic['infraCont']['attributes']['dn'])
        cluster._populate_from_attributes(cluster_info[0]['infraCont']['attributes'])
        return cluster

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Fills in an object with desired attributes.

        Args:
            attributes: Dictionary of attributes
        """
        self.cluster_size = int(attributes['size'])
        self.name = str(attributes['fbDmNm'])

    def get_config_size(self) -> Optional[int]:
        """
        Returns:
            configured size of the cluster, i.e. # of APICs
        """
        return self.config_size

    def get_cluster_size(self) -> Optional[int]:
        """
        Returns:
            reads information about the APIC cluster
        """
        return self.cluster_size

    def get_apics(self) -> List[str]:
        """
        Returns:
            list of APIC DNs
        """
        return self.apics


class Linecard(BaseACIPhysModule):
    """This class defines a line card module of a node.
    """

    def __init__(self, pod: str, node: str, slot: str, parent: Optional[BaseACIObject] = None) -> None:
        """Initialize the basic object.  This should be called by the
           init routines of inheriting subclasses.

        Args:
            pod: Pod ID
            node: Node ID
            slot: Slot ID
            parent: Optional parent object
        """
        self.pod: str = pod
        self.node: str = node
        self.slot: str = slot
        self.type: str = 'linecard'
        self.dn: str = 'topology/pod-{0}/node-{1}/sys/ch/lcslot-{2}/lc'.format(pod, node, slot)
        self.descr: str = ''
        self.status: str = ''
        self.hardware_version: str = ''
        self.hardware_vendor: str = ''
        self.serial: str = ''
        self.model: str = ''
        self.name: str = 'LC-' + slot
        super(Linecard, self).__init__(pod, node, slot, parent)

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Gets the APIC classes used by this acitoolkit class.

        Returns:
            list of strings containing APIC class names
        """
        return ['eqptLC']

    @staticmethod
    def _get_parent_class() -> Type[BaseACIObject]:
        """Gets the class of the parent object

        Returns:
            class of parent object
        """
        return Node

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Gets the parent DN from the child DN

        Args:
            dn: string containing the distinguished name URL

        Returns:
            string containing the parent DN
        """
        return dn.split('/lcslot')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Gets the instance name from the DN

        Args:
            dn: string containing the distinguished name URL

        Returns:
            string containing the instance name
        """
        name = dn.split('/lcslot-')[1].split('/')[0]
        return name

    @classmethod
    def get(cls, session: Session, parent: Optional[BaseACIObject] = None) -> List['Linecard']:
        """Gets all of the line card modules from the APIC.
           If parent is specified, it will only get line cards that are children of the parent.

        Args:
            session: Session instance used to communicate with the APIC
            parent: Parent instance to limit line cards to a specific parent

        Returns:
            list of line card modules
        """
        return cls.get_obj(session, cls._get_apic_classes(), parent)

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Fills in an object with the desired attributes.
           Overridden by inheriting classes to provide the specific attributes
           when getting objects from the APIC.

        Args:
            attributes: Dictionary containing the attributes to fill in
        """
        self.serial = str(attributes.get('ser', ''))
        self.model = str(attributes.get('model', ''))
        self.dn = str(attributes.get('dn', ''))
        self.descr = str(attributes.get('descr', ''))
        self.status = str(attributes.get('status', ''))
        self.hardware_version = str(attributes.get('hwVer', ''))
        self.hardware_vendor = str(attributes.get('vendor', ''))

    def __eq__(self, other: object) -> bool:
        """Checks equality between two Linecard instances.

        Args:
            other: Instance to compare to

        Returns:
            True if equal, False if not equal
        """
        if isinstance(other, self.__class__):
            key_attrs = attrgetter('pod', 'node', 'slot')
            return key_attrs(self) == key_attrs(other)
        return NotImplemented

    def __str__(self) -> str:
        """
        Returns:
            string representation of the linecard
        """
        return self.name

    @staticmethod
    def get_table(linecards: List['Linecard'], title: str = '') -> Table:
        """Will create table of linecard information for a given node

        Args:
            linecards: list of linecards
            title: optional title for the table

        Returns:
            Table object containing the linecard information
        """
        result = Table()
        result.title = 'Linecards'
        if title:
            result.title = title + result.title
        result.add_row(['Name', 'Model', 'Serial', 'Status', 'Description'])
        result.add_row(['----', '-----', '------', '------', '-----------'])
        for linecard in sorted(linecards, key=attrgetter('name')):
            result.add_row([linecard.name, linecard.model, linecard.serial,
                           linecard.oper_st, linecard.descr])
        return result


class Supervisorcard(BaseACIPhysModule):
    """This class defines a supervisor card module of a node.
    """

    def __init__(self, pod: str, node: str, slot: str, parent: Optional[BaseACIObject] = None) -> None:
        """Initialize the basic object.  This should be called by the
           init routines of inheriting subclasses.

        Args:
            pod: Pod ID
            node: Node ID
            slot: Slot ID
            parent: Optional parent object
        """
        self.pod: str = pod
        self.node: str = node
        self.slot: str = slot
        self.type: str = 'supervisor'
        self.dn: str = 'topology/pod-{0}/node-{1}/sys/ch/supslot-{2}/sup'.format(pod, node, slot)
        self.descr: str = ''
        self.status: str = ''
        self.hardware_version: str = ''
        self.hardware_vendor: str = ''
        self.serial: str = ''
        self.model: str = ''
        self.name: str = 'Sup-' + slot
        super(Supervisorcard, self).__init__(pod, node, slot, parent)

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Gets the APIC classes used by this acitoolkit class.

        Returns:
            list of strings containing APIC class names
        """
        return ['eqptSupC']

    @staticmethod
    def _get_parent_class() -> Type[BaseACIObject]:
        """Gets the class of the parent object

        Returns:
            class of parent object
        """
        return Node

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Gets the parent DN from the child DN

        Args:
            dn: string containing the distinguished name URL

        Returns:
            string containing the parent DN
        """
        return dn.split('/supslot')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Gets the instance name from the DN

        Args:
            dn: string containing the distinguished name URL

        Returns:
            string containing the instance name
        """
        name = dn.split('/supslot-')[1].split('/')[0]
        return name

    @classmethod
    def get(cls, session: Session, parent: Optional[BaseACIObject] = None) -> List['Supervisorcard']:
        """Gets all of the supervisor card modules from the APIC.
           If parent is specified, it will only get supervisor cards that are children of the parent.

        Args:
            session: Session instance used to communicate with the APIC
            parent: Parent instance to limit supervisor cards to a specific parent

        Returns:
            list of supervisor card modules
        """
        return cls.get_obj(session, cls._get_apic_classes(), parent)

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Fills in an object with the desired attributes.
           Overridden by inheriting classes to provide the specific attributes
           when getting objects from the APIC.

        Args:
            attributes: Dictionary containing the attributes to fill in
        """
        self.serial = str(attributes.get('ser', ''))
        self.model = str(attributes.get('model', ''))
        self.dn = str(attributes.get('dn', ''))
        self.descr = str(attributes.get('descr', ''))
        self.status = str(attributes.get('status', ''))
        self.hardware_version = str(attributes.get('hwVer', ''))
        self.hardware_vendor = str(attributes.get('vendor', ''))

    def __eq__(self, other: object) -> bool:
        """Checks equality between two Supervisorcard instances.

        Args:
            other: Instance to compare to

        Returns:
            True if equal, False if not equal
        """
        if isinstance(other, self.__class__):
            key_attrs = attrgetter('pod', 'node', 'slot')
            return key_attrs(self) == key_attrs(other)
        return NotImplemented

    @staticmethod
    def get_table(modules: List['Supervisorcard'], super_title: str = '') -> Table:
        """Will create table of supervisor card information for a given pod

        Args:
            modules: list of supervisor cards
            super_title: optional title for the table

        Returns:
            Table object containing the supervisor card information
        """
        result = Table()
        result.title = 'Supervisor Cards'
        if super_title:
            result.title = super_title + result.title
        result.add_row(['Name', 'Model', 'Serial', 'Status', 'Description'])
        result.add_row(['----', '-----', '------', '------', '-----------'])
        for module in sorted(modules, key=attrgetter('name')):
            result.add_row([module.name, module.model, module.serial,
                           module.oper_st, module.descr])
        return result


class Fantray(BaseACIPhysModule):
    """This class defines a fan tray module of a node.
    """

    def __init__(self, pod: str, node: str, slot: str, parent: Optional[BaseACIObject] = None) -> None:
        """Initialize the basic object.  This should be called by the
           init routines of inheriting subclasses.

        Args:
            pod: Pod ID
            node: Node ID
            slot: Slot ID
            parent: Optional parent object
        """
        self.pod: str = pod
        self.node: str = node
        self.slot: str = slot
        self.type: str = 'fantray'
        self.dn: str = 'topology/pod-{0}/node-{1}/sys/ch/fanslot-{2}/fantray'.format(pod, node, slot)
        self.descr: str = ''
        self.status: str = ''
        self.hardware_version: str = ''
        self.hardware_vendor: str = ''
        self.serial: str = ''
        self.model: str = ''
        self.name: str = 'FanTray-' + slot
        super(Fantray, self).__init__(pod, node, slot, parent)

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Gets the APIC classes used by this acitoolkit class.

        Returns:
            list of strings containing APIC class names
        """
        return ['eqptFt']

    @staticmethod
    def _get_parent_class() -> Type[BaseACIObject]:
        """Gets the class of the parent object

        Returns:
            class of parent object
        """
        return Node

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Gets the parent DN from the child DN

        Args:
            dn: string containing the distinguished name URL

        Returns:
            string containing the parent DN
        """
        return dn.split('/fanslot')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Gets the instance name from the DN

        Args:
            dn: string containing the distinguished name URL

        Returns:
            string containing the instance name
        """
        name = dn.split('/fanslot-')[1].split('/')[0]
        return name

    @classmethod
    def get(cls, session: Session, parent: Optional[BaseACIObject] = None) -> List['Fantray']:
        """Gets all of the fan tray modules from the APIC.
           If parent is specified, it will only get fan trays that are children of the parent.

        Args:
            session: Session instance used to communicate with the APIC
            parent: Parent instance to limit fan trays to a specific parent

        Returns:
            list of fan tray modules
        """
        return cls.get_obj(session, cls._get_apic_classes(), parent)

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Fills in an object with the desired attributes.
           Overridden by inheriting classes to provide the specific attributes
           when getting objects from the APIC.

        Args:
            attributes: Dictionary containing the attributes to fill in
        """
        self.serial = str(attributes.get('ser', ''))
        self.model = str(attributes.get('model', ''))
        self.dn = str(attributes.get('dn', ''))
        self.descr = str(attributes.get('descr', ''))
        self.status = str(attributes.get('status', ''))
        self.hardware_version = str(attributes.get('hwVer', ''))
        self.hardware_vendor = str(attributes.get('vendor', ''))

    def __eq__(self, other: object) -> bool:
        """Checks equality between two Fantray instances.

        Args:
            other: Instance to compare to

        Returns:
            True if equal, False if not equal
        """
        if isinstance(other, self.__class__):
            key_attrs = attrgetter('pod', 'node', 'slot')
            return key_attrs(self) == key_attrs(other)
        return NotImplemented

    def _get_firmware(self, dist_name: str) -> Tuple[Optional[str], Optional[str]]:
        """Gets the firmware version of the Fan tray
        from the firmwareFtRunning attribute of the
        ftrunning object under the ftfwstatuscont object.
        It will set the bios to None.

        Args:
            dist_name: distinguished name

        Returns:
            tuple of (firmware, bios)
        """
        firmware = None
        bios = None
        return firmware, bios

    @staticmethod
    def get_table(modules: List['Fantray'], title: str = '') -> Table:
        """Will create table of fan tray information for a given pod

        Args:
            modules: list of fan trays
            title: optional title for the table

        Returns:
            Table object containing the fan tray information
        """
        result = Table()
        result.title = 'Fan Trays'
        if title:
            result.title = title + result.title
        result.add_row(['Name', 'Model', 'Serial', 'Status', 'Description'])
        result.add_row(['----', '-----', '------', '------', '-----------'])
        for module in sorted(modules, key=attrgetter('name')):
            result.add_row([module.name, module.model, module.serial,
                           module.oper_st, module.descr])
        return result

    def __str__(self) -> str:
        """
        Returns:
            string representation of the fan tray
        """
        return self.name


class Fan(BaseACIPhysModule):
    """This class defines a fan module of a node.
    """

    def __init__(self, pod: str, node: str, slot: str, parent: Optional[BaseACIObject] = None) -> None:
        """Initialize the basic object.  This should be called by the
           init routines of inheriting subclasses.

        Args:
            pod: Pod ID
            node: Node ID
            slot: Slot ID
            parent: Optional parent object
        """
        self.pod: str = pod
        self.node: str = node
        self.slot: str = slot
        self.type: str = 'fan'
        self.dn: str = 'topology/pod-{0}/node-{1}/sys/ch/fanslot-{2}/fan'.format(pod, node, slot)
        self.descr: str = ''
        self.status: str = ''
        self.hardware_version: str = ''
        self.hardware_vendor: str = ''
        self.serial: str = ''
        self.model: str = ''
        self.name: str = 'Fan-' + slot
        super(Fan, self).__init__(pod, node, slot, parent)

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Gets the APIC classes used by this acitoolkit class.

        Returns:
            list of strings containing APIC class names
        """
        return ['eqptFan']

    @staticmethod
    def _get_parent_class() -> Type[BaseACIObject]:
        """Gets the class of the parent object

        Returns:
            class of parent object
        """
        return Fantray

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Gets the parent DN from the child DN

        Args:
            dn: string containing the distinguished name URL

        Returns:
            string containing the parent DN
        """
        return dn.split('/fanslot')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Gets the instance name from the DN

        Args:
            dn: string containing the distinguished name URL

        Returns:
            string containing the instance name
        """
        name = dn.split('/fanslot-')[1].split('/')[0]
        return name

    @classmethod
    def get(cls, session: Session, parent: Optional[BaseACIObject] = None) -> List['Fan']:
        """Gets all of the fan modules from the APIC.
           If parent is specified, it will only get fans that are children of the parent.

        Args:
            session: Session instance used to communicate with the APIC
            parent: Parent instance to limit fans to a specific parent

        Returns:
            list of fan modules
        """
        return cls.get_obj(session, cls._get_apic_classes(), parent)

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Fills in an object with the desired attributes.
           Overridden by inheriting classes to provide the specific attributes
           when getting objects from the APIC.

        Args:
            attributes: Dictionary containing the attributes to fill in
        """
        self.serial = str(attributes.get('ser', ''))
        self.model = str(attributes.get('model', ''))
        self.dn = str(attributes.get('dn', ''))
        self.descr = str(attributes.get('descr', ''))
        self.status = str(attributes.get('status', ''))
        self.hardware_version = str(attributes.get('hwVer', ''))
        self.hardware_vendor = str(attributes.get('vendor', ''))

    def __eq__(self, other: object) -> bool:
        """Checks equality between two PowersupplyModule instances.

        Args:
            other: Instance to compare to

        Returns:
            True if equal, False if not equal
        """
        if isinstance(other, self.__class__):
            key_attrs = attrgetter('pod', 'node', 'slot')
            return key_attrs(self) == key_attrs(other)
        return NotImplemented

class Port(BaseACIPhysModule):
    """This class defines a physical port of a linecard.
    """

    def __init__(self, pod: str, node: str, slot: str, port: str, parent: Optional[BaseACIObject] = None) -> None:
        """Initialize the basic object.  This should be called by the
           init routines of inheriting subclasses.

        Args:
            pod: Pod ID
            node: Node ID
            slot: Slot ID
            port: Port ID
            parent: Optional parent object
        """
        self.pod: str = pod
        self.node: str = node
        self.slot: str = slot
        self.port: str = port
        self.type: str = 'port'
        self.dn: str = 'topology/pod-{0}/node-{1}/sys/ch/lcslot-{2}/lc/leafports-{3}/port-{4}'.format(pod, node, slot, slot, port)
        self.descr: str = ''
        self.status: str = ''
        self.hardware_version: str = ''
        self.hardware_vendor: str = ''
        self.serial: str = ''
        self.model: str = ''
        self.name: str = 'Port-' + port
        super(Port, self).__init__(pod, node, slot, parent)

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Gets the APIC classes used by this acitoolkit class.

        Returns:
            list of strings containing APIC class names
        """
        return ['eqptPort']

    @staticmethod
    def _get_parent_class() -> Type[BaseACIObject]:
        """Gets the class of the parent object

        Returns:
            class of parent object
        """
        return Linecard

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Gets the parent DN from the child DN

        Args:
            dn: string containing the distinguished name URL

        Returns:
            string containing the parent DN
        """
        return dn.split('/leafports')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Gets the instance name from the DN

        Args:
            dn: string containing the distinguished name URL

        Returns:
            string containing the instance name
        """
        name = dn.split('/port-')[1].split('/')[0]
        return name

    @classmethod
    def get(cls, session: Session, parent: Optional[BaseACIObject] = None) -> List['Port']:
        """Gets all of the ports from the APIC.
           If parent is specified, it will only get ports that are children of the parent.

        Args:
            session: Session instance used to communicate with the APIC
            parent: Parent instance to limit ports to a specific parent

        Returns:
            list of ports
        """
        return cls.get_obj(session, cls._get_apic_classes(), parent)

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Fills in an object with the desired attributes.
           Overridden by inheriting classes to provide the specific attributes
           when getting objects from the APIC.

        Args:
            attributes: Dictionary containing the attributes to fill in
        """
        self.serial = str(attributes.get('ser', ''))
        self.model = str(attributes.get('model', ''))
        self.dn = str(attributes.get('dn', ''))
        self.descr = str(attributes.get('descr', ''))
        self.status = str(attributes.get('status', ''))
        self.hardware_version = str(attributes.get('hwVer', ''))
        self.hardware_vendor = str(attributes.get('vendor', ''))

    def __eq__(self, other: object) -> bool:
        """Checks equality between two Port instances.

        Args:
            other: Instance to compare to

        Returns:
            True if equal, False if not equal
        """
        if isinstance(other, self.__class__):
            key_attrs = attrgetter('pod', 'node', 'slot', 'port')
            return key_attrs(self) == key_attrs(other)
        return NotImplemented

class PowersupplyModule(BaseACIPhysModule):
    """This class defines a power supply module of a node.
    """

    def __init__(self, pod: str, node: str, slot: str, parent: Optional[BaseACIObject] = None) -> None:
        """Initialize the basic object.  This should be called by the
           init routines of inheriting subclasses.

        Args:
            pod: Pod ID
            node: Node ID
            slot: Slot ID
            parent: Optional parent object
        """
        self.pod: str = pod
        self.node: str = node
        self.slot: str = slot
        self.type: str = 'powersupply'
        self.dn: str = 'topology/pod-{0}/node-{1}/sys/ch/pslot-{2}/ps'.format(pod, node, slot)
        self.descr: str = ''
        self.status: str = ''
        self.hardware_version: str = ''
        self.hardware_vendor: str = ''
        self.serial: str = ''
        self.model: str = ''
        self.name: str = 'PS-' + slot
        super(PowersupplyModule, self).__init__(pod, node, slot, parent)

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """Gets the APIC classes used by this acitoolkit class.

        Returns:
            list of strings containing APIC class names
        """
        return ['eqptPsu']

    @staticmethod
    def _get_parent_class() -> Type[BaseACIObject]:
        """Gets the class of the parent object

        Returns:
            class of parent object
        """
        return Node

    @staticmethod
    def _get_parent_dn(dn: str) -> str:
        """Gets the parent DN from the child DN

        Args:
            dn: string containing the distinguished name URL

        Returns:
            string containing the parent DN
        """
        return dn.split('/pslot')[0]

    @staticmethod
    def _get_name_from_dn(dn: str) -> str:
        """Gets the instance name from the DN

        Args:
            dn: string containing the distinguished name URL

        Returns:
            string containing the instance name
        """
        name = dn.split('/pslot-')[1].split('/')[0]
        return name

    @classmethod
    def get(cls, session: Session, parent: Optional[BaseACIObject] = None) -> List['PowersupplyModule']:
        """Gets all of the power supply modules from the APIC.
           If parent is specified, it will only get power supplies that are children of the parent.

        Args:
            session: Session instance used to communicate with the APIC
            parent: Parent instance to limit power supplies to a specific parent

        Returns:
            list of power supply modules
        """
        return cls.get_obj(session, cls._get_apic_classes(), parent)

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """Fills in an object with the desired attributes.
           Overridden by inheriting classes to provide the specific attributes
           when getting objects from the APIC.

        Args:
            attributes: Dictionary containing the attributes to fill in
        """
        self.serial = str(attributes.get('ser', ''))
        self.model = str(attributes.get('model', ''))
        self.dn = str(attributes.get('dn', ''))
        self.descr = str(attributes.get('descr', ''))
        self.status = str(attributes.get('status', ''))
        self.hardware_version = str(attributes.get('hwVer', ''))
        self.hardware_vendor = str(attributes.get('vendor', ''))

    def __eq__(self, other: object) -> bool:
        """Checks equality between two PowersupplyModule instances.

        Args:
            other: Instance to compare to

        Returns:
            True if equal, False if not equal
        """
        if isinstance(other, self.__class__):
            key_attrs = attrgetter('pod', 'node', 'slot')
            return key_attrs(self) == key_attrs(other)
        return NotImplemented