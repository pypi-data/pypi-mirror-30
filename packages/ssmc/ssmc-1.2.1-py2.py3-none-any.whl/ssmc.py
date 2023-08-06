"""
Library for Secure Mobile Connect of SAKURA Cloud.
"""

import json
import logging
from typing import Optional, Iterable, List
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)
default_size = 3000


class SIM:
    """
    SIMクラスはSIMのリソースを表します。
    """
    _filter = {
        "Filter": {"Provider.Class": "sim"},
        "Sort": ["ID"],
        "Exclude": ["ServiceClass", "SettingsHash", "Icon", "Provider"]
    }

    def __init__(self, **args):
        self.id: str = args.get("ID", None)
        self.name: str = args.get("Name", None)
        self.iccid: str = args["Status"]["ICCID"]
        self.description: dict = args["Description"]
        self.tags: list(str) = args["Tags"]
        self.created_at: str = args["CreatedAt"]
        self.modified_at: str = args["ModifiedAt"]
        self.availability = args["Availability"] if "Availability" in args else None

    def __repr__(self):
        return (
                "SIM: {ID: %s, ICCID: %s, Name: %s, Description: %s, Tags: %s, CreatedAt: %s}"
                % (self.id, self.iccid, self.name, json.dumps(self.description), self.tags, self.created_at)
        )


class SIMStatus:
    """
    SIMStatus はSIMの設定情報や通信状態といった、実行時に変化するものを扱います。
    """
    _filter = {
        "Sort": ["ID"]
    }

    def __init__(self, **args):
        self.iccid: str = args["iccid"]
        self.imsi: list(str) = args["imsi"]
        self.session_status = args["session_status"]
        self.imei_lock: bool = args["imei_lock"]
        self.registered: bool = args["registered"]
        self.activated: bool = args["activated"]
        self.sim_resource_id: str = args["resource_id"]
        self.registered_date: Optional[str] = args.get("registered_date", None)  # list sim status のときは返ってきていない
        self.activated_date: Optional[str] = args.get("activated_date", None)
        self.deactivated_date: Optional[str] = args.get("deactivated_date", None)
        self.traffic_bytes_of_current_month = args.get("traffic_bytes_of_current_month", {})
        # exist if configured
        self.simgroup_id: Optional[str] = args.get("simgroup_id", None)
        self.ip: Optional[str] = args.get("ip", None)
        self.imei: Optional[str] = args.get("imei", None)
        self.connected_imei: Optional[str] = args.get("connected_imei", None)

    def __repr__(self):
        return (
                "SIMStuts: {sim_resource_id: %s, session_status: %s, simgroup_id: %s}"
                % (self.sim_resource_id, self.session_status, self.simgroup_id)
        )

    def get_traffic_uplink(self):
        key = "uplink_bytes"
        if key in self.traffic_bytes_of_current_month:
            return self.traffic_bytes_of_current_month[key]
        else:
            return 0

    def get_traffic_downlink(self):
        key = "downlink_bytes"
        if key in self.traffic_bytes_of_current_month:
            return self.traffic_bytes_of_current_month[key]
        else:
            return 0


class MGW:
    """
    MGWについてはこのライブラリでは中心的に扱っていないため、SIMをアサインするための最小限の情報のみ取得します
    """
    _filter = {
        "Filter": {"Class": "mobilegateway"},
        "Sort": ["ID"],
        "Exclude": ["ServiceClass", "Settings", "SettingsHash", "Icon", "Remark", "Interfaces"]
    }

    def __init__(self, **args):
        self.id = args['ID']
        self.name = args['Name']

    def __repr__(self):
        return "MGW: {ID: %s, Name: %s}" % (self.id, self.name)


class PagingInfo:
    """
    ページングされた情報をハンドルするための共通クラスです。
    あるAPIについて、ページングされた内容をすべて取得したい場合には以下のようにして、PagingInfoをチェックすることで可能です。::

        while True:
            _, paging = api.some_request(size=size, offset=offset)
            total = paging.total
            offset = paging.size + paging.offset
            if offset >= total:
                break
    """

    def __init__(self, total=None, size=None, offset=None):
        """
        ページング情報

        :param total: 全体の件数
        :param size: 今取得している件数
        :param offset: オフセット
        """
        self.total = total
        self.size = size
        self.offset = offset

    def __repr__(self):
        return f"PagingInfo: {{total: {self.total}, size: {self.size}, offset: {self.offset}}}"


class APIClient:
    """
    セキュアモバイルコネクトのためのAPIクライアントです。
    """
    url_format = "{base_url}/zone/{zone}/api/cloud/1.1/"

    def __init__(self, token: str, secret: str, zone: str = "tk1v",
                 debug: bool = False,
                 base_url="https://secure.sakura.ad.jp/cloud",
                 common_service_item_master_zone="is1a"):
        """
        APIクライアント

        :param token: APIキー
        :param secret: APIシークレットキー
        :param zone: MGWが存在するゾーン
        :param debug: debug mode。request/response のログを見たい場合に利用
        :param base_url: テストのためのオプション。APIエンドポイント
        :param common_service_item_master_zone: テストのためのオプション。CommonServiceItemは特定のゾーンのAPIだけ早いので指定する
        """
        self.debug = debug
        self.client = requests.Session()
        self.client.auth = HTTPBasicAuth(token, secret)

        self.api_url = self.url_format.format(base_url=base_url, zone=zone)
        self.common_service_item_master_url = self.url_format.format(
            base_url=base_url, zone=common_service_item_master_zone
        )

    def _request(self, method, path, params=None, data=None):
        """request helper"""
        base_url = self.api_url
        # TODO: commonserviceitem 系だけはmasterゾーンを叩かないと遅い
        if path.startswith("/commonserviceitem") or path.startswith("commonserviceitem"):
            base_url = self.common_service_item_master_url

        r = self.client.request(method=method,
                                url=urljoin(base_url, path),
                                params=params, data=data)
        if self.debug:
            logger.debug('request url: %s', r.request.url)
            logger.debug('request headers: %s', r.request.headers)
            logger.debug('request body: %s', r.request.body)
            logger.debug("response: %s" % r.text)
        # PUT で 409 のときはなかったことにする
        if (method == "put" or method == "delete") and r.status_code == 409:
            return
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
        status_success = r.json().get("Success", True)
        status_ok = r.json().get("is_ok", True)
        if not status_ok or not status_success:
            raise Exception("Failed to run: method=%s, path=%s" % (method, path))
        return r

    def list_mgws(self, filter=MGW._filter, size=default_size, offset=0) -> (List[MGW], PagingInfo):
        """
        MGWの一覧を取得する

        :param filter: フィルター条件の指定
        :param size: 取得件数
        :param offset: オフセット
        :return: MGWのリスト, ページング情報
        """
        logger.debug("list mgws")
        path = "appliance"
        filter["Count"] = size
        filter["From"] = offset
        r = self._request(method="get", path=path, params=json.dumps(filter))

        resp = r.json()
        result = []
        if "Appliances" in resp:
            for m in resp["Appliances"]:
                result.append(MGW(**m))

        paging = PagingInfo()
        paging.total = int(resp["Total"]) if "Total" in resp else 0
        paging.size = int(resp["Count"]) if "Count" in resp else size
        paging.offset = int(resp["From"]) if "From" in resp else offset
        return result, paging

    def list_sims(self, filter=SIM._filter, size=default_size, offset=0) -> (List[SIM], PagingInfo):
        """
        登録済みのSIM一覧を取得する

        :param filter: フィルター条件の指定
        :param size: 取得件数
        :param offset: オフセット
        :return: SIMのリスト, ページング情報
        """
        logger.debug("list sims of ID")
        path = "commonserviceitem"
        item_key = "CommonServiceItems"

        filter["Count"] = size
        filter["From"] = offset
        r = self._request(method="get", path=path, params=json.dumps(filter))
        resp = r.json()

        result = []
        if item_key in resp:
            for s in resp[item_key]:
                result.append(SIM(**s))

        paging = PagingInfo()
        paging.total = int(resp["Total"]) if "Total" in resp else 0
        paging.size = int(resp["Count"]) if "Count" in resp else size
        paging.offset = int(resp["From"]) if "From" in resp else offset

        return result, paging

    def search_sims_by_name(self, name: str, filter=SIM._filter,
                            size=default_size, offset=0) -> (List[SIM], PagingInfo):
        """
        SIMを名前で部分一致で検索する

        :param name: 中間一致で検索したい名前の文字列
        :param filter: フィルター条件の指定
        :param size: 取得件数
        :param offset: オフセット
        :return: SIMのリスト, ページング情報
        """
        logger.debug(f"search sims by name: {name}")
        filter["Filter"]["Name"] = name
        return self.list_sims(filter=filter, size=size, offset=offset)

    def get_sim_by_name(self, name: str, filter=SIM._filter,
                        size=default_size, offset=0) -> Optional[SIM]:
        """
        SIMを名前で完全一致で検索する"

        :param name: 取得するSIMの名前
        :param filter: フィルター条件の指定
        :param size: 取得件数
        :param offset: オフセット
        :return: SIM or None
        """
        logger.debug(f"get sim by name: {name}")
        filter["Filter"]["Name"] = name
        while True:
            sims, paging = self.list_sims(filter=filter, size=size, offset=offset)
            for sim in sims:
                if sim.name == name:
                    return sim
            offset = paging.size + paging.offset
            total = paging.total
            if offset >= total:
                return None

    def list_sim_statuses_of_mgw(self, mgw_id: str, filter=SIMStatus._filter, size=default_size, offset=0) \
            -> (List[SIMStatus], PagingInfo):
        """
        指定されたMGWにアサインされているSIMのステータス一覧を取得する

        :param mgw_id: MGW のID
        :param filter: フィルター条件の指定
        :param size: 取得件数
        :param offset: オフセット
        :return: SIMのリスト, ページング情報
        """
        logger.debug("list sim status: %s", mgw_id)
        path = f"appliance/{mgw_id}/mobilegateway/sims"

        filter["Count"] = size
        filter["From"] = offset

        r = self._request(method="get", path=path, params=json.dumps(filter))
        resp = r.json()

        result = []
        if "sim" in resp:
            for s in resp["sim"]:
                result.append(SIMStatus(**s))
        paging = PagingInfo()
        paging.total = int(resp["Total"]) if "Total" in resp else 0
        paging.size = int(resp["Count"]) if "Count" in resp else size
        paging.offset = int(resp["From"]) if "From" in resp else offset

        return result, paging

    list_sims_of_mgw = list_sim_statuses_of_mgw

    def get_sim_status(self, sim_id: str) -> SIMStatus:
        """
        指定されたSIMのステータスを取得する

        :param sim_id: SIMのID
        :return: SIMStatus
        """
        logger.debug("get sim status: %s", sim_id)
        path = "commonserviceitem/%s/sim/status" % sim_id
        r = self._request(method="get", path=path)
        if "sim" in r.json():
            return SIMStatus(**r.json()["sim"])
        else:
            raise RuntimeError("Invalid response from cloud api.")

    def create_sim(self, iccid: str, passcode: str,
                   name: Optional[str] = None, description: dict = None,
                   tags: Iterable[str] = None) -> SIM:
        """
        SIMを登録する

        :param iccid: ICCID
        :param passcode: 登録用パスコード
        :param name: 名前(セキュアモバイルコネクトでは、ICCIDで検索できないため、名前をICCIDにすることを強く推奨する)
        :param description: メモ欄に記載する内容を含んだdict
        :param tags: タグ
        :return: 登録に成功していれば、SIMが返る
        """
        path = "commonserviceitem"
        logger.debug("create sim: iccid=%s", iccid)
        name = iccid if name is None else name
        description = json.dumps({"type_num": "dummy-test"}) if description is None else description
        tags = ["test"] if tags is None else tags
        payload = {
            "CommonServiceItem": {
                "Name": name,
                "Description": description,
                "Tags": tags,
                "Status": {
                    "ICCID": iccid
                },
                "Remark": {"PassCode": passcode},
                "Provider": {"Class": "sim"}
            }
        }
        logger.debug("payload: %s", payload)

        r = self._request(method="post", path=path, data=json.dumps(payload))
        if "CommonServiceItem" in r.json():
            return SIM(**r.json()["CommonServiceItem"])
        else:
            raise RuntimeError("Invalid response from cloud api.")

    def update_sim(self, sim: SIM):
        """
        SIMの情報をアップデートする。ただし、アップデート可能なのは、

        * Name
        * Description
        * Tags

        :param sim: 与えられたSIMインスタンスの情報を元にアップデートされる
        :return:
        """
        path = "commonserviceitem/" + sim.id
        logger.debug("update sim: resource id=%s", sim.id)
        payload = {
            "CommonServiceItem": {
                "Name": sim.name,
                "Description": sim.description,
                "Tags": sim.tags,
            }
        }
        logger.debug("payload: %s", payload)
        self._request(method="put", path=path)

    def delete_sim(self, sim_id: str):
        """
        指定されたSIMを登録解除する

        :param sim_id: SIMのID
        :return:
        """
        logger.debug("delete sim: resource id=%s", sim_id)
        path = "commonserviceitem/" + sim_id
        self._request(method="delete", path=path)

    def activate_sim(self, sim_id: str):
        """
        SIMを有効化する

        :param sim_id: SIMのID
        :return:
        """
        logger.debug("activate sim: resource id=%s", sim_id)
        path = "commonserviceitem/" + sim_id + "/sim/activate"
        self._request(method="put", path=path)

    def deactivate_sim(self, sim_id: str):
        """
        SIMを無効化する

        :param sim_id: SIMのID
        :return:
        """
        logger.debug("deactivate sim: resource id=%s", sim_id)
        path = "commonserviceitem/" + sim_id + "/sim/deactivate"
        self._request(method="put", path=path)

    def lock_imei(self, sim_id: str, imei: str):
        """
        IMEI Lock を設定する

        :param sim_id: SIMのID
        :param imei: imei
        :return: sim_id
        """
        logger.debug("lock imei: sim_id=%s, imei=%s" % (sim_id, imei))
        path = "commonserviceitem/%s/sim/imeilock" % sim_id
        payload = {"sim": {"imei": imei}}
        logger.debug("payload: %s", payload)
        self._request(method="put", path=path, data=json.dumps(payload))

    def unlock_imei(self, sim_id: str):
        """
        IMEI を解除する

        :param sim_id: SIMのID
        :param imei: imei
        :return: sim_id
        """
        logger.debug("unlock imei: sim_id=%s" % (sim_id,))
        path = "commonserviceitem/%s/sim/imeilock" % sim_id
        self._request(method="delete", path=path)

    def assign_sim_to_mgw(self, mgw_id: str, sim_id: str):
        """
        SIMをMGWにアサインする
        :param mgw_id: MGWのID
        :param sim_id: SIMのID
        :return:
        """
        logger.debug("assign sim to mgw: sim=%s, mgw=%s", mgw_id, sim_id)
        path = "appliance/%s/mobilegateway/sims" % mgw_id
        payload = {"sim": {"resource_id": sim_id}}
        self._request(method="post", path=path, data=json.dumps(payload))

    def unassign_sim_from_mgw(self, mgw_id: str, sim_id: str):
        """
        MGWからSIMを unassign する
        :param mgw_id: MGWのID
        :param sim_id: SIMのID
        :return:
        """
        logger.debug("unassign sim to mgw: sim=%s, mgw=%s", mgw_id, sim_id)
        path = "appliance/%s/mobilegateway/sims/%s" % (mgw_id, sim_id)
        self._request(method="delete", path=path)

    def set_ip(self, sim_id: str, ip: str):
        """
        SIMに割り当てられるIPを設定する

        * このメソッドを呼ぶためには、SIMはMGWにアサインされている必要がある

        :param sim_id: SIMのID
        :param ip: 割り当てるIPアドレス
        :return:
        """
        logger.debug("set ip: sim=%s, ip=%s", sim_id, ip)
        path = "commonserviceitem/%s/sim/ip" % sim_id
        payload = {"sim": {"ip": ip}}
        self._request(method="put", path=path, data=json.dumps(payload))

    def delete_ip(self, sim_id: str):
        """
        SIMに割り当てられるIPの設定を解除する

        * このメソッドを呼ぶためには、SIMはMGWにアサインされている必要がある

        :param sim_id: SIMのID
        :return:
        """
        logger.debug("delete ip: sim=%s", sim_id)
        path = "commonserviceitem/%s/sim/ip" % sim_id
        self._request(method="delete", path=path)
