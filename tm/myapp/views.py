from django.shortcuts import render, redirect, reverse
from .models import Users, Task
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import random
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def welcome(request):
    return render(request, 'welcomePage.html')



# Signup page view
def signupPage(request):
    return render(request, "signupPage.html",{'otp_range': range(4)})

def home(request):
    email = request.session.get('email')

    if not email:
        return redirect('myapp:login')

def logout_view(request):
    request.session.flush()
    return redirect('myapp:login')



# Signup logic
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        otp_digits = []
        
        # Collect OTP digits from the form
        for i in range(4):
            otp_digit = request.POST.get(f'otp_digit_{i}')
            if otp_digit:  # Ensure the OTP digit exists
                otp_digits.append(otp_digit)
            else:
                otp_digits.append('')  # Empty string if OTP digit is missing
        
        # Join OTP digits into a single string
        otp = ''.join(otp_digits)
        print(f"Entered OTP: {otp}")
        
        print(username, otp, email)
        
        # Get the OTP stored in session
        session_otp = request.session.get('otp', '')
        print(f"Session OTP: {session_otp}")
        
        if email and username and password and otp == session_otp:
            print('OTP checked')
            try:
                user = Users.objects.get(email=email)
                pop = {'note': 'Email already exists'}
                return render(request, 'signupPage.html', pop)
            except Users.DoesNotExist:
                # Create new user
                user = Users(user_name=username, email=email, password=password)
                print('User added')
                user.save()
                return render(request, 'login.html', {'note': 'User created successfully'})
        else:
            pop = {'note': 'Invalid OTP or missing fields'}
            return render(request, 'signupPage.html', pop)






def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        username = request.POST.get('username', '')

        if email and username:
            try:
                # Validate email format
                validate_email(email)
            except ValidationError:
                return JsonResponse({'status': 'error', 'message': 'Invalid email format'})

            otp = str(random.randint(1000, 9999))
            print(f"Generated OTP: {otp}")
            request.session['otp'] = otp  # Store OTP in session

            subject = "Your OTP Code"
            message = f"Your OTP code is: {otp}\n\nPlease use this code to proceed. It is valid for 10 minutes."

            try:
                send_mail(
                    subject,
                    message,
                    "kingprincepriyanshu1138@gmail.com",
                    [email],  # Recipient email
                    fail_silently=False,
                )
                return JsonResponse({'status': 'success', 'message': 'OTP sent successfully!'})
            except Exception as e:
                print(e)
                return JsonResponse({'status': 'error', 'message': 'Failed to send OTP.'})

        return JsonResponse({'status': 'error', 'message': 'Email and username required.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})




def loginPage(request):
    return render(request, 'login.html')
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if email and password:
            try:
                user = Users.objects.get(email=email)
                if password == user.password:
                    request.session['email'] = user.email
                    tasks = Task.objects.filter(owner=user)

                    return render(request, 'home.html', {
                        'user': user,
                        'tasks': tasks,
                        'current_page': 'table.html'  # ✅ required for {% include %}
                    })
                else:
                    return render(request, 'login.html', {'note': 'Invalid email or password'})
            except Users.DoesNotExist:
                return render(request, 'login.html', {'note': 'Invalid email or password'})
        else:
            return render(request, 'login.html', {'note': 'Please fill in all fields'})

    return render(request, 'login.html')



from django.shortcuts import redirect
from .models import Users, Task

def addTask(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        due_date = request.POST.get('due_date', '').strip()
        email = request.session.get('email')

        if not email:
            return redirect('myapp:login')

        user = Users.objects.get(email=email)

        if title:
            Task.objects.create(
                title=title,
                description=description,
                due_date=due_date if due_date else None,
                owner=user
            )
            return redirect('myapp:table')  # ✅ Use a GET-view after POST
        else:
            # Optionally save error in session or use messages framework
            return redirect('myapp:table')  # Still redirect to prevent form re-submit

    return redirect('myapp:table')



from datetime import datetime
from datetime import datetime
from django.shortcuts import redirect, render
from .models import Users, Task

def editTask(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id', '').strip()
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        due_date_str = request.POST.get('due_date', '').strip()

        email = request.session.get('email')
        if not email:
            return redirect('myapp:login')

        try:
            user = Users.objects.get(email=email)
            task = Task.objects.get(id=task_id, owner=user)

            task.title = title
            task.description = description

            if due_date_str:
                task.due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M")
            else:
                task.due_date = None

            task.save()

            return redirect('myapp:table')  # ✅ Avoid duplicate resubmission
        except (Users.DoesNotExist, Task.DoesNotExist):
            return redirect('myapp:table')  # Or a custom error page

    return redirect('myapp:table')




from django.views.decorators.csrf import csrf_protect

@csrf_protect
def deleteTask(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id', '').strip()

        email = request.session.get('email')
        if not email:
            return redirect('login')
        total_tasks = Task.objects.filter(owner__email=email).count()

        try:
            user = Users.objects.get(email=email)
            task = Task.objects.get(id=task_id, owner=user)
            task.delete()
            return render(request, 'home.html' , {'note': 'Task deleted successfully', 'tasks': Task.objects.filter(owner=user),"user": user,'current_page': 'table.html'})
        except (Users.DoesNotExist, Task.DoesNotExist):
            return render(request, 'home.html', {'note': 'Task not found or unauthorized'})

    return redirect('home')

from django.shortcuts import redirect
from .models import Users, Task

def toggleTaskCompletion(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id', '').strip()

        email = request.session.get('email')
        if not email:
            return redirect('myapp:login')

        try:
            user = Users.objects.get(email=email)
            task = Task.objects.get(id=task_id, owner=user)
            task.completed = not task.completed
            task.save()

            return redirect('myapp:table')  # ✅ Prevents duplicate toggle on reload
        except (Users.DoesNotExist, Task.DoesNotExist):
            return redirect('myapp:table')  # You can add an error message using messages framework if needed

    return redirect('myapp:table')



def get_task_data(request):
    email = request.session.get('email')
    if not email:
        return redirect('myapp:login')

    user = Users.objects.get(email=email)
    tasks = Task.objects.filter(owner=user)

    completed_count = tasks.filter(completed=True).count()
    pending_count = tasks.filter(completed=False).count()
    total_tasks = tasks.count()

    task_data = {
        'completed_count': completed_count,
        'pending_count': pending_count,
        'total_tasks': total_tasks,
    }
    print(f"Task Data: {task_data}")

    return JsonResponse({'task_data': task_data})

def table_view(request):
    email = request.session.get('email')
    if not email:
        return redirect('myapp:login')

    user = Users.objects.get(email=email)
    tasks = Task.objects.filter(owner=user)

    return render(request, 'home.html', {
        'tasks': tasks,
        'user': user,
        'current_page': 'table.html'  # path to the inner content
    })

def discription_view(request):
    email = request.session.get('email')
    if not email:
        return redirect('myapp:login')

    user = Users.objects.get(email=email)
    tasks = Task.objects.filter(owner=user)

    return render(request, 'home.html', {
        'tasks': tasks,
        'user': user,
        'current_page': 'dec.html'  # path to the inner content
    })


from django.shortcuts import render, redirect
from .models import Users, Task
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def stat(request):
    email = request.session.get('email')
    if not email:
        return redirect('myapp:login')

    user = Users.objects.get(email=email)
    tasks = Task.objects.filter(owner=user)

    completed = tasks.filter(completed=True).count()
    pending = tasks.filter(completed=False).count()
    total = tasks.count()

    # Bar Chart
    fig1, ax1 = plt.subplots(figsize=(4, 3))
    ax1.bar(['Completed', 'Pending'], [completed, pending], color=['#22c55e', '#facc15'])
    ax1.set_title('Tasks Status')
    ax1.set_ylabel('Count')
    bar_buffer = BytesIO()
    plt.tight_layout()
    fig1.savefig(bar_buffer, format='png', bbox_inches='tight', transparent=True)
    bar_buffer.seek(0)
    bar_chart_url = 'data:image/png;base64,' + base64.b64encode(bar_buffer.getvalue()).decode('utf-8')
    bar_buffer.close()
    plt.close(fig1)

    # Donut Chart
    fig2, ax2 = plt.subplots(figsize=(4, 4))
    if total == 0:
        # ONLY 2 VALUES RETURNED WHEN autopct IS NOT SET
        wedges, texts = ax2.pie(
            [1],
            labels=['No Tasks'],
            colors=['#cbd5e1'],
            startangle=90
        )
    else:
        wedges, texts, autotexts = ax2.pie(
            [completed, pending],
            labels=['Completed', 'Pending'],
            autopct='%1.1f%%',
            startangle=90,
            colors=['#22c55e', '#facc15']
        )

    centre_circle = plt.Circle((0, 0), 0.60, fc='white')
    fig2.gca().add_artist(centre_circle)
    ax2.axis('equal')
    donut_buffer = BytesIO()
    fig2.savefig(donut_buffer, format='png', bbox_inches='tight', transparent=True)
    donut_buffer.seek(0)
    donut_chart_url = 'data:image/png;base64,' + base64.b64encode(donut_buffer.getvalue()).decode('utf-8')
    donut_buffer.close()
    plt.close(fig2)

    return render(request, 'home.html', {
        'user': user,
        'task_data': {
            'completed_count': completed,
            'pending_count': pending,
            'total_tasks': total
        },
        'bar_chart_url': bar_chart_url,
        'donut_chart_url': donut_chart_url,
        'current_page': 'stat.html'
    })
