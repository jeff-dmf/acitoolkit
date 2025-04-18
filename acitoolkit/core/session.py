"""
Session management for the ACI Toolkit.
This module handles communication with the APIC controller.
"""

from typing import Optional, Dict, Any, List, Union
import logging
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin

# Configure logging
log = logging.getLogger(__name__)

class Session:
    """
    Session class for communicating with the APIC controller.
    
    This class manages the connection to the APIC controller and handles
    authentication, requests, and responses.
    
    Attributes:
        url (str): The base URL of the APIC controller
        username (str): The username for authentication
        password (str): The password for authentication
        verify_ssl (bool): Whether to verify SSL certificates
        timeout (int): Request timeout in seconds
    """
    
    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        verify_ssl: bool = True,
        timeout: int = 30
    ) -> None:
        """
        Initialize a new APIC session.
        
        Args:
            url: The base URL of the APIC controller
            username: The username for authentication
            password: The password for authentication
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
        """
        self.url = url.rstrip('/')
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self._auth = HTTPBasicAuth(username, password)
        self._session = requests.Session()
        
        log.info("Created new APIC session for %s", url)
    
    def login(self) -> bool:
        """
        Log in to the APIC controller.
        
        Returns:
            True if login was successful, False otherwise
        """
        try:
            response = self._session.get(
                urljoin(self.url, '/api/aaaLogin.json'),
                auth=self._auth,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            log.info("Successfully logged in to APIC")
            return True
        except requests.exceptions.RequestException as e:
            log.error("Failed to log in to APIC: %s", str(e))
            return False
    
    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send a GET request to the APIC controller.
        
        Args:
            path: The API path to request
            params: Optional query parameters
            
        Returns:
            The JSON response or None if the request failed
        """
        try:
            response = self._session.get(
                urljoin(self.url, path),
                params=params,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log.error("GET request failed for %s: %s", path, str(e))
            return None
    
    def post(
        self,
        path: str,
        data: Union[Dict[str, Any], str],
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send a POST request to the APIC controller.
        
        Args:
            path: The API path to request
            data: The data to send in the request body
            params: Optional query parameters
            
        Returns:
            The JSON response or None if the request failed
        """
        try:
            response = self._session.post(
                urljoin(self.url, path),
                json=data if isinstance(data, dict) else data,
                params=params,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log.error("POST request failed for %s: %s", path, str(e))
            return None
    
    def subscribe(
        self,
        path: str,
        callback: callable,
        params: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Subscribe to APIC events.
        
        Args:
            path: The API path to subscribe to
            callback: The callback function to call when events are received
            params: Optional query parameters
        """
        try:
            response = self._session.get(
                urljoin(self.url, path),
                params=params,
                verify=self.verify_ssl,
                timeout=None,  # No timeout for subscriptions
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = response.json()
                        callback(data)
                    except ValueError:
                        log.error("Failed to parse JSON from subscription response")
        except requests.exceptions.RequestException as e:
            log.error("Subscription failed for %s: %s", path, str(e))
    
    def close(self) -> None:
        """
        Close the session.
        """
        self._session.close()
        log.info("Closed APIC session") 