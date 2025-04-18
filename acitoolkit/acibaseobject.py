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
"""
This module implements the Base Class for creating all of the ACI Objects.
"""
from typing import Optional, List, Dict, Any, Type, Union, Set, Tuple
import logging
from operator import attrgetter
import sys

from .aciSearch import AciSearch, Searchable
from .acisession import Session


log = logging.getLogger(__name__)


class BaseRelation:
    """
    Class for all basic relations.
    """

    def __init__(self, item: Any, status: str, relation_type: Optional[str] = None) -> None:
        """
        A relation consists of the following elements:

        :param item:    The object to which the relationship applies
        :param status:  The status of the relationship.\
                        Valid values are 'attached' and 'detached'
        :param relation_type:   Optional additional information to distinguish\
                                the relationship.\
                                Used in cases where more than 1 type of\
                                relation exists.
        """
        if status not in ('attached', 'detached'):
            raise ValueError
        self.item = item
        self.status = status
        self.relation_type = relation_type

    def is_attached(self) -> bool:
        """
        :returns: True or False indicating whether the relation is attached.\
        If a relation is detached, it will be deleted from the APIC when the\
        configuration is pushed.
        """
        return self.status == 'attached'

    def is_detached(self) -> bool:
        """
        :returns: True or False indicating whether the relation is detached.\
        If a relation is detached, it will be deleted from the APIC when the\
        configuration is pushed.
        """
        return not self.is_attached()

    def set_as_detached(self) -> None:
        """
        Sets the relation status to 'detached'
        """
        self.status = 'detached'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            key_attrs = attrgetter('item', 'status', 'relation_type')
            return key_attrs(self) == key_attrs(other)
        raise TypeError

    def __hash__(self) -> int:
        return hash((self.item, self.status, self.relation_type))

    def __ne__(self, other: Any) -> bool:
        return not self == other


class BaseACIObject(AciSearch):
    """
    This class defines functionality common to all ACI objects.
    Functions may be overwritten by inheriting classes.
    """

    def __init__(self, name: Optional[str] = None, parent: Optional['BaseACIObject'] = None) -> None:
        """
        Constructor initializes the basic object and should be called by\
        the init routines of inheriting subclasses.

        :param name: String containing the name of the object\
                     instance
        :param parent: Parent object within the acitoolkit object model.
        """
        if sys.version_info < (3, 0, 0):
            if isinstance(name, unicode):
                name = str(name)
        if name is None or not isinstance(name, str):
            raise TypeError
        if isinstance(parent, str):
            raise TypeError("Parent object can't be a string")
        self.name = name
        self._deleted = False
        self._children: List['BaseACIObject'] = []
        self._relations: List[BaseRelation] = []
        self._attachments: List[BaseRelation] = []
        self._tags: List[str] = []
        self._parent = parent
        self.descr: Optional[str] = None
        self.dn = ''
        self._session: Optional[Session] = None
        # self.subscribe = self._instance_subscribe
        # self.unsubscribe = self._instance_unsubscribe
        # self.has_events = self._instance_has_events
        # self.get_event = self._instance_get_event
        log.debug('Creating %s %s', self.__class__.__name__, name)
        if self._parent is not None:
            if self._parent.has_child(self):
                self._parent.remove_child(self)
            self._parent.add_child(self)

    def __lt__(self, other: 'BaseACIObject') -> bool:
        return self.name < other.name

    @classmethod
    def _get_subscription_urls(cls, extension: str = '') -> List[str]:
        """
        Gets the set of URLs used to subscribe to class changes
        in the APIC.

        :returns: Set of URL strings
        """
        resp = []
        for class_name in cls._get_apic_classes():
            url = '/api/class/%s.json?subscription=yes' % class_name
            url += extension
            resp.append(url)
        return resp

    def _get_instance_subscription_urls(self) -> List[str]:
        """
        Gets the set of URLs used to subscribe to instance changes
        in the APIC.

        :returns: Set of URL strings
        """
        raise NotImplementedError

    @classmethod
    def _get_apic_classes(cls) -> List[str]:
        """
        Get the APIC classes used by the acitoolkit class.
        Meant to be overridden by inheriting classes.
        Raises exception if not overridden.

        :returns: list of strings containing APIC class names
        """
        raise NotImplementedError

    @staticmethod
    def _get_children_concrete_classes() -> List[Type['BaseACIObject']]:
        """
        Get the acitoolkit class of the concrete children of this object.
        This is meant to be overridden by any inheriting classes that have children.
        If they don't have children, this will return an empty list.
        :return: list of classes
        """
        return []

    @classmethod
    def get_deep_apic_classes(cls, include_concrete: bool = False) -> List[str]:
        """
        Get all the apic classes needed for this acitoolkit class and
        all of its children.
        :return: list of all apic classes
        """
        resp = cls._get_apic_classes()
        for child_class in cls._get_children_classes():
            resp.extend(child_class.get_deep_apic_classes(include_concrete))
        if include_concrete:
            for child_class in cls._get_children_concrete_classes():
                resp.extend(child_class.get_deep_apic_classes(include_concrete))

        return list(set(resp))

    @staticmethod
    def _get_parent_class():
        """
        Gets the class of the parent object
        Meant to be overridden by inheriting classes.
        Raises exception if not overridden.

        :returns: class of parent object
        """
        raise NotImplementedError

    @staticmethod
    def _get_children_classes():
        """
        Get the acitoolkit class of the children of this object.
        This is meant to be overridden by any inheriting classes that have children.
        If they don't have children, this will return an empty list.
        :return: list of classes
        """
        return []

    @classmethod
    def _get_parent_dn(cls, dn: str):
        """
        Get the parent DN

        :param dn: string containing the distinguished name URL
        :return: None
        """
        return dn.split(cls._get_starting_name_delimiter())[0]

    @staticmethod
    def _get_name_dn_delimiters():
        """
        Return a list of strings that surround the name within the dn
        :return: list of strings that surround the name within the dn
        """
        return None

    @classmethod
    def _get_starting_name_delimiter(cls):
        """
        Return the string that prefaces the object name within the dn
        :return: string that prefaces the object name within the dn
        """
        delimiters = cls._get_name_dn_delimiters()
        if len(delimiters) == 0:
            return None
        return delimiters[0]

    @classmethod
    def _get_name_from_dn(cls, dn: str):
        """
        Get the instance name from the dn

        :param dn: string containing the distinguished name URL
        :return: string containing the name or None if not present
        """
        delimits = cls._get_name_dn_delimiters()
        name = None
        if len(delimits) == 2:
            if delimits[0] in dn:
                name = dn.split(delimits[0])[1].split(delimits[1])[0]
        elif len(delimits) == 1:
            if delimits[0] in dn:
                name = dn.split(delimits[0])[1]
        return name

    @classmethod
    def _get_toolkit_to_apic_classmap(cls):
        """
        Gets the APIC class to an acitoolkit class mapping dictionary
        :returns: dict of APIC class names to acitoolkit classes
        """
        return {}

    def _extract_relationships(self, data: Dict[str, Any], obj_dict: Dict[str, Any]) -> None:
        """
        Used internally by get_deep to populate the relationships
        Will be overridden when necessary.  The default implementation
        is here.

        :param data: data to extract relationships from
        """
        for child in self.get_children():
            child._extract_relationships(data, obj_dict)

    @classmethod
    def mask_class_from_graphs(cls):
        """
        Mask (hide) this class from graph creation

        :return: False indicating that this class should not be masked.
        """
        return False

    def has_tag(self, tag: str) -> bool:
        """
        Checks whether this object has a particular tag assigned.

        :param tag: string containing the tag name or an instance of _Tag
        :returns: True or False.  True indicates the object has this\
                  tag assigned.
        """
        if not isinstance(tag, _Tag):
            tag = _Tag(tag)
        return tag in self.get_tags()

    def has_tags(self) -> bool:
        """
        Checks whether this object has any tags assigned at all.

        :returns: True or False.  True indicates the object has at least one \
                  tag assigned.
        """
        return len(self.get_tags()) > 0

    def get_tags(self) -> List[str]:
        """
        Get the tags assigned to this object.

        :returns: List of tag instances
        """
        return self._tags

    def add_tag(self, tag: str) -> None:
        """
        Assign this object a particular tag.  Tags are strings that can be
        used to classify objects.  More than 1 tag can be assigned to an
        object.

        :param tag: string containing the tag to assign to this object or
                    an instance of _Tag
        """
        if not isinstance(tag, _Tag):
            tag = _Tag(tag)
        self.get_tags().append(tag)

    def remove_tag(self, tag: str) -> None:
        """
        Remove a particular tag from being assigned to this object.
        Note that this does not delete the tag from the APIC.

        :param tag: string containing the tag to remove from this object
                    or an instance of _Tag
        """
        if not isinstance(tag, _Tag):
            tag = _Tag(tag)
        self.get_tags().remove(tag)

    def delete_tag(self, tag: str) -> None:
        """
        Mark a particular tag as being deleted from this object.

        :param tag: string containing the tag to delete from this object
                    or an instance of _Tag
        """
        if not isinstance(tag, _Tag):
            tag = _Tag(tag)
        for existing_tag in self.get_tags():
            if existing_tag == tag:
                existing_tag.mark_as_deleted()

    @classmethod
    def _get_parent_from_dn(cls, dn: str):
        """
        Derive the parent object using a dn

        :param dn: String containing a distinguished name of an object
        """
        parent_class = cls._get_parent_class()
        if parent_class is None:
            return None
        if isinstance(parent_class, list):
            for parent_class_name in parent_class:
                parent_name = parent_class_name._get_name_from_dn(dn)
                if parent_name is not None:
                    parent_class = parent_class_name
                    break
        else:
            parent_name = parent_class._get_name_from_dn(dn)

        # if the parent_class is still a list, no class matches the DN
        if isinstance(parent_class, list):
            return None

        parent_dn = cls._get_parent_dn(dn)
        if parent_name is None:
            parent_obj = parent_class('')
        else:
            parent_obj = parent_class(parent_name,
                                      parent_class._get_parent_from_dn(parent_dn))
        return parent_obj

    @classmethod
    def get_deep(cls, full_data: Dict[str, Any], working_data: Dict[str, Any], parent: Optional['BaseACIObject'] = None, limit_to: Tuple[str, ...] = (), subtree: str = 'full', config_only: bool = False):
        """
        Gets all instances of this class from the APIC and gets all of the
        children as well.

        :param full_data:
        :param working_data:
        :param parent:
        :param limit_to:
        :param subtree:
        :param config_only:
        """
        obj = None
        for item in working_data:
            for key in item:
                if key in cls._get_apic_classes():
                    attribute_data = item[key]['attributes']
                    obj = cls(str(attribute_data['name']), parent)
                    obj._populate_from_attributes(attribute_data)
                    if 'children' in item[key]:
                        for child in item[key]['children']:
                            for apic_class in child:
                                class_map = cls._get_toolkit_to_apic_classmap()
                                if apic_class not in class_map:
                                    if apic_class == 'tagInst':
                                        obj._tags.append(_Tag(str(child[apic_class]['attributes']['name'])))
                                    continue
                                else:
                                    class_map[apic_class].get_deep(full_data=full_data,
                                                                   working_data=[child],
                                                                   parent=obj,
                                                                   limit_to=limit_to,
                                                                   subtree=subtree,
                                                                   config_only=config_only)
        return obj

    @classmethod
    def subscribe(cls, session: Session, extension: str = '', only_new: bool = False):
        """
        Subscribe to events from the APIC that pertain to instances of this
        class.

        :param session:  the instance of Session used for APIC communication
        :param only_new: Boolean indicating whether to get all events or only the new events. All events (indicated by
                         setting only_new to False) will queue a create event for all of the currently existing objects.
                         Setting only_new to True will only queue events that occur after the initial subscribe. The
                         default has only_new set to False.
        """
        urls = cls._get_subscription_urls()
        for url in urls:
            url += extension
            resp = session.subscribe(url, only_new=only_new)
            if resp is not None:
                if not resp.ok:
                    return False
        return True

    @classmethod
    def get_event(cls, session: Session):
        """
        Gets the event that is pending for this class.  Events are
        returned in the form of objects.  Objects that have been deleted
        are marked as such.

        :param session:  the instance of Session used for APIC communication
        """
        urls = cls._get_subscription_urls()
        for url in urls:
            if not session.has_events(url):
                continue
            event = session.get_event(url)
            class_name = None
            for class_name in cls._get_apic_classes():
                if class_name in event['imdata'][0]:
                    break
            if class_name is None:
                return None
            attributes = event['imdata'][0][class_name]['attributes']
            status = str(attributes['status'])
            dn = str(attributes['dn'])
            parent = cls._get_parent_from_dn(cls._get_parent_dn(dn))
            if status == 'created':
                name = str(attributes['name'])
            else:
                name = cls._get_name_from_dn(dn)
            obj = cls(name, parent=parent)
            obj._populate_from_attributes(attributes)
            if status == 'deleted':
                obj.mark_as_deleted()
            return obj

    @classmethod
    def has_events(cls, session: Session, extension: str = ''):
        """
        Check for pending events from the APIC that pertain to instances
        of this class.

        :param session:  the instance of Session used for APIC communication
        :returns: True or False.  True if there are events pending.
        """
        urls = cls._get_subscription_urls(extension)
        return any(session.has_events(url) for url in urls)

    def _instance_subscribe(self, session: Session, extension: str = '') -> Optional[Union[bool, Dict[str, Any]]]:
        """
        not yet fully implemented
        """
        urls = self._get_instance_subscription_urls()
        for url in urls:
            url = url + extension
            if not session.is_subscribed(url):
                resp = session.subscribe(url)
                if not resp.ok:
                    return resp
        return

    def _instance_has_events(self, session: Session, extension: str = '') -> bool:
        """
        Check for pending events from the APIC that pertain to this specific instance

        :param session:  the instance of Session used for APIC communication
        :param extension: Optional string that can be used to extend the URL
        :returns: True or False.  True if there are events pending.
        """
        urls = self._get_instance_subscription_urls()
        return any(session.has_events(url + extension) for url in urls)

    def _instance_get_event(self, session: Session, extension: str = '') -> Optional[Dict[str, Any]]:
        """
        Gets the event that is pending for this specific instance.  Events are
        returned in the form of a dictionary containing the event data.
        """
        urls = self._get_instance_subscription_urls()
        for url in urls:
            if session.has_events(url):
                return session.get_event(url)
        return None

    @classmethod
    def unsubscribe(cls, session: Session) -> None:
        """
        Unsubscribe from events from the APIC that pertain to instances of this
        class.
        """
        urls = cls._get_subscription_urls()
        for url in urls:
            session.unsubscribe(url)

    def _instance_unsubscribe(self) -> None:
        """
        Unsubscribe from events from the APIC that pertain to this specific
        instance.
        """
        raise NotImplementedError

    def mark_as_deleted(self) -> None:
        """
        Mark this object as deleted.  This will cause the object to be deleted
        from the APIC when the configuration is pushed.
        """
        self._deleted = True

    @staticmethod
    def is_interface() -> bool:
        """
        Check if this object is an interface.
        """
        return False

    def is_deleted(self) -> bool:
        """
        Check if this object is marked as deleted.
        """
        return self._deleted

    def attach(self, item: Any) -> None:
        """
        Attach an object to this object.  This will cause the object to be
        attached to this object in the APIC when the configuration is pushed.
        """
        self._check_relation(item, 'attached')
        self._relations.append(BaseRelation(item, 'attached'))

    def _check_relation(self, item: Any, status: str) -> None:
        """
        Check if a relation exists.
        """
        for relation in self._relations:
            if relation.item == item and relation.status == status:
                raise ValueError

    def is_attached(self, item: Any) -> bool:
        """
        Check if an object is attached to this object.
        """
        for relation in self._relations:
            if relation.item == item and relation.is_attached():
                return True
        return False

    def is_detached(self, item: Any) -> bool:
        """
        Check if an object is detached from this object.
        """
        for relation in self._relations:
            if relation.item == item and relation.is_detached():
                return True
        return False

    def detach(self, item: Any) -> None:
        """
        Detach an object from this object.  This will cause the object to be
        detached from this object in the APIC when the configuration is pushed.
        """
        self._check_relation(item, 'detached')
        self._relations.append(BaseRelation(item, 'detached'))

    def _check_attachment(self, item: Any, status: str) -> None:
        """
        Check if an attachment exists.
        """
        for attachment in self._attachments:
            if attachment.item == item and attachment.status == status:
                raise ValueError

    def has_attachment(self, item: Any) -> bool:
        """
        Check if an object is attached to this object.
        """
        for attachment in self._attachments:
            if attachment.item == item and attachment.is_attached():
                return True
        return False

    def has_detachment(self, item: Any) -> bool:
        """
        Check if an object is detached from this object.
        """
        for attachment in self._attachments:
            if attachment.item == item and attachment.is_detached():
                return True
        return False

    def get_child(self, child_type: Type['BaseACIObject'], child_name: str) -> Optional['BaseACIObject']:
        """
        Get a child object of a specific type and name.
        """
        for child in self._children:
            if isinstance(child, child_type) and child.name == child_name:
                return child
        return None

    def get_children(self, only_class: Optional[Type['BaseACIObject']] = None) -> List['BaseACIObject']:
        """
        Get all child objects, optionally filtered by class.
        """
        if only_class is None:
            return self._children
        return [child for child in self._children if isinstance(child, only_class)]

    def add_child(self, obj: 'BaseACIObject') -> None:
        """
        Add a child object to this object.
        """
        if obj not in self._children:
            self._children.append(obj)
            obj._parent = self

    def has_child(self, obj: 'BaseACIObject') -> bool:
        """
        Check if an object is a child of this object.
        """
        return obj in self._children

    def remove_child(self, obj: 'BaseACIObject') -> None:
        """
        Remove a child object from this object.
        """
        if obj in self._children:
            self._children.remove(obj)
            obj._parent = None

    def populate_children(self, deep: bool = False, include_concrete: bool = False) -> None:
        """
        Populate the children of this object.
        """
        raise NotImplementedError

    def update_db(self, session: Session, subscribed_classes: List[str], deep: bool = False) -> None:
        """
        Update the database with the current state of this object.
        """
        raise NotImplementedError

    def get_parent(self) -> Optional['BaseACIObject']:
        """
        Get the parent object of this object.
        """
        return self._parent

    def set_parent(self, parent_obj: Optional['BaseACIObject']) -> None:
        """
        Set the parent object of this object.
        """
        self._parent = parent_obj

    def has_parent(self) -> bool:
        """
        Check if this object has a parent object.
        """
        return self._parent is not None

    def _has_any_relation(self, other_class: Type['BaseACIObject']) -> bool:
        """
        Check if this object has any relation to objects of a specific class.
        """
        for relation in self._relations:
            if isinstance(relation.item, other_class):
                return True
        return False

    def _has_relation(self, obj: 'BaseACIObject', relation_type: Optional[str] = None) -> bool:
        """
        Check if this object has a relation to a specific object.
        """
        for relation in self._relations:
            if relation.item == obj and (relation_type is None or relation.relation_type == relation_type):
                return True
        return False

    def _add_relation(self, obj: 'BaseACIObject', relation_type: Optional[str] = None) -> None:
        """
        Add a relation to a specific object.
        """
        self._relations.append(BaseRelation(obj, 'attached', relation_type))

    def _remove_attachment(self, obj: 'BaseACIObject', relation_type: Optional[str] = None) -> None:
        """
        Remove an attachment to a specific object.
        """
        for attachment in self._attachments:
            if attachment.item == obj and (relation_type is None or attachment.relation_type == relation_type):
                self._attachments.remove(attachment)
                return

    def _remove_relation(self, obj: 'BaseACIObject', relation_type: Optional[str] = None) -> None:
        """
        Remove a relation to a specific object.
        """
        for relation in self._relations:
            if relation.item == obj and (relation_type is None or relation.relation_type == relation_type):
                self._relations.remove(relation)
                return

    def _remove_all_relation(self, obj_class: Type['BaseACIObject'], relation_type: Optional[str] = None) -> None:
        """
        Remove all relations to objects of a specific class.
        """
        self._relations = [relation for relation in self._relations
                         if not (isinstance(relation.item, obj_class) and
                               (relation_type is None or relation.relation_type == relation_type))]

    def _get_any_relation(self, obj_class: Type['BaseACIObject'], relation_type: Optional[str] = None) -> Optional['BaseACIObject']:
        """
        Get any relation to an object of a specific class.
        """
        for relation in self._relations:
            if isinstance(relation.item, obj_class) and (relation_type is None or relation.relation_type == relation_type):
                return relation.item
        return None

    def _get_all_relation(self, obj_class: Type['BaseACIObject'], relation_type: Optional[str] = None) -> List['BaseACIObject']:
        """
        Get all relations to objects of a specific class.
        """
        return [relation.item for relation in self._relations
                if isinstance(relation.item, obj_class) and
                (relation_type is None or relation.relation_type == relation_type)]

    def _get_all_detached_relation(self, obj_class: Type['BaseACIObject'], relation_type: Optional[str] = None) -> List['BaseACIObject']:
        """
        Get all detached relations to objects of a specific class.
        """
        return [relation.item for relation in self._relations
                if isinstance(relation.item, obj_class) and relation.is_detached() and
                (relation_type is None or relation.relation_type == relation_type)]

    def get_interfaces(self, status: str = 'attached') -> List['BaseInterface']:
        """
        Get all interfaces of this object.
        """
        from .aciphysobject import BaseInterface
        return [relation.item for relation in self._relations
                if isinstance(relation.item, BaseInterface) and
                (status == 'attached' and relation.is_attached() or
                 status == 'detached' and relation.is_detached())]

    @staticmethod
    def _get_all_relations_by_class(relations: List[BaseRelation], attached_class: Type['BaseACIObject'],
                                   status: str = 'attached', relation_type: Optional[str] = None) -> List['BaseACIObject']:
        """
        Get all relations of a specific class.
        """
        return [relation.item for relation in relations
                if isinstance(relation.item, attached_class) and
                (status == 'attached' and relation.is_attached() or
                 status == 'detached' and relation.is_detached()) and
                (relation_type is None or relation.relation_type == relation_type)]

    def get_all_attached(self, attached_class: Type['BaseACIObject'], status: str = 'attached',
                        relation_type: Optional[str] = None) -> List['BaseACIObject']:
        """
        Get all attached objects of a specific class.
        """
        return self._get_all_relations_by_class(self._relations, attached_class, status, relation_type)

    def get_all_attachments(self, attached_class: Type['BaseACIObject'], status: str = 'attached',
                          relation_type: Optional[str] = None) -> List['BaseACIObject']:
        """
        Get all attachments of a specific class.
        """
        return self._get_all_relations_by_class(self._attachments, attached_class, status, relation_type)

    def _get_url_extension(self) -> str:
        """
        Get the URL extension for this object.
        """
        return ''

    def __str__(self) -> str:
        """
        Get the string representation of this object.
        """
        return self.name

    def get_from_json(self, data: Dict[str, Any], parent: Optional['BaseACIObject'] = None) -> 'BaseACIObject':
        """
        Get an object from JSON data.
        """
        raise NotImplementedError

    def get_json(self, obj_class: str, attributes: Optional[Dict[str, Any]] = None,
                children: Optional[List[Dict[str, Any]]] = None, get_children: bool = True) -> Dict[str, Any]:
        """
        Get the JSON representation of this object.
        """
        raise NotImplementedError

    def __eq__(self, other: Any) -> bool:
        """
        Check if this object is equal to another object.
        """
        if isinstance(other, self.__class__):
            return self.name == other.name
        return False

    def __hash__(self) -> int:
        """
        Get the hash of this object.
        """
        return hash(self.name)

    def __ne__(self, other: Any) -> bool:
        """
        Check if this object is not equal to another object.
        """
        return not self == other

    def _populate_from_attributes(self, attributes: Dict[str, Any]) -> None:
        """
        Populate this object from attributes.
        """
        raise NotImplementedError

    def get_dn_from_attributes(self, attributes: Dict[str, Any]) -> str:
        """
        Get the DN from attributes.
        """
        raise NotImplementedError

    def _generate_attributes(self) -> Dict[str, Any]:
        """
        Generate attributes for this object.
        """
        raise NotImplementedError

    @classmethod
    def get(cls, session: Session, toolkit_class: Type['BaseACIObject'], apic_class: str,
            parent: Optional['BaseACIObject'] = None, tenant: Optional['BaseACIObject'] = None,
            query_target_type: str = 'subtree') -> List['BaseACIObject']:
        """
        Get objects from the APIC.
        """
        raise NotImplementedError

    def find(self, search_object: 'BaseACIObject') -> Optional['BaseACIObject']:
        """
        Find an object in this object's children.
        """
        raise NotImplementedError

    def info(self) -> str:
        """
        Get information about this object.
        """
        raise NotImplementedError

    def infoList(self) -> List[str]:
        """
        Get a list of information about this object.
        """
        raise NotImplementedError

    @staticmethod
    def get_table(aci_object: 'BaseACIObject', title: str = '') -> str:
        """
        Get a table representation of an object.
        """
        raise NotImplementedError

    @staticmethod
    def check_session(session: Session) -> None:
        """
        Check if a session is valid.
        """
        if not isinstance(session, Session):
            raise TypeError

    def get_attributes(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get attributes of this object.
        """
        raise NotImplementedError

    @classmethod
    def get_fault(cls, session: Session, extension: str = '') -> List['BaseACIObject']:
        """
        Get faults for this object.
        """
        raise NotImplementedError

    def subscribe_to_fault_instances_subtree(self, session: Session, extension: str = '', deep: bool = False) -> None:
        """
        Subscribe to faults for this object's subtree.
        """
        raise NotImplementedError

    def _instance_has_subtree_faults(self, session: Session, extension: str = '', deep: bool = False) -> bool:
        """
        Check if this object's subtree has faults.
        """
        raise NotImplementedError

    def _instance_get_subtree_faults(self, session: Session, fault_objs: List['BaseACIObject'],
                                   extension: str = '', deep: bool = False) -> None:
        """
        Get faults for this object's subtree.
        """
        raise NotImplementedError


class BaseACIPhysObject(BaseACIObject):
    """Base class for physical objects
    """
    def __init__(self, name='', parent=None, pod=None):
        self._session = None
        if not hasattr(self, 'type'):
            self.type = None
        if not hasattr(self, 'module'):
            self.module = None
        self.pod = None
        if pod:
            self.pod = pod
        else:
            if parent:
                self.pod = parent.pod
        super(BaseACIPhysObject, self).__init__(name=name, parent=parent)

    @staticmethod
    def _delete_redundant_policy(infra, policy_type):
        """
        Removes redundant policies
        """
        policies = []
        for idx, child in enumerate(infra['infraInfra']['children']):
            if policy_type in child:
                policy_name = child[policy_type]['attributes']['name']
                if policy_name in policies:
                    del infra['infraInfra']['children'][idx]
                else:
                    policies.append(policy_name)
        return infra

    def _combine_json(self, data, other):
        """
        Combines the json
        """
        if len(data) == 0:
            return other
        if len(other) == 0:
            return data
        phys_domain, fabric, infra = data
        _, _, other_infra = other
        infra['infraInfra']['children'].extend(other_infra['infraInfra']['children'])

        # Remove duplicate named policies
        for item in infra['infraInfra']['children']:
            for key in item:
                if 'name' in item[key]['attributes']:
                    self._delete_redundant_policy(infra, key)

        # Combine all of the infraFuncP items
        first_occur = None
        for idx, child in enumerate(infra['infraInfra']['children']):
            if 'infraFuncP' in child:
                if first_occur is None:
                    first_occur = idx
                else:
                    for other_child in child['infraFuncP']['children']:
                        infra['infraInfra']['children'][first_occur]['infraFuncP']['children'].append(other_child)
                    del infra['infraInfra']['children'][idx]
        return phys_domain, fabric, infra

    def get_json(self):
        """Returns json representation of the object

        :returns: JSON of contained Interfaces
        """
        data = []
        for child in self.get_children():
            other = child.get_json()
            if other is not None:
                data = self._combine_json(data, other)
        if len(data) == 0:
            return None
        return data

    @staticmethod
    def get_url(fmt='json'):
        """Get the URL used to push the configuration to the APIC
        if no fmt parameter is specified, the format will be 'json'
        otherwise it will return '/api/mo/uni.' with the fmt string appended.

        :param fmt: optional fmt string
        :returns: Nothing - physical objects are not modifiable
        """
        pass

    def add_child(self, child_obj):
        """Add a child to the children list. All children must be unique so it
        will first delete the child if it already exists.

        :param child_obj: a child object to be added as a child to this object.
                          This will be put into the _children list.

        :returns: None
        """
        if self.has_child(child_obj):
            self.remove_child(child_obj)
        self._children.append(child_obj)

    def get_children(self, child_type=None):
        """Returns the list of children.  If childType is provided, then
        it will return all of the children of the matching type.

        :param child_type: This optional parameter will cause this method to\
                        return only those children\
                        that match the type of childType.  If this parameter\
                        is ommitted, then all of the children will be returned.

        :returns: list of children
        """
        if child_type:
            children = []
            for child in self._children:
                if isinstance(child, child_type):
                    children.append(child)
            return children
        else:
            return list(self._children)

    @classmethod
    def exists(cls, session, phys_obj):
        """Check if an apic phys_obj exists on the APIC.
        Returns True if the phys_obj does exist.

        :param session: APIC session to use when accessing the APIC controller.
        :param phys_obj: The object that you are checking for.
        :returns: True if the phys_obj exists, False if it does not.
        """

        # TODO: this does not work.  There are more parameters in the .get method.
        apic_nodes = cls.get(session)
        return any(apic_node == phys_obj for apic_node in apic_nodes)

    def get_type(self):
        """Gets physical object type

        :returns: type string of the object.
        """
        return self.type

    def get_pod(self):
        """Gets pod_id
        :returns: id of pod
        """
        return self.pod

    def get_node(self):
        """Gets node id

        :returns: id of node
        """
        return self.node

    def get_name(self):
        """Gets name.

        :returns: Name string
        """
        return self.name

    def get_serial(self):
        """Gets serial number.

        :returns: serial number string
        """
        return None

    @classmethod
    def check_parent(cls, parent):
        """
        If a parent is specified, it will check that it is the correct class of parent
        If not, then an exception is raised.
        :param parent:
        :return:
        """
        if parent:
            if not isinstance(parent, cls._get_parent_class()):
                raise TypeError('The parent of this object must be of class {0}'.format(cls._get_parent_class()))

    @classmethod
    def get_deep(cls, session, include_concrete=False):
        """
        Will return the atk object and the entire tree under it.
        :param session: APIC session to use
        :param include_concrete: flag to indicate that concrete objects should also be included
        :return:
        """
        atk_objects = cls.get(session)
        for atk_object in atk_objects:
            atk_object.populate_children(deep=True, include_concrete=include_concrete)
        return atk_objects


class _Tag(BaseACIObject):
    """
    Tag class
    """
    def __init__(self, name=None, parent=None):
        self.name = name
        self._deleted = False
        self._parent = parent

    def is_deleted(self):
        return self._deleted

    def mark_as_deleted(self):
        self._deleted = True

    def __eq__(self, other):
        if isinstance(other, str):
            other = _Tag(other)
        return self.name == other.name and self._deleted == other._deleted

    def __ne__(self, other):
        return not self == other

    @classmethod
    def _get_apic_classes(cls):
        return ['tagInst']

    @staticmethod
    def _get_parent_dn(dn):
        """
        Get the parent DN

        :param dn: string containing the distinguished name URL
        :return: string containing the parent object's distinguished name
        """
        return dn.split('/tag-')[0]

    @classmethod
    def _get_name_from_dn(cls, dn):
        """
        Parse the name out of a dn string.
        Meant to be overridden by inheriting classes.
        Raises exception if not overridden.

        :returns: string containing name
        """
        name = dn.split('/tag-')[1].split('/')[0]
        return name


class BaseACIPhysModule(BaseACIPhysObject):
    """BaseACIPhysModule: base class for modules  """

    def __init__(self, pod, node, slot, parent=None):
        """ Initialize the basic object.  This should be called by the
            init routines of inheriting subclasses.

            :param pod: pod id of module
            :param node: node id of module
            :param slot: slot id of module
            :param parent: optional parent object
        """
        super(BaseACIPhysModule, self).__init__(name='', parent=None)

        self.pod = str(pod)
        self.node = str(node)
        self.slot = str(slot)
        self.serial = None
        self.model = None
        self.dn = None
        self.descr = None
        self.bios = None
        self.firmware = None

        if parent:
            if not isinstance(parent, str):
                self._parent = parent
                self._parent.add_child(self)

        log.debug('Creating %s %s', self.__class__.__name__,
                  'pod-' + self.pod + '/node-' + self.node + '/slot-' + self.slot)

    def get_slot(self):
        """Gets slot id

        :returns: slot id
        """
        return self.slot

    def __eq__(self, other):
        """ Two modules are considered equal if their class type is the same
        and pod, node, slot, type all match.
        """
        if isinstance(other, self.__class__):
            key_attrs = attrgetter('pod', 'node', 'slot', 'type')
            return key_attrs(self) == key_attrs(other)
        return NotImplemented

    @staticmethod
    def _parse_dn(dn):
        """Parses the pod, node, and slot from a
           distinguished name of the node.

           :param dn: str - distinguished name

           :returns: pod, node, slot strings
        """
        name = dn.split('/')
        pod = str(name[1].split('-')[1])
        node = str(name[2].split('-')[1])
        slot = str(name[5].split('-')[1])
        return pod, node, slot

    @classmethod
    def get_obj(cls, session, apic_classes, parent_node):
        """Gets all of the Nodes from the APIC.  This is called by the
        module specific get() methods.  The parameters passed include the
        APIC object class, apic_classes, so that this will work for
        different kinds of modules.

        :param parent_node: parent object or node id
        :param session: APIC session to use when retrieving the nodes
        :param apic_classes: The object class in APIC to retrieve
        :returns: list of module objects derived from the specified apic_classes

        """
        cls.check_session(session)

        node = None
        if parent_node:
            if not isinstance(parent_node, str):
                cls.check_parent(parent_node)
                node = parent_node.node
            else:
                node = parent_node
        pod = '1'
        if parent_node:
            parent_dn = 'topology/pod-{0}/node-{1}/sys'.format(pod, node)
            interface_query_url = '/api/mo/' + parent_dn + \
                                  '.json?query-target=subtree&target-subtree-class=' + ','.join(apic_classes)
        else:
            interface_query_url = '/api/node/class/' + apic_classes[0] + '.json?query-target=self'
        cards = []
        ret = session.get(interface_query_url)
        card_data = ret.json()['imdata']
        for apic_obj in card_data:
            if apic_classes[0] in apic_obj:
                dist_name = str(apic_obj[apic_classes[0]]['attributes']['dn'])
                (pod, node_id, slot) = cls._parse_dn(dist_name)
                card = cls(pod, node_id, slot)
                card._session = session
                card._populate_from_attributes(apic_obj[apic_classes[0]]['attributes'])

                (card.firmware, card.bios) = card._get_firmware(dist_name)
                if parent_node:
                    if card.node == parent_node.node:
                        if not isinstance(parent_node, str):
                            card._parent = parent_node
                            card._parent.add_child(card)
                        cards.append(card)
                else:
                    cards.append(card)

        return cards

    def _populate_from_attributes(self, attributes):
        """Fills in an object with the desired attributes.
           Overridden by inheriting classes to provide the specific attributes
           when getting objects from the APIC.
        """
        self.serial = str(attributes['ser'])
        self.model = str(attributes['model'])
        self.dn = str(attributes['dn'])
        self.descr = str(attributes['descr'])
        self.modify_time = str(attributes['modTs'])

    def _get_firmware(self, dist_name):
        """Gets the firmware and bios version for the module from the "running" object in APIC.

        :param dist_name: dn of module, a string

        :returns: firmware, bios
        """
        mo_query_url = '/api/mo/' + dist_name + '/running.json?query-target=self'
        ret = self._session.get(mo_query_url)
        node_data = ret.json()['imdata']
        if node_data:
            firmware = str(node_data[0]['firmwareCardRunning']['attributes']['version'])
            bios = str(node_data[0]['firmwareCardRunning']['attributes']['biosVer'])
        else:
            firmware = None
            bios = None
        return firmware, bios

    def get_serial(self):
        """Returns the serial number.
        :returns: serial number string
        """
        return self.serial


class BaseInterface(BaseACIObject):
    """Abstract class used to provide base functionality to other Interface
       classes.
    """
    def __init__(self, name, parent=None):
        if not hasattr(self, 'module'):
            self.module = None
        if not hasattr(self, 'port'):
            self.port = None
        if not hasattr(self, 'node'):
            self.node = None
        super(BaseInterface, self).__init__(name, parent)

    @staticmethod
    def is_dn_vpc(dn):
        """
        Check if the DN is a VPC

        :param dn: String containing the DN
        :return: True if the the DN is a VPC. False otherwise.
        """
        if '/protpaths' in dn:
            return True
        return False

    def _get_port_selector_json(self, port_type, port_name):
        """Returns the json used for selecting the specified interfaces
        """
        name = self._get_name_for_json()
        port_blk = {'name': name,
                    'fromCard': self.module,
                    'toCard': self.module,
                    'fromPort': self.port,
                    'toPort': self.port}
        port_blk = {'infraPortBlk': {'attributes': port_blk,
                                     'children': []}}
        pc_url = 'uni/infra/funcprof/%s-%s' % (port_type, port_name)
        accbasegrp = {'infraRsAccBaseGrp': {'attributes': {'tDn': pc_url},
                                            'children': []}}
        portselect = {'infraHPortS': {'attributes': {'name': name,
                                                     'type': 'range'},
                                      'children': [port_blk, accbasegrp]}}
        accport_selector = {'infraAccPortP': {'attributes': {'name': name},
                                              'children': [portselect]}}
        node_blk = {'name': name,
                    'from_': self.node, 'to_': self.node}
        node_blk = {'infraNodeBlk': {'attributes': node_blk, 'children': []}}
        leaf_selector = {'infraLeafS': {'attributes': {'name': name,
                                                       'type': 'range'},
                                        'children': [node_blk]}}
        accport = {'infraRsAccPortP':
                   {'attributes': {'tDn': 'uni/infra/accportprof-%s' % name},
                    'children': []}}
        node_profile = {'infraNodeP': {'attributes': {'name': name},
                                       'children': [leaf_selector,
                                                    accport]}}
        return node_profile, accport_selector

    def get_port_selector_json(self):
        """
        Returns the port selector.

        :return:
        """
        return self._get_port_selector_json('accportgrp',
                                            self._get_name_for_json())

    def get_port_channel_selector_json(self, port_name):
        """
        Get the JSON for the Port Channel selector

        :param port_name: String containing the port name
        :return: Dictonary containing the JSON for the Port Channel selector
        """
        return self._get_port_selector_json('accbundle', port_name)
