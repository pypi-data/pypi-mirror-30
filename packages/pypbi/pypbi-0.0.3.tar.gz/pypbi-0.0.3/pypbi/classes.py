from . import constants as const
import logging
log = logging.getLogger()
import requests
import yaml
import os
import json
dirname = os.path.dirname(__file__)

API_CALLS = yaml.load(open(os.path.join(dirname, "api_calls.yaml"),"r"))

def get_api_call(callname, wks_id = None):
    """gets an api call depending whether wks_id is None(default workspace)
        or is a workspace ID
    """
    if wks_id:
        base =  const.API_BASE_GROUP
    else:
        base = const.API_BASE

    return base + API_CALLS[callname]

class EntityMixin(object):
    def _get_entities(self, entity_class, api_call):
        cll = get_api_call(api_call, self.wks_id)
        ents = self._pbi._request(cll.format(**vars(self)))
        return [entity_class(self, e) for e in ents]

class GenerateTokenMixin(object):
    def _get_token(self, api_call,  access_level = "View",  identities = ""):
        cll = get_api_call(api_call, self.wks_id)
        if identities != "": identities = ', "identities": ' + identities
        headers = {'Authorization': 'Bearer ' + self._pbi._aad_token}
        headers.update( {'Content-type': 'application/json'})

        data = '{{"accessLevel": "{}" {} }} '.format(access_level, identities)
        resp = requests.post(cll.format(**vars(self)), data = data, headers = headers)
        log.debug(resp.text)
        return json.loads(resp.text)["token"]

class Workspace(EntityMixin):
    def __init__(self, pbi, wks_id = None, wks_name = "", isReadOnly = False):
        '''
        initializes the Workspace class. requires powerbi object.
        If workspace id is passed as None(default), it assumes default (My Workspace)
        '''
        self._pbi = pbi
        self.wks_id = wks_id
        self.wks_name = wks_name
        self.isReadOnly = isReadOnly
    def __str__(self):
        s = "Workspace ID: %s Name: %s" % (self.wks_id, self.wks_name) \
                                    if self.wks_id is not None \
                                    else "Workspace ID: Default Name: My Workspace"
        return s

    def __repr__(self):
        return str(self)

    def get_dashboards(self):
        return self._get_entities(Dashboard, "get_dashboards")

    def get_reports(self):
        return self._get_entities(Report, "get_reports")

    def get_datasets(self):
        return self._get_entities(Dataset, "get_datasets")

    def get_dataset_by_id(self, ds_id):
        ret = [d for d in self.get_datasets() if d.ds_id == ds_id]
        return ret[0] if len(ret) > 0 else None

    def get_report_by_id(self, report_id):
        ret = [r for r in self.get_reports() if r.report_id == report_id]
        return ret[0] if len(ret) > 0 else None

    def get_report_by_name(self, report_name):
        ret = [r for r in self.get_reports() if r.report_name == report_name]
        return ret[0] if len(ret) > 0 else None

    def get_dashboard_by_name(self, dashboard_name):
        ret = [d for d in self.get_dashboards() if d.dashboard_name == dashboard_name]
        return ret[0] if len(ret) > 0 else None

class Dashboard(EntityMixin, GenerateTokenMixin):
    def __init__(self, wks, dashboard):
        self._pbi = wks._pbi
        self._wks = wks
        self.wks_id = wks.wks_id
        self.dashboard_id = dashboard["id"]
        self.dashboard_name = dashboard["displayName"]
    def __str__(self):
        return "Dashboard ID: %s Name: %s" % (self.dashboard_id, self.dashboard_name)

    def __repr__(self):
        log.debug(vars(self))
        return "Dashboard ID: %s Name: %s" % (self.dashboard_id, self.dashboard_name)
    def get_token(self,  access_level = "View",  identities = ""):
        return self._get_token("get_dashboard_token", access_level, identities)

    def get_tiles(self):
        return self._get_entities(Tile, "get_tiles")

    def get_embedUrl(self):
        ''' Dashboards are messed up since they don't return embedUrl
            from REST API. embedUrls are available from tiles,
            and they are the same for all tiles.
            C# API returns it by default, and here we have to get the first
            tile and give back its embedUrl
        '''
        embedUrl = ""
        try:
            embedUrl = self.get_tiles()[0].embedUrl
        except Exception as e:
            log.error("Dashboard {} does not have any tiles".format(self))
            raise e
        self.embedUrl = embedUrl
        return embedUrl

class Tile(GenerateTokenMixin):
    def __init__(self, dashboard, tile):
        self._pbi = dashboard._pbi
        self._wks = dashboard._wks
        self.wks_id = dashboard.wks_id
        self.dashboard_id = dashboard.dashboard_id
        self.tile_id = tile["id"]
        self.title = tile["title"]
        self.subTitle = tile.get("subTitle")
        self.embedUrl = tile["embedUrl"]
        self.rowSpan = tile.get("rowSpan")
        self.colSpan = tile.get("colSpan")
        self.reportId = tile["reportId"]
        self.datasetId = tile["datasetId"]
    def __str__(self):
        return "Tile ID: %s Name: %s" % (self.tile_id, self.title)
    def __repr__(self):
        log.debug(vars(self))
        return "Tile ID: %s Name: %s" % (self.tile_id, self.title)
    def get_token(self,  access_level = "View",  identities = ""):
        return self._get_token("get_tile_token", access_level, identities)


class Report(EntityMixin, GenerateTokenMixin):
    def __init__(self, wks, report):
        self._pbi = wks._pbi
        self._wks = wks
        self.wks_id = wks.wks_id
        self.report_id = report["id"]
        self.report_name = report["name"]
        self.embedUrl = report["embedUrl"]
        self.webUrl = report["webUrl"]

    def __str__(self):
        return "Report ID: %s Name: %s" % (self.report_id, self.report_name)

    def __repr__(self):
        log.debug(vars(self))
        return "Report ID: %s Name: %s" % (self.report_id, self.report_name)
    def get_token(self,  access_level = "View",  identities = ""):
        return self._get_token("get_report_token", access_level, identities)

class Dataset(EntityMixin):
    def __init__(self, wks, ds):
        '''
        Constructs a dataset. If only the ID has been passed, retrieve the dataset
        '''

        self._pbi = wks._pbi
        self._wks = wks
        self.wks_id = wks.wks_id
        self.ds_id = ds["id"]
        self.ds_name = ds["name"]
        self.addRowsAPIEnabled = ds["addRowsAPIEnabled"]
        self.isRefreshable = ds["isRefreshable"]
        self.details = ds
    def __str__(self):
        return "Dataset ID: %s Name: %s" % (self.ds_id, self.ds_name)

    def __repr__(self):
        log.debug(vars(self))
        return "Dataset ID: %s Name: %s" % (self.ds_id, self.ds_name)

    def get_tables(self):
        if not self.addRowsAPIEnabled:
            log.warning("Non-push datasets do not support table API")
            return []
        return self._get_entities(Table, "get_tables")

class Table(object):
    def __init__(self, ds, tbl):
        self._pbi = ds._wks._pbi
        self._ds = ds
        self._wks = ds._wks

        self.ds_id = ds.ds_id
        self.wks_id = ds._wks.wks_id
        self.tbl_name = tbl["name"]
    def _str_(self):
        return "Table: %s" % (self.tbl_name)

    def __repr__(self):
        return "Table: %s" % (self.tbl_name)

    def delete_rows(self):
        headers = {"Authorization": "Bearer " + self._pbi._aad_token}

        req = get_api_call("delete_table_rows", self.wks_id).format(**vars(self))
        log.debug("Deleting rows with request: " + req)
        response = requests.delete(req, headers=headers)