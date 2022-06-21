from abc import ABCMeta, abstractmethod
from enum import Enum

class state(Enum):
    PREFER = 0
    DISLIKE = 1
    WATCHED = 2


class UserDBBase(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self) -> None:
        pass
    @abstractmethod
    def Register(self, userid :str):
        '''
        Register new user to databse
        '''
    @abstractmethod
    def Watched(self, userid:str, movieid:int):
        '''
        Mark movie as watched
        '''
    @abstractmethod
    def Prefer(self, userid:str, movieid:int, islike:bool):
        pass
    @abstractmethod
    def ExtractLnDForMovie(self, movieid :int):
        pass
    @abstractmethod
    def ExtractLnDForUser(self, userid :str):
        pass
    @abstractmethod
    def ExtarctWatched(self, userid :str):
        pass
    @abstractmethod
    def ExtractUserList(self):
        pass

class recommenderBase(metaclass=ABCMeta):
    @abstractmethod
    def Similar_Moive_RecSys(self,userid:str, movie_id :int):
        pass

    @abstractmethod
    def Personalized_Movie_RecSys(self, userid:str, customlist=None, top=None):
        pass

    @abstractmethod
    def Similar_User_Movie_RecSys(self, user_id):
        pass

    @abstractmethod
    def MovieSearch(self,userid, searchstr :str):
        pass

class MovieDBBase(metaclass=ABCMeta):
    @abstractmethod
    def GetTitle(self,movieid):
        pass

    @abstractmethod
    def GetPoster(self,movieid):
        pass

    @abstractmethod
    def GetPlot(self,movieid):
        pass

    @abstractmethod
    def GetGenre(self,movieid):
        pass

    @abstractmethod
    def GetRuntime(self,movieid):
        pass

    @abstractmethod
    def GetSimMovie(self,movieid):
        pass 

    @abstractmethod
    def GetTags(self,movieid):
        pass 

    @abstractmethod
    def GetRelease(self,movieid):
        pass

    @abstractmethod
    def GetGenreMovies(self,genre):
        pass
    @abstractmethod
    def GetTitles(self):
        pass


# ---- View ----
# ---- View ----
#####수정
class EntrancePageBase(metaclass=ABCMeta):
    @abstractmethod
    def LogIn(self,userid):
        pass

    @abstractmethod
    def Register(self,userid):
        pass

    @abstractmethod
    def getnow(self):
        pass

class GenrepageBase(metaclass= ABCMeta):
    @abstractmethod
    def getrecgenre(self, userid, genre):
        # Call moviedrawframe::GenreShow  return : list( movie poster + title )
        pass

    @abstractmethod
    def showrecgenre(self):
        # Print list( call getRecGenre )
        pass


class MainpageBase(metaclass=ABCMeta):
    @abstractmethod
    def SimliarRecommendation(self, User_id:str):
        #self.LnD_DB=UserDB.ExtractLndForUser(User _id)
        #->get movie id, bool islike
        #self.mv_prefer=self.Lnd_DB.bool_islike
        #self.mv_id=self.Lnd_DB.movie id
        #self.plot=MovieDB.GetPlot(Self.mv_id)
        #-> Need determination // mechanisms for how data is contained
        #return self.Similar_Recommended_list = Recommender.Personalized_Movie_RecSys(self.plot, mv_prefer)
        pass

    @abstractmethod
    def HistoryRecommendation(self, User_id:str):
        #self.WatchedList=UserDB.Extractwatched(User_id)
        #return self.History_Recommended_list = Recommender.Similar_User_Movie_RecSys(self.WatchedList)
        pass


    @abstractmethod
    def HistoryList(self, User_id:str):
        #return self.WatchedList=UserDB.Extractwatched(User_id)
        pass

    def WriteSearchWord(self,Input_word):
        #self.Searchword=input_word
        #return self.Searchword
        # Plus fuction Button
        pass

    @abstractmethod
    def PageShow(self):
        #return self.GetMain=MovieDrawFrame.MainPageShow()
        pass

class PreferencePageBase(metaclass=ABCMeta):
    @abstractmethod
    def GetMovie(self):
        pass
    @abstractmethod
    def PageShow(self):
        pass
    @abstractmethod
    def PreferWatchMovie(self, userid:str, movieid :int):
        pass
    @abstractmethod
    def Prefer_Thumbs(self, userid :str, movieid :int, islike :bool):
        #islike는 유저가 해당 영화에대해 like를 표시했을때 true, 아니면 false
        pass

class searchcomponentBase(metaclass=ABCMeta):
    @abstractmethod
    def input_SearchWord(self, words):
        pass

    @abstractmethod
    def Find_movie(self, userid:str, searchstr :str):
        pass