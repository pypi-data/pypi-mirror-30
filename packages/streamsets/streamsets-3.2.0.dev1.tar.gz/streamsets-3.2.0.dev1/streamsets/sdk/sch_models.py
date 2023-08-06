# Copyright 2017 StreamSets Inc.

"""Classes for SCH-related models.

This module provides implementations of classes with which users may interact in the course of
writing tests that exercise SCH functionality.
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewOrganization:
    """ Model that represents a new organization"""

    def __init__(self, organization=None, organization_admin_user=None):
        self._data = {
            'organization': organization._data,
            'organizationAdminUser': organization_admin_user._data
        }

    @property
    def organization(self):
        """Gets the organization of this NewOrganization.

        Args:

        Returns:
            (:obj:`Organization`): Organization
        """
        return self._data['organization']

    @organization.setter
    def organization(self, organization):
        """Sets the organization of this NewOrganization.

        Args:
            organization (:obj:`Organization`): The organization of this NewOrganization
        """
        self._data['organization'] = organization

    @property
    def organization_admin_user(self):
        """Gets the organization_admin_user of this NewOrganization.

        Returns:
            (:obj:`User`): The organization admin user
        """
        return self._data['organization_admin_user']

    @organization_admin_user.setter
    def organization_admin_user(self, organization_admin_user):
        """Sets the organization_admin_user of this NewOrganization.

        Args:
            organization_admin_user (:obj:`User`): The organization_admin_user of this NewOrganization

        """
        self._data['organization_admin_user'] = organization_admin_user


#############################

class Organization:
    """ Model for an Organization """
    # pylint: disable=too-many-arguments,C0103,W0622

    def __init__(self, id=None, name=None, creator=None, created_on=None, last_modified_by=None,
                 last_modified_on=None, primary_admin_id=None, active=False, password_expiry_time_in_millis=None,
                 valid_domains=None, external_auth_enabled=False):
        self._data = {
            'id': id,
            'name': name,
            'creator': creator,
            'createdOn': created_on,
            'lastModifiedBy': last_modified_by,
            'lastModifiedOn': last_modified_on,
            'primaryAdminId': primary_admin_id,
            'active': active,
            'passwordExpiryTimeInMillis': password_expiry_time_in_millis,
            'validDomains': valid_domains,
            'externalAuthEnabled': external_auth_enabled
        }

    @property
    def id(self):
        """Gets the id of this Organization.

        Returns:
            (:obj:`str`): The id of this Organization.
        """
        return self._data['id']

    @id.setter
    def id(self, id):
        """Sets the id of this Organization.

        Args:
            id (:obj:`str`): The id of this Organization.
        """
        self._data['id'] = id

    @property
    def name(self):
        """Gets the name of this Organization.

        Returns:
            (:obj:`str`): The name of this Organization.
        """
        return self._data['name']

    @name.setter
    def name(self, name):
        """Sets the name of this Organization.

        Args:
            name (:obj:`str`): The name of this Organization.
        """
        self._data['name'] = name

    @property
    def creator(self):
        """Gets the creator of this Organization.

        Returns:
            (:obj:`str`): The creator of this Organization.
        """
        return self._data['creator']

    @creator.setter
    def creator(self, creator):
        """Sets the creator of this Organization.

        Args:
            creator (:obj:`str`): The creator of this Organization.
        """
        self._data['creator'] = creator

    @property
    def created_on(self):
        """Gets the created_on of this Organization.

        Returns:
            (:obj:`str`): The created_on of this Organization.
        """
        return self._data['createdOn']

    @created_on.setter
    def created_on(self, created_on):
        """Sets the created_on of this Organization.

        Args:
            created_on (:obj:`int`): The created_on of this Organization.
        """
        self._data['createdOn'] = created_on

    @property
    def last_modified_by(self):
        """Gets the last_modified_by of this Organization.

        Returns:
            (:obj:`str`): The last_modified_by of this Organization.
        """
        return self._data['lastModifiedBy']

    @last_modified_by.setter
    def last_modified_by(self, last_modified_by):
        """Sets the last_modified_by of this Organization.

        Args:
            last_modified_by (:obj:`str`): The last_modified_by of this Organization.
        """
        self._data['lastModifiedBy'] = last_modified_by

    @property
    def last_modified_on(self):
        """Gets the last_modified_on of this Organization.

        Returns:
            (:obj:`str`): The last_modified_on of this Organization.
        """
        return self._data['lastModifiedOn']

    @last_modified_on.setter
    def last_modified_on(self, last_modified_on):
        """Sets the last_modified_on of this Organization.

        Args:
            last_modified_on (:obj:`int `): The last_modified_on of this Organization.
        """
        self._data['lastModifiedOn'] = last_modified_on

    @property
    def primary_admin_id(self):
        """Gets the primary_admin_id of this Organization.

        Returns:
            (:obj:`str`): The primary_admin_id of this Organization.
        """
        return self._data['primaryAdminId']

    @primary_admin_id.setter
    def primary_admin_id(self, primary_admin_id):
        """Sets the primary_admin_id of this Organization.

        Args:
            primary_admin_id (:obj:`str `): The primary_admin_id of this Organization.
        """
        self._data['primaryAdminId'] = primary_admin_id

    @property
    def active(self):
        """Gets the active of this Organization.

        Returns:
            (:obj:`bool`): The active of this Organization.
        """
        return self._data['active']

    @active.setter
    def active(self, active):
        """Sets the active of this Organization.

        Args:
            active (:obj:`bool `): The active of this Organization.
        """
        self._data['active'] = active

    @property
    def password_expiry_time_in_millis(self):
        """Gets the password_expiry_time_in_millis of this Organization.

        Returns:
            (:obj:`int`): The password_expiry_time_in_millis of this Organization.
        """
        return self._data['passwordExpiryTimeInMillis']

    @password_expiry_time_in_millis.setter
    def password_expiry_time_in_millis(self, password_expiry_time_in_millis):
        """Sets the password_expiry_time_in_millis of this Organization.

        Args:
            password_expiry_time_in_millis (:obj:`int`): The password_expiry_time_in_millis of this Organization.
        """
        self._data['passwordExpiryTimeInMillis'] = password_expiry_time_in_millis

    @property
    def valid_domains(self):
        """Gets the valid_domains of this Organization.

        Returns:
            (:obj:`str`): The valid_domains of this Organization.
        """
        return self._data['validDomains']

    @valid_domains.setter
    def valid_domains(self, valid_domains):
        """Sets the valid_domains of this Organization.

        Args:
            valid_domains (:obj:`str`): The valid_domains of this Organization.
        """
        self._data['validDomains'] = valid_domains

    @property
    def external_auth_enabled(self):
        """Gets the external_auth_enabled of this Organization.

        Returns:
            (:obj:`bool`): The external_auth_enabled of this Organization.
        """
        return self._data['externalAuthEnabled']

    @external_auth_enabled.setter
    def external_auth_enabled(self, external_auth_enabled):
        """Sets the external_auth_enabled of this Organization.

        Args:
            external_auth_enabled (:obj:`bool`): The external_auth_enabled of this Organization.
        """
        self._data['externalAuthEnabled'] = external_auth_enabled


class User:
    """ Model for a User """
    def __init__(self, id=None, organization=None, name=None, email=None, roles=None, groups=None, active=False,
                 password_expiry_time=None, creator=None, created_on=None, last_modified_by=None, last_modified_on=None,
                 destroyer=None, delete_time=None, user_deleted=False, name_in_org=None, password_generated=False):
        self._data = {
            'id': id,
            'organization': organization,
            'name': name,
            'email': email,
            'roles': roles,
            'groups': groups,
            'active': active,
            'passwordExpiryTime': password_expiry_time,
            'creator': creator,
            'createdOn': created_on,
            'lastModifiedBy': last_modified_by,
            'lastModifiedOn': last_modified_on,
            'destroyer': destroyer,
            'deleteTime': delete_time,
            'userDeleted': user_deleted,
            'nameInOrg': name_in_org,
            'passwordGenerated': password_generated
        }

    @property
    def id(self):
        """Gets the id of this User.

        Returns:
            (:obj:`str`): The id of this User.
        """
        return self._data['id']

    @id.setter
    def id(self, id):
        """Sets the id of this User.

        Args:
            id (:obj:`str`): The id of this User.
        """
        self._data['id'] = id

    @property
    def organization(self):
        """Gets the organization of this User.

        Returns:
            (:obj:`str`): The organization of this User.
        """
        return self._data['organization']

    @organization.setter
    def organization(self, organization):
        """Sets the organization of this User.

        Args:
            organization (:obj:`Organization`): The organization of this User.
        """
        self._data['organization'] = organization

    @property
    def name(self):
        """Gets the name of this User.

        Returns:
            (:obj:`str`): The name of this User.
        """
        return self._data['name']

    @name.setter
    def name(self, name):
        """Sets the name of this User.

        Args:
            name (:obj:`str`): The name of this User.
        """
        self._data['name'] = name

    @property
    def email(self):
        """Gets the email of this User.

        Returns:
            (:obj:`str`): The email of this User.
        """
        return self._data['email']

    @email.setter
    def email(self, email):
        """Sets the email of this User.

        Args:
            email (:obj:`str`): The email of this User.
        """
        self._data['email'] = email

    @property
    def roles(self):
        """Gets the roles of this User.

        Returns:
            (:obj:`str`): The roles of this User.
        """
        return self._data['roles']

    @roles.setter
    def roles(self, roles):
        """Sets the roles of this User.

        Args:
            roles (:obj:`list[str]`): The roles of this User.
        """
        self._data['roles'] = roles

    @property
    def groups(self):
        """Gets the groups of this User.

        Returns:
            (:obj:`str`): The groups of this User.
        """
        return self._data['groups']

    @groups.setter
    def groups(self, groups):
        """Sets the groups of this User.

        Args:
            groups (:obj:`list[str]`): The groups of this User.
        """
        self._data['groups'] = groups

    @property
    def active(self):
        """Gets the active of this User.

        Returns:
            (:obj:`bool`): The active of this User.
        """
        return self._data['active']

    @active.setter
    def active(self, active):
        """Sets the active of this User.

        Args:
            active (:obj:`bool`): The active of this User.
        """
        self._data['active'] = active

    @property
    def password_expiry_time(self):
        """Gets the password_expiry_time of this User.

        Returns:
            (:obj:`int`): The password_expiry_time of this User.
        """
        return self._data['passwordExpiryTime']

    @password_expiry_time.setter
    def password_expiry_time(self, password_expiry_time):
        """Sets the password_expiry_time of this User.

        Args:
            password_expiry_time (:obj:`int`): The password_expiry_time of this User.
        """
        self._data['passwordExpiryTime'] = password_expiry_time

    @property
    def creator(self):
        """Gets the creator of this User.

        Returns:
            (:obj:`str`): The creator of this User.
        """
        return self._data['creator']

    @creator.setter
    def creator(self, creator):
        """Sets the creator of this User.

        Args:
            creator (:obj:`str`): The creator of this User.
        """
        self._data['creator'] = creator

    @property
    def created_on(self):
        """Gets the created_on of this User.

        Returns:
            (:obj:`int`): The created_on of this User.
        """
        return self._data['createdOn']

    @created_on.setter
    def created_on(self, created_on):
        """Sets the created_on of this User.

        Args:
            created_on (:obj:`int`): The created_on of this User.
        """
        self._data['createdOn'] = created_on

    @property
    def last_modified_by(self):
        """Gets the last_modified_by of this User.

        Returns:
            (:obj:`str`): The last_modified_by of this User.
        """
        return self._data['lastModifiedBy']

    @last_modified_by.setter
    def last_modified_by(self, last_modified_by):
        """Sets the last_modified_by of this User.

        Args:
            last_modified_by (:obj:`str`): The last_modified_by of this User.
        """
        self._data['lastModifiedBy'] = last_modified_by

    @property
    def last_modified_on(self):
        """Gets the last_modified_on of this User.

        Returns:
            (:obj:`int`): The last_modified_on of this User.
        :rtype: int
        """
        return self._data['lastModifiedOn']

    @last_modified_on.setter
    def last_modified_on(self, last_modified_on):
        """
        Sets the last_modified_on of this User.

        Args:
            last_modified_on (:obj:`int`): The last_modified_on of this User.
        """
        self._data['lastModifiedOn'] = last_modified_on

    @property
    def destroyer(self):
        """Gets the destroyer of this User.

        Returns:
            (:obj:`str`): The destroyer of this User.
        """
        return self._data['destroyer']

    @destroyer.setter
    def destroyer(self, destroyer):
        """Sets the destroyer of this User.

        Args:
            destroyer (:obj:`str`): The destroyer of this User.
        """
        self._data['destroyer'] = destroyer

    @property
    def delete_time(self):
        """Gets the delete_time of this User.

        Returns:
            (:obj:`int`): The delete_time of this User.
        """
        return self._data['deleteTime']

    @delete_time.setter
    def delete_time(self, delete_time):
        """Sets the delete_time of this User.

        Args:
            delete_time (:obj:`int`): The delete_time of this User.
        """
        self._data['deleteTime'] = delete_time

    @property
    def user_deleted(self):
        """Gets the user_deleted of this User.

        Returns:
            (:obj:`bool`): The user_deleted of this User.
        """
        return self._data['userDeleted']

    @user_deleted.setter
    def user_deleted(self, user_deleted):
        """Sets the user_deleted of this User.

        :param user_deleted: The user_deleted of this User.
        :type: bool
        """
        self._data['userDeleted'] = user_deleted

    @property
    def name_in_org(self):
        """Gets the name_in_org of this User.

        Returns:
            (:obj:`str`): The name_in_org of this User.
        """
        return self._data['nameInOrg']

    @name_in_org.setter
    def name_in_org(self, name_in_org):
        """Sets the name_in_org of this User.

        Args:
            name_in_org (:obj:`str`): The name_in_org of this User.
        """
        self._data['nameInOrg'] = name_in_org

    @property
    def password_generated(self):
        """Gets the password_generated of this User.

        Returns:
            (:obj:`bool`): The password_generated of this User.
        """
        return self._data['passwordGenerated']

    @password_generated.setter
    def password_generated(self, password_generated):
        """Sets the password_generated of this User.

        Args:
            password_generated (:obj:`bool`): The password_generated of this User.
        """
        self._data['passwordGenerated'] = password_generated

#############################
