from django.shortcuts import render, redirect
from .models import Profile, Blog
from django.contrib.auth.models import User
from .form import LoginForm, DeletePostForm, PostBlog, SignupForm, ChangeProfileForm
from django.contrib.auth import authenticate, login, logout
import datetime

def home(request):
    form = DeletePostForm(request.POST)
    if request.method == "POST":
        if 'deleteId' in request.POST:
            instance = Blog.objects.get(id=request.POST['deleteId'])
            instance.delete()
            return redirect("SeiFinance:dashboard")
        if 'editId' in request.POST: 
            return redirect("SeiFinance:editBlog", request.POST['editId'])
    # username = database.child('Data').child('name').get().val()
    username = request.user.username
    blog = Blog.objects.all().order_by('-created_at')
    return render(request, "dashboard/dashboard.html", {"username": username, "blog": blog})

def userLogin(request): 
    form = LoginForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                form = LoginForm()
                return redirect("SeiFinance:dashboard")
            else: 
                return render(request, "login/login.html", {"isExist": True})
        else: 
            return render(request, "login/login.html", {"isExist": True})
    return render(request, "login/login.html", {"form": form})

def userSignup(request): 
    form = SignupForm(request.POST)
    if request.method == "POST": 
        if form.is_valid(): 
            isExist = User.objects.filter(username=request.POST['username']).exists()
            if isExist == False:
                user = User.objects.create_user(first_name=request.POST['name'], username=request.POST['username'], password=request.POST['password'], email=request.POST['email'])
                user.save()
                login(request, user)
                return redirect("SeiFinance:dashboard")
            else: 
                return render(request, "login/signup.html", {"isExist": isExist})
        else: 
            isExist = True
            return render(request, "login/signup.html", {"isExist": isExist})
    return render(request, "login/signup.html", {"form": form})

def userLogout(request): 
    logout(request)
    return redirect("SeiFinance:dashboard")

def profile(request): 
    form = ChangeProfileForm(request.POST)
    if request.method == "POST": 
        response = dict()
        instance = User.objects.get(username=request.user.username)
        if 'passwordOld' in request.POST and instance.check_password(request.POST['passwordOld']):
            if ('password' in  request.POST) or ('passwordAgain' in request.POST): 
                if ('password' in  request.POST) and ('passwordAgain' in request.POST): 
                    if (request.POST['password'] != request.POST['passwordAgain']): 
                        response['password'] = False
                    else: 
                        response['password'] = True
                else: 
                    response['password'] = False

            if 'name' in request.POST: 
                if User.objects.filter(first_name=request.POST['name']).exists() == False:
                    response['name'] = True
                elif request.POST['name'] == request.user.first_name: 
                    response['name'] = True
                else: 
                    response['name'] = False

            if 'email' in request.POST: 
                if User.objects.filter(email=request.POST['email']).exists() == False:
                    response['email'] = True
                elif request.POST['email'] == request.user.email: 
                    response['email'] = True
                else: 
                    response['email'] = False
        else: 
            response['checkPassword'] = False
        print(response)
        if len(response) != 0 and (('checkPassword' in response) == False): 
            if 'password' in response and response['password'] == True: 
                instance.set_password(request.POST['password'])
            if 'name' in response and response['name'] == True:
                instance.first_name = request.POST['name']
            if 'email' in response and response['email'] == True: 
                instance.email = request.POST['email']
            instance.save()
        return render(request, "profile/profile.html", {"response": response})
    return render(request, "profile/profile.html")

def myBlog(request): 
    form = DeletePostForm(request.POST)
    if request.method == "POST":
        if 'deleteId' in request.POST:
            instance = Blog.objects.get(id=request.POST['deleteId'])
            instance.delete()
            return redirect("SeiFinance:myBlog")
        if 'editId' in request.POST: 
            return redirect("SeiFinance:editBlog", request.POST['editId'])
    userId = request.user.id
    blog = Blog.objects.filter(user=userId).order_by('-created_at')
    return render(request, "blog/myBlog.html", {"blog": blog})

def editBlog(request, postId): 
    form = PostBlog(request.POST or None)
    blog = Blog.objects.get(id=postId)
    if request.method == "POST": 
        if form.is_valid(): 
            blog.header=request.POST['header']
            blog.body=request.POST['description']
            blog.created_at = datetime.datetime.now()
            blog.save()
            listBlogs = Blog.objects.filter(user=blog.user.id).order_by('-created_at')
            return redirect("SeiFinance:profile")
    return render(request, "blog/editBlog.html", {"blog": blog})

def addBlog(request): 
    form = PostBlog(request.POST or None)
    if request.method == "POST": 
        if form.is_valid(): 
            blog=Blog(header=request.POST['header'], body=request.POST['description'], user=request.user, created_at=datetime.datetime.now())
            blog.save()
            return redirect("SeiFinance:dashboard")
    return render(request, "blog/editBlog.html")