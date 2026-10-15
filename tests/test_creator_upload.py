from src.creator_upload import AssetRequest, prepare_asset, visible_state


class FakeClient:
    def __init__(self):
        self.calls = []

    def create_bucket(self, name):
        self.calls.append(("create_bucket", name))

    def presign_upload(self, bucket, key, content_type, request_id):
        self.calls.append(("presign_upload", bucket, key, content_type, request_id))
        return {"url": "https://upload.example/signed"}


def test_upload_handoff_marks_subscriber_processing():
    client = FakeClient()
    result = prepare_asset(AssetRequest("c-7", "lesson.mp4", "video/mp4", "sub-2"), client)
    assert visible_state(result) == "processing"
    assert result["processing"]["state"] == "queued"
    assert client.calls[0] == ("create_bucket", "creator-assets")
    assert client.calls[1][0] == "presign_upload"
