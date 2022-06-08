from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from books.models import BookModel
from django.core.paginator import Paginator
from users.models import ReviewModel
from django.db.models import Count, Avg




def genre_view(request, name, page):
    books_list = BookModel.objects.filter(genre=name)
    paginator = Paginator(books_list, 10)
    pages = paginator.get_page(page)
    return render(request, 'main_genre/genre.html', {'pages': pages})


def main_view(request):
    return render(request, 'main_genre/main.html')


@login_required
def create_review(request, book_id):
    if request.method == 'POST':
        user = request.user
        current_book = BookModel.objects.get(id=book_id)
        star = int(request.POST.get('rating', 0))
        review = request.POST.get('review', '')

        ReviewModel.objects.create(user=user, book=current_book, star=star, desc=review)
        return redirect('book_info', book_id)


@login_required
def delete_review(request, book_id, review_id):
    review = ReviewModel.objects.get(id=review_id)
    review.delete()
    return redirect('book_info', book_id)


# @login_required
# def modify_review(request, book_id, review_id):
#     if request.method == "POST":
#         review = ReviewModel.objects.get(id=review_id)
