from django.shortcuts import render, HttpResponse, get_object_or_404, redirect, Http404
from .models import author,category,post
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q, Count
from .forms import CreateForm, registerUser, createAuthor, categoryForm
from django.contrib import messages
from django.views import View
from .require import renderPdf

## registration with email imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError

# close registration import
# token import
from .token import activation_token
# close token


# Create your views here.
def index(request):
    post1 = post.published_objects.all().order_by('-posted_on')
    recent = post.published_objects.filter().order_by('-posted_on')[0:6]
    cat = category.objects.all().annotate(num_post=Count('post'))
    search = request.GET.get('q')
    if search:
        post1 = post1.filter(
            Q(post_title__icontains = search)|
            Q(post_body__icontains = search)
        )
    paginator = Paginator(post1, 2)
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
        'post1':post1,
        'recent':recent,
        'cat':cat,
        'items': items,
        'page_range': page_range,
    }
    return render(request,'index.html', context)


def getAuthor(request, name):
    p_author = get_object_or_404(User, username=name)
    auth = get_object_or_404(author, auth_name=p_author.id)
    post1 = post.published_objects.filter(post_author=auth.id)
    cat = category.objects.all()
    recent = post.published_objects.filter().order_by('-posted_on')[0:6]
    paginator = Paginator(post1, 3)
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
        'auth':auth,
        'cat':cat,
        'recent':recent,
        'post1':post1,
        'items': items,
        'page_range': page_range
    }
    return render(request,'author.html', context)

def PostDetail(request, id):
    post1 = get_object_or_404(post, pk=id)
    cat = category.objects.all()
    first = post.published_objects.first()
    last = post.published_objects.last()
    related = post.published_objects.filter(post_category=post1.post_category).exclude(id=id)[:6]
    if post1.status == 'published':
        post1.views += 1  # clock up the number of post views
        post1.save()
    context ={
        "post1":post1,
        "cat":cat,
        "first":first,
        "last":last,
        "related":related
    }
    return render(request,'post_detail.html', context)

def PostTopic(request, name):
    topic = get_object_or_404(category, name=name)
    post1 = post.published_objects.filter(post_category=topic.id)
    cat = category.objects.all().annotate(num_post = Count('post'))
    recent = post.published_objects.filter().order_by('-posted_on')[0:6]
    paginator = Paginator(post1, 2)
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
    return render(request,'category.html', {"post1":post1, "topic":topic, 'cat':cat , 'recent': recent,'items': items, 'page_range': page_range })

def LogIn(request):
    if request.user.is_authenticated:
        return redirect('nfc:index')
    else:
        if request.method == "POST":
            user = request.POST.get('user')
            password = request.POST.get('pass')
            auth = authenticate(request, username=user, password=password)
            if auth is not None:
                login(request, auth)
                return redirect('nfc:index')
            else:
                messages.add_message(request, messages.ERROR, 'username or password not match')
                return render(request, 'login.html')
    return render(request,'login.html')

def LogOut(request):
    logout(request)
    return redirect('nfc:index')

def CreatePost(request):
    if request.user.is_authenticated:
        u = get_object_or_404(author, auth_name= request.user.id)
        form = CreateForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.post_author = u
            instance.save()
            return redirect('nfc:index')
        return render(request, 'create.html', {"form": form})
    else:
        return redirect('nfc:login')

def PostUpdate(request, id):
    if request.user.is_authenticated:
        u = get_object_or_404(author, auth_name= request.user.id)
        post1 = get_object_or_404(post, id=id)
        form = CreateForm(request.POST or None, request.FILES or None, instance=post1)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.post_author = u
            instance.save()
            messages.success(request, "Post updated successfully")
            return redirect('nfc:profile')
        return render(request, 'create.html', {"form": form})
    else:
        return redirect('nfc:login')

def PostDelete(request, id):
    if request.user.is_authenticated:
        post1 = get_object_or_404(post, id=id)
        post1.delete()
        messages.warning(request, 'post deleted successfully')
        return redirect('nfc:profile')
    else:
        return redirect('nfc:login')


def profile(request):
    if request.user.is_authenticated:
        user = get_object_or_404(User, id= request.user.id)
        author_profile = author.objects.filter(auth_name = user.id)
        if author_profile:
            authorUser = get_object_or_404(author, auth_name = request.user.id)
            post1 = post.published_objects.filter(post_author = authorUser.id)
            return render(request, 'profile.html', {"post1":post1}, {"user":authorUser})
        else:
            form = createAuthor(request.POST or None, request.FILES or None)
            if form.is_valid():
                instance = form.save(commit = False)
                instance.auth_name = user
                instance.save()
                return redirect('nfc:profile')
            return render(request, 'createAuthor.html', {"form":form})
    else:
        return redirect('nfc:login')


def register(request):
    form =registerUser(request.POST or None)
    if form.is_valid():
        instance = form.save(commit = False)
        instance.is_active = False
        instance.save()
        site = get_current_site(request)
        mail_subject = "confirmation message for blog"
        message = render_to_string('confirmation_email.html',{
            'user': instance,
            'domain': site.domain,
            'uid' : instance.id,
            'token': activation_token.make_token(instance)
        })
        to_email = form.cleaned_data.get('email')
        to_list = [to_email]
        from_email = settings.EMAIL_HOST_USER
        send_mail(mail_subject, message, from_email, to_list, fail_silently=True)
        return HttpResponse("<h1>Thanks for your registration. A confirmation link was sent to your mail</h1>")
    return render(request, 'register.html', {"form":form})

def ShowTopic(request):
    query = category.objects.all()
    return render(request, "AllTopic.html", {"topic":query})

def AddCategory(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            form = categoryForm(request.POST or None)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, "topics created successfully")
                return redirect('nfc:category')
            return render(request, "CreateTopics.html", {"form": form})
        else:
            raise Http404("Access denied")
    else:
        return redirect('nfc:login')
"""

"""
def activate(request, uid, token):
    try:
        user = get_object_or_404(User, pk=uid)
    except:
        raise Http404("No user found")
    if user is not None and activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse("<h1>Account is activated. Now you can <a href='/login'>login</a></h1>")
    else:
        return HttpResponse("<h3>Invalid activation</h3>")

class pdf(View):
    def get(self, request, id):
        try:
            query = get_object_or_404(post, id=id)
        except:
            Http404('Content not found')
        context = {
            'post' : query
        }
        post_pdf = renderPdf('pdf.html', context)
        return HttpResponse(post_pdf, content_type='application/pdf')

def About(request):
    return render(request, 'about.html')


def PortFolio(request):
    return render(request, 'portfolio.html')


