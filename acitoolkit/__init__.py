# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
ACI Toolkit
A Python library for interacting with Cisco ACI (Application Centric Infrastructure).
"""

import logging
from .core import (
    BaseACIObject,
    BaseInterface,
    Session,
    validate_ip_address,
    validate_ip_network,
    parse_encap,
    format_encap,
    get_current_time,
    validate_mac_address,
    format_mac_address,
    validate_name,
    validate_description,
    get_class_name,
    get_module_name,
    get_full_class_name
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a logger for the package
log = logging.getLogger(__name__)

# Version information
__version__ = '1.0.0'
__author__ = 'Cisco Systems'
__license__ = 'Apache License, Version 2.0'

__all__ = [
    'BaseACIObject',
    'BaseInterface',
    'Session',
    'validate_ip_address',
    'validate_ip_network',
    'parse_encap',
    'format_encap',
    'get_current_time',
    'validate_mac_address',
    'format_mac_address',
    'validate_name',
    'validate_description',
    'get_class_name',
    'get_module_name',
    'get_full_class_name',
    '__version__',
    '__author__',
    '__license__'
]
