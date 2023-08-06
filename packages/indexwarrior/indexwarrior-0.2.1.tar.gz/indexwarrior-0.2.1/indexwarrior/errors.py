# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#     Luis Cañas-Díaz <lcanas@bitergia.com>
#


class BaseError(Exception):
    """Base class for Index Warrior exceptions.

    Derived classes can overwrite the error message declaring ``message``
    property.
    """
    message = "Index Warrior base error"

    def __init__(self, **kwargs):
        super().__init__()
        self.msg = self.message % kwargs

    def __str__(self):
        return self.msg


class InvalidConfigurationFileError(BaseError):
    """Exception raised when the configuration file is not valid."""

    message = "Invalid configuration file at ~/.indexwarrior"


class NotFoundConfigurationFileError(BaseError):
    """Exception raised when the configuration file is not valid."""

    message = "Missing configuration file at ~/.indexwarrior"


class MissingShortcutConfigurationFileError(BaseError):
    """Exception raised when the shortcut is not found."""

    message = "Missing shortcut name at ~/.indexwarrior"


class ESConnectionError(BaseError):
    """Exception raised when the Elasticsearch connection does not work."""

    message = "Failed to establish a connection with %(cause)s, it is alive?"
