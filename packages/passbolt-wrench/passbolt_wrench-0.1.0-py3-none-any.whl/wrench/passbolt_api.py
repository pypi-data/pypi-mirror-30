# wrench -- A CLI for Passbolt
# Copyright (C) 2018 Liip SA <wrench@liip.ch>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA

import logging
from typing import Any, Dict, Iterable, Mapping

from requests_gpgauthlib import GPGAuthSession

from .exceptions import HttpRequestError

base_params = {'api-version': 'v2'}
logger = logging.getLogger(__name__)


def get_passbolt_response(session: GPGAuthSession, path: str, params: Mapping[str, Any] = None,
                          method: str = 'get', **kwargs) -> Any:
    """
    Execute a request on the given `path` on the passbolt server and returns the response body.
    """
    if not params:
        params = {}

    params = dict(base_params, **params)
    response = getattr(session, method)(session.build_absolute_uri(path), params=params, **kwargs)

    if not response.ok:
        logger.error("Got non-ok response from server (status code %s). Contents: %s", response.status_code,
                     response.text)
        raise HttpRequestError(response)

    return response.json()['body']


def get_resources(session: GPGAuthSession, favourite_only: bool) -> Iterable[Dict[str, Any]]:
    """
    Return a list of resource dicts from Passbolt.
    """
    params = {'contain[secret]': 1}
    if favourite_only:
        params['filter[is-favorite]'] = 1

    return get_passbolt_response(session, '/resources.json', params)


def share_resource(session: GPGAuthSession, resource_id: str, data: Dict[str, str]) -> Dict[str, Any]:
    """
    Share the resource identified by `resource_id`.
    """
    return get_passbolt_response(session, '/share/resource/{}.json'.format(resource_id), method='put', data=data)


def get_users(session: GPGAuthSession, terms: str = None) -> Iterable[Dict[str, Any]]:
    """
    Return a list of user dicts from Passbolt.
    """
    params = {'keywords': terms} if terms else {}

    return get_passbolt_response(session, '/users.json', params)


def get_user(session: GPGAuthSession, id: str) -> Dict[str, Any]:
    """
    Return the given user from Passbolt. According to the Passbolt code, `id` can be 'me', in which case the current
    logged in user info is returned.
    """
    return get_passbolt_response(session, '/users/{}.json'.format(id))


def get_groups(session: GPGAuthSession) -> Iterable[Dict[str, Any]]:
    """
    Return a list of group dicts from Passbolt.
    """
    return get_passbolt_response(session, '/groups.json')


def add_resource(session: GPGAuthSession, resource_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add the given resource to Passbolt.
    """
    return get_passbolt_response(session, '/resources.json', method='post', data=resource_data)
