import adal
import requests
import json
from pypbi import constants as const
from pypbi import classes as C

import logging
log = logging.getLogger()

class PowerBI(object):
    def __init__(self, user_name, password, client_id):
        self._user_name, self._password, self._client_id  = \
             user_name, password, client_id

        self._aad_token = None
        self.is_connected = False

    def connect(self):
        context = adal.AuthenticationContext(
                    const.PBI_AUTHORITY,
                    validate_authority=True,
                    api_version=None)

        token_response = context.acquire_token_with_username_password(
                                 const.PBI_RESOURCE,
                                 self._user_name,
                                 self._password,
                                 self._client_id)

        self._aad_token = token_response["accessToken"]
        self.is_connected = True
    def _request(self, req,  **params):
        '''
        sends a request to PBI Service. It must be formed beforehand
        '''
        headers = {"Authorization": "Bearer " + self._aad_token}

        log.debug(req)

        response = requests.get(req, headers=headers, **params)
        resp = json.loads(response.text)

        log.debug(response.text)

        if "error" in resp:
            raise RuntimeError("Site returned error: " + str(resp))
        return json.loads(response.text)["value"]

    def get_workspaces(self):
        """
        returns workspaces(groups) as iterator of tuples (id, name)
        """
        groups =  self._request(C.get_api_call("get_groups"))
        ret = []

        #return default workspace (My workspace)
        ret.append( C.Workspace(self))

        for g in groups:
            ret.append( C.Workspace(self, g["id"], g["name"], g["isReadOnly"]))

        return ret

    def get_workspace_by_id(self, wks_id):
        """get workspace (or group in PBI terminology) by id
        If "default" is specified, then the default workspace is returned
        """
        ret = [w for w in self.get_workspaces() if w.wks_id == wks_id]
        return ret[0] if len(ret) > 0 else None

    def get_workspace_by_name(self, wks_name):
        """
        Returns workspace by name
        """
        ret = [w for w in self.get_workspaces() if w.wks_name == wks_name]
        return ret[0] if len(ret) > 0 else None

    def get_report_by_id(self, report_id):
        """Returns report by id"""
        reports  = []
        for w in self.get_workspaces():
            r = w.get_report_by_id(report_id)
            if r: reports.append(r)
        if len(reports) > 1:
            raise ValueError("Duplicate ReportIDs")
        return reports[0] if len(reports) > 0 else None

    def get_report_by_name(self, report_name, wks_name = None):
        """Retuns powerBI report given name
        If workspace is None, assumes there are no duplicates
        """
        wks = self.get_workspace_by_name(wks_name)
        if wks:
            return wks.get_report_by_name(report_name)
        else:
            reports  = []
            for w in self.get_workspaces():
                r = w.get_report_by_name(report_name)
                if r: reports.append(r)
            if len(reports) > 1:
                raise ValueError("Duplicate ReportIDs")
            return reports[0] if len(reports) > 0 else None