from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
from polls.forms import PollForm, CommentForm, ChangePasswordForm, ProfileForm
from polls.models import Poll, Question, Answer, Comment, Profile


def index(request):
  poll_list = Poll.objects.all()

  for poll in poll_list:
    question_count = Question.objects.filter(poll_id=poll.id).count()
    poll.question_count = question_count

  context = {
    'page_title': 'My polls',
    'poll_list': poll_list
  }

  return render(request, template_name='polls/index.html', context=context)


@login_required
@permission_required('polls.view_poll')
def detail(request, poll_id):
  poll = Poll.objects.get(pk=poll_id)

  for question in poll.question_set.all():
    name = 'choice' + str(question.id)
    choice_id = request.GET.get(name)

    if choice_id:
      try:
        ans = Answer.objects.get(question_id=question.id)
        ans.choice_id = choice_id
        ans.save()
      except Answer.DoesNotExist:
        Answer.objects.create(
          choice_id=choice_id,
          question_id=question.id
        )

  return render(request, 'polls/poll.html', {'poll': poll})


@login_required
@permission_required('polls.add_poll')
def create(request):
  if request.method == 'POST':
    form = PollForm(request.POST)

    if form.is_valid():
      poll = Poll.objects.create(
        title=form.cleaned_data.get('title'),
        start_date=form.cleaned_data.get('start_date'),
        end_date=form.cleaned_data.get('end_date')
      )

      for i in range(1, form.cleaned_data.get('no_question') + 1):
        Question.objects.create(
          text=poll.title + str(i),
          type='01',
          poll=poll
        )

  else:
    form = PollForm()

  context = {'form': form}
  return render(request, 'polls/create.html', context=context)


def create_comments(request, poll_id):
  if request.method == 'POST':
    form = CommentForm(request.POST)
    if form.is_valid():
      poll = Poll.objects.get(id=poll_id)
      Comment.objects.create(
        poll=poll,
        title=form.cleaned_data.get('title'),
        body=form.cleaned_data.get('body'),
        email=form.cleaned_data.get('email'),
        tel=form.cleaned_data.get('tel'),
      )

  else:
    form = CommentForm()

  context = {'form': form, 'poll_id': poll_id}
  return render(request, 'polls/create-comment.html', context=context)


def my_login(request):
  context = {}

  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)

    if user:
      login(request, user)

      next_url = request.POST.get('next_url')
      if next_url:
        return redirect(next_url)
      else:
        return redirect('index')
    else:
      context['username'] = username
      context['password'] = password
      context['error'] = 'Wrong username or password!'

  next_url = request.GET.get('next')
  if next_url:
    context['next_url'] = next_url

  return render(request, 'polls/login.html', context=context)


def my_logout(request):
  logout(request)
  return redirect('login')


@login_required
def change_password(request):
  if request.method == 'POST':
    form = ChangePasswordForm(request.user, request.POST)
    if form.is_valid():
      u = User.objects.get(username=request.user)
      u.set_password(request.POST.get('new_password'))
      u.save()

      return redirect('login')

  else:
    form = ChangePasswordForm(request.user)

  context = {'form': form}
  return render(request, 'polls/change-password.html', context=context)


def register(request):
  if request.method == 'POST':
    form = ProfileForm(request.POST)
    if form.is_valid():
      form.save()
      username = form.cleaned_data.get('username')
      raw_password = form.cleaned_data.get('password1')
      user = authenticate(username=username, password=raw_password)
      Profile.objects.create(
        user=user,
        line_id=form.cleaned_data.get('line_id'),
        facebook=form.cleaned_data.get('facebook'),
        gender=form.cleaned_data.get('gender'),
        birthdate=form.cleaned_data.get('birthdate')
      )
      login(request, user)
      return redirect('index')

  else:
    form = ProfileForm()

  context = {'form': form}

  return render(request, 'polls/register.html', context=context)
