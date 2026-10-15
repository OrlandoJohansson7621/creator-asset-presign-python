from dataclasses import dataclass
from typing import Any

from .infrai_client import InfraiClient


@dataclass(frozen=True)
class AssetRequest:
    creator_id: str
    filename: str
    content_type: str
    subscriber_id: str


def prepare_asset(request: AssetRequest, client: InfraiClient, bucket: str = "creator-assets") -> dict[str, Any]:
    key = f"{request.creator_id}/{request.filename}"
    client.create_bucket(bucket)
    signed = client.presign_upload(bucket, key, request.content_type, f"{request.creator_id}:{request.filename}")
    return {
        "upload": {"method": "PUT", "url": signed["url"], "key": key},
        "subscriber_update": {"subscriber_id": request.subscriber_id, "state": "processing", "asset_key": key},
        "processing": {"state": "queued", "content_type": request.content_type},
    }


def visible_state(result: dict[str, Any]) -> str:
    return result["subscriber_update"]["state"]

