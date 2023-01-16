from django.shortcuts import render, redirect
from django.views import generic
from core.models import *
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Q
from .forms import *
from django.db import transaction


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(email=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                user_frame = UserFrame.objects.select_related('frame').filter(user_id=request.user.id,active=True).all()
                for i in user_frame:
                    if i.frame.type == "background":
                        request.session['background_color'] = i.frame.color
                    if i.frame.type == "login":
                        request.session['login_color'] = i.frame.color
                return redirect('test')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def user_registration(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.create(email=cd['username'], password=cd['password'])
            print(user)
            if user is not None:
                login(request, user)
                return redirect('test')
            else:
                return HttpResponse('Invalid register')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def user_logout(request):
    try:
        logout(request)
        del request.session['background_color']
        del request.session['login_color']
    except KeyError:
        pass
    return redirect('login')


class TestListView(generic.ListView):
    model = Test
    template_name = 'tests.html'


class TestPassView(generic.DetailView):
    model = Test
    template_name = 'passing_test.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = Test.objects
        q = Test.prefetch(q)
        test = q.filter(id=self.object.id).first()
        question = test.question_set.order_by("order").first()
        print(test)
        print(test.question_set.order_by("order"))
        context.update({
            'test': test,
            'question': question,
        })
        return context


@transaction.atomic
def question_view(request, test_id, question_id):
    test = Test.objects.get(id=test_id)
    question = Question.objects.get(id=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, question=question, test=test)
        if form.is_valid():
            cd = form.cleaned_data
            if question.answer == cd['answer']:
                user_test = UserTest.objects.filter(user_id=request.user.id,
                                                    test=test,
                                                    passed=False).first()
                UserTest.objects.filter(user_id=request.user.id,
                                        test=test,
                                        ).update(result=user_test.result+1)
            if Question.objects.filter(test=test).count() == question.order:
                result = UserTest.objects.filter(user_id=request.user.id,
                                                 test=test,
                                                 passed=False).first().result
                UserTest.objects.filter(user_id=request.user.id, test=test, passed=False).update(passed=True)
                User.objects.filter(id=request.user.id).update(account=request.user.account+result)
                return redirect('test')
            question = Question.objects.filter(test=test, order=question.order+1).first()
            form = QuestionForm(question=question, test=test)
            return render(request, 'question.html', {'form': form})
    else:
        UserTest.objects.create(user_id=request.user.id, test=test)
        form = QuestionForm(question=question, test=test)
    return render(request, 'question.html', {'form': form})


class MarketplaceView(generic.ListView):
    model = Frame
    template_name = 'marketplace.html'


@transaction.atomic
def frame_view(request, pk):
    if request.method == 'POST':
        frame = Frame.objects.get(id=pk)
        if UserFrame.objects.filter(user_id=request.user.id, frame_id=pk).exists():
            frame_list = Frame.objects.all()
            return render(request, 'marketplace.html',
                          {"frame_list": frame_list, "is_exist": True, "frame_id": frame.id})
        if request.user.account >= frame.price:
            User.objects.filter(id=request.user.id).update(account=request.user.account-frame.price)
            UserFrame.objects.select_related('frame').filter(user_id=request.user.id,
                                                             active=True,
                                                             frame__type=frame.type).update(active=False)
            UserFrame.objects.create(user_id=request.user.id, frame_id=pk, active=True)
            if frame.type == "background":
                request.session['background_color'] = frame.color
            if frame.type == "login":
                request.session['login_color'] = frame.color
        else:
            frame_list = Frame.objects.all()
            return render(request, 'marketplace.html',
                          {"frame_list": frame_list, "not_enough": True, "frame_id": frame.id})
    return redirect('my-frames')


class MyFramesView(generic.ListView):
    model = Frame
    template_name = 'my_frames.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_frames = UserFrame.objects.select_related('frame').filter(user_id=self.request.user.id)
        context.update({
            'frames': user_frames,
        })
        return context


@transaction.atomic
def my_frame_view(request, pk):
    if request.method == 'POST':
        frame = Frame.objects.get(id=pk)
        UserFrame.objects.select_related('frame').filter(user_id=request.user.id,
                                                         active=True,
                                                         frame__type=frame.type).update(active=False)
        UserFrame.objects.select_related('frame').filter(user_id=request.user.id,
                                                         frame_id=pk).update(active=True)
        if frame.type == "background":
            request.session['background_color'] = frame.color
        if frame.type == "login":
            request.session['login_color'] = frame.color
    return redirect('my-frames')


class StatisticsView(generic.ListView):
    model = User
    template_name = 'statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects
        users = User.prefetch(users)
        users = users.annotate(
            test_count=Count(
                'usertest__id',
                filter=Q(usertest__passed=True),
                distinct=True
            )
        )
        # users = users.filter(is_superuser=False)
        context.update({
            'users': users,
        })
        return context
