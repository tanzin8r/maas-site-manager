from dataclasses import dataclass

SYNC_UPSTREAM_SOURCE_WF_NAME = "SyncUpstreamSource"
REFRESH_UPSTREAM_SOURCE_WF_NAME = "RefreshUpstreamSource"

DOWNLOAD_UPSTREAM_IMAGE_WF_NAME = "DownloadUpstreamImage"


@dataclass
class S3Params:
    endpoint: str
    access_key: str
    secret_key: str
    bucket: str
    path: str


@dataclass
class DownloadUpstreamImageParams:
    ss_root_url: str
    msm_url: str
    msm_jwt: str
    boot_asset_item_id: int
    s3_params: S3Params
    timeout: int = 120


@dataclass
class SyncUpstreamSourceParams:
    msm_url: str
    msm_jwt: str
    boot_source_id: int
    s3_params: S3Params


@dataclass
class RefreshUpstreamSourceParams:
    msm_url: str
    msm_jwt: str
    boot_source_id: int
