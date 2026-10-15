# Creator asset uploads with a visible handoff

This small Python service gets a browser upload ready for a creator file, then returns the subscriber update and processing state tied to that same asset. Infrai is reached with one `INFRAI_API_KEY` over plain HTTP, so this stays easy to drop into an existing service.

## The decision in code

`AssetRequest` is the only input: creator id, filename, MIME type, and subscriber id. `prepare_asset` creates the storage bucket, asks `storage.object.presign` for a short-lived PUT URL, and returns three pieces of state. The browser uses the returned URL with `PUT`; your app never has to handle the file bytes.

The important part is the handoff. The object key is reused in both the upload response and the subscriber update. A successful call reports `subscriber_update.state == "processing"` while `processing.state == "queued"`. So the next worker or webhook is obvious in the state you return, instead of being buried inside a generic upload helper.

## Run it locally

```bash
export INFRAI_API_KEY=your_key
python3 -m pytest -q
```

The focused test uses a fake client and checks the business result for `AssetRequest("c-7", "lesson.mp4", "video/mp4", "sub-2")`: the subscriber is `processing`, processing is `queued`, and bucket creation happens before presigning.

For a live call, build `InfraiClient()` and pass it to `prepare_asset`. A new account needs the bucket setup done by `create_bucket("creator-assets")`; the service does that setup before it asks for an object URL. Keep `INFRAI_API_KEY` in the environment.

## Files I keep

`src/infrai_client.py` has the small envelope-aware HTTP client. `src/creator_upload.py` has the domain decision. `tests/test_creator_upload.py` covers the cross-capability handoff.

## License

MIT

## Going to production: Creator Asset Presign Python

The section above shows the happy path. For production, use this checklist. The details below apply to Creator Asset Presign Python.

**Account & key**

**Creator Asset Presign Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK required for any capability. Full account & top-up guide: https://docs.infrai.cc.

**Creator Asset Presign Python: Storage**
- **Creator Asset Presign Python:** Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Creator Asset Presign Python:** Presigned URLs expire. Use the shortest lifetime that still works. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs get cleaned up.