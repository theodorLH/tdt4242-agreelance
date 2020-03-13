from django.http import HttpResponse
from projects.models import ProjectCategory
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import SignUpForm

def index(request):
    return render(request, 'base.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()

            user.profile.company = form.cleaned_data.get('company')

            user.is_active = False
            user.profile.categories.add(*form.cleaned_data['categories'])
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            from django.contrib import messages
            messages.success(request, 'Your account has been created and is awaiting verification.')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'user/signup.html', {'form': form})


#def getFormInput():



@login_required
def profile(request):
    #old_user = request.user
    old_user = request.user
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        #newForm = SignUpForm2(request.POST)   #nødvendig?
        if form.is_valid():
           
           #Dette jeg prøver på nå, at hele form-et skal endres, ikke bare enkelt fields

            new_user = form.save()
            old_user = models.update_user_profile(old_user, new_user,created, **kwargs)






            #---------------------------------------------------------------
            #Her skal logikken være riktig. Her har jeg valgt bare noen fields som skal ta inn verdi og kunne byttes, ikke alle som var i sign-up. 
            #Her tar hver variabel/field inn en ny verdi og "cleaner" den forrige verdien. Deretter skal den nye verdien lagres. 2 setninger per field. Problemet her er save().
            #Hvis save() fikses for integer verdier så er vi ferdig. Da kan vi kjøre samme logikk for alle mulige fields, men kan også bare ta med de under. Jeg får ikke fikset save()


            #.save() kalles på user objektet etter at du er ferdig med å sette parameterene. Se her for mer informasjon:  https://docs.djangoproject.com/en/3.0/topics/forms/modelforms/#the-save-method
            
            #user.profile.first_name = form.cleaned_data.get('first_name') #hnavnet til feltet i forms.py 
            #user.profile.first_name.save()
            #user.profile.last_name = form.cleaned_data.get('last_name')
            #user.profile.last_name.save()
            #user.profile.email = form.cleaned_data.get('email')
            #user.profile.email.save()
            #user.profile.email_confirmation = form.cleaned_data.get('email_confirmation')
            #user.profile.email_confirmation.save()
            #user.profile.city = form.cleaned_data.get('city')
            #user.profile.city.save()
            #user.profile.postal_code = form.cleaned_data.get('postal_code')
            #user.profile.postal_code.save()

            #---------------------------------------------------------------
            #Alternativ versjon av over:

            #data = request.POST.copy()
            #data['username'] = form.cleaned_data.get('username')
            #new_form = SignUpForm(data) 
            #if new_form.is_valid():
                #new_form.save() 


            #----------------------------------------------------------------
            #Skaper bare en ny bruker:
            
            
            #user = form.save()
            #user.refresh_from_db()

            #user.profile.company = form.cleaned_data.get('company')

            #user.is_active = True
            #user.profile.categories.add(*form.cleaned_data['categories'])
            #user.save()
            #raw_password = form.cleaned_data.get('password1')
            #user = authenticate(username=user.username, password=raw_password)
            #old_user = user


            #------------------------------------------------------------------------
            
            
            #user.save()
        
            from django.contrib import messages
            messages.success(request, 'Your account information has been updated')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'user/profile.html', {'form': form})
    