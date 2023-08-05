
import json

version_json = '''
{"date": "2018-03-21T18:52:24.742000", "full-revisionid": "a97d4c3092a057fa906089a18fa5d8c51021db25", "dirty": false, "version": "0.11.0", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

