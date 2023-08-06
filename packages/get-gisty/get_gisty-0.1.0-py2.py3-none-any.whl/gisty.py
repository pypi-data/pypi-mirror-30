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
    def __init__(self, filename:str) -> None:
        self._filename: str = filename
        self._contents: str = None

        with io.open(filename, encoding='utf-8') as f:
            self._contents = f.read()


    @property
    def filename(self):
        return self._filename


    @property
    def contents(self):
        return self._contents



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
    def files(self) -> Dict[str,Dict[str,str]]:
        return {
            i.filename: {'content': i.contents} for i in self._files
        }


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


    def get_public_gists(self, max_page: int = 5, per_page: int = 25) -> Iterable[Gist]:
        url = '{0}/gists/public'.format(BASE_URL)
        for i in Gisterator(url=url, token=self.token, max_page=max_page, per_page=per_page):
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


    def create_gist(self, gist: Gist):
        url = '{0}/gists'.format(BASE_URL)
        obj = {
            'description': gist.description,
            'public': gist.public,
            'files': gist.files
        }
        data = json.dumps(obj)
        r = session.post(url=url, data=data, headers=self.headers) # type: ignore
        return Gist(r.json())