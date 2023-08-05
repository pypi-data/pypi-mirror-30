
import json

version_json = '''
{"version": "0.11.0", "full-revisionid": "a97d4c3092a057fa906089a18fa5d8c51021db25", "date": "2018-03-21T18:00:34.937827", "dirty": false, "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

