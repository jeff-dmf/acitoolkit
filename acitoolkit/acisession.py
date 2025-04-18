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
"""  This module contains the Session class that controls communication
     with the APIC.
"""
import copy
import json
import logging
import ssl
import threading
import time
import socket
import base64
import requests
import sys
from collections import namedtuple
from typing import Optional, Dict, Any, List, Union, Callable, Tuple, TypeVar, Type

if sys.version_info < (3, 0, 0):
    from urllib import unquote
else:
    from urllib.parse import unquote

try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
except ImportError:
    pass
from six.moves.queue import Queue
from websocket import create_connection, WebSocketException
from requests.exceptions import ConnectionError
try:
    from OpenSSL.crypto import FILETYPE_PEM, load_privatekey, sign
    NO_OPENSSL = False
except ImportError:
    NO_OPENSSL = True
try:
    import urllib3
    urllib3.disable_warnings()
except (ImportError, AttributeError):
    pass
else:
    try:
        urllib3.disable_warnings()
    except AttributeError:
        pass


log = logging.getLogger(__name__)

T = TypeVar('T')

class CredentialsError(Exception):
    """
    Exception class for errors with Credentials class
    """
    def __init__(self, message: str) -> None:
        """
        Initialize the exception.
        
        Args:
            message: The error message
        """
        super(CredentialsError, self).__init__(message)


class Login(threading.Thread):
    """
    Login thread responsible for refreshing the APIC login before timeout.
    """
    def __init__(self, apic: 'Session') -> None:
        """
        Initialize the login thread.
        
        Args:
            apic: The Session instance to handle login for
        """
        super(Login, self).__init__()
        self._apic = apic
        self._login_timeout = 0
        self._exit = False
        self.daemon = True

    def exit(self) -> None:
        """
        Indicate that the thread should exit.
        """
        self._exit = True

    def _check_callbacks(self) -> None:
        """
        Invoke the callback functions on a successful relogin
        if there was an error response

        :param resp: Instance of requests.Response
        """
        if self._apic.login_error:
            log.info('Logged back into the APIC')
            self._apic.login_error = False
            self._apic.invoke_login_callbacks()

    def run(self) -> None:
        while not self._exit:
            time.sleep(self._login_timeout)
            try:
                resp = self._apic.refresh_login(timeout=120)
            except ConnectionError:
                log.error('Could not refresh APIC login due to ConnectionError')
                self._login_timeout = 30
                self._apic.login_error = True
            except requests.exceptions.Timeout:
                log.error('Could not refresh APIC login due to Timeout')
            else:
                if resp.ok:
                    self._check_callbacks()
                    continue
            try:
                resp = self._apic._send_login()
                self._apic.resubscribe()
                if resp.ok:
                    self._check_callbacks()
                else:
                    log.error('Could not relogin to APIC.')
                    self._login_timeout = 30
            except ConnectionError:
                log.error('Could not relogin to APIC due to ConnectionError')
                self._apic.login_error = True


class EventHandler(threading.Thread):
    """
    Thread responsible for websocket communication.
    Receives events through the websocket and places them into a Queue
    """
    def __init__(self, subscriber: 'Subscriber') -> None:
        """
        Initialize the event handler thread.
        
        Args:
            subscriber: The Subscriber instance to handle events for
        """
        super(EventHandler, self).__init__()
        self._subscriber = subscriber
        self._exit = False
        self.daemon = True

    def exit(self) -> None:
        """
        Indicate that the thread should exit.
        """
        self._exit = True

    def run(self) -> None:
        while not self._exit:
            try:
                event = self._subscriber._ws.recv()
            except:
                break
            if not len(event):
                continue
            self._subscriber._event_q.put(event)


class Subscriber(threading.Thread):
    """
    Thread responsible for event subscriptions.
    Issues subscriptions, creates the websocket, and refreshes the
    subscriptions before timer expiry.  It also reissues the
    subscriptions when the APIC login is refreshed.
    """
    def __init__(self, apic: 'Session') -> None:
        """
        Initialize the subscriber thread.
        
        Args:
            apic: The Session instance to handle subscriptions for
        """
        super(Subscriber, self).__init__()
        self._apic = apic
        self._subscriptions = {}
        self._ws = None
        self._ws_url = None
        self._refresh_time = 30
        self._event_q = Queue()
        self._events = {}
        self._exit = False
        self.event_handler_thread = None
        self._event_handler = EventHandler(self)
        self._event_handler.start()
        self.daemon = True

    def exit(self) -> None:
        """
        Indicate that the thread should exit.
        """
        self._exit = True
        self._event_handler.exit()

    def _send_subscription(self, url: str, only_new: bool = False) -> None:
        """
        Send the subscription for the specified URL.

        :param url: URL string to issue the subscription
        """
        try:
            resp = self._apic.get(url)
        except ConnectionError:
            self._subscriptions[url] = None
            log.error('Could not send subscription to APIC for url %s', url)
            resp = requests.Response()
            resp.status_code = 404
            resp._content = '{"error": "Could not send subscription to APIC"}'
            return resp
        if not resp.ok:
            self._subscriptions[url] = None
            log.error('Could not send subscription to APIC for url %s', url)
            resp = requests.Response()
            resp.status_code = 404
            resp._content = '{"error": "Could not send subscription to APIC"}'
            return resp
        resp_data = json.loads(resp.text)
        if 'subscriptionId' not in resp_data:
            log.error('Did not receive proper subscription response from APIC for url %s response: %s',
                      url, resp_data)
            resp = requests.Response()
            resp.status_code = 404
            resp._content = '{"error": "Could not send subscription to APIC"}'
            return resp
        subscription_id = resp_data['subscriptionId']
        self._subscriptions[url] = subscription_id
        if not only_new:
            while len(resp_data['imdata']):
                event = {"totalCount": "1",
                         "subscriptionId": [resp_data['subscriptionId']],
                         "imdata": [resp_data["imdata"][0]]}
                self._event_q.put(json.dumps(event))
                resp_data["imdata"].remove(resp_data["imdata"][0])
        return resp

    def refresh_subscriptions(self) -> None:
        """
        Refresh all of the subscriptions.
        """
        # Make a copy of the current subscriptions in case of changes
        # while we are refreshing
        current_subscriptions = {}
        for subscription in self._subscriptions:
            try:
                current_subscriptions[subscription] = self._subscriptions[subscription]
            except KeyError:
                log.warning('Subscription removed while copying')

        # Refresh the subscriptions
        for subscription in current_subscriptions:
            if self._ws is not None:
                if not self._ws.connected:
                    log.warning('Websocket not established on subscription refresh. Re-establishing websocket')
                    self._open_web_socket('wss://' in self._ws_url)
            try:
                subscription_id = self._subscriptions[subscription]
            except KeyError:
                log.warning('Subscription has been removed while trying to refresh')
                continue
            if subscription_id is None:
                self._send_subscription(subscription)
                continue
            refresh_url = '/api/subscriptionRefresh.json?id=' + str(subscription_id)
            resp = self._apic.get(refresh_url)
            if not resp.ok:
                log.warning('Could not refresh subscription: %s', refresh_url)
                # Try to resubscribe
                self._resubscribe()

    def _open_web_socket(self, use_secure: bool = True) -> None:
        """
        Opens the web socket connection with the APIC.

        :param use_secure: Boolean indicating whether the web socket
                           should be secure.  Default is True.
        """
        sslopt = {}
        if use_secure:
            sslopt['cert_reqs'] = ssl.CERT_NONE
            self._ws_url = 'wss://%s/socket%s' % (self._apic.ipaddr,
                                                  self._apic.token)
        else:
            self._ws_url = 'ws://%s/socket%s' % (self._apic.ipaddr,
                                                 self._apic.token)

        kwargs = {}
        if self._ws is not None:
            if self._ws.connected:
                self._ws.close()
                self.event_handler_thread.exit()
        try:
            self._ws = create_connection(self._ws_url, sslopt=sslopt, **kwargs)
            if not self._ws.connected:
                log.error('Unable to open websocket connection')
            self.event_handler_thread = EventHandler(self)
            self.event_handler_thread.daemon = True
            self.event_handler_thread.start()
        except WebSocketException:
            log.error('Unable to open websocket connection due to WebSocketException')
        except socket.error:
            log.error('Unable to open websocket connection due to Socket Error')

    def _resubscribe(self) -> None:
        """
        Reissue the subscriptions.
        Used to when the APIC login timeout occurs and a new subscription
        must be issued instead of simply a refresh.  Not meant to be called
        directly by end user applications.
        """
        self._process_event_q()
        urls = []
        for url in self._subscriptions:
            urls.append(url)
        self._subscriptions = {}
        for url in urls:
            self.subscribe(url, only_new=True)

    def _process_event_q(self) -> None:
        """
        Put the event into correct bucket based on URLs that have been
        subscribed.
        """
        if self._event_q.empty():
            return

        while not self._event_q.empty():
            event = self._event_q.get()
            orig_event = event
            try:
                event = json.loads(event)
            except ValueError:
                log.error('Non-JSON event: %s', orig_event)
                continue
            # Find the URL for this event
            num_subscriptions = len(event['subscriptionId'])
            for i in range(0, num_subscriptions):
                url = None
                for k in self._subscriptions:
                    if self._subscriptions[k] == str(event['subscriptionId'][i]):
                        url = k
                        break
                if url not in self._events:
                    self._events[url] = []
                self._events[url].append(event)
                if num_subscriptions > 1:
                    event = copy.deepcopy(event)

    def subscribe(self, url: str, only_new: bool = False) -> None:
        """
        Subscribe to a particular APIC URL.  Used internally by the
        Class and Instance subscriptions.

        :param url: URL string to send as a subscription
        """
        log.info('Subscribing to url: %s', url)
        # Check if already subscribed.  If so, skip
        if url in self._subscriptions:
            return

        if self._ws is not None:
            if not self._ws.connected:
                self._open_web_socket('wss://' in self._ws_url)

        resp = self._send_subscription(url, only_new=only_new)
        return resp

    def is_subscribed(self, url: str) -> bool:
        """
        Check if subscribed to a particular APIC URL.

        :param url: URL string to send as a subscription
        """
        return url in self._subscriptions

    def has_events(self, url: str) -> bool:
        """
        Check if a particular APIC URL subscription has any events.
        Used internally by the Class and Instance subscriptions.

        :param url: URL string to check for pending events
        """
        self._process_event_q()
        if url not in self._events:
            return False
        result = len(self._events[url]) != 0
        return result

    def get_event_count(self, url: str) -> int:
        """
        Check the number of subscription events for a particular APIC URL

        :param url: URL string to check for pending events
        :returns: Interger number of events in event queue
        """
        self._process_event_q()
        if url not in self._events:
            return 0
        return len(self._events[url])

    def get_event(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get an event for a particular APIC URL subscription.
        Used internally by the Class and Instance subscriptions.

        :param url: URL string to get pending event
        """
        self._process_event_q()
        if url not in self._events:
            raise ValueError
        event = self._events[url].pop(0)
        log.debug('Event received %s', event)
        return event

    def unsubscribe(self, url: str) -> None:
        """
        Unsubscribe from a particular APIC URL.  Used internally by the
        Class and Instance subscriptions.

        :param url: URL string to unsubscribe
        """
        log.info('Unsubscribing from url: %s', url)
        if url not in self._subscriptions:
            return
        if '&subscription=yes' in url:
            unsubscribe_url = url.split('&subscription=yes')[0] + '&subscription=no'
        elif '?subscription=yes' in url:
            unsubscribe_url = url.split('?subscription=yes')[0] + '?subscription=no'
        else:
            raise ValueError('No subscription string in URL being unsubscribed')
        resp = self._apic.get(unsubscribe_url)
        if not resp.ok:
            log.warning('Could not unsubscribe from url: %s', unsubscribe_url)
        # Chew up any outstanding events
        while self.has_events(url):
            self.get_event(url)
        del self._subscriptions[url]
        if not self._subscriptions:
            self._ws.close(timeout=0)

    def run(self) -> None:
        while not self._exit:
            # Sleep for some interval and send subscription list
            time.sleep(self._refresh_time)
            try:
                self.refresh_subscriptions()
            except ConnectionError:
                log.error('Could not refresh subscriptions due to ConnectionError')


class Session(object):
    """
       Session class
       This class is responsible for all communication with the APIC.
    """
    def __init__(self, url: str, uid: str, pwd: Optional[str] = None, cert_name: Optional[str] = None, key: Optional[str] = None, verify_ssl: bool = False,
                 appcenter_user: bool = False, subscription_enabled: bool = True, proxies: Optional[Dict[str, str]] = None,
                 relogin_forever: bool = False):
        """
        :param url:  String containing the APIC URL such as ``https://1.2.3.4``
        :param uid: String containing the username that will be used as\
        part of the  the APIC login credentials.
        :param pwd: String containing the password that will be used as\
        part of the  the APIC login credentials.
        :param cert_name: String containing the certificate name that will be used\
        as part of the  the APIC certificate authentication credentials.
        :param key: String containing the private key file name that will be used\
        as part of the  the APIC certificate authentication credentials.
        :param verify_ssl:  Used only for SSL connections with the APIC.\
        Indicates whether SSL certificates must be verified.  Possible\
        values are True and False with the default being False.
        :param appcenter_user:  Set True when using certificate authentication from\
        the context of an APIC appcenter app
        :param proxies: Optional dictionary containing the proxies passed\
        directly to the Requests library
        :param relogin_forever: Boolean that when set to True will attempt to re-login
                                forever regardless of the error returned from APIC.
        """
        if not isinstance(url, str):
            url = str(url)
        if not isinstance(uid, str):
            uid = str(uid)
        if not isinstance(pwd, str):
            pwd = str(pwd)
        if not isinstance(url, str):
            raise CredentialsError("The URL or APIC address must be a string")
        if not isinstance(uid, str):
            raise CredentialsError("The user ID must be a string")
        if (pwd is None or pwd == 'None') and not cert_name and not key:
            raise CredentialsError("An authentication method must be provided")
        if pwd:
            if not isinstance(pwd, str):
                raise CredentialsError("The password must be a string")
        if cert_name:
            if not isinstance(cert_name, str):
                raise CredentialsError("The certificate name must be a string")
        if key:
            if not isinstance(key, str):
                raise CredentialsError("The key path must be a string")
        if (cert_name and not key) or (not cert_name and key):
            raise CredentialsError("Both a certificate name and private key must be provided")
        if not isinstance(relogin_forever, bool):
            raise CredentialsError("relogin_forever must be a boolean")

        if 'https://' in url:
            self.ipaddr = url[len('https://'):]
        else:
            self.ipaddr = url[len('http://'):]
        self.uid = uid
        self.pwd = pwd
        self.key = key
        self.cert_name = cert_name
        self.appcenter_user = appcenter_user
        if key and cert_name:
            if NO_OPENSSL:
                raise ImportError('Cannot use certificate authentication because pyopenssl is not available.\n\
                Please install it using "pip install pyopenssl"')

            self.cert_auth = True
            # Cert based auth does not support subscriptions :(
            # there's an exception for appcenter_user relying on the requestAppToken api
            if subscription_enabled and not self.appcenter_user:
                log.warning('Disabling subscription support as certificate authentication does not support it.')
                log.warning('Consider passing subscription_enabled=False to hide this warning message.')
                subscription_enabled = False
            # Disable the warnings for SSL
            if not verify_ssl:
                try:
                    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                except (AttributeError, NameError):
                    pass
            with open(self.key, 'r') as f:
                key_text = f.read()
            try:
                self._x509Key = load_privatekey(FILETYPE_PEM, key_text)
            except Exception:
                raise TypeError('Could not load private key file %s\
                \nAre you sure you provided the private key? (Not the certificate)' % self.key)
        else:
            self.cert_auth = False
        # self.api = 'http://%s:80/api/' % self.ip # 7580
        self.api = url
        self.session = None
        self.verify_ssl = verify_ssl
        self.token = None
        self.login_thread = Login(self)
        self._relogin_callbacks = []
        self.login_error = False
        self._logged_in = False
        self.relogin_forever = relogin_forever
        self._subscription_enabled = subscription_enabled
        self._proxies = proxies
        if subscription_enabled:
            self._subscriber = Subscriber(self)
            self._subscriber.daemon = True
            self._subscriber.start()

    def __reduce__(self) -> Tuple[Type['Session'], Tuple[str, str, Optional[str]]]:
        """
        Get the state of this object for pickling.
        
        Returns:
            Tuple containing the class and constructor arguments
        """
        return self.__class__, (self.api, self.uid, self.pwd)

    def _prep_x509_header(self, method: str, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Prepare the X509 authentication header.
        
        Args:
            method: The HTTP method
            url: The URL to authenticate against
            data: Optional request data
            
        Returns:
            Dictionary containing the authentication header
        """
        if not self.cert_name or not self.key:
            raise CredentialsError("Certificate name and key required for X509 authentication")
            
        timestamp = str(int(time.time()))
        signature = self._generate_signature(method, url, data, timestamp)
        
        return {
            'X-Auth-Token': f"{self.cert_name}:{timestamp}:{signature}"
        }

    def _send_login(self, timeout: Optional[int] = None) -> requests.Response:
        """
        Send a login request to the APIC.
        
        Args:
            timeout: Optional timeout in seconds
            
        Returns:
            The response from the APIC
            
        Raises:
            CredentialsError: If authentication fails
        """
        if not self.uid or not self.pwd:
            raise CredentialsError("Username and password required for authentication")
            
        data = {
            'aaaUser': {
                'attributes': {
                    'name': self.uid,
                    'pwd': self.pwd
                }
            }
        }
        
        try:
            response = self._session.post(
                f"{self.url}/api/aaaLogin.json",
                json=data,
                verify=self.verify_ssl,
                timeout=timeout,
                proxies=self.proxies
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            log.error("Login failed: %s", str(e))
            raise CredentialsError(str(e))

    def login(self, timeout: Optional[int] = None) -> requests.Response:
        """
        Log in to the APIC.
        
        Args:
            timeout: Optional timeout in seconds
            
        Returns:
            The response from the APIC
            
        Raises:
            CredentialsError: If authentication fails
        """
        response = self._send_login(timeout)
        self._logged_in = True
        log.info("Successfully logged in to APIC")
        return response

    def logged_in(self) -> bool:
        """
        Check if logged in to the APIC.
        
        Returns:
            True if logged in, False otherwise
        """
        return self._logged_in

    def refresh_login(self, timeout: Optional[int] = None) -> requests.Response:
        """
        Refresh the login to the APIC.
        
        Args:
            timeout: Optional timeout in seconds
            
        Returns:
            The response from the APIC
            
        Raises:
            CredentialsError: If authentication fails
        """
        return self.login(timeout)

    def close(self) -> None:
        """
        Close the session.
        """
        if self._login_thread:
            self._login_thread.exit()
        if self._subscriber:
            self._subscriber.exit()
        self._session.close()
        self._logged_in = False
        log.info("Closed APIC session")

    def subscribe(self, url: str, only_new: bool = False) -> Optional[requests.Response]:
        """
        Subscribe to events from a URL.
        
        Args:
            url: The URL to subscribe to
            only_new: Whether to only get new events
            
        Returns:
            The response from the APIC or None if subscriptions are disabled
        """
        if not self.subscription_enabled:
            return None
        return self._subscriber.subscribe(url, only_new)

    def is_subscribed(self, url: str) -> bool:
        """
        Check if subscribed to a URL.
        
        Args:
            url: The URL to check
            
        Returns:
            True if subscribed, False otherwise
        """
        if not self.subscription_enabled:
            return False
        return self._subscriber.is_subscribed(url)

    def resubscribe(self) -> None:
        """
        Resubscribe to all active subscriptions.
        """
        if self.subscription_enabled:
            self._subscriber.refresh_subscriptions()

    def has_events(self, url: str) -> bool:
        """
        Check if there are events for a URL.
        
        Args:
            url: The URL to check
            
        Returns:
            True if there are events, False otherwise
        """
        if not self.subscription_enabled:
            return False
        return self._subscriber.has_events(url)

    def get_event_count(self, url: str) -> int:
        """
        Get the number of events for a URL.
        
        Args:
            url: The URL to check
            
        Returns:
            The number of events
        """
        if not self.subscription_enabled:
            return 0
        return self._subscriber.get_event_count(url)

    def get_event(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get an event for a URL.
        
        Args:
            url: The URL to get an event for
            
        Returns:
            The event data or None if no events
        """
        if not self.subscription_enabled:
            return None
        return self._subscriber.get_event(url)

    def unsubscribe(self, url: str) -> None:
        """
        Unsubscribe from a URL.
        
        Args:
            url: The URL to unsubscribe from
        """
        if self.subscription_enabled:
            self._subscriber.unsubscribe(url)

    def push_to_apic(self, url: str, data: Dict[str, Any], timeout: Optional[int] = None) -> requests.Response:
        """
        Push data to the APIC.
        
        Args:
            url: The URL to push to
            data: The data to push
            timeout: Optional timeout in seconds
            
        Returns:
            The response from the APIC
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        try:
            response = self._session.post(
                f"{self.url}{url}",
                json=data,
                verify=self.verify_ssl,
                timeout=timeout,
                proxies=self.proxies
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            log.error("Failed to push to APIC: %s", str(e))
            raise

    def get(self, url: str, timeout: Optional[int] = None) -> requests.Response:
        """
        Get data from the APIC.
        
        Args:
            url: The URL to get from
            timeout: Optional timeout in seconds
            
        Returns:
            The response from the APIC
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        try:
            response = self._session.get(
                f"{self.url}{url}",
                verify=self.verify_ssl,
                timeout=timeout,
                proxies=self.proxies
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            log.error("Failed to get from APIC: %s", str(e))
            raise

    def register_login_callback(self, callback_fn: Callable[[], None]) -> None:
        """
        Register a callback function to be called on login.
        
        Args:
            callback_fn: The callback function to register
        """
        if callback_fn not in self._login_callbacks:
            self._login_callbacks.append(callback_fn)

    def deregister_login_callback(self, callback_fn: Callable[[], None]) -> None:
        """
        Deregister a callback function.
        
        Args:
            callback_fn: The callback function to deregister
        """
        if callback_fn in self._login_callbacks:
            self._login_callbacks.remove(callback_fn)

    def invoke_login_callbacks(self) -> None:
        """
        Invoke all registered login callback functions.
        """
        for callback in self._login_callbacks:
            try:
                callback()
            except Exception as e:
                log.error("Login callback failed: %s", str(e))
