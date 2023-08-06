#!/usr/bin/env python

import requests


class GembaRestClient:

    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.headers = { "X-Auth-Token": self.token }


    def response(self, res):
        if res.status_code == 404:
            return None
        if res.status_code != 200:
            raise Exception(res.json())
        return res.json()

    def get(self, url, payload = {}):
        return self.response(requests.get(self.url + url, headers=self.headers, params=payload))

    def post(self, url, payload):
        return self.response(requests.post(self.url + url, headers=self.headers, json=payload))

    def post_form(self, url, files):
        return self.response(requests.post(self.url + url, headers=self.headers, files=files))

    def put(self, url, payload):
        return self.response(requests.put(self.url + url, headers=self.headers, params=payload))

    def delete(self, url):
        return self.response(requests.delete(self.url + url, headers=self.headers))



class GembaFaceClient:

    def __init__(self, url, token, pid = None, fid = None):
        self.rest = GembaRestClient(url, token)
        self.person_id = pid
        self.face_id = fid

    def pid(self, pid):
        if pid is not None:
            return pid
        else:
            return self.person_id

    def fid(self, fid):
        if fid is not None:
            return fid
        else:
            return self.face_id


    def get(self, pid = None, fid = None, offset = 0, limit = 10):
        payload = {"offset": offset, "limit": limit}

        if self.pid(pid) is None:
            # All faces of all persons
            return self.rest.get("/faces", payload)
        else:
            if self.fid(fid) is None:
                # All faces of one person
                return self.rest.get("/persons/%s/faces" % self.pid(pid), payload)
            else:
                # One face of one person
                return self.rest.get("/persons/%s/faces/%s" % (self.pid(pid), self.fid(fid)))


    def add(self, face, pid = None, fid = None):
        if (self.pid(pid) is None) or (self.fid(fid) is None):
            return None
        payload = {"id" : ('', self.fid(fid)), "face": face}
        return self.rest.post_form("/persons/%s/faces" % self.pid(pid), payload)


    def delete(self, pid = None, fid = None):
        if (self.pid(pid) is None) or (self.fid(fid) is None):
            return None
        return self.rest.delete("/persons/%s/faces/%s" % (self.pid(pid), self.fid(fid)))



class GembaPersonClient:

    def __init__(self, url, token, pid = None):
        self.rest = GembaRestClient(url, token)
        self.faces = GembaFaceClient(url, token, pid=pid)
        self.url = url
        self.token = token
        self.person_id = pid


    def pid(self, pid):
        if pid is not None:
            return pid
        else:
            return self.person_id
    

    def get(self, pid = None, offset = 0, limit = 10):
        if self.pid(pid) is not None:
            return self.rest.get("/persons/%s" % self.pid(pid))
        else:
            payload = { "offset": offset, "limit": limit }
            return self.rest.get('/persons', payload)


    def add(self, pid = None, tags = []):
        payload = { "id": self.pid(pid), "tags": tags }
        return self.rest.post("/persons", payload)


    def delete(self, pid = None):
        return self.rest.delete("/persons/%s" % self.pid(pid))


    def face(self, fid, pid = None):
        return GembaFaceClient(self.url, self.token, pid=self.pid(pid), fid=fid)



class GembaClient:

    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.rest = GembaRestClient(url, token)
        self.persons = GembaPersonClient(url, token)
        self.faces = GembaFaceClient(url, token)

    def person(self, pid):
        return GembaPersonClient(self.url, self.token, pid)

    def find(self, face):
        return self.rest.post_form("/find", { "face": face })

    def find_all(self, face):
        return self.rest.post_form("/find/all", { "face": face })

    def compare(self, face1, face2):
        return self.rest.post_form("/compare", { "face1": face1, "face2": face2 })

    def compare_self(self, face):
        return self.rest.post_form("/compare/self", { "face": face })

