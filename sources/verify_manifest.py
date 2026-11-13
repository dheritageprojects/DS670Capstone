"""Verify the committed snapshot bytes and schema against the recorded source manifest."""
# Check both compressed and uncompressed hashes so archive repacking is distinguishable from data changes.
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'sources/manifest.json').read_text())
for source in manifest['sources']:
    archive_bytes=(root/source['archive_path']).read_bytes()
    assert len(archive_bytes)==source['archive_bytes'], source['id']
    assert hashlib.sha256(archive_bytes).hexdigest()==source['archive_sha256'], source['id']
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        assert [n for n in archive.namelist() if n.endswith('.csv')]==[source['csv_member']]
        content=archive.read(source['csv_member'])
    assert len(content)==source['csv_bytes'], source['id']
    assert hashlib.sha256(content).hexdigest()==source['csv_sha256'], source['id']
    reader=csv.DictReader(io.StringIO(content.decode('utf-8-sig')))
    assert reader.fieldnames==source['columns'], source['id']
    assert sum(1 for _ in reader)==source['raw_rows'], source['id']
    print(f"PASS: {source['id']} archive, CSV, schema, and raw row count verified.")
print('Original CDC URLs and release provenance remain incomplete; hash verification does not establish them.')
