import io
import json

import requests

from datetime import datetime
from typing import Dict, List, Iterable

from requests import Response

BASE_URL = 'https://api.github.com'

MEDIA_TYPE = 'application/vnd.github.v3+json'

session = requests.session()


class File:

    def __init__(self, token: str = None) -> None:
        self._filename: str = None
        self._content: str = None
        self._url: str = None
        self._size: int = None
        self._mime: str = None
        self._language: str = None
        self._truncated: bool = None
        self._token = token
        self._headers: Dict[str,str] = None


    def __repr__(self) -> str:
        return '<File={0}>'.format(self._filename)


    @property
    def filename(self):
        return self._filename


    @filename.setter
    def filename(self, value):
        self._filename = value


    @property
    def url(self) -> str:
        return self._url


    @url.setter
    def url(self, value):
        self._url = value


    @property
    def content(self):
        if self._content is None:
            if self.url:
                r = session.get(self.url)
                self._content = r.text
            else:
                try:
                    with io.open(self.filename, encoding='utf-8') as f:
                        self._content = f.read()
                except IOError:
                    self._content = None

        return self._content


    @content.setter
    def content(self, value):
        self._content = value


    @property
    def size(self) -> int:
        return self._size


    @size.setter
    def size(self, value):
        self._size = value


    @property
    def mime(self) -> str:
        return self._mime


    @mime.setter
    def mime(self, value):
        self._mime = value


    @property
    def language(self) -> str:
        return self._language


    @language.setter
    def language(self, value):
        self._language = value

    @property
    def truncated(self) -> bool:
        return self._truncated


    @truncated.setter
    def truncated(self, value):
        self._truncated = value


class Gist:

    __slots__ = [
            '_url', '_id', '_description', '_public', '_truncated',
            '_comments', '_comments_url', '_html_url', '_git_remote',
            '_created_at', '_updated_at', '_files', '_owner', '_history'
    ]

    def __init__(self, gist_dict: Dict = {}) -> None:


        self._url: str = gist_dict.get('url')
        self._id: str = gist_dict.get('id')
        self._description: str = gist_dict.get('description')
        self._public: bool = gist_dict.get('public', True)
        self._truncated: bool = gist_dict.get('truncated', False)
        self._comments: int = gist_dict.get('comments', 0)
        self._comments_url: str = gist_dict.get('comments_url')
        self._html_url: str = gist_dict.get('html_url')
        self._git_remote: str = gist_dict.get('git_push_url')
        self._created_at: str = gist_dict.get('created_at')
        self._updated_at: str = gist_dict.get('updated_at')
        self._files: List[File] = []
        self._owner: str = None
        self._history:Dict[str,str]
        try:
            self._owner = gist_dict['owner']['login']
        except KeyError as e:
            self._owner = None

        try:
            self._history = {i['committed_at']: i['version'] for i in gist_dict['history']}
        except KeyError:
            self._history = None


        try:
            f = gist_dict['files']
            for k, v in f.items():
                file = File()
                file.filename = v['filename']
                file.language = v['language']
                file.mime = v['type']
                file.size = v['size']
                file.url = v['raw_url']
                file.content = v.get('content')
                self._files.append(file)

        except KeyError:
            self._files = []


    def __repr__(self):
        return '<Gist id={0}>'.format(self._id)


    @property
    def url(self) -> str:
        return self._url


    @property
    def id(self) -> str:
        return self._id


    @property
    def description(self) -> str:
        return self._description


    @description.setter
    def description(self, value) -> None:
        self._description = value


    @property
    def public(self) -> bool:
        return self._public


    @public.setter
    def public(self, value: bool) -> None:
        self._public = value


    @property
    def truncated(self) -> bool:
        return self._truncated


    @property
    def comments(self) -> int:
        return self._comments


    @property
    def comments_url(self) -> str:
        return self._comments_url


    @property
    def html_url(self) -> str:
        return self._html_url


    @property
    def git_remote(self) -> str:
        return self._git_remote


    @property
    def created_at(self) -> datetime:
        d = datetime.strptime(self._created_at, "%Y-%m-%dT%H:%M:%SZ")
        return d


    @property
    def updated_at(self) -> datetime:
        d = datetime.strptime(self._updated_at, "%Y-%m-%dT%H:%M:%SZ")
        return d


    @property
    def files_upload(self) -> Dict[str,Dict[str,str]]:
        return {
            i.filename: {'content': i.content} for i in self._files
        }


    @property
    def files(self) -> List[File]:
        return self._files


    @property
    def owner(self):
        return self._owner


    @property
    def history(self) -> Dict[str,str]:
        return self._history


    def add_file(self, file: File):
        self._files.append(file)


class Gisterator:

    def __init__(self, url: str, token: str, max_page: int = 5, per_page: int = 25) -> None:
        self._headers: Dict[str,str] = None
        self._token = token
        self._max_page = max_page
        self._per_page = per_page
        self._current_page: int = 0
        self._url = url
        self._index = 0
        self._req: Response = None
        self._req_len: int = None


    @property
    def token(self) -> str:
        return self._token


    @property
    def headers(self) -> Dict[str,str]:
        if self._headers is None:
            self._headers = {
                'Accept': MEDIA_TYPE,
                'Authorization': 'token {0}'.format(self.token)
            }

        return self._headers


    @property
    def url(self) -> str:
        return self._url


    @url.setter
    def url(self, value) -> None:
        self._url = value


    @property
    def max_page(self) -> int:
        return self._max_page


    @property
    def per_page(self) -> int:
        return self._per_page


    @property
    def params(self) -> Dict[str,int]:
        return {'page': self._current_page, 'per_page': self.per_page}


    @property
    def req(self) -> Response:
        return self._req


    @req.setter
    def req(self, value: Response) -> None:
        self._req = value


    def __iter__(self):
        return self


    def __next__(self) -> Gist:

        if self._index == 0:
            self.req = session.get(url=self.url, headers=self.headers, params=self.params)
            g = Gist(self.req.json()[self._index])
            self._index += 1
            return g

        elif self._index < len(self.req.json()):
            g = Gist(self.req.json()[self._index])
            self._index += 1
            return g

        elif self._current_page <= self.max_page:
            try:
                self._current_page += 1
                self._index = 0
                self.url = self.req.links['next']['url']
                self.req = session.get(url=self.url, headers=self.headers, params=self.params)
                g = Gist(self.req.json()[self._index])
                self._index += 1
                return g

            except KeyError:
                raise StopIteration

        else:
            raise StopIteration



class Gists:

    def __init__(self, user: str, token: str) -> None:
        self._headers: Dict[str,str] = None
        self._username: str = user
        self._token: str = token


    @property
    def username(self) -> str:
        return self._username


    @property
    def token(self) -> str:
        return self._token


    @property
    def headers(self) -> Dict[str,str]:
        if self._headers is None:
            self._headers = {
                'Accept': MEDIA_TYPE,
                'Authorization': 'token {0}'.format(self.token)
            }

        return self._headers


    def get_gists(self, username: str = None, max_page: int = 5, per_page: int = 25) -> Iterable[Gist]:
        username = self.username if username is None else username
        url = '{0}/users/{1}/gists'.format(BASE_URL, username)
        for i in Gisterator(url=url, token=self.token):
            yield i

    @staticmethod
    def get_public_gists(max_page: int = 5, per_page: int = 25) -> Iterable[Gist]:
        url = '{0}/gists/public'.format(BASE_URL)
        for i in Gisterator(url=url, token=None, max_page=max_page, per_page=per_page):
            yield i


    def get_starred_gists(self, max_page: int = 5, per_page: int = 25) -> Iterable[Gist]:
        url = '{0}/gists/starred'.format(BASE_URL)
        for i in Gisterator(url=url, token=self.token, max_page=max_page, per_page=per_page):
            yield i


    def get_gist(self, id: str, revision: str = None) -> Gist:
        url = '{0}/gists/{1}/{2}'.format(BASE_URL, id, revision)
        r = session.get(url=url, headers=self.headers)
        assert r.status_code == 200
        return Gist(r.json())


    def create_gist(self, gist: Gist) -> Gist:
        url = '{0}/gists'.format(BASE_URL)
        obj = {
            'description': gist.description,
            'public': gist.public,
            'files': gist.files_upload
        }
        data = json.dumps(obj)
        r = session.post(url=url, data=data, headers=self.headers) # type: ignore
        print(r.json())
        return Gist(r.json())