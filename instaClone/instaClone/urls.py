from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from myapp.views import signup_view, login_view, feed_view, post_view, like_view, comment_view, logout_view, upvote_view
urlpatterns = [
    url('post/', post_view),
    url('feed/', feed_view),
    url('login/', login_view),
    url('comment/', comment_view),
    url('like/', like_view),
    url('logout/', logout_view),
    url('upvote/', upvote_view),
    url('', signup_view)
]