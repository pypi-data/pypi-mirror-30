# Copyright 2017 StreamSets Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Abstractions for interacting with StreamSets Dataflow Performance Manager."""

from . import sch_api


class ControlHub:
    """Class to interact with StreamSets Control Hub.

    Args:
        server_url (:obj:`str`): SCH server base URL.
        username (:obj:`str`): SCH username.
        password (:obj:`str`): SCH password.
    """
    def __init__(self, server_url, username, password):
        self.server_url = server_url
        self.username = username
        self.password = password

        self.api_client = sch_api.ApiClient(server_url=self.server_url,
                                            username=self.username,
                                            password=self.password)

        self.login_command = self.api_client.login()

    def create_components(self, component_type, org_id=None, number_of_components=1, active=True):
        """Create components.

        Args:
            component_type (:obj:`str`): Component type.
            org_id (:obj:`str`, optional): Organization ID. Default: DPM organization deduced from username
            number_of_components (:obj:`int`, optional): Default: 1
            active (:obj:`bool`, optional): Default: True

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.CreateComponentsCommand`.
        """
        return self.api_client.create_components(org_id=org_id or self.username.split('@')[1],
                                                 component_type=component_type,
                                                 number_of_components=number_of_components,
                                                 active=active)

    def create_organization(self, new_org):
        """Create Organization.

        Args:
            new_org (:py:obj:`streamsets.sdk.sch_models.NewOrganization`)
        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.CreateOrganizationCommand`
        """
        return self.api_client.create_organization(new_org)
