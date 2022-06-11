'''
mc.py -> model, controller (recommender, db, etc..)
'''
import csv
import urllib.request
import json

from mybase import state
import mybase

class UserDB(mybase.UserDBBase):
    def __init__(self) -> None:
        super().__init__()
        self._db={}
    def Register(self, userid :str):
        if self._GetUserContents(userid) is None:
            self._db.update({userid:{}})
    def Watched(self, userid:str, movieid:int):
        if userid in self._db:
            self._db[userid].update({movieid:state.WATCHED})
    def Prefer(self, userid:str, movieid:int, islike:bool):
        if userid in self._db:
            self._db[userid].update({movieid:state.PREFER if islike else state.DISLIKE})
    def _GetUserContents(self, userid:str) -> dict:
        if userid in self._db:
            return self._db[userid]
        else:
            return None
    def ExtarctWatched(self, userid: str):
        user=self._GetUserContents(userid)
        return user.keys()
    def ExtractLnDForMovie(self, movieid: int):
        res=[]
        for k, v in self._db.items():
            if movieid in self.ExtarctWatched(k):
                res.append({k:v[movieid]})
        return res#808bd703133d56fbd4b679d54a6aab61
    def ExtractLnDForUser(self, userid: str):
        return self._GetUserContents(userid)

class MovieDB(mybase.MovieDBBase):
    def __init__(self, userdb:mybase.UserDBBase) -> None:
        self._tmdb_api_key=""
        self._tmdb_language="en-US"
        self._userdb=userdb
        self._LoadUserData()
    def _LoadUserData(self,path="./ml/ratings.csv"):
        with open(path, "r", newline='') as f:
            raw=csv.reader(f)
            data=[tuple(d) for i, d in enumerate(raw) if i!=0]
        for i in [j[0] for j in data]:
            self._userdb.Register(f"lens{i}")
        for i in data:
            self._userdb.Prefer(f"lens{i[0]}", int(i[1]), True if (float(i[2])>=4) else False)
    def _LoadAPIData(self, key=862):
        req = urllib.request.Request(f"https://api.themoviedb.org/3/movie/{key}?api_key={self._tmdb_api_key}&language={self._tmdb_language}")
        with urllib.request.urlopen(req) as response:
            page = response.read()
            raw=json.loads(page)
        return raw
    def GetGenre(self, movieid):
        pass
    def GetGenreMovies(self, genre):
        pass
    def GetPlot(self, movieid):
        pass
    def GetPoster(self, movieid):
        pass
    def GetRelease(self, movieid):
        pass
    def GetRuntime(self, movieid):
        pass
    def GetSimMovie(self, movieid):
        pass
    def GetTags(self, movieid):
        pass
    def GetTitle(self, movieid):
        pass
udb=UserDB()
movdb=MovieDB(udb)
print(udb.ExtarctWatched("lens1"))