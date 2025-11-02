from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from users.decorators import ban_guard
from .models import Article, Category, LikeDislike, Bookmark, Rating


# --- FEEDS ---
def feed_all(request):
    articles = Article.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'articles/index.html', {'articles': articles})

def feed_popular(request):
    articles = Article.objects.filter(is_published=True, rating__gte=4).order_by('-rating', '-created_at')
    return render(request, 'articles/feed_popular.html', {'articles': articles})


def feed_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = category.articles.filter(is_published=True).order_by('-created_at')
    return render(request, 'articles/feed_category.html', {'category': category, 'articles': articles})


# --- DETAIL ---
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    likes = article.votes.filter(value=1).count()
    dislikes = article.votes.filter(value=-1).count()
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, article=article).exists()

    return render(request, 'articles/article_detail.html', {
        'a': article,
        'likes': likes,
        'dislikes': dislikes,
        'is_bookmarked': is_bookmarked
    })


# --- CRUD ---
@login_required
@ban_guard
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
            is_published=request.user.can_manage_articles()  # модерация
        )
        return redirect('article_detail', pk=article.pk)

    categories = Category.objects.all()
    return render(request, 'articles/article_form.html', {'categories': categories})


@login_required
@ban_guard
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if not (request.user.can_manage_articles() or request.user == article.author):
        return redirect('feed_all')

    if request.method == 'POST':
        article.delete()
        return redirect('feed_all')

    return render(request, 'articles/article_confirm_delete.html', {'a': article})


@login_required
@ban_guard
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
            article.is_published = False  # на повторную модерацию
        article.save()
        return redirect('article_detail', pk=article.pk)

    categories = Category.objects.all()
    return render(request, 'articles/article_form.html', {'a': article, 'categories': categories})


# --- INTERACTIONS ---
@login_required
@ban_guard
def article_like(request, pk):
    article = get_object_or_404(Article, pk=pk)
    LikeDislike.objects.update_or_create(user=request.user, article=article, defaults={'value': 1})
    return redirect('article_detail', pk=pk)


@login_required
@ban_guard
def article_dislike(request, pk):
    article = get_object_or_404(Article, pk=pk)
    LikeDislike.objects.update_or_create(user=request.user, article=article, defaults={'value': -1})
    return redirect('article_detail', pk=pk)


@login_required
@ban_guard
def article_bookmark_toggle(request, pk):
    article = get_object_or_404(Article, pk=pk)
    bm, created = Bookmark.objects.get_or_create(user=request.user, article=article)
    if not created:
        bm.delete()
    return redirect('article_detail', pk=pk)


@login_required
@ban_guard
def article_rate(request, pk, value):
    article = get_object_or_404(Article, pk=pk)
    value = max(1, min(5, int(value)))
    Rating.objects.update_or_create(user=request.user, article=article, defaults={'value': value})
    avg = article.ratings.aggregate(v=Avg('value'))['v'] or 0
    article.rating = round(float(avg), 2)
    article.save(update_fields=['rating'])
    return redirect('article_detail', pk=pk)
