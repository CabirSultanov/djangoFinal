from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Article, Category, LikeDislike, Bookmark, Rating




def feed_all(request):

    articles = Article.objects.filter(is_published=True).order_by('-created_at')

    for article in articles:
        likes = article.votes.filter(value=1).count()
        dislikes = article.votes.filter(value=-1).count()
        total = likes + dislikes
        article.rating_percent = round((likes / total * 100), 1) if total > 0 else 0

    return render(request, 'articles/index.html', {'articles': articles})



def feed_popular(request):

    articles = Article.objects.filter(is_published=True).order_by('-rating', '-created_at')


    for article in articles:
        likes = article.votes.filter(value=1).count()
        dislikes = article.votes.filter(value=-1).count()
        total = likes + dislikes
        article.rating_percent = round((likes / total * 100), 1) if total > 0 else 0

    # сортируем именно по вычисленному проценту (если нужно)
    articles = sorted(articles, key=lambda a: a.rating_percent, reverse=True)

    return render(request, 'articles/feed_popular.html', {'articles': articles})



def feed_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = category.articles.filter(is_published=True).order_by('-created_at')
    for article in articles:
        likes = article.votes.filter(value=1).count()
        dislikes = article.votes.filter(value=-1).count()
        total = likes + dislikes
        article.rating_percent = round((likes / total * 100), 1) if total > 0 else 0
    return render(request, 'articles/feed_category.html', {'category': category, 'articles': articles})



def feed_authors(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    authors = (
        User.objects
        .filter(articles__is_published=True)
        .annotate(total_articles=Count('articles'))
        .order_by('-total_articles', 'username')
    )
    return render(request, 'articles/feed_authors.html', {'authors': authors})


@login_required
def feed_favorites(request):
    articles = Article.objects.filter(bookmarks__user=request.user).order_by('-created_at')
    return render(request, 'articles/feed_favorites.html', {'articles': articles})


@login_required
def feed_my_articles(request):

    articles = Article.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'articles/feed_my.html', {'articles': articles})




def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    can_view = article.is_published or request.user.is_authenticated and (
        request.user == article.author or request.user.can_manage_articles()
    )
    if not can_view:
        return redirect('feed_all')

    likes = article.votes.filter(value=1).count()
    dislikes = article.votes.filter(value=-1).count()
    total = likes + dislikes
    rating_percent = round((likes / total) * 100, 1) if total > 0 else 0

    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, article=article).exists()

    return render(request, 'articles/article_detail.html', {
        'a': article,
        'likes': likes,
        'dislikes': dislikes,
        'is_bookmarked': is_bookmarked,
        'rating_percent': rating_percent,
        'is_approved': article.is_published
    })




@login_required
def article_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        category = Category.objects.get(pk=category_id)
        article = Article.objects.create(
            author=request.user,
            title=title,
            content=content,
            image=image,
            category=category,
            is_published=request.user.can_manage_articles()
        )
        messages.success(request, "Article created successfully!" if article.is_published else "Article sent for moderation.")
        return redirect('article_detail', pk=article.pk)

    categories = Category.objects.all()
    return render(request, 'articles/article_form.html', {'categories': categories})


@login_required
def article_update(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if not (request.user.can_manage_articles() or request.user == article.author):
        return redirect('feed_all')

    if request.method == 'POST':
        article.title = request.POST.get('title')
        article.content = request.POST.get('content')
        category_id = request.POST.get('category')
        article.category = Category.objects.get(pk=category_id)
        image = request.FILES.get('image')
        if image:
            article.image = image

        if not request.user.can_manage_articles():
            article.is_published = False

        article.save()
        messages.info(request, "Article updated and sent for approval.")
        return redirect('article_detail', pk=article.pk)

    categories = Category.objects.all()
    return render(request, 'articles/article_form.html', {'a': article, 'categories': categories})


@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if not (request.user.can_manage_articles() or request.user == article.author):
        return redirect('feed_all')

    if request.method == 'POST':
        article.delete()
        messages.success(request, "Article deleted.")
        return redirect('feed_all')

    return render(request, 'articles/article_confirm_delete.html', {'a': article})



@login_required
@require_POST
def article_like(request, pk):
    article = get_object_or_404(Article, pk=pk)
    existing_vote = LikeDislike.objects.filter(user=request.user, article=article).first()

    if existing_vote and existing_vote.value == 1:
        existing_vote.delete()
    else:
        LikeDislike.objects.update_or_create(user=request.user, article=article, defaults={'value': 1})

    likes = article.votes.filter(value=1).count()
    dislikes = article.votes.filter(value=-1).count()
    total = likes + dislikes
    rating_percent = round((likes / total) * 100, 1) if total > 0 else 0

    return JsonResponse({'likes': likes, 'dislikes': dislikes, 'rating_percent': rating_percent})


@login_required
@require_POST
def article_dislike(request, pk):
    article = get_object_or_404(Article, pk=pk)
    existing_vote = LikeDislike.objects.filter(user=request.user, article=article).first()

    if existing_vote and existing_vote.value == -1:
        existing_vote.delete()
    else:
        LikeDislike.objects.update_or_create(user=request.user, article=article, defaults={'value': -1})

    likes = article.votes.filter(value=1).count()
    dislikes = article.votes.filter(value=-1).count()
    total = likes + dislikes
    rating_percent = round((likes / total) * 100, 1) if total > 0 else 0

    return JsonResponse({'likes': likes, 'dislikes': dislikes, 'rating_percent': rating_percent})


@login_required
@require_POST
def article_bookmark_toggle(request, pk):
    article = get_object_or_404(Article, pk=pk)
    bm, created = Bookmark.objects.get_or_create(user=request.user, article=article)

    if not created:
        bm.delete()
        bookmarked = False
    else:
        bookmarked = True

    if request.META.get('HTTP_REFERER', '').endswith('/favorites/'):
        return redirect('feed_favorites')

    return JsonResponse({'bookmarked': bookmarked})


@login_required
@require_POST
def article_rate(request, pk, value):
    article = get_object_or_404(Article, pk=pk)
    value = max(1, min(5, int(value)))
    Rating.objects.update_or_create(user=request.user, article=article, defaults={'value': value})
    avg = article.ratings.aggregate(v=Avg('value'))['v'] or 0
    article.rating = round(float(avg), 2)
    article.save(update_fields=['rating'])
    return JsonResponse({'rating': article.rating})



@login_required
def moderation_queue(request):
    if not request.user.can_manage_articles():
        return redirect('feed_all')
    articles = Article.objects.filter(is_published=False).order_by('created_at')
    return render(request, 'articles/mod_queue.html', {'articles': articles})


@login_required
def moderation_approve(request, pk):
    if not request.user.can_manage_articles():
        return redirect('feed_all')
    article = get_object_or_404(Article, pk=pk)
    article.is_published = True
    article.save(update_fields=['is_published'])
    messages.success(request, "Article published.")
    return redirect('moderation_queue')


@login_required
def article_confirm(request, pk):
    article = get_object_or_404(Article, pk=pk, author=request.user)
    article.is_published = False
    article.save(update_fields=['is_published'])
    return JsonResponse({'status': 'waiting'})
