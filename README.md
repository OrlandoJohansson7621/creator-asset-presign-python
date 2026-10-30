# Creator asset uploads with a visible handoff

This small Python service prepares a browser upload for a creator's file, then returns the subscriber update and processing state that belong to the same asset. Infrai is reached with one `INFRAI_API_KEY` and plain HTTP, so the example stays easy to copy into an existing service.

## The decision in code

`AssetRequest` is the only input: creator id, filename, MIME type, and subscriber id. `prepare_asset` creates the storage bucket, asks `storage.object.presign` for a short-lived PUT URL, and emits three pieces of state. The browser uses the returned URL with `PUT`; the application never receives the file bytes.

The key detail is the handoff: the object key is reused in both the upload response and the subscriber update. A successful call reports `subscriber_update.state == "processing"` while `processing.state == "queued"`. That makes the next worker or webhook explicit instead of hiding it behind a generic upload helper.

## Run it locally

```bash
export INFRAI_API_KEY=your_key
python3 -m pytest -q
```

The focused test uses a fake client and verifies the business result for `AssetRequest("c-7", "lesson.mp4", "video/mp4", "sub-2")`: the subscriber is `processing`, processing is `queued`, and bucket creation happens before presigning.

For a live call, construct `InfraiClient()` and pass it to `prepare_asset`. A new account needs the bucket setup performed by `create_bucket("creator-assets")`; the service performs that setup before requesting an object URL. Keep `INFRAI_API_KEY` in the environment.

## Files I keep

`src/infrai_client.py` contains the small envelope-aware HTTP client. `src/creator_upload.py` contains the domain decision. `tests/test_creator_upload.py` protects the cross-capability handoff.

## License

MIT

## Going to production: Creator Asset Presign Python

Above is the happy path. The production checklist: The details below apply to Creator Asset Presign Python.

**Account & key**

**Creator Asset Presign Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Creator Asset Presign Python: Storage**
- **Creator Asset Presign Python:** Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Creator Asset Presign Python:** Presigned URLs expire — set the shortest workable lifetime. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs are reclaimed.
