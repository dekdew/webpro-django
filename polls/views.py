import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from polls.forms import ChangePasswordForm, ProfileForm, PollModelForm, QuestionForm, ChoiceModelForm, \
  CommentModelForm
from polls.models import Poll, Question, Answer, Profile, Choice


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
  context = {}
  QuestionFormSet = formset_factory(QuestionForm, extra=2, max_num=10)

  if request.method == 'POST':
    form = PollModelForm(request.POST)
    formset = QuestionFormSet(request.POST)
    if form.is_valid():
      poll = form.save()
      if formset.is_valid():
        for question_form in formset:
          if question_form.cleaned_data.get('text'):
            Question.objects.create(
              text=question_form.cleaned_data.get('text'),
              type=question_form.cleaned_data.get('type'),
              poll=poll
            )
        context['success'] = "Poll %s is created successfully" % poll.title

  else:
    form = PollModelForm()
    formset = QuestionFormSet

  context['form'] = form
  context['formset'] = formset
  return render(request, 'polls/create.html', context=context)


@login_required
@permission_required('polls.change_poll')
def update(request, poll_id):
  poll = Poll.objects.get(id=poll_id)
  QuestionFormSet = formset_factory(QuestionForm, extra=2, max_num=10)
  if request.method == 'POST':
    form = PollModelForm(request.POST, instance=poll)
    formset = QuestionFormSet(request.POST)
    if form.is_valid():
      form.save()
      if formset.is_valid():
        for question_form in formset:
          if question_form.cleaned_data.get('question_id'):
            question = Question.objects.get(id=question_form.cleaned_data.get('question_id'))
            if question:
              question.text = question_form.cleaned_data.get('text')
              question.type = question_form.cleaned_data.get('type')
              question.save()
          else:
            if question_form.cleaned_data.get('text'):
              Question.objects.create(
                text=question_form.cleaned_data.get('text'),
                type=question_form.cleaned_data.get('type'),
                poll=poll
              )
        return redirect('update_poll', poll_id=poll_id)

  else:
    form = PollModelForm(instance=poll)
    data = []
    for question in poll.question_set.all():
      data.append(
        {
          'question_id': question.id,
          'text': question.text,
          'type': question.type
        }
      )

    formset = QuestionFormSet(initial=data)

  context = {'form': form, 'formset': formset, 'poll': poll}
  return render(request, 'polls/update.html', context=context)


@login_required
@permission_required('poll.change_poll')
def delete_question(request, question_id):
  question = Question.objects.get(id=question_id)
  question.delete()
  return redirect('update_poll', poll_id=question.poll_id)


@login_required
@permission_required('poll.change_poll')
def add_choice(request, question_id):
  question = Question.objects.get(id=question_id)
  context = {'question':question}
  return render(request, 'choices/add.html', context=context)


def add_choice_api(request, question_id):
  if request.method == 'POST':
    choice_list = json.loads(request.body)
    err_list = []

    for choice in choice_list:
      data = {
        'text': choice['text'],
        'value': choice['value'],
        'question': question_id
      }
      try:
        id = choice['id']
      except:
        id = None
      try:
        choice_model = Choice.objects.get(id=id)
      except Choice.DoesNotExist:
        choice_model = None

      if choice_model:
        form = ChoiceModelForm(data, instance=choice_model)
        if form.is_valid():
          form.save()

      else:
        form = ChoiceModelForm(data)
        if form.is_valid():
          form.save()
        else:
          err_list.append(form.errors.as_text())

    if len(err_list) == 0:
      return JsonResponse({'message': 'success'}, status=200)
    else:
      return JsonResponse({'message': err_list}, status=400)

  return JsonResponse({'message': 'This API dose not accept GET request.'}, status=405)


def get_choice_api(request, question_id):
  if request.method == 'GET':
    choice_list = Choice.objects.filter(question=question_id)
    response = []
    for choice in choice_list:
      temp = {}
      temp['text'] = choice.text
      temp['value'] = choice.value
      temp['id'] = choice.id
      response.append(temp)
    return JsonResponse({'message': response}, status=200)

  return JsonResponse({'message': 'This API dose not accept POST request.'}, status=405)


@csrf_exempt
def delete_choice_api(request, choice_id):
  if request.method == 'POST':
    print(choice_id)
    choice = Choice.objects.get(id=choice_id)
    print(choice)
    choice.delete()

    return JsonResponse({'message': 'success'}, status=200)

  return JsonResponse({'message': 'This API dose not accept GET request.'}, status=405)


def create_comments(request, poll_id):
  if request.method == 'POST':
    form = CommentModelForm(request.POST)
    if form.is_valid():
      comment = form.save(commit=False)
      comment.poll_id = poll_id
      comment.save()
      # poll = Poll.objects.get(id=poll_id)
      # Comment.objects.create(
      #   poll=poll,
      #   title=form.cleaned_data.get('title'),
      #   body=form.cleaned_data.get('body'),
      #   email=form.cleaned_data.get('email'),
      #   tel=form.cleaned_data.get('tel'),
      # )

  else:
    form = CommentModelForm()

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
