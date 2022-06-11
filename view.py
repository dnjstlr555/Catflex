#view.py -> view (main page, genre page....)
from mybase import state
import mybase

class MainPage(mybase.MainpageBase):
    def __init__(self, Search :mybase.searchcomponentBase, UserDB :mybase.UserDBBase, Recommender :mybase.recommenderBase, MovieDrawFrame :mybase.MovieDrawFrameBase) -> None:
        super().__init__()
        self._search=Search
        self._userdb=UserDB
        self._recommender=Recommender
        self._movieframe=MovieDrawFrame
    def HistoryRecommendation(self, User_id: str):
        self.WatchedList=self._userdb.ExtarctWatched(User_id)