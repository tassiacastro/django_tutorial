from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import Question
from django.template import loader
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .models import Choice, Question
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import QuestionSerializer, ChoiceSerializer
# Create your views here.

@login_required
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

@login_required
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    current_user = request.user
    
    # If the user logged in created the question, dont allow he/she to answer it
    if current_user.id == question.user_id:
        return HttpResponse("You can't answer your own question =)")
    else:
        return render(request, 'polls/detail.html', {'question': question})

@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    current_user = request.user
    
    if current_user.id == question.user_id:
        return HttpResponse("You can't answer your own question =)")

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', { 'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

@login_required
def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

@login_required
def new_question(request):
    if request.method == 'POST':
        q = Question(question_text = request.POST['question_text'], pub_date = timezone.now())
        q.save()
        
        total_choice = int(request.POST['choice_set-TOTAL_FORMS'])
        
        for i in range(0, total_choice):
            choice_key = "choice_set-" + str(i) + "-choice_text"
            q.choice_set.create(choice_text = request.POST[choice_key], votes = 0)
            q.user_id = request.user.id

        q.save()
        return HttpResponseRedirect(reverse("polls:index"))
    else:
        return render(request, 'polls/new_question.html')

def new_user(request):
    if request.method == 'POST':
        
        if User.objects.filter(username=request.POST['username']).exists():
            return HttpResponse("This username is already taken, please choose another one")
        
        current_user = User.objects.create_user(username=request.POST['username'],
                                                password=request.POST['psw'])
        current_user.save()
        
        return HttpResponseRedirect(reverse("polls:index"))
    else:
        return render(request, 'registration/new_user.html')


class QuestionView(APIView):
    def get(self, request):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response({"questions": serializer.data})

class ChoiceView(APIView):
    def get(self, request, question_id):
        choices = Choice.objects.filter(question= question_id)
        serializer = ChoiceSerializer(choices, many=True)
        return Response({"choices": serializer.data})