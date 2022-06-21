from django.shortcuts import render, redirect
from .form import UserForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from mc import *
from view import *
udb=UserDB()
mdb=MovieDB(udb)
rec=Recommender(udb,mdb)
entr=EntrancePage(udb)
# Create your views here.

def index(request):
    return HttpResponse("HI",request)

def genrepage(request, genre_name):
    #Fantasy Action Adventure Crime Thriller Animation Comedy Romance Children Drama Horror Mystery Sci-Fi  War Musical Documentary IMAX Western Film-Noir
    gpage = GenrePage(entr,mdb,udb,rec)
    gpage.getrecgenre(entr.getnow(),genre_name)
    movies = gpage.showrecgenre()
    username = entr.getnow()

    context = {
        'movies': movies,
        'genre_name': genre_name,
        'username': username,
    }
    return render(request, 'catflex/genrepage.html', context)

def login(request):
    #print(udb.ExtractUserList())
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                if entr.LogIn(form.cleaned_data.get('id')):
                    entr.LogIn(form.cleaned_data.get('id'))
                    #(udb.ExtractUserList())
                    return redirect('/myview/genre/Action/')
                else:
                    form = UserForm()
            except:
                pass
    else:
        form = UserForm()

    return render(request, 'catflex/login.html',{'form':form})


def logout(request):
    return HttpResponse(
        '''
        <p><h1>logout</h1></p>
        <a href="/myview/login/">
        login
        </a>
                '''
                )


def signup(request):
    """
    회원가입
    """

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            entr.Register(form.cleaned_data.get('id'))
            #print(udb.ExtractUserList())
            login(request)
            return redirect('/myview/login/')
    else:
        form = UserForm()
    return render(request, 'catflex/signup.html', {'form': form})
'''
def Home (request):
    hmpage = homepage(entr, mdb, udb, rec)
    recmvlist=hmpage.SimilarRecommendmovies(entr.getnow())
    histroyrecommendlist=hmpage.HistoryRecommendation(entr.getnow())
    watchedlist=hmpage.HistoryList(entr.getnow())
    for items in recmvlist[:5]:
        recmvlist+=recmvlist[items]
        posterlist=list(posterlist.extend(hmpage.getmovieposter(items)))
        titlelist = list(titlelist.extend(hmpage.getmovietitle(items)))
        moviegenrelist = list(moviegenrelist.extend(hmpage.getmoviegenre(items)))
    for items in recommendmvsimiaritylist[:5]:
        simiaritylist=list(simiaritylist.extend(items))
    for items in histroyrecommendlist[:5]:
        hisrecmvlist=list(hisrecmvlist.extend(items))
        hisposterlist=list(hisposterlist.extend(hmpage.getmovieposter(items)))
        histitlelist = list(histitlelist.extend(hmpage.getmovietitle(items)))
        hismoviegenrelist = list(hismoviegenrelist.extend(hmpage.getmoviegenre(items)))
    for items in watchedlist[:5]:
        watchedrecmvlist=list(watchedrecmvlist.extend(items))
        watchedposterlist=list(watchedposterlist.extend(hmpage.getmovieposter(items)))
        watchedtitlelist = list(watchedtitlelist.extend(hmpage.getmovietitle(items)))
        watchedmoviegenrelist = list(watchedmoviegenrelist.extend(hmpage.getmoviegenre(items)))
    #리스트: for i in list[:꺼내고싶은 갯수 하면 갯수만큼 나옴]

    # 영화보여주고 아래에 유사도 표시를 한다고함

    context={'recmvlist':recmvlist,'posterlist':posterlist,'titlelist':titlelist,'moviegenrelist':moviegenrelist,
             'simiaritylist':simiaritylist,'hisrecmvlist':hisrecmvlist,'hisposterlist':hisposterlist,
             'histitlelist':histitlelist,'hismoviegenrelist':hismoviegenrelist,'watchedrecmvlist':watchedrecmvlist,
             'watchedposterlist':watchedposterlist,'watchedtitlelist':watchedtitlelist,
             'watchedmoviegenrelist':watchedmoviegenrelist}

    #로그인에서 로그인pk값으로 recommender 함수 돌아가게 해주는게 바람직함
    # SimSimliarRecommendation


    return render(request, "catfelx/홈.html", context)
'''
def MovieDetail(request, movieid):
    movie_id = movieid

    movie = {'title':mdb.GetTitle(movieid),'poster':mdb.GetPoster(movieid),'plot': mdb.GetPlot(movieid),'tag': mdb.GetTags(movie_id), 'release': mdb.GetRelease(movie_id), 'runtime': mdb.GetRuntime(movie_id) }
    context={
        'movie_id':movie_id, 'movie': movie, 'username': entr.getnow(),
    }

    return render(request, 'catflex/무비페이지.html', context)

def Like(request,movie_id):
    moviepage.thumbsup(entr.getnow(), movie_id)

def dislike(request,movie_id):
    moviepage.thumbsdown(entr.getnow(), movie_id)

def markwatched(request,movie_id):
    moviepage.WatchedMovie(entr.getnow(), movie_id)
