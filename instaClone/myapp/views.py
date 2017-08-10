# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from tokenize import Comment

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect


from forms import SignUpForm, LoginForm,PostForm,LikeForm, CommentForm,  UpvoteForm
from datetime import datetime
from models import UserModel, SessionToken,PostModel,LikeModel, CommentModel

from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from django.utils import timezone
from instaClone.settings import BASE_DIR
from imgurpython import ImgurClient
#where users can upload images of products along with reviews in the caption. The application should have the functionality of marking the review as positive or negative.using parallel dots
from paralleldots.config import get_api_key
import requests
import json






# Create your views here.

def signup_view(request):
    #check if request is post
   if request.method == "POST":
       #define form
       form = SignUpForm(request.POST)
       print request.body
       #check form is valid
       if form.is_valid():
           #retrieve username
           username = form.cleaned_data['username']
           #retrieve email
           email = form.cleaned_data['email']
           #retrieve  password
           password = form.cleaned_data['password']

           # saving data to DB
           user = UserModel( username=username,  password=make_password(password),
                       email=email)
           user.save()

       return render(request, 'success.html')
   elif request.method == "GET":
       form = SignUpForm()
       today = datetime.now()

#load index page
   return render(request, 'index.html', { 'today': today,  'form': form})



def login_view(request):
    response_data = {}
    # check if request is post
    if request.method == "POST":
        # define form
        form = LoginForm(request.POST)
        # check form is valid
        if form.is_valid():
            print "here"
            #retrieve username
            username = form.cleaned_data.get('username')
            #retrieve password
            password = form.cleaned_data.get('password')
            print UserModel.objects.all()
            user = UserModel.objects.filter(username=username).first()
            print user
           #check if user exists
            if user:
                # Check for the password is correct
                print 'A'
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    #create session token
                    token.create_token()
                    #saving session token
                    token.save()
                    #redirect to feed page
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    response_data['message'] = 'Incorrect Password! Please try again!'
            else:
                response_data['msg'] = "Incorrect Username! Please try again!"

    elif request.method == 'GET':
        form = LoginForm()

    response_data['form']= form
    #load login page
    return render(request, 'login.html', response_data)

def feed_view(request):
    return render(request, 'feed.html')



#create a view for check validation
def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            return session.user
    else:
        return None

#create view for post
def post_view(request):
    #check if user is valid
    user = check_validation(request)
     #check if user exists
    if user:
        #check if request is post
        if request.method == 'POST':

          form = PostForm(request.POST, request.FILES)
            #check if form is valid
        if form.is_valid():
            #accept image
            image = form.cleaned_data.get('image')
            #accept caption
            caption = form.cleaned_data.get('caption')
            post = PostModel(user=user,image=image,caption=caption)
            #post is  save
            post.save()
            path = str(BASE_DIR + "/" + post.image.url)
            #define client
            client = ImgurClient('8fd0103958ccceb', 'aa73c860636e25e381ec473bd76fb4f2d3ca1adb')
            #define image url
            post.image_url = client.upload_from_path(path, anon=True)['link']
            #save the image url
            post.save()
            #redirect to feed page
            return redirect('/feed/')
        else:
          form = PostForm()
        #load post page
        return render(request, 'post.html', {'form': form})
    else:
        return redirect('/login/')


#define feed view
def feed_view(request):
    user = check_validation(request)
    if user:

        posts = PostModel.objects.all().order_by('created_on')

        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True


        return render(request, 'feed.html', {'posts': posts})
    else:

        return redirect('/login/')

#create view for like
def like_view(request):
    #check if user is valid
    user = check_validation(request)
    #check if user exists and request is post
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        #check if form is valid
        if form.is_valid():
            #retrieve post id
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
            else:
                existing_like.delete()
            return redirect('/feed/')
    else:
        return redirect('/login/')
#create view for comment
def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            apikey = 'UXqiW0EEfpWD1oB8AgJXAveneCAQxkIQSGXZwbAioS0'
            request_url = ('https://apis.paralleldots.com/sentiment?sentence1=%s&apikey=%s') % (comment_text, apikey)
            print 'POST request url : %s' % (request_url)
            sentiment = requests.get(request_url, verify=False).json()
            sentiment_value = sentiment['sentiment']
            print sentiment_value
            if sentiment_value < 0.5:
                print 'Negative Comment'
            else:
                print 'Positive Comment'

            print 'commented'
            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')


#method to log user out of this account
def logout_view(request):
        user = check_validation(request)
        if user is not None:
            latest_session = SessionToken.objects.filter(user=user).last()
            if latest_session:
                latest_session.delete()

        return redirect("/login/")
   # how to get cookies in python to delete cookie n session


# For validating the session
def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None

# method to create upvote for comments
def upvote_view(request):
    user = check_validation(request)
    comment = None

    print ("upvote view")
    if user and request.method == 'POST':

        form = UpvoteForm(request.POST)
        if form.is_valid():

            comment_id = int(form.cleaned_data.get('id'))

            comment = CommentModel.objects.filter(id=comment_id).first()
            print ("upvoted not yet")

            if comment is not None:
                # print ' unliking post'
                print ("upvoted")
                comment.upvote_num += 1
                comment.save()
                print (comment.upvote_num)
            else:
                print ('stupid mistake')
                #liked_msg = 'Unliked!'

        return redirect('/feed/')
    else:
        return redirect('/feed/')