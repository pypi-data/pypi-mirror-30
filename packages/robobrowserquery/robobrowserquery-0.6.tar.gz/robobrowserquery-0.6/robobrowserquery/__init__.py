#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals, print_function

try:
    from http.cookies import SimpleCookie
except ImportError:
    from Cookie import SimpleCookie

import pyquery

from robobrowser import RoboBrowser


class RoboBrowserQuery(RoboBrowser):
    simple_cookie = None

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('parser', 'lxml')
        super(RoboBrowserQuery, self).__init__(*args, **kwargs)

    @property
    def query(self):
        if not hasattr(self.state, 'pyquery'):
            self.state.pyquery = pyquery.PyQuery(
                self.state.response.content)

        return self.state.pyquery

    def set_cookie_at_next_request(self, cookie_text):
        """
        DEPRECATED
        set cookie text.
        recommend: from django.utils.encoding import smart_str
                   set_cookie_at_next_request(smart_str(cookie_text))
        """
        self.simple_cookie = SimpleCookie()
        self.simple_cookie.load(cookie_text)

    def set_cookie(self, cookie_dict):
        """
        DEPRECATED
        :param cookie_dict:
        """
        self.session.cookies.set(**cookie_dict)

    def cookie_as_dict(self):
        """
        DEPRECATED
        """
        if not self.simple_cookie:
            return None
        return {k: v.value for k, v in self.simple_cookie.items()}

    def get_cookies(self):
        """
        :return: http.cookiejar.Cookie list
        For serialize, example django cache
        """
        return list(iter(self.session.cookies))

    def save_cookies_to_file(self, file_path):
        """
        Save pickled cookies to file
        """
        import pickle
        with open(file_path, 'wb') as fp:
            pickle.dump(self.get_cookies(), fp)

    def set_cookies(self, cookies):
        """
        From serialized, example django cache
        """
        for cookie in cookies:
            self.session.cookies.set_cookie(cookie)

    def load_cookies_from_file(self, file_path):
        """
        Load unpickled cookies to file
        """
        import pickle
        with open(file_path, 'rb') as fp:
            cookies = pickle.load(fp)
            self.set_cookies(cookies)

    def get_cookies_as_dicts(self):
        """
        Get cookies for debug
        """
        return [c.__dict__ for c in iter(self.session.cookies)]

    def get_cookie_values_as_dicts(self):
        """
        Get cookies for eazy debug.
        """
        return [
            {
                "domain": c.domain,
                "name": c.name,
                "value": c.value,
            } for c in iter(self.session.cookies)
        ]

    def open(self, *args, **kwargs):
        if self.simple_cookie:
            kwargs.update({'cookies': self.cookie_as_dict()})
        super(RoboBrowserQuery, self).open(*args, **kwargs)

    def preview(self):
        """
        Preview latest response with GUI web browser
        """
        import tempfile
        import subprocess

        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(self.state.response.content)
        f.close()

        # for mac.
        subprocess.Popen(['open', f.name])
        # Auto delete required?

    def get_decoded_content(self):
        """
        Get html content as str
        """
        return self.response.content.decode(errors="ignore")

    def take_snapshot(self, file_path):
        """
        take html snapshot to file
        """
        with open(file_path, "wb") as fp:
            fp.write(self.state.response.content)
