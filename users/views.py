from django.shortcuts import render, redirect
from .models import UserModel, ReviewModel
from django.contrib.auth import get_user_model
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db import connection
from books.book_views import make_keyword


# Create your views here.
def sign_up_view(request):
    if request.method == 'GET':
        user = request.user.is_authenticated
        if user:
            return redirect('/')
        else:
            return render(request, 'user/signup.html')
    elif request.method == 'POST':
        email = request.POST.get('email', '')
        first_name = request.POST.get('name', '')
        username = request.POST.get('id', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if password != password2:
            return render(request, 'user/signup.html', {'error': '패스워드를 확인 해 주세요!'})
        else:
            if username == '' or password == '' or first_name == '' or email == '':
                return render(request, 'user/signup.html', {'error': '입력되지 않은 정보가 있습니다!'})

            exist_user = get_user_model().objects.filter(username=username)
            if exist_user:
                return render(request, 'user/signup.html', {'error':'사용자가 존재합니다.'})
            else:
                UserModel.objects.create_user(email=email, username=username, password=password, first_name=first_name)
                return redirect('/sign-in')


def sign_in_view(request):
    if request.method == 'POST':
        username = request.POST.get('id', '')
        password = request.POST.get('password', '')
        me = auth.authenticate(request, username=username, password=password)
        if me is not None:
            auth.login(request, me)
            return redirect('/')
        else:
            return render(request,'user/signin.html',{'error':'ID 혹은 패스워드를 확인 해 주세요'})
    elif request.method == 'GET':
        return render(request, 'user/signin.html')


@login_required
def logout(request):
    auth.logout(request)
    return redirect("/")


def home(request):
    user = request.user.is_authenticated
    if user:
        return redirect('/main')
    else:
        return redirect('/sign-in')


@login_required
def mypage(request):
    if request.method == 'GET':
        user = request.user
        
        favorite = query_favorite(user)

        review_data = ReviewModel.objects.filter(user=user)
        favorite_data = user.favorite.all()

        reviews = review_data[::-1][:3]

        fav_cnt = favorite_data.count()
        review_cnt = review_data.count()
        count = {'fav': fav_cnt, 'rev': review_cnt}

        keyword = make_keyword(favorite_data, 'story', 10)

        for review in reviews:
            review.star = review.star * 20

    return render(request, 'user/mypage.html', {'reviews': reviews, 'favorite': favorite, 'count': count, 'keyword': keyword})


@login_required
def my_favorites(request):
    if request.method == 'GET':
        user = request.user
        user_id = user.id
        cursor = connection.cursor()
        query = "SELECT * FROM users_favorite WHERE usermodel_id=%s" % user_id
        cursor.execute(query)
        stocks = cursor.fetchall()

        stocks.sort(key=lambda x: -x[0])
        favorite = []
        for i in range(len(stocks)):
            favorite.append(user.favorite.get(id=stocks[i][2]))
        return render(request, 'user/favorites.html', {'favorite': favorite})


@login_required
def my_reviews(request):
    if request.method == 'GET':
        user = request.user
        reviews = ReviewModel.objects.filter(user=user)[::-1]
        for review in reviews:
            review.star = review.star * 20
        return render(request, 'user/reviews.html', {'reviews': reviews})


def query_favorite(user):
    cursor = connection.cursor()
    query = "SELECT * FROM users_favorite WHERE usermodel_id=%s" % user.id
    cursor.execute(query)
    stocks = cursor.fetchall()

    stocks_length = len(stocks)
    if stocks_length > 5:
        stocks_length = 5

    stocks.sort(key=lambda x: -x[0])

    favorite = []
    for i in range(stocks_length):
        fav = user.favorite.get(id=stocks[i][2])
        fav.star = fav.star * 20
        favorite.append(fav)

    return favorite
