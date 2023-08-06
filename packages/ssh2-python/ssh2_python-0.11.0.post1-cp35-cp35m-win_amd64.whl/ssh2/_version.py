
import json

version_json = '''
{"error": null, "version": "0.11.0.post1", "full-revisionid": "ab06213a90deb94ff4e2915e5a174dd8cb7360e0", "date": "2018-03-30T20:58:46.887013", "dirty": false}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

