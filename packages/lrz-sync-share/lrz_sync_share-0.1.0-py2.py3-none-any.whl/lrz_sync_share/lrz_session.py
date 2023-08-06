import requests
import re
import json


LOGIN_URL = "https://syncandshare.lrz.de/login"
FOLDERS_TABLE_URL = "https://syncandshare.lrz.de/folderstable"
FOLDERS_URL = "https://syncandshare.lrz.de/wapi/folders?CSRFToken=%s&action=getAll&maxResults=500"
FILES_URL = "https://syncandshare.lrz.de/wapi/files/%s?action=getAll&CSRFToken=%s"
GET_LINK_URL = "https://syncandshare.lrz.de/getlink/%s/%s"
UPLOAD_URL = "https://syncandshare.lrz.de/upload/"


class wapi(object):
    def __init__(self, json_data, identifier):
        json_data = json.loads(json_data)
        self.obj = {}
        for folder_json in json_data["ResultSet"]["Result"]:
            resURL = folder_json["resourceURL"]
            folder_json["urlID"] = resURL[resURL.rindex("/"):]
            self.obj[folder_json[identifier]] = folder_json


class folders(wapi):
    def __init__(self, json_data):
        super(folders, self).__init__(json_data, "name")


class files(wapi):
    def __init__(self, json_data):
        super(files, self).__init__(json_data, "fileName")


class lrz_session(object):
    """
    username format: [a-z]{2}\d\d[a-z]{3}
    """
    def __init__(self, username, password, shibboleth):
        self.username = username
        self.password = password
        self.shibboleth = shibboleth
        self.session = requests.Session()

    def _login(self):
        fields = {
            "idpSelect": self.shibboleth,
            "Username": self.username,
            "Password": self.password,
            "autoLogin": "true"
        }
        self.r = self.session.post(LOGIN_URL, data=fields)
        if not self.session.cookies.get_dict():
            print("Error: Could not log in.")

    def login(self):
        self._login()
        self.get_root_folders()

    def get_csrf_token(self, reset_url=False):
        if reset_url:
            self.r = self.session.get(FOLDERS_TABLE_URL)

        pattern = re.compile("csrf_token = '(.*?)'")

        return re.search(pattern, self.r.text).group(1)

    def get_root_folders(self):
        token = self.get_csrf_token()
        if not token:
            print("Error: CSRF token not found. "\
                    "Either site structure changed or you're not logged in.")
            return

        r = self.session.get(FOLDERS_URL % token)

        self.folders = folders(r.text)
        return self.folders

    def get_files_in_folder(self, foldername):
        if not self.folders:
            if not self.get_root_folders():
                return

        token = self.get_csrf_token()
        urlID = self.folders.obj[foldername]["urlID"]

        r = self.session.get(FOLDERS_URL % (urlID, token))

        return files(r.text)

    def get_link(self, foldername, filename):
        if not self.folders:
            if not self.get_root_folders():
                return

        root_folder, rest_folders = self.parse_foldername(foldername)

        urlID = self.folders.obj[root_folder]["urlID"]

        r = self.session.get(GET_LINK_URL % (urlID, rest_folders + "/" + filename))

        return r.url.replace("getlink", "dl") + "?inline"

    def parse_foldername(self, foldername):
        folders = foldername.split("/")
        root_folder = folders[0]

        if len(folders) > 1:
            rest_folders = "/".join(folders[1:])
        else:
            rest_folders = ""

        return root_folder, rest_folders

    def upload(self, foldername, filename):
        if not self.folders:
            if not self.get_root_folders():
                return

        root_folder, rest_folders = self.parse_foldername(foldername)

        folder = self.folders.obj[root_folder]

        fields = {
            "folderID": folder["folderID"],
            "path": rest_folders,
            "ajax": "1"
        }
        id_ = folder["urlID"]
        files = {"file": open(filename, "rb")}

        r = self.session.post(UPLOAD_URL + id_, files=files, data=fields)

        return r.text
