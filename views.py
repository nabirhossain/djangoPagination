from django.shortcuts import render
from .models import Post
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# Create your views here.
def index(request):
    post = Post.published_objects.all().order_by('-posted_on')
    paginator = Paginator(post, 2)
    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    index = items.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 4 if index >= 4 else 0
    end_index = index + 4 if index <= max_index else max_index
    page_range = paginator.page_range[start_index:end_index]
    context = {
        'post':post,
        'items': items,
        'page_range': page_range,
    }
    return render(request,'index.html', context)

