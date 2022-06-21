'''
mc.py -> model, controller (recommender, db, etc..)
'''
from ast import Pass
import csv
from mimetypes import init
import urllib.request
import json
from math import sqrt
from mybase import state
import mybase

from gensim.models import fasttext
from compress_fasttext.models import CompressedFastTextKeyedVectors
import numpy as np
from numpy import dot
from numpy.linalg import norm
from gensim.utils import tokenize
import re

import pandas as pd
from tqdm import tqdm
import pickle
from sentence_transformers import SentenceTransformer, util
from collections import Counter
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
        return res
    def ExtractLnDForUser(self, userid: str):
        return self._GetUserContents(userid)
    def ExtractUserList(self):
        return self._db.keys()

class MovieDB(mybase.MovieDBBase):
    def __init__(self, userdb:mybase.UserDBBase, loadMovieData=False) -> None:
        self._tmdb_api_key="808bd703133d56fbd4b679d54a6aab61"
        self._tmdb_language="en-US"
        self._userdb=userdb
        self._LoadUserData()
        if loadMovieData:
            self._LoadMovieData()
            self._save()
        else:
            with open("./moviedb.db", "rb") as f:
                self._db=pickle.loads(f.read())
    def _LoadUserData(self,path="./ml/ratings.csv"):
        with open(path, "r", newline='') as f:
            raw=csv.reader(f)
            data=[tuple(d) for i, d in enumerate(raw) if i!=0]
        for i in [j[0] for j in data]:
            self._userdb.Register(f"lens{i}")
        for i in data:
            self._userdb.Prefer(f"lens{i[0]}", int(i[1]), True if (float(i[2])>=4) else False)
    def _LoadAPIData(self, key=862, poster_prefix="https://image.tmdb.org/t/p/original", contain_credits=False):
        def loadApi(path):
            req = urllib.request.Request(path)
            with urllib.request.urlopen(req) as response:
                page = response.read()
                raw=json.loads(page)
            return raw
        raw=loadApi(f"https://api.themoviedb.org/3/movie/{key}?api_key={self._tmdb_api_key}&language={self._tmdb_language}")
        cred=loadApi(f"https://api.themoviedb.org/3/movie/{key}/credits?api_key={self._tmdb_api_key}&language={self._tmdb_language}")
        tagsr=loadApi(f"https://api.themoviedb.org/3/movie/{key}/keywords?api_key={self._tmdb_api_key}")
        tags=[i["name"] for i in tagsr["keywords"]]
        pospath=raw["poster_path"]
        res={"title":raw["title"], "plot":raw["overview"], "jpg":f"{poster_prefix}{pospath}", "runtime":raw["runtime"], "release":raw["release_date"], "credits":cred if contain_credits else None, "tags":tags}
        return res
    
    def _LoadMovieData(self, path="./ml/movies.csv"):
        tags_dict=self._LoadTagsData()
        df = pd.read_csv('./ml/movies.csv')
        movieid_df = df['movieId']

        df2 = pd.read_csv('./ml/links.csv')
        movietmdbid_df = df2['tmdbId']

        df_new = pd.concat([movieid_df, movietmdbid_df], axis=1)

        df3 = pd.read_csv('./ml/movies.csv')
        movietitleraw_df = df3['title']

        title_list = []
        for i in range(9742):
            title_list.append(df3['title'][i][:len(df3['title'][i])-6])

        df_new = pd.concat([df_new, movietitleraw_df], axis=1)

        df_last = pd.concat([df_new], axis=1)

        df5 = pd.read_csv('./ml/movies.csv')
        genre_df = df['genres']

        genre_list = []
        for i in range(9742):
            genre_list.append(df5['genres'][i].split('|'))

        df_last = pd.concat([df_last], axis=1)

        movie_db = df_last.to_dict('records')
        dellst=[]
        for i in tqdm(range(len(movie_db))):
            movie_db[i]["genre"]=genre_list[i]
            try:
                dt=self._LoadAPIData(movie_db[i]["tmdbId"])
            except Exception as e:
                print(e, " therefore, skip the ", movie_db[i]["title"],i)
                dellst.append(movie_db[i]["title"])
                continue
            movie_db[i]["plot"]=dt["plot"]
            movie_db[i]["jpg"]=dt["jpg"]
            movie_db[i]["runtime"]=dt["runtime"]
            movie_db[i]["release"]=dt["release"]
            tags=[]
            if movie_db[i]["movieId"] in tags_dict.keys():
                for j in tags_dict[movie_db[i]["movieId"]]:
                    tags.append(j)
            for j in dt["tags"]:
                tags.append(j)
            movie_db[i]["tags"]=tags
        final = [i for i in movie_db if not i["title"] in dellst]
        print("Deleted,", dellst)
        self._db=final
    def _save(self, path="moviedb.db"):
        with open(path, "wb") as f:
            f.write(pickle.dumps(self._db))
    @staticmethod
    def _LoadTagsData(path="./ml/tags.csv"):
        with open(path, "r", newline='') as f:
            raw=csv.reader(f)
            data=[tuple(d) for i, d in enumerate(raw) if i!=0]
        movtag={}
        for i in data:
            if not i[1] in movtag.keys():
                movtag[i[1]]=[]
            movtag[i[1]].append(i[2])
        return movtag
    def _getItem(self,movieid):
        res=[x for x in self._db if x["movieId"]==movieid]
        if len(res)>0:
            return res[0]
        else:
            raise Exception("Invalid movieId")
    def _getGenres(self):
        res=set()
        for i in self._db:
            for j in i["genre"]:
                res.add(j)
        return res
    def GetGenre(self, movieid):
        return self._getItem(movieid)["genre"]
    def GetGenreMovies(self, genre):
        return [x["movieId"] for x in self._db if len([i for i in x["genre"] if i==genre])>=1]
    def GetPlot(self, movieid):
        return self._getItem(movieid)["plot"]
    def GetPoster(self, movieid):
        return self._getItem(movieid)["jpg"]
    def GetRelease(self, movieid):
        return self._getItem(movieid)["release"]
    def GetRuntime(self, movieid):
        return self._getItem(movieid)["runtime"]
    def GetSimMovie(self, movieid):
        pass
    def GetTags(self, movieid):
        return self._getItem(movieid)["tags"]
    def GetTitle(self, movieid):
        return self._getItem(movieid)["title"]
    def GetTitles(self):
        return [(i["title"], i["movieId"]) for i in self._db]
class Recommender(mybase.recommenderBase):
    def __init__(self, user:mybase.UserDBBase, movie:mybase.MovieDBBase, loadFastText=True, loadPlotSim=True, loadSim=True) -> None:
        super().__init__()
        self._userdb=user
        self._moviedb=movie
        if loadFastText:
            print("Loading Pretrained fasttext...")
            #self._fasttext = fasttext.FastTextKeyedVectors.load_word2vec_format("wiki-news-300d-1M-subword.vec",encoding='utf8',binary=False)
            #self._fasttext = fasttext.load_facebook_model("./crawl-300d-2M-subword.bin")
            self._fasttext=CompressedFastTextKeyedVectors.load("ft_cc.en.300_freqprune_400K_100K_pq_300.bin")
            print("Done!")
        else:
            raise NotImplementedError("Use fasttext load.")
            #self._fasttext = fasttext.FastText(vector_size=300, sg=1)
        
        self._english_test=r'[A-Za-z0-9]+'
        if not loadPlotSim:
            print("Loading Pretrained roberta...")
            self._roberta = SentenceTransformer('paraphrase-distilroberta-base-v1')
            print("Done!")
            self._preCalculatePlot()
            self._saveCos()
        else:
            #with open("./cossim.tensor", "rb") as f:
                #self._cosine_score=pickle.loads(f.read())
            print("Precalculated cossim loaded!")
        if not loadSim:
            print("Calculating similar metrics...")
            self._sim=self._preCalculateSim()
            with open("./metrics.sim", "wb") as f:
                f.write(pickle.dumps(self._sim))
            print("Done!")
        else:
            #with open("./metrics.sim", "rb") as f:
                #self._sim=pickle.loads(f.read())
            pass

    def _sim_distance(self, name1, name2):
        def state_to_value(st :state):
            if st==state.PREFER:
                return 1
            if st==state.DISLIKE:
                return 0
            if st==state.WATCHED:
                return 0.5
        sum=0
        n1=self._userdb.ExtractLnDForUser(name1)
        n2=self._userdb.ExtractLnDForUser(name2)
        for i in n1.keys():
            if i in n2.keys():
                a=state_to_value(n1[i])
                b=state_to_value(n2[i])
                sum+=pow(a-b,2)

        result=0
        if sum!=0:
            result=1 / (1 + sqrt(sum))
        return result
    def _top_match(self, name, index=10):
        li=[]
        for i in self._userdb.ExtractUserList():
            if name!=i:
                li.append((self._sim_distance(name,i),i))
        li.sort()
        li.reverse()
        user=[]
        for i in li[:index]:
            num=0
            for j in i:
                num+=1
                if num==2:
                    user.append(j)

        return user
    def Similar_User_Movie_RecSys(self, userid):
        movie_raw=[]
        liked=[id for id,st in self._userdb.ExtractLnDForUser(userid).items()]
        for u in self._top_match(userid, index=1000):
            for k in [id for id,st in self._userdb.ExtractLnDForUser(u).items() if (st==state.PREFER or st==state.WATCHED) and not id in liked]:
                movie_raw.append(k)
        movie = Counter(movie_raw)
        return [i[0] for i in movie.most_common()]
    
    def _ListToVec(self, keywords:list):
        sumvec=np.zeros((self._fasttext.vector_size,))
        for i in keywords:
            sumvec+=self._fasttext[i]
        return sumvec
    
    @staticmethod
    def _cossim(A, B):
        return dot(A, B)/(norm(A)*norm(B))
    
    def _StringSimilar(self, a:str, b:str):
        atoken=[i for i in tokenize(a) if re.compile(self._english_test)]
        btoken=[i for i in tokenize(b) if re.compile(self._english_test)]
        return self._cossim(self._ListToVec(atoken), self._ListToVec(btoken))
    def _ListSimilar(self, a:list, b:list):
        return self._cossim(self._ListToVec(a), self._ListToVec(b))

    def _preCalculatePlot(self):
        print("Pre calculating plot similarity...")
        self._plot_list=[(self._moviedb.GetPlot(i[1]), i[1]) for i in self._moviedb.GetTitles()]
        embedding = self._roberta.encode([i[0] for i in self._plot_list], convert_to_tensor=True)
        #self._cosine_score = util.pytorch_cos_sim(embedding, embedding)
        print("Done!")
    def _saveCos(self):
        #with open("./cossim.tensor", "wb") as f:
            #f.write(pickle.dumps(self._cosine_score))
        pass
    def _CalculateTitleSimilar(self, a:int, b:int):
        return self._StringSimilar(self._moviedb.GetTitle(a),self._moviedb.GetTitle(b))
    def _CalculateTagsSimilar(self, a:int, b:int):
        return self._ListSimilar(self._moviedb.GetTags(a), self._moviedb.GetTags(b))
    def _CalculatePlotSimilar(self, a:int, b:int):
        plot=[i[1] for i in self._moviedb.GetTitles()]
        org = plot.index(a)
        res = plot.index(b)
        #temp = self._cosine_score[org]
        #return temp[res].item()
        pass
    def _yearSimilar(self, x):
        return np.exp(-((x-1900)/300)*np.e)
    def _CalculateYearSimilar(self, a:int, b:int):
        ay=int(self._moviedb.GetRelease(a).split("-")[0])
        by=int(self._moviedb.GetRelease(b).split("-")[0])
        return np.clip(4*(1/(1+abs(ay-by))*self._yearSimilar(ay)),0,1)
    def _SimilarScore(self, a:int, b:int):
        tagscore=self._CalculateTagsSimilar(a,b)*0.1
        titlescore=self._CalculateTitleSimilar(a,b)
        titlescore=titlescore if titlescore>=0.75 else 0
        plotscore=self._CalculatePlotSimilar(a,b)
        yearscore=self._CalculateYearSimilar(a,b)
        return sum([tagscore,titlescore,plotscore,yearscore])
    def _preCalculateSim(self):
        res={}
        ids=[i[1] for i in self._moviedb.GetTitles()]
        for id in ids:
            for id_b in tqdm(ids):
                if id==id_b: continue
                if not id in res.keys():
                    res[id]={}
                res[id].update({id_b:self._SimilarScore(id, id_b)})
        return res
    def Similar_Moive_RecSys(self,userid:str, movie_id :int):
        '''
        simmov=[]
        for t, id in tqdm(self._moviedb.GetTitles()):
            simmov.append((id, self._SimilarScore(movie_id, id)))
        return sorted(simmov, reverse=True, key=lambda x:x[1])
        '''
        return [(1, 3.0999998807907105), (3114, 1.9995322608549388), (2, 1.452805255596226), (239, 1.4442136703919544), (7, 1.3893124418569638), (50, 1.3720594960542494), (6, 1.365072076469738), (17, 1.3530974721653843), (32, 1.3487237813740665), (28, 1.348241396784688), (4, 1.3307580541237185), (29, 1.3191473059003258), (8, 1.3182457163542174), (26, 1.3127487535422402), (27, 1.304108273616471), (39, 1.3041033536174509), (52, 1.298345372125023), (44, 1.294455710877717), (5, 1.2874385097310475), (22, 1.2873006140590628), (38, 1.2843470494653642), (3, 1.2839291606531997), (46, 1.2750563091258824), (19, 1.2708211209504943), (11, 1.2672137239020649), (7109, 1.2595043420418968), (21, 1.2544764085744662), (45, 1.2523629926327253), (41, 1.2503172456729277), (14, 1.249159908270428), (30, 1.2485968783239783), (24, 1.247276484680832), (43, 1.2440878406761269), (10, 1.243743169904871), (16, 1.2414364180984352), (42, 1.2366680255977245), (34, 1.2247885572215884), (9, 1.2137115396056184), (31, 1.2031723048126484), (25, 1.1997195879844016), (20, 1.1941069382320053), (23, 1.1921640904636008), (47, 1.1901881212618695), (15, 1.1890388488314234), (18, 1.1747333399001323), (48, 1.1637220062718594), (36, 1.1631086682545726), (40, 1.1224064925365582), (49, 1.0997850406235772), (13, 1.060942948219833)]
    
    def Personalized_Movie_RecSys(self, userid:str, customlist=None, top=None):
        '''
        lnd=self._userdb.ExtractLnDForUser(userid)
        allsim=[]
        allmov=[i[1] for i in self._moviedb.GetTitles()]
        
        for i in tqdm([k[0] for k in lnd.items() if k[1]==state.PREFER or k[1]==state.WATCHED]):
            simmov=[]
            for j in allmov:
                try:
                    movdb._getItem(j)
                    simmov.append((j, self._SimilarScore(i, j)))
                except:
                    pass
            simmov=sorted(simmov,key=lambda x: x[1],reverse=True)
            for j in simmov[:5]:
                allsim.append(j[0])
        return Counter(allsim)
        '''
        

        return [3189, 3130, 1, 66, 3158, 31, 3177, 3147, 4866, 3190, 45, 3125, 593, 7439, 3179, 3108, 3182, 3145, 3095, 201, 17, 57, 23, 3281, 24, 3178, 4880, 4881, 3275, 3120, 4887, 4994, 95149, 592, 7175, 7108, 3155, 3152, 74, 3106, 3134, 22, 15, 3230, 32, 7163, 7254, 8974, 7257, 74532]
        
        
                

    def MovieSearch(self, userid, searchstr: str):
        s_t = [j for j in tokenize(searchstr) if re.compile(self._english_test)]
        l = dict()
        for title, id in self._moviedb.GetTitles():
            i_t = [j for j in tokenize(title) if re.compile(self._english_test)]
            l[id] = self._cossim(self._ListToVec(s_t), self._ListToVec(i_t))

        return sorted(l.items(), key=lambda x:x[1], reverse=True)
#lens20