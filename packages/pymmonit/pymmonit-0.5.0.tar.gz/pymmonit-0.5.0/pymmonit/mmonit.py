import logging

import requests


log = logging.getLogger(__name__)


class MMonit(object):
    def __init__(self, mmonit_url, username, password, tzinfo=None):
        self.mmonit_url = mmonit_url
        self.username = username
        self.password = password
        self.tzinfo = tzinfo
        self._login()
        self._cache = {}

    def _login(self):
        log.debug('mmonit is requiring a logging in')
        self._session = requests.session()
        self._get('/index.csp')
        login_data = {
            "z_username": self.username,
            "z_password": self.password,
            "z_csrf_protection": "off"
        }
        self._post('/z_security_check', data=login_data)
        log.debug('successfully logged in')

    def _get(self, url, params=None):
        result = self._session.get(self.mmonit_url + url, params=params)
        result.raise_for_status()
        return result

    def _post(self, url, data=None):
        result = self._session.post(self.mmonit_url + url, data)
        result.raise_for_status()
        return result

    def _check_result(self, requestor, attempts=2):
        for _ in range(attempts):
            result = requestor()
            # If an html document is returned, then we need to login
            if result.headers.get('Content-Type') == 'text/html':
                self._login()
            else:
                return result

    def _get_json(self, url, params=None):
        return self._check_result(
            lambda url=url, params=params: self._get(url, params)).json()

    def _post_json(self, url, data=None):
        return self._check_result(
            lambda url=url, data=data: self._post(url, data)).json()

    def _build_dict(self, **kwargs):
        """ Build a dictionary from keyword arguments, dropping any keys where
        the value is None

        Returns
        -------
        dict
        """
        d = {}
        for k, v in kwargs.items():
            if v is not None:
                d[k] = v
        return d

    def _all_results(self, url, base_params):
        idx = 0
        records_total = None
        records_received = 0
        run = True
        while run:
            params = dict(base_params,
                          results=500,
                          startindex=records_received)
            results = self._get_json(url, params)
            if records_total == None:
                records_total = results['totalRecords']
            records_received += results['recordsReturned']
            run = (records_received < records_total
                    or results['recordsReturned'] == 0)
            for record in results['records']:
                yield record

    def _map(self, url, invert=False):
        """ Get a map specified by the URL, a map converts ids to strings.
        For example /map/id/range maps a range id (e.g. 0) to a name (e.g. now)

        Parameters
        ----------
        url : string
            Relative path to the mapping
        invert : boolean (default=False)
            If set to True, returns the inverse mapping. E.g. if /map/id/range
            returns an int -> string mapping then this will invert it so that
            it is a string -> int mapping.

        Returns
        -------
        The mapping or inverse mapping from the specified URL
        """
        cached_resp = self._cache.get(url)
        if cached_resp is not None:
            return cached_resp['inverted' if invert else 'forward']
        resp = self._get_json(url)
        for key in url.strip(' /').split('/'):
            resp = resp[key]
        mapping = {int(k):v for k, v in resp.items()}
        mapping_inv = {v:k for k, v in mapping.items()}
        self._cache[url] = {
            'forward': mapping,
            'inverted': mapping_inv
        }
        return mapping_inv if invert else mapping

    def hosts_list(self, hostid=None, hostgroupid=None, status=None,
                   platform=None, led=None):
        """
        Returns the current status of all hosts registered in M/Monit.

        http://mmonit.com/documentation/http-api/Methods/Status
        """
        data = self._build_dict(
            hostid=hostid,
            hostgroupid=hostgroupid,
            status=status,
            platform=platform,
            led=led)
        if not data:
            return self._get_json('/status/hosts/list')
        return self._post_json('/status/hosts/list', data)

    def hosts_get(self, hostid):
        """
        Returns detailed status of the given host.
        """
        params = dict(id=hostid)
        return self._get_json('/status/hosts/get', params)

    def hosts_summary(self):
        """
        Returns a status summary of all hosts.
        """
        return self._get_json('/status/hosts/summary')

    def map_rangeids(self, invert=False):
        return self._map('/map/id/range', invert=invert)

    def map_statisticstype(self, invert=False):
        return self._map('/map/id/statisticstype', invert=invert)

    def map_hoststatus(self, invert=False):
        return self._map('/map/id/hoststatus', invert=invert)

    def analytics_get(self, timerange='now', hostid=None, statistic=None,
                      kwargs={}):
        """
        Get analytics data, this is an undocument API.

        Parameters
        ----------
        timerange : str (default="today")
            Name of time range, e.g. now, 3 years, minute, etc.
        hostid : int (default=None)
        statistic : str (default=None)
            Name of statistic to get
        """
        if timerange is None:
            rangeid = None
        else:
            rangeid = self.map_rangeids(invert=True)[timerange]
        if statistic is None:
            statisticstype = None
        else:
            statisticstype = self.map_statisticstype(invert=True).get(statistic)
        params = self._build_dict(
            hostid=hostid,
            range=rangeid,
            statisticstype=statisticstype, **kwargs)
        resp = self._post_json('/reports/analytics/get', params)
        return resp

    def uptime_hosts(self):
        """
        http://mmonit.com/documentation/http-api/Methods/Uptime
        """
        return self._get_json('/reports/uptime/list')

    def uptime_services(self, **kwargs):
        params = self._build_dict(**kwargs)
        return self._get_json('/reports/uptime/get', params)

    def events_list(self, **kwargs):
        """ Events overview
        See http://mmonit.com/documentation/http-api/Methods/Events for more
        details on acceptible parameters.

        Parameters
        ----------
        kwargs : keyword arguments
            These are converted to a standard query string

        Returns
        -------
        A generator of events
        """
        params = self._build_dict(**kwargs)
        return self._all_results('/reports/events/list', params)

    def events_get(self, eventid):
        """ Event details """
        params = self._build_dict(id=eventid)
        return self._get_json('/reports/events/get', params)

    def events_summary(self):
        """ Events summary for the last 24 hours """
        return self._get_json('/reports/events/summary')

    def events_dismiss(self, event_id):
        """ Dismiss and active event so it doesn't show up in the event list
        if active filter is set to 2.
        """
        return self._post_json('/reports/events/dismiss', event_id)

    def admin_hosts_list(self):
        """
        http://mmonit.com/documentation/http-api/Methods/Admin_Hosts
        """
        return self._get_json('/admin/hosts/list')

    def admin_hosts_get(self, hostid):
        params = dict(id=hostid)
        return self._get_json('/admin/hosts/get', params)

    def admin_hosts_update(self, hostid, **kwargs):
        return NotImplemented

    def admin_hosts_delete(self, hostid):
        return self._post_json('/admin/hosts/delete', {'id': hostid})

    def admin_hosts_test(self, ipaddr, port, ssl, monituser, monitpassword):
        data = {
            'ipaddr': ipaddr,
            'port': port,
            'ssl': ssl,
            'monituser': monituser,
            'monitpassword': monitpassword
        }
        return self._post_json('/admin/hosts/test', data)

    def admin_hosts_action(self, id, action, service):
        data = {
            'id': id,
            'action': action,
            'service': service
        }
        return self._post_json('/admin/hosts/action', data)

    def admin_groups_list(self):
        return self._get_json('/admin/groups/list')

    def admin_groups_create(self, name):
        """ Create a new host group """
        data = {
            'name': name
        }
        return self._post_json('/admin/groups/create', data)

    def admin_groups_update(self, id, name):
        """ Rename an existing host group
        Parameters
        ----------
        id : int
            host group id
        name : str
            new host group name
        """
        data = {
            'id': id,
            'name': name
        }
        return self._post_json('/admin/groups/update', data)

    def admin_groups_delete(self, id):
        """ Delete an existing host group
        Parameters
        ----------
        id : int
            host group id
        """
        data = {
            'id': id
        }
        return self._post_json('/admin/groups/delete', data)

    def admin_groups_add(self, id, hostids):
        """ Add a host to an existing group
        Parameters
        ----------
        id : int
            host group id
        hostids : int or list(int)
            list of host ids or single host id
        """
        data = {
            'id': id,
            'hostid': hostids
        }
        return self._post_json('/admin/groups/add', data)

    def admin_groups_remove(self, id, hostids):
        """ Remove hosts from an existing group
        Parameters
        ----------
        id : int
            host group id
        hostids : int or list(int)
            list of host ids or single host id
        """
        data = {
            'id': id,
            'hostid': hostids
        }
        return self._post_json('/admin/groups/remove', data)
