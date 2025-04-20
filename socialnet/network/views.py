from django.shortcuts import render, redirect
from .forms import RegisterForm, PostForm , CommentForm
from .models import Post, Comment, Like
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .forms import EditUserForm, EditProfileForm
from django.contrib.auth.models import User
from .models import Chat, Message
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post, Activity


def home(request):


    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})



def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'feed.html', {'posts': posts, 'users': users})

def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            Activity.objects.create(
                user=request.user,
                activity_type="New Post"

            )
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            Activity.objects.create(
                user=request.user,
                activity_type="New Comment"
            )
            return redirect('feed')
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form, 'post': post})

@login_required
def add_like(request, post_id):
    post = Post.objects.get(id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()

    return JsonResponse({
        'likes_count': post.likes.count(),
        'liked': created
    })

def view_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    return render(request, 'view_comments.html', {'post': post, 'comments': comments})

@login_required
def edit_profile(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=user)
        profile_form = EditProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('feed')
    else:
        user_form = EditUserForm(instance=user)
        profile_form = EditProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def view_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    posts = user.post_set.all().order_by('-created_at')

    return render(request, 'view_profile.html', {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
    })

@login_required
def chat_list(request):
    chats = request.user.chats.all()
    return render(request, 'chat_list.html', {'chats': chats})


@login_required
def chat_detail(request, chat_id):
    chat = Chat.objects.get(id=chat_id)
    if request.user not in chat.participants.all():
        return redirect('chat_list')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(chat=chat, sender=request.user, content=content)

    messages = chat.messages.order_by('timestamp')
    return render(request, 'chat_detail.html', {'chat': chat, 'messages': messages})

@login_required
def start_chat(request, username):
    other_user = get_object_or_404(User, username=username)
    chat = Chat.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not chat:
        chat = Chat.objects.create()
        chat.participants.add(request.user, other_user)
    return redirect('chat_detail', chat_id=chat.id)

@receiver(post_save, sender=Post)
def create_post_activity(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            user=instance.author,
            activity_type='post_created',
            content=instance.content,
            target_post=instance,
        )

@receiver(post_save, sender=Comment)
def create_comment_activity(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            user=instance.user,
            activity_type='comment_created',
            content=instance.content,
            target_post=instance.post,
            target_comment=instance,
        )

@receiver(post_save, sender=Like)
def create_like_activity(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            user=instance.user,
            activity_type='like_created',
            target_post=instance.post,
        )

@receiver(post_save, sender=Message)
def create_message_activity(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            user=instance.sender,
            activity_type='message_sent',
            content=instance.content,
            target_post=None,
        )
def activity_feed(request):
    activities = Activity.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'activity_feed.html', {'activities': activities})

def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'view_post.html', {'post': post})