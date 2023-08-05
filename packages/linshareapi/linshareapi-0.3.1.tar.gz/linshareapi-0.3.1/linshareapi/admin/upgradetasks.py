#! /usr/bin/env python
# -*- coding: utf-8 -*-


# This file is part of Linshare api.
#
# LinShare api is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LinShare api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LinShare api.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#


from __future__ import unicode_literals

from linshareapi.core import ResourceBuilder
from linshareapi.cache import Cache as CCache
from linshareapi.cache import Invalid as IInvalid
from linshareapi.admin.core import GenericClass
from linshareapi.admin.core import Time as CTime
from linshareapi.admin.core import CM

# pylint: disable=C0111
# Missing docstring
# pylint: disable=R0903
# Too few public methods
# -----------------------------------------------------------------------------
class Time(CTime):
    def __init__(self, suffix, **kwargs):
        super(Time, self).__init__('up_tasks.' + suffix, **kwargs)


# -----------------------------------------------------------------------------
class Cache(CCache):
    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'up_tasks', **kwargs)


# -----------------------------------------------------------------------------
class Invalid(IInvalid):
    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'up_tasks', **kwargs)


# -----------------------------------------------------------------------------
class UpgradeTasks(GenericClass):

    local_base_url = "upgrade_tasks"

    def get_rbu(self):
        rbu = ResourceBuilder("upgrade_tasks")
        rbu.add_field('identifier', required=True)
        rbu.add_field('taskOrder')
        rbu.add_field('status')
        rbu.add_field('priority')
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate')
        rbu.add_field('parentIdentifier', extended=True)
        rbu.add_field('taskGroup', extended=True)
        rbu.add_field('asyncTaskUuid', extended=True)
        return rbu

    @Time('invalid')
    @Invalid()
    def invalid(self):
        return "invalid : ok"

    @Time('list')
    @Cache()
    def list(self):
        return self.core.list(self.local_base_url)

    @Time('get')
    def get(self, uuid):
        url = "{base}/{uuid}".format({
            'base': self.local_base_url,
            'uuid': uuid
        })
        return self.core.get(url)

    # @Time('delete')
    # @Invalid()
    # def delete(self, uuid):
    #     """ Delete one list."""
    #     url = "{base}/{uuid}".format({
    #         'base': self.local_base_url,
    #         'uuid': uuid
    #     })
    #     return self.core.delete(url)

    # @Time('update')
    # @Invalid()
    # def update(self, data):
    #     """ Update a list."""
    #     self.debug(data)
    #     url = "{base}/{uuid}".format({
    #         'base': self.local_base_url,
    #         'uuid': data.get('uuid')
    #     })
    #     return self.core.update(url, data)
