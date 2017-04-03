# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals
# функция генерирующая 404 страницу
from django.http import Http404

# функция отрисовки страницы, принимающая путь до шаблона и данные помещенные в шаблон
from django.shortcuts import render_to_response
from django.contrib.contenttypes.models import ContentType
# наша модель
from polls.models import Game
from polls.models import Team
from polls.models import Comment
from polls.models import BlogPost
from polls.models import CommentBlogPost
from polls.models import Screenshot
from polls.models import Rating
from polls.models import ProfilePhoto
from polls.models import MyUser
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth import logout
from polls.forms import CustomUserCreationForm, CommentsForm
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
import json
from json import dumps
from django.core import serializers
from django.core.mail import send_mail
from .forms import UploadFileForm
from PIL import Image
#new
from django.core.mail import EmailMultiAlternatives

def logout_view(request):
  logout(request)
  # Redirect to a success page.
  return HttpResponseRedirect("/")

class LoginFormView(FormView):
    form_class = AuthenticationForm
    template_name = "login.html"
    success_url = "/"
    def form_valid(self, form):
        self.user = form.get_user()
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)

class RegisterFormView(FormView):
    form_class = CustomUserCreationForm
    success_url = "/auth/"
    template_name = "register.html"

    def form_valid(self, form):
        form.save()
        # mes = "Look here http://127.0.0.1/posts/ for new games!"
        # send_mail('Regisration complete', mes, 'from@example.com',
        #             ['ericovva@yandex.ru'], fail_silently=True)
        return super(RegisterFormView, self).form_valid(form)

from social.apps.django_app.utils import psa
@psa('social:complete')
def login_vk(request, backend):
    token = request.GET.get('access_token')
    user = request.backend.do_auth(request.GET.get('access_token'))
    if user:
        login(request, user)
        return 'OK'
    else:
        return 'ERROR'


    return HttpResponseRedirect("/app/oauth2login")
def oauth2login_view(request, **kwargs):
    print('sada')
    # access_token = request.GET.get('access_token')
    # user = backend.do_auth(access_token)
    # if user and user.is_active:
    #     login(request, user)
    return HttpResponseRedirect("/profile")

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def upload_file(request):
    print("zzz")
    if request.method == 'POST':
        print("ccc")
        form = UploadFileForm(request.POST, request.FILES)
        print(request.FILES.get('file', False))
        if form.is_valid():
            print(request.user.username)
            path = 'media/' + str(request.user.id) + ".png"
            handle_uploaded_file(request.FILES.get('file', False),path)
            print("aaaa")
            response = {
                    'msg' : path,
                    'status' : 'OK'
                }

            image = Image.open(path)

            pw = image.width
            ph = image.height
            print(pw)
            nw = 150
            nh = 150
            pr = float(pw) / float(ph)
            nr = float(nw) / float(nh)

            if pr > nr:
                # photo aspect is wider than destination ratio
                tw = int(round(nh * pr))
                image = image.resize((tw, nh), Image.ANTIALIAS)
                l = int(round(( tw - nw ) / 2.0))
                image = image.crop((l, 0, l + nw, nh))
            elif pr < nr:
                # photo aspect is taller than destination ratio
                th = int(round(nw / pr))
                image = image.resize((nw, th), Image.ANTIALIAS)
                t = int(round(( th - nh ) / 2.0))
                print((0, t, nw, t + nh))
                image = image.crop((0, t, nw, t + nh))
            else:
                # photo aspect matches the destination ratio
                image = image.resize((nw,nh), Image.ANTIALIAS)
            image.save(path)
            profile_photo = ProfilePhoto.objects.filter(user=request.user.id)
            print(profile_photo)
            if profile_photo:
                profile_photo.delete()
            u = MyUser.objects.get(id=request.user.id)
            u.img = "/" + path
            u.save()
            print(u)
            new_photo = ProfilePhoto(img_src=path,user=u)
            new_photo.save()
            print("profile_p_saved_success")
            return HttpResponse(json.dumps(response), content_type="application/json")#return HttpResponseRedirect('/')
    else:
        form = UploadFileForm()
    return render(request,'profile.html', {'form': form})

def handle_uploaded_file(f,path):

    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)



def main_page (request):

    return render(request,'index.html')#render_to_response('index.html')

def auth (request):
    #user = authenticate(email=email, password=password)
    #login(request, user)
    return render(request,'login.html')#render_to_response('login.html')

def blog (request):
    blog_posts = BlogPost.objects.all()
    return render(request,'blog.html',{"blog_posts": blog_posts})#render_to_response('blog.html',{"blog_posts": blog_posts})



def get_blog_post(request, blog_post_id):
    try:
        # выбираем конкретный пост, pk - primary key
        blog_post = BlogPost.objects.get(pk=blog_post_id)
        blog_comments = CommentBlogPost.objects.filter(post=blog_post_id)
    except BlogPost.DoesNotExist:
        # если такого поста нет, то генерируем 404
        raise Http404
    # отрисовываем
    return render(request,'blog_post.html', {"title":  blog_post.title, "img": blog_post.img, "user": blog_post.user ,"id": blog_post.id, "text": blog_post.text,"comments": blog_comments})#render_to_response('blog_post.html', {"title":  blog_post.title, "img": blog_post.img, "user": blog_post.user ,"id": blog_post.id, "text": blog_post.text,"comments": blog_comments})


def profile (request):
    form = UploadFileForm()
    profile_photo = ProfilePhoto.objects.filter(user=request.user.id)
    if profile_photo:
        photo = "/" + profile_photo[0].img_src
    else:
        photo = "http://robohash.org/sitsequiquia.png?size=120x120"

    return render(request,'profile.html', {'form': form, 'photo': photo})#render_to_response('profile.html')


def we (request):

    # Получаем список постов
    teams = Team.objects.all()
    # отрисовываем
    return render(request,'our_team.html', {"teams":  teams})#render_to_response('our_team.html', {"teams":  teams})
def compute_rating(type_,id_):
    rating = Rating.objects.filter(content_type=type_,object_id=id_)
    print(id_)
    print(len(rating))
    sum = 0.0
    votes = len(rating)
    if votes != 0:
        for rate in rating:
            sum = sum + rate.mark
        sum = sum / len(rating)
    return sum

@csrf_protect
def change_view_unlike(request):
    if request.method == "POST":
        print(request)
        #if request.POST["content_type"] == "game":
         #   print("ok")
        content_object_ = Game.objects.get(id = int(request.POST["id"]))
        content_object_type = ContentType.objects.get_for_model(content_object_)
        was_rate = Rating.objects.filter(user = request.user.id,content_type= content_object_type.id,object_id = int(request.POST["id"]))
        print(was_rate)
        if request.POST["content_type"] == "game":
            if was_rate:
               was_rate.delete()
               num = compute_rating(type_=content_object_type.id,id_=int(request.POST["id"]))
               response = {
                    'msg' : str(num),
                    'status' : 'OK'
                }
            else:
                response = {
                    'msg' : "hack",
                    'status' : 'error'
                }
        return HttpResponse(json.dumps(response), content_type="application/json")

def change_view(request):
    if request.method == "POST":
        print(request.user)
        print(request.POST["votes"])
        print(request.POST)
        u = MyUser.objects.get(id=request.user.id)
        new_voice = request.POST["score"]
        content_object_type_id = 0
        if request.POST["content_type"] == "game":
            content_object_ = Game.objects.get(id = int(request.POST["id"]))
            content_object_type = ContentType.objects.get_for_model(content_object_)
            was_rate = Rating.objects.filter(user = request.user.id,content_type= content_object_type.id,object_id = int(request.POST["id"]))
            content_object_type_id = content_object_type.id
            print(was_rate)
            if was_rate:
                was_rate.delete()
        print("ok")
        new_rating = Rating(mark = float(new_voice), content_object = content_object_)
        new_rating.save()

        u.rating_set.add(new_rating)
        num = compute_rating(type_=content_object_type.id,id_=int(request.POST["id"]))
        response = {
            'msg' : str(num),
            'status' : 'OK'
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

def post_comment(request):
    if request.method == "POST":
        print(request.user)
        print(request.POST)
        print(request.user.id)
        form = CommentsForm(request.POST)
        if form.is_valid() and request.POST["id"]!="":
        # text_ = request.POST["text"]
            print("==========")
            print(request.POST["to_user_id"])
            print(request.POST["answer_to_comment_id"])
            if request.POST["to_user_id"]!="" and request.POST["answer_to_comment_id"]!="":
                to_user_id = MyUser.objects.get(id=int(request.POST["to_user_id"]));
                print(to_user_id.email)
                answer_to = Comment.objects.get(id=int(request.POST["answer_to_comment_id"]));
                print(answer_to)
                mes = "http://playnoch.cloudapp.net/post/" + str(request.POST["id"]) + "/"
                print("==========")
                #send_mail("На ваш комментарий <<" + answer_to.text + ">>", mes, 'from@example.com',[to_user_id.email], fail_silently=False)
                ###########
                subject, from_email, to = 'Ёу, ' + to_user_id.username, 'from@example.com', to_user_id.email
                text_content = 'This is an important message.'
                html_content = "<div style=\'font-size:30px; color: red;\'>NOCH</div><pre>На твой комментарий, <a href=\'" + mes + "\'>ответил</a>  " + request.user.username + "</pre>"
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                #########

            game_id_ = request.POST["id"]

        # g = Game.objects.get(id=int(game_id_))
        # u = MyUser.objects.get(id=request.user.id)
        # e = Comment(text = text_)
        # g.comment_set.add(e)
        # u.comment_set.add(e)
            new_comment = form.save()
            g = Game.objects.get(id=int(game_id_))
            u = MyUser.objects.get(id=request.user.id)
            g.comment_set.add(new_comment)
            u.comment_set.add(new_comment)
            # comments = Comment.objects.filter(game=int(game_id_))
            # #print(comments)

            # objectQuerySet = Comment.objects.filter(game=int(game_id_))
            # data = serializers.serialize('json', objectQuerySet, fields=('user','text','date'))
            # data2 = json.loads(data)
            # for d in data2:
            #     d["fields"]["user"] = MyUser.objects.get(id=int(d["fields"]["user"])).username
            #     #print(d)
            # data = serializers.serialize('json', data2, fields=('user','text','date'))

            # print(data)
            # response = data

            profile_photo = ProfilePhoto.objects.filter(user=request.user.id)
            print(profile_photo)
            photo_src = "media/profile.png"
            print("2==============")
            print(profile_photo)
            if len(profile_photo) > 0:
                print("in")
                photo_src = profile_photo[0].img_src

            print("3==============")
            response = {
                'user' : request.user.username,
                'date' : new_comment.date.strftime('%Y-%m-%d %H:%M'),
                'text' : new_comment.text,
                'profile_photo': photo_src,
                'status' : 'OK',
            }
            print("4==============")
            print(response)
            print("valid")
        else:
            response = {
                'msg' : 'lel',
                'status' : 'bad',
            }
            print("invalid")
        return HttpResponse(json.dumps(response), content_type="application/json")

def get_post (request, post_id):
    try:
        if request.method == 'POST':
            form = CommentsForm(request.POST)
            if form.is_valid():
                st = "/post/" + str (post_id) + '/'
                form.save()
                return HttpResponseRedirect(st)
        else:
            form = CommentsForm()
        # выбираем конкретный пост, pk - primary key
        post = Game.objects.get(pk=post_id)
        post.show_times = post.show_times + 1
        post.save()
        comments = Comment.objects.filter(game=post_id).order_by("date").reverse()
        images = Screenshot.objects.filter(game=post_id)
        post_type = ContentType.objects.get_for_model(post)
        rating = Rating.objects.filter(content_type=post_type.id,object_id=post_id)
        print(len(rating))
        sum = 0.0
        votes = len(rating)
        if votes != 0:
            for rate in rating:
                sum = sum + rate.mark
            sum = sum / len(rating)

        count = len(images)
        images_list = list(images)
        first_img_link = ""
        if len(images_list) > 0:
            first_img_link = images_list[0].img
            images_list.pop(0)
        else:
            first_img_link = "screenshots/default.jpg"
        lists = []
        for i in range(0,count):
            lists.append(i)
    except Game.DoesNotExist:
        # если такого поста нет, то генерируем 404
        raise Http404
    # отрисовываем
    return render(request,'single.html', {"title":  post.title,
                                              "description": post.description,
                                              "comments": comments ,"id": post.id,
                                              "images": images_list,"first_img_link": first_img_link,
                                              "count": lists,
                                              "rating": str(sum),"votes": votes,
                                              'form': form,'show_times': post.show_times
                                              })


def posts_page (request):
    # Получаем список постов
    games = Game.objects.all()
    # i = 0
    # ratings = []
    # while i < len(games):
        # game_type = ContentType.objects.get_for_model(games[i])
        # rating = Rating.objects.filter(content_type=game_type.id,object_id=games[i].id)
        # print("rating")
        # print(rating)
        # j = 0
        # sum = 0.0
        # if (len(rating) != 0):
        #     while j < len(rating):
        #         sum = sum + rating[j].mark
        #         j = j + 1
        #     ratings.append(sum / len(rating))
        # else:
        #     ratings.append(sum)
        # print("ratings[i]")
        # print(ratings[i])
        # i = i + 1
        # print("______________") django agregation
    # отрисовываем
    return render(request,'list.html', {"posts":  games})#render_to_response('list.html', {"posts":  games})


def vk (request):

    return render(request,'auth.html');






