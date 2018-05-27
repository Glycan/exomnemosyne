# -*- coding: utf-8 -*-
from __future__ import print_function
from pdb import pm, set_trace
from pprint import pprint as pp
from difflib import Differ
import os
import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Exomnemosyne'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'exomnemosyne.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)
    name = service.about().get().execute()["name"]
    results = service.files().list(q="mimeType = 'application/vnd.google-apps.document'").execute()
    docs = results.get('items', [])
    if not docs:
        print('No files found.')
    else:
        entries = []
        for doc in docs[:2]:
            if doc["capabilities"]["canEdit"]:
                revisions = service.revisions().list(fileId=doc["id"]).execute()
                last_revision = []
                for revision in revisions["items"]:
                    revision_text = http.request(revision["exportLinks"]["text/plain"])[1].decode("utf-8-sig").splitlines()
                    if revision.get("lastModifyingUser", {}).get("displayName", "") == name:
                        entries.append({
                            "content": "\n".join([line[2:] for line in
                                Differ().compare(last_revision, revision_text)
                                if line[:2] == "+ "]),
                            "timestamp": revision["modifiedDate"], # strftime?
                            "title": doc["title"],
                            "link": "https://docs.google.com/document/d/" + doc["id"],
                            "kind": "writing",
                            "source": "drive",
                            "account": name
                            })
                    last_revision = revision_text
    return entries

if __name__ == '__main__':
    entries = main()
