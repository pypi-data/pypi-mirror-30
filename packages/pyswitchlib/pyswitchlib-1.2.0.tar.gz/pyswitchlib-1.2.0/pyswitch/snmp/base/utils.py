"""
Copyright 2017 Brocade Communications Systems, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


class Utils(object):
    """
        This class implements utlis like ping. This class takes extra argument
        like host and auth parameters which can be used to establish CLI connection.
        Attributes:
            None
    """

    def __init__(self, callback):
        """
        utils object init.

        Args:
            callback: Callback function that will be called for each action.
            host: device mgmt_ip
            auth: authentication parameter for device ssh (username, password)

        Returns:

        Raises:
            None
        """
        self._callback = callback
