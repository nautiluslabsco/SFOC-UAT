import io
import json
import os
import urllib.parse as urlparse
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlencode

import dateutil.parser
import jsonlines
import requests

#from .ds_model import DSModel

PROD = "prod"
STAGING = "staging"
QA = "qa"
DEV = "dev"

endpoints = {
    PROD: "https://api.nautiluslabs.co",
    STAGING: "https://staging-api.nautiluslabs.co",
    QA: "https://qa-api.nautiluslabs.co",
    DEV: "http://localhost:8080",
}


def truncate_dt(t, duration=timedelta(hours=1)):
    """
    truncate_dt performs datetime truncation to the give duration
    """
    return t - (timedelta(seconds=t.timestamp()) % duration)


def as_epoch(timevalue):
    if isinstance(timevalue, datetime):
        timevalue = timevalue.timestamp()

    if isinstance(timevalue, (int, float)):
        return int(timevalue)

    return int(
        dateutil.parser.parse(
            timevalue, default=dateutil.parser.parse("00:00Z")
        ).timestamp()
    )


def feats_to_df(feats):
    from numpy import nan

    df = timeseries_to_df(feats["timestamps"], feats["means"])
    df["lat"] = [
        lat_lng[0] if lat_lng is not None else nan for lat_lng in feats["positions"]
    ]
    df["lng"] = [
        lat_lng[1] if lat_lng is not None else nan for lat_lng in feats["positions"]
    ]
    return df


def timeseries_to_df(timestamps, metrics):
    from numpy import nan
    from pandas import DataFrame, to_datetime

    df = DataFrame(
            metrics,
            index= to_datetime(timestamps, unit='s'),
            )
    df.fillna(value=nan, inplace=True)
    return df


def get_aligned_hourly_timestamps(start_time, end_time):
    """
    start_time (datetime object) start of the aligned timestamps
    end_time end time (datetime object) of the aligned timestamps

    function creates a date range from start_time to end_time with 1 hour period between each element
    """

    import pandas as pd

    return pd.date_range(
        freq="H",
        start=start_time,
        end=end_time,
        tz="utc",
    )


def align_timestamps_df(start_time, end_time, features_df):
    import pandas as pd

    """
    features_df features data frame
    start_time (datetime object) start of the aligned timestamps
    end_time (datetime object) end time of the aligned timestamps

    function creates a date range from start_time to end_time with 1 hour period between each element,
    and performs a "left join" on features to retrieve feature elements within matching timestamps
    """
    return features_df.reindex(
        get_aligned_hourly_timestamps(start_time, end_time),
    )


class NLClient(object):
    """NLClient is a client for interacting with the Nautilus Labs API"""

    def __init__(self, stage=PROD, endpoint=None):
        if endpoint:
            endpoint = endpoint
        elif stage in endpoints:
            endpoint = endpoints[stage]
        else:
            raise ValueError("invalid stage identifier: {}".format(stage))

        p = urlparse.urlparse(endpoint)

        if not p.scheme or not p.netloc:
            raise ValueError(
                "endpoint must specify a scheme and location: {}".format(endpoint)
            )

        self.__scheme = p.scheme
        self.__netloc = p.netloc
        self.__cookies = None

    def do(self, method, path, output="json", **kwargs):
        if output not in ("json", "text", "raw"):
            raise Exception("unexpected output type: {}".format(output))
        kwargs["cookies"] = self.__cookies
        resp = requests.request(method, self.__build_url(path), **kwargs)
        self.__raise_for_status(resp)

        if output == "json":
            return resp.json()
        elif output == "text":
            return resp.text
        else:
            return resp

    def login(self, *, token=None, email=None, password=None):
        if token:
            self.__cookies = dict(access_token=token)
            return self

        if email is None and password is None:
            email = os.getenv("NAUTILUS_EMAIL")
            password = os.getenv("NAUTILUS_PASSWORD")
            if email == "" and password == "":
                raise ValueError(
                    "NAUTILUS_EMAIL and NAUTILUS_PASSWORD are not set, please refer to https://www.notion.so/nautiluslabs/Onboarding-7896dbd4881741458b34a29ba375111f"
                )

        resp = requests.post(
            self.__build_url("login"), json={"email": email, "password": password}
        )
        self.__raise_for_status(resp)

        self.__cookies = resp.cookies
        return self

    def access_token(self):
        return self.__cookies.get("access_token") if self.__cookies else None

    def __build_url(self, path):
        return urlparse.urlunparse([self.__scheme, self.__netloc, path, "", "", ""])

    def __raise_for_status(self, resp):
        if 400 <= resp.status_code < 600:
            if len(resp.text) > 0:
                raise requests.HTTPError(
                    "Error status {}: {}".format(resp.status_code, resp.text),
                    response=resp,
                )
            else:
                raise requests.HTTPError(
                    "Error status {}".format(resp.status_code), response=resp
                )

    def get_features(
        self,
        ship_id,
        start_time=None,
        end_time=-1,
        minute=False,
        weather=False,
        cleanup_data=True,
        as_df=False,
        properties=[],
        timeout=None,
        exclude_noon=False,
        **kwargs,
    ):
        """
        get_features returns features from the features API.

        It also takes a start_time and end_time parameter that are either a
        datetime, a unix timestamp, or an approximation of an RFC3339 date
        string, to be parsed in UTC or the strings specifed timezone.

        Additional kwargs get passed along to the features API.
        """

        # when startTime is unspecified, default to 7 days of data
        if start_time is None:
            start_time = datetime.now() - timedelta(days=7)

        params = {
            "startTime": as_epoch(start_time),
            "endTime": as_epoch(end_time),
            "properties": json.dumps(properties),
        }

        if not cleanup_data:
            params["nocleanup"] = ""

        if minute:
            params["minute"] = ""

        if weather:
            params["weather"] = ""

        if exclude_noon:
            params["excludeNoon"] = ""

        params.update(kwargs)

        url = "api/features/{}".format(ship_id)
        resp_json = self.do(method="GET", path=url, params=params, timeout=timeout)

        if as_df:
            return feats_to_df(resp_json)
        else:
            return resp_json

    def persist_model(self, model):
        self.do("POST", "api/models", json=model)

    def get_model(self, ship_id, model_type):
        url = "api/models/{}/{}".format(model_type, ship_id)
        return self.do(method="GET", path=url)

    def persist_model_timeseries(self, model):
        self.do("POST", "api/model-timeseries", json=model)

    def get_model_timeseries(self, ship_id, model_type):
        url = "api/model-timeseries/{}/{}".format(model_type, ship_id)
        return self.do(method="GET", path=url)

    def get_vendors(self):
        '''
        get_vendors return all vendor information from the vendors table.
        '''

        return self.do(
            method="GET",
            path="api/admin/ingest/vendors",
            output="json",
            stream=True,
        )

    def get_vendor(self, vendor_id: int):
        '''
        get_vendor return vendor specific information from the vendors table.
        '''

        return self.do(
            method="GET",
            path=f"api/admin/ingest/vendor/{vendor_id}",
            output="json",
            stream=True,
        )

    def get_ship_vendor_association(
        self, ship_id: Optional[int] = None, vendor_id: Optional[int] = None
    ):
        '''
        get_ship_vendor_association returns ship_id and vendor_id pairs that are associated
        in the ship_vendor_association table for any given ship_id or vendor_id.
        '''
        if ship_id is None and vendor_id is None:
            return None

        path = (
            f"api/admin/ingest/ship/{ship_id}/vendors"
            if ship_id is not None
            else f"api/admin/ingest/vendor/{vendor_id}/ships"
        )
        return self.do(
            method="GET",
            path=path,
            output="json",
            stream=True,
        )["ship_vendor_associations"]

    def get_records(self, ship_id, start_time, end_time):
        """
        get_records returns records from the ingest API.

        It takes a start and end time parameter that are either a
        datetime, a unix timestamp, or an approximation of an RFC3339 date
        string, to be parsed in UTC or the strings specified timezone.
        """

        resp = self.do(
            method="GET",
            path="api/admin/ingest/ship/{}/records".format(ship_id),
            output="raw",
            params={"startTime": as_epoch(start_time), "endTime": as_epoch(end_time)},
            headers={"Accept-Encoding": "chunked"},
            stream=True,
        )

        return list(jsonlines.Reader(resp.iter_lines(chunk_size=None)))

    def persist_records(
        self, records, ship_id: Optional[int] = None, backfill=True, output='json'
    ):
        """
        posts records to the ingest API.

        ship_id is required if records are shipless
        """
        buf = io.StringIO()
        with jsonlines.Writer(buf, compact=True) as w:
            w.write_all(records)

        path = (
            f"api/admin/ingest/ship/{ship_id}/records"
            if ship_id
            else "api/admin/ingest/records"
        )
        return self.do(
            method="POST",
            path=path,
            data=buf.getvalue(),
            output=output,
            params={"backfill": backfill},
        )

    def persist_samples(self, ship_id, samples, succession_strategy="created_at"):
        """
        persist_samples persists samples for ship_id to the ingest API.

        It takes a list of samples and uses created_at sample succession.
        """

        buf = io.StringIO()
        with jsonlines.Writer(buf, compact=True) as w:
            w.write_all(samples)

        return self.do(
            method="POST",
            path="api/admin/ingest/ship/{}/samples".format(ship_id),
            data=buf.getvalue(),
            params={"successionStrategy": succession_strategy},
        )

    def get_tce_projection(
        self, ship_id, voyage_id, leg_id, time, params={"kind": "best-tce"}
    ):
        """
        get_tce_projection gets the tce projection for the specific ship/voyage/leg at the
        specified time
        """
        params["startTime"] = as_epoch(time)
        params["refTime"] = as_epoch(time)
        url = "api/projections/ship/{}/voyage/{}/{}/tce".format(
            ship_id, voyage_id, leg_id
        )
        return self.do(method="GET", path=url, params=params)

    def get_route(self, id, params={}):
        """
        get_route returns the route with the provided id, if the id is None, queries the route api with the provided search params
        """
        url = "api/routes" if id is None else f"api/routes/{id}"
        return self.do(method="GET", path=url, params=params)

    def get_voyages(self, ship_id):
        """
        get_voyages returns metadata about the voyages and corresponding legs
        including the start and end times and ballast/laden tags
        """

        url = "api/voyages/{}".format(ship_id)
        return self.do(method="GET", path=url)

    def get_noon_features(self, ship_id, start_time=None, end_time=-1, as_df=False):
        """
        get_noon_features returns the noon data for the specified input parameters

        It takes a start and end time parameter that are either a
        datetime, a unix timestamp, or an approximation of an RFC3339 date
        string, to be parsed in UTC or the strings specifed timezone.
        """

        # when startTime is unspecified, default to 7 days of data
        if start_time is None:
            start_time = datetime.now() - timedelta(days=7)

        params = {"startTime": as_epoch(start_time), "endTime": as_epoch(end_time)}

        url = "api/noon-features/{}".format(ship_id)
        resp_json = self.do(method="GET", path=url, params=params)

        if as_df:
            return feats_to_df(resp_json)
        else:
            return resp_json

    def get_ship(self, ship_id):
        """
        get_ship returns a ship
        """

        url = "api/fleet/ships/{}".format(ship_id)
        return self.do(method="GET", path=url)

    def get_ships(self, **kwargs):
        """
        get_ships returns ships
        zero parameters returns ships relevant to your user - all ships if you are a super user
        pass the query parameter "integration_company_id" to select ships for a specific integration
        """

        return self.do(method="GET", path="api/fleet/ships", **kwargs)

    def get_ship_metadata(self, ship_id):
        """
        get_ship_metadata returns ship metadata
        """

        url = "api/fleet/ships/{}/meta".format(ship_id)
        return self.do(method="GET", path=url)

    def get_performance_config(self, **kwargs):
        """
        get_performance_config returns performance config for the specified primary key in kwargs.

        kwargs can be any combination of primary key (ship_id, module_id)
        ex1: {"ship_id": "2", "module_id": "*"}
        ex2: {"ship_id": "*"}
        """

        path = "/api/performance/config"
        return self.do(method="GET", path=path, params=kwargs)

    def put_performance_config(self, data, **kwargs):
        """
        put_performance_config will update config with specified primary key with data,
        if primary key does not exist in db, it will create a config with specified primary key with data

        kwargs can be any combination of primary key (ship_id, module_id), and overwrite_on_update
        ex1: {"ship_id": "2", "module_id": "*"}
        ex2: {"ship_id": "*", overwrite_on_update:"true"}

        if overwrite_on_update is present and an update occurs, data will overwrite the config stored in specified primary key;
        if an update occurs without overwrite_on_update, data will be merged with existing config stored
        """

        path = "/api/performance/config"
        return self.do(method="PUT", path=path, params=kwargs, json=data)

    def get_ds_model(
        self,
        ds_model_id=None,
        include_blob=False,
        json_format=False,
        ship_id=None,
        product=None,
        core_input=None,
        output=None,
    ):
        """
        get_ds_model returns a ds_model for the specified ds_model_id and returns a blob if include_blob is True
        """
        if ds_model_id is None and (None in [ship_id, product, core_input, output]):
            raise Exception(
                "must specify a ds_model_id or a ship_id, product, core_input, and output"
            )

        if ds_model_id is None:
            product_refs = self.get_ds_model_product_references(
                product, ship_id, core_input, output
            )
            if len(product_refs) == 0:
                raise Exception(
                    "no product references for ({}, {}, {})".format(
                        product, core_input, output
                    )
                )
            ds_model_id = product_refs[0]["ds_model_id"]

        path = f"/api/ds/models/{ds_model_id}"
        params = {}
        if include_blob:
            params[
                "include_blob"
            ] = "true"  # needs to be a string because this is the format webportal expects

        ds_model_dict = self.do(method="GET", path=path, params=params)
        if json_format:
            return ds_model_dict
        return DSModel.from_dict(ds_model_dict)

    def get_ds_models(self):
        """
        get_ds_models returns all the ds_models

        blobs are not include as a part of the response
        """

        path = "/api/ds/models"
        return self.do(method="GET", path=path)

    def create_ds_model(
        self,
        blob,
        blob_format,
        core_input,
        inputs,
        output,
        ship_id=None,
        algorithm=None,
        error_metrics=None,
        metadata=None,
    ):
        """
        create_ds_model creates a ds_model with the provided inputs

        ship_id None is for multi ship model

        blob_format is an enum and must be either 'argus', 'modeler', 'lua', 'xgb', or 'serialized'

        if the hash of blob does not exist in db, a new row will be created in the db. Otherwise, updated_at column will be updated to now.
        the created or updated model will be returned.
        """

        path = "/api/ds/models"
        return self.do(
            method="POST",
            path=path,
            json={
                "ship_id": ship_id,
                "blob": blob,
                "blob_format": blob_format,
                "core_input": core_input,
                "inputs": inputs,
                "output": output,
                "algorithm": algorithm,
                "error_metrics": error_metrics,
                "metadata": metadata,
            },
        )

    def get_ds_model_product_references(
        self, product, ship_id, core_input=None, output=None
    ):
        """
        get_ds_model_product_references returns all ds_model_product_references, along with their associated core_input and output in ds_model
        for the specified arguments
        """
        path = f"/api/ds/models/products/{product}/ships/{ship_id}"
        params = {}
        if core_input:
            params["core_input"] = core_input
        if output:
            params["output"] = output
        return self.do(method="GET", path=path, params=params)

    def create_ds_model_product_reference(self, ship_id, ds_model_id, product):
        """
        create_ds_model_product_reference creates a ds_model_product_reference

        the ds_model_product_reference created will be returned as a part of the response, along with its corresponding core_input and ouput from ds_model
        """

        path = f"/api/ds/models/products"
        return self.do(
            method="POST",
            path=path,
            json={
                "ds_model_id": ds_model_id,
                "ship_id": ship_id,
                "product": product,
            },
        )

    def get_features_v2(
        self,
        ship_id,
        start_time=None,
        end_time=None,
        properties=[],
        as_df=False,
        df_key=lambda feature: feature["metadata"]["name"],
        **kwargs,
    ):
        """
        get features_v2 returns features from features_v2

        properties is a list of properties; example: [{"domain": "features_v1", "args": "Draft Aft}]
        start_time start time in unix; if not provided, use 07/12/2016, which is the min (time) from a non "Nautilus" ship from raw_samples table
        end_time end time in unix; if not provided, truncate to start of today

        default start_time and end_time are the same as performance frontend requests
        """
        if not start_time:
            start_time = datetime(2016, 7, 12, tzinfo=timezone.utc).timestamp()
        if not end_time:
            end_time = truncate_dt(datetime.now()).timestamp()

        if as_df:
            properties = properties + [{"domain": "features_v1", "args": "timestamps"}]

        resp = self.do(
            "POST",
            f"/proteus/api/features/ship/{ship_id}",
            json={
                "start_time": start_time,
                "end_time": end_time,
                "properties": properties,
            },
            **kwargs,
        )

        if as_df:
            feats = [
                {
                    "data": f["data"]["values"] if "values" in f["data"] else f["data"],
                    "metadata": f["metadata"],
                }
                for f in resp["features"]
            ]

            return timeseries_to_df(
                feats[-1]["data"],
                {df_key(feature): feature["data"] for feature in feats[:-1]},
            )

        return resp

    def get_metrics(
        self, ship_id, start_time=None, end_time=-1, properties=[], as_df=False
    ):
        """
        get_metrics returns tethys metrics for the given ship_id and property list over the specified interval
        """
        # when startTime is unspecified, default to 7 days of data
        if start_time is None:
            start_time = datetime.now() - timedelta(days=7)

        if end_time == -1:
            end_time = datetime.now()

        resp = self.do(
            "POST",
            f"api/fleetview/metrics/{ship_id}",
            params={
                "rate": 3600,
                "startTime": as_epoch(start_time),
                "endTime": as_epoch(end_time),
            },
            json=properties,
        )

        if resp["metrics"] == None:
            raise Exception("metrics in response is None")

        if as_df:
            timestamps = resp["metrics"]["Timestamps"]
            del resp["metrics"]["Timestamps"]
            return timeseries_to_df(timestamps, resp["metrics"])

        return resp
