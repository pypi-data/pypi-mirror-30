
import json

version_json = '''
{"date": "2018-03-30T20:40:31.433000", "full-revisionid": "ab06213a90deb94ff4e2915e5a174dd8cb7360e0", "dirty": false, "version": "0.11.0.post1", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

