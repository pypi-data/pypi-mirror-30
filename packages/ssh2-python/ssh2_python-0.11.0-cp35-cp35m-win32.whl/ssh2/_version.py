
import json

version_json = '''
{"version": "0.11.0", "error": null, "date": "2018-03-21T17:54:17.453848", "dirty": false, "full-revisionid": "a97d4c3092a057fa906089a18fa5d8c51021db25"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

