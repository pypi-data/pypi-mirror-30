
import json

version_json = '''
{"date": "2018-03-30T21:10:24.315133", "dirty": false, "error": null, "full-revisionid": "ab06213a90deb94ff4e2915e5a174dd8cb7360e0", "version": "0.11.0.post1"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

