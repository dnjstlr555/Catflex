#view.py -> view (main page, genre page....)
from mybase import state
import mybase


class homepage:
    def __init__(self,Entrance: mybase.EntrancePageBase, MovieDB: mybase.MovieDBBase, UserDB :mybase.UserDBBase, Recommender :mybase.recommenderBase) -> None:
        super().__init__()
        self._moviedb=MovieDB
        self._userdb=UserDB
        self._recommender=Recommender
        self._entr = Entrance
        self._recmvlist = []
        self._posterlist = []
        self._titlelist = []
        self._moviegenrelist = []
        self._simiaritylist = []
        self._hisrecmvlist = []
        self._hisposterlist = []
        self._histitlelist = []
        self._hismoviegenrelist = []
        self._watchedrecmvlist = []
        self._watchedposterlist = []
        self._watchedtitlelist = []
        self._watchedmoviegenrelist = []
        self._Main_Recommended_list=[]
        self._Main_similarity_list=[]
        self._Main_Recommended_movieidlist=[]

    def SimilarRecommendmovies(self, User_id:str):
        self._Main_Recommended_list=self._recommender.Similar_User_Movie_RecSys(User_id)
        return self._Main_Recommended_list
    # -> list[i][0] 영화 id list[i][1] 유사도 // [[영화 id, 유사도],[영화 id, 유사도],[영화 id, 유사도]]

    def HistoryRecommendation(self, User_id: str):
        self._History_Recommended_list=self._recommender.Personalized_Movie_RecSys(User_id)
        return self._History_Recommended_list

    def HistoryList(self, User_id: str):
        self._WatchedList = self._userdb.ExtarctWatched(User_id)
        return self._WatchedList

    def getmovieposter (self, movie_id: int):
        self._poster = self._moviedb.GetPoster(movie_id)
        return self._poster

    def getmovietitle (self, movie_id: int):
        self._title = self._moviedb.GetTitle(movie_id)
        return self._title

    def getmoviegenre (self, movie_id: int):
        self._genre = self._moviedb.GetGenre(movie_id)
        return self._genre

class moviepage:
    def __init__(self,Entrance: mybase.EntrancePageBase, MovieDB: mybase.MovieDBBase, UserDB :mybase.UserDBBase, Recommender :mybase.recommenderBase) -> None:
        super().__init__()
        self._moviedb=MovieDB
        self._userdb=UserDB
        self._recommender=Recommender
        self._entr = Entrance


    def getmovietitle (self, movie_id: int):
        self._title = self._moviedb.GetTitle(movie_id)
        return self._title

    def getmovieposter (self, movie_id: int):
        self._poster = self._moviedb.GetPoster(movie_id)
        return self._poster

    def getmoviegenre (self, movie_id: int):
        self._genre = self._moviedb.GetGenre(movie_id)
        return self._genre

    def getmovieplot (self, movie_id: int):
        self._plot = self._moviedb.GetPlot(movie_id)
        return self._plot

    def getmovierelease (self, movie_id: int):
        self._release = self._moviedb.GetRelease(movie_id)
        return self._release

    def getmovieruntime(self, movie_id: int):
        self._runtime = self._moviedb.GetRuntime(movie_id)
        return self._runtime

    def getlnds(self,movie_id:int):
        self._lnds = self._userdb.ExtractLnDForMovie(movie_id)
        return self._lnds

    def getsimmovie (self, User_id:str, movie_id: int):
        self._simmovie = self._recommender.Similar_Moive_RecSys(User_id,movie_id)
        return self._simmovie

    def thumbsup(self, User_id:str, movie_id:int):
        self._userdb.Prefer(User_id,movie_id,True)

    def thumbsdown(self, User_id:str,movie_id:int):
        self._userdb.Prefer(User_id,movie_id,False)

    def WatchedMovie(self, User_id:str, movie_id:int):
        self._userdb.Watched(User_id,movie_id)


class GenrePage(mybase.GenrepageBase):
    def __init__(self, Entrance: mybase.EntrancePageBase,MovieDB: mybase.MovieDBBase, UserDB :mybase.UserDBBase, Recommender :mybase.recommenderBase) -> None:
        super().__init__()
        self._moviedb=MovieDB
        self._userdb=UserDB
        self._recommender=Recommender
        self._entr=Entrance
        self._movielist = []

    def getrecgenre(self, userid, genre):
        self._movielist = self._moviedb.GetGenreMovies(genre)
        self._movielist = self._recommender.Personalized_Movie_RecSys(self._entr.getnow(),self._movielist)
        #print(self._movielist)
    def showrecgenre(self):
        movies= []
        for i in self._movielist:
            movies += [{'title': self._moviedb.GetTitle(i), 'poster': self._moviedb.GetPoster(i), 'url': 'http://localhost:8000/myview/'+str(i)}]
        #print(movies)
        return movies


class EntrancePage(mybase.EntrancePageBase):
    def __init__(self,  UserDB :mybase.UserDBBase, ) -> None:
        super().__init__()
        self._userdb=UserDB
        self._now = ''

    def LogIn(self,userid):
        if userid in self._userdb.ExtractUserList():
            self._now = userid
            return True
        else:
            return False

    def Register(self,userid):
        self._userdb.Register(userid)

    def getnow(self):
        return self._now
