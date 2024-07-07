import requests
import hashlib
from xml.etree import ElementTree
from .scstream import md5crypt
class Webshare:
  """
  Webshare API wrapper.
  """
  headers = {
    'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'text/xml; charset=UTF-8',
    'Accept-Encoding': 'identity',
    'User-Agent': 'Kodi/21.0-BETA2 (Macintosh; ARM Mac OS X 14_2_1) App_Bitness/64 Version/21.0-BETA2-(20.90.821)-Git:20231217-176032a3b8',
  }
  url = "https://webshare.cz"
  deviceId = None
  token = None
  # deviceId = "562737bb-2a38-4d3e-a891-b41b6c19e732"
  # token = ""
  def __init__(self, deviceId=None, token=None):
    """
    _summary_
    """
    self.deviceId = deviceId
    self.token = token
  def __repr__(self):
        return self.__class__.__name__

  def common_headers(self):
    requestHeaders = self.headers
    requestHeaders['X-Uuid'] = self.deviceId
    return requestHeaders
  @staticmethod
  def hash_password(password, salt):
    """Creates password hash with salt from Webshare API"""
    return hashlib.sha1(md5crypt(password, salt=salt).encode('utf-8')).hexdigest()

  def get_salt(self, username):
        """
        POST /api/salt/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        data = {
          "username_or_email": username
        }
        response = requests.post(
            self.url + '/api/salt/',
            headers=self.common_headers(),
            data=data,
        )
        tree = ElementTree.fromstring(response.content)
        status = tree.findtext("status")
        if status == "OK":
          return tree.findtext("salt")
        else:
          return None

  def file_password_salt(self, ident):
        data={
              'ident': ident,
           }
        data.setdefault("wst", self.token)
        response = requests.post(
           self.url + '/api/file_password_salt/',
           headers=self.common_headers(),
           data=data
        )
        tree = ElementTree.fromstring(response.content)
        status = tree.findtext("status")
        if status == "OK":
          return tree.findtext("salt")
        else:
          return None
  def get_file_link(self, ident, password):
        data={
              'ident': ident,
              'download_type': 'video_stream',
              'device_uuid': self.deviceId,
              'password': password,
           }
        data.setdefault("wst", self.token)
        response = requests.post(
           self.url + '/api/file_link/',
           headers=self.common_headers(),
           data=data
        )
        tree = ElementTree.fromstring(response.content)
        status = tree.findtext("status")
        if status == "OK":
          return tree.findtext("link")
        else:
          return None

  def login(self, username, password):
    """
    Log in to the webshare.cz API using the provided email and password.

    Returns:
    If the login is successful, returns the JSON response from the API.
    If the login fails, returns False.
    """

    salt = self.get_salt(username)
    if not salt:
      return None

    securePassword = self.hash_password(password, salt)
    response = requests.post(
        self.url + '/api/login/',
        headers=self.common_headers(),
        data={
          "username_or_email": username,
          "password": securePassword,
          'keep_logged_in': 1,
        },
    )
    tree = ElementTree.fromstring(response.content)
    status = tree.findtext("status")
    if status == "OK":
      return tree.findtext("token")
    else:
      return None
