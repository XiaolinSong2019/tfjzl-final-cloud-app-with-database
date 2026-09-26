from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
import logging

# Imported models including Question, Choice, and Submission
from .models import Course, Enrollment, Question, Choice, Submission

# Get an instance of a logger
logger = logging.getLogger(__name__)


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# Helper method to collect the selected choice IDs from the exam POST request
def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_answers.append(choice_id)
    return submitted_answers


# -------------------------------------------------------------
# Submit view
# -------------------------------------------------------------
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    # Get enrollment associated with user and course
    enrollment = Enrollment.objects.get(user=user, course=course)

    # Create submission record
    submission = Submission.objects.create(enrollment=enrollment)

    # Extract answers from POST request and associate choices with submission
    choice_ids = extract_answers(request)
    for choice_id in choice_ids:
        choice = Choice.objects.get(pk=choice_id)
        submission.choices.add(choice)

    submission.save()
    return HttpResponseRedirect(reverse('onlinecourse:exam_result', args=(course.id, submission.id)))


# -------------------------------------------------------------
# Show exam result view
# -------------------------------------------------------------
def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    # Extract all selected choices IDs from this submission
    selected_ids = [choice.id for choice in submission.choices.all()]

    total_score = 0
    total_grade = 0

    for question in course.question_set.all():
        total_grade += question.grade
        if question.is_get_score(selected_ids):
            total_score += question.grade

    # Calculate percentage grade (avoid division by zero if course has no questions)
    grade = int((total_score / total_grade) * 100) if total_grade > 0 else 0

    context['course'] = course
    context['submission'] = submission
    context['selected_ids'] = selected_ids
    context['grade'] = grade

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
