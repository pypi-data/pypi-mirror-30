
import json

version_json = '''
{"full-revisionid": "ab06213a90deb94ff4e2915e5a174dd8cb7360e0", "dirty": false, "version": "0.11.0.post1", "date": "2018-03-30T20:48:53.298426", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

