from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import LoginForm
from firebase_admin import firestore
from datetime import datetime 
import firebase_admin
from firebase_admin import credentials, db 
from googletrans import Translator
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://geospeak-b0974-default-rtdb.firebaseio.com/' 
})





def home(request):
    if request.session.get('email') is not None:
       source_lang = request.session.get('source')  
       target_lang = request.session.get('target')
    
       context = {
        'source_lang': source_lang,
        'target_lang': target_lang,
       }
       return render(request, 'main/home.html', context)
    else:
       return render(request, 'main/translate2.html')

   

def index(request):
    return render(request, 'main/index.html')

def detect_lang(request):
    text = request.GET.get('text', '')
    trans = Translator()
    detect = trans.detect(text)
    return JsonResponse({'language': detect.lang})


def translate_text(request):
    text = request.GET.get('text', '')
    target_language = request.GET.get('target_language', 'en')

    translator = Translator()
    translated = translator.translate(text, dest=target_language).text
   
    if request.session.get('email') is not None:
       current_time = datetime.now().isoformat()
       userid=request.session.get('user_id')
       ref = db.reference('History')
       ref.push({
        'User_id': userid,  
        'prompt': text,
        'Target_Language': target_language, 
        'Result': translated,  
        'createdAt': current_time,
        
       })

    return JsonResponse({'translated_text': translated})

def signup_create(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        source = request.POST.get('source')
        target = request.POST.get('target')
        # Name = request.POST.get('Name')
        current_time = datetime.now().isoformat()
    

        ref = db.reference('Users')
        useremail = ref.order_by_child('email').equal_to(email).get()
        if useremail:
            message = "Already exist "
            return render(request, 'main/signup.html', {'message': message})   
        ref.push({
          'email': email,
          'password': password, 
          'source': source,  
          'target': target,   
          'createdAt': current_time,  
        })

        return redirect('login')
    return render(request, 'main/signup.html')


def profile(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        source = request.POST.get('source')
        target = request.POST.get('target')
        current_time = datetime.now().isoformat()
        userid=request.session.get('user_id')

        ref = db.reference('Users')
        user_data = ref.child(userid).get()
        
        if not user_data:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # useremail = ref.order_by_child('email').equal_to(email).get()
        # if useremail:
        #    return JsonResponse({'error': 'already exist'}, status=400)   
       
          
        ref.child(userid).update({
            'email':email,
            'password': password,  
            'source': source,
            'target': target,
            'updatedAt': current_time,  
        })

        request.session['source'] = source
        request.session['target'] = target
        return redirect('home')
    
    else:
        userid = request.session.get('user_id')

        if not userid:
            return render(request, 'main/login.html', {'error': 'User not logged in'})

        ref = db.reference('Users')
        user_data = ref.child(userid).get()
        
       
     
        print(f"User Context: {user_data}") 

        return render(request, 'main/profile.html', {'user_data': user_data})


def login_view(request):
    if request.session.get('email') is not None:
         return render(request, 'main/home.html')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        ref = db.reference('Users')
        userdata = ref.order_by_child('email').equal_to(email).get()
        if userdata:
            user_id=list(userdata.keys())[0]
            userinfo=userdata[user_id]
            if userinfo['password']==password:
               request.session['user_id']=user_id
               request.session['email'] = userinfo['email']
               request.session['source'] = userinfo['source']
               request.session['target'] = userinfo['target']
               request.session.save()
               return redirect('home')
            else:
                message = "Invalid credential. Please try again."
                return render(request, 'main/login.html', {'message': message})     
        else:
            message = "Invalid credential. Please try again."
            return render(request, 'main/login.html', {'message': message})
        
    
    return render(request, 'main/login.html')


# Logout Function
def logout(request):
   request.session.flush()
   return redirect('login')



def history_view(request):
    userid=request.session.get('user_id')
    ref=db.reference('History')
    history=ref.order_by_child('User_id').equal_to(userid).get()
    # user_ref = db.reference('Users')
    # user = user_ref.child(userid).get()
    # user_name = user.get('name') if user else None
    if history:
       print('Data Does Not Exist')
       context={'history':history,}
    else:
       print('Data Does Not Exist')
       context={'history':None}    
    return render(request, 'main/history.html',context)