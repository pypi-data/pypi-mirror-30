import aiohttp
import asyncio
import base64
import re

from urllib.parse import quote, unquote

class Xeoma():
    def __init__(self, base_url, login=None, password=None):
        """
            Create a Xeoma Object for interacting with Xeoma web server

            Arguments:
                base_url: the url of the Xeoma web server
                new_version: True if the Xeoma version > 17.5
                login: the Xeoma web server username
                password: the Xeoma web server password
        """

        self._base_url = base_url.rstrip('/')
        self._login = login
        self._password = password

    async def async_test_connection(self):
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(self._base_url, timeout=5)
                assert resp.status == 200
        except asyncio.TimeoutError:
            raise XeomaError('Connection to Xeoma server timed out')
        except AssertionError:
            raise XeomaError('Received bad response from Xeoma server')

    async def async_get_camera_image(self, image_name, username=None, password=None):
        """
            Grab a single image from the Xeoma web server

            Arguments:
                image_name: the name of the image to fetch (i.e. image01)
                username: the username to directly access this image
                password: the password to directly access this image
        """

        try:
            data = await self.async_fetch_image_data(
                image_name, username, password)
            if data is None:
                raise XeomaError('Unable to authenticate with Xeoma web '
                                 'server')
            return data
        except asyncio.TimeoutError:
            raise XeomaError('Connection timeout while fetching camera image.')
        except aiohttp.ClientError as e:
            raise XeomaError('Unable to fetch image: {}'.format(e))

    async def async_fetch_image_data(self, image_name, username, password):
        """
            Fetch image data from the Xeoma web server

            Arguments:
                image_name: the name of the image to fetch (i.e. image01)
                username: the username to directly access this image
                password: the password to directly access this image
        """
        params = {}
        cookies = self.get_session_cookie()
        if username is not None and password is not None:
            params['user'] = self.encode_user(username, password)
        else:
            params['user'] = ''
        async with aiohttp.ClientSession(cookies=cookies) as session:
            resp = await session.get(
                '{}/{}.jpg'.format(self._base_url, image_name),
                params=params
            )
            if resp.headers['Content-Type'] == 'image/jpeg':
                data = await resp.read()
            else:
                data = None
        return data

    async def async_get_image_names(self):
        """
            Parse web server camera view for camera image names
        """

        cookies = self.get_session_cookie()
        try:
            async with aiohttp.ClientSession(cookies=cookies) as session:
                resp = await session.get(
                    self._base_url
                )
                t = await resp.text()
                match = re.findall('(?:\w|\d)/(.*?).(?:mjpg|jpg)', t)
                if len(match) == 0:
                    raise XeomaError('Unable to find any camera image names')
                image_names = set(match)
                results = []
                for image_name in image_names:
                    match = re.search(
                        image_name + '\.(?:mjpg|jpg).*?user=(.*?)&', t
                    )
                    if match and len(match.group(1)) > 0:
                        d = base64.b64decode(unquote(match.group(1))) \
                            .decode('ASCII')
                        creds = d.split(':')
                        if len(creds) < 2:
                            raise XeomaError('Error parsing image credentials')
                        results.append((image_name, creds[0], creds[1]))
                    else:
                        results.append((image_name, None, None))
                return results
        except asyncio.TimeoutError as e:
            raise XeomaError("Unable to connect to Xeoma web server")

    def encode_user(self, username, password):
        credentials = '{}:{}'.format(username, password)
        b = base64.b64encode(bytes(credentials, encoding='ASCII'))
        return quote(b.decode('ASCII'))

    def get_session_cookie(self):
        """
            Create a session cookie object for use by aiohttp
        """

        if self._login is not None and self._password is not None:
            session_key = self.encode_user(self._login, self._password)
            return {'sessionkey': session_key}
        else:
            return None

class XeomaError(Exception):
    def __init__(self, message):
        self.message = message

