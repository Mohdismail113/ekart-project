from django.shortcuts import render, HttpResponse,redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import Product, Cart,Order
from django.db.models import Q
import random
from django.shortcuts import redirect
import razorpay
from django.core.mail import send_mail
# Create your views here.

def about(request):
    return HttpResponse("This is About page")

def edit(request,rid):   # edit/3   ===>rid=3
    print("Id to be edited is:",rid)
    return HttpResponse("Id to be edited is "+ rid)

def delete(request,x1,x2):  #x1='10', x2='20'
    t=int(x1)+int(x2)   #t=10+20 =>30
    print(t)   #int
    return HttpResponse("Addition of xa and x2 is: "+ str(t))


class SimpleView(View):
    def get(self,request):
        return HttpResponse("Hello from view class")
    

#---------- estore project--------------
def home(request):
    context={}
    p=Product.objects.filter(is_active=True)
    # print(p)
    context['products']=p 
    return render(request,'index.html',context)

def about(request):
    return render(request,'about.html')

def search(request):
    query = request.GET.get('q', '').strip()
    context = {'query': query}

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(pdetails__icontains=query),
            is_active=True
        )
        context['products'] = products
    else:
        context['products'] = []

    return render(request, 'search_results.html', context)




def product_details(request,pid): 
    p=Product.objects.filter(id=pid)
    context={}
    context['products']=p
    return render(request,'product_details.html',context)

def register(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        context={}
        if uname=="" or upass=="" or ucpass=="":
            context['errmsg']="Fields cannot be Empty"
        elif upass != ucpass: 
            context['errmsg']="Password & confirm password didn't match"
        else:
            try:
                u=User.objects.create(password=upass,username=uname,email=uname)
                u.set_password(upass)
                u.save()
                context['success']="User Created Successfully, Please Login"
            except Exception:
                context['errmsg']="User with same username already exists!!!!"
        
        return render(request,'register.html',context)
    else:
        return render(request,'register.html')
    
def user_login(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        context={}
        if uname=="" or upass=="":
            context['errmsg']="Fields cannot be Empty"
            return render(request,'login.html',context)
        else:
            u=authenticate(username=uname,password=upass)
            if u is not None:
                login(request,u)
                return redirect('/')
            else:
                context['errmsg']="Invalid username and password"
                return render(request,'login.html',context)
            
    else:
        return render(request,'login.html')
    
def user_logout(request):
    logout(request)
    return redirect('/')

def catfilter(request,cv):  
    q1=Q(cat=cv)
    q2=Q(is_active=True)
    p=Product.objects.filter(q1&q2)
    print(p)
    context={}
    context['products']=p   
    return render(request,'index.html',context)

def sort(request,sv):
    if sv=='0':
        col='price'
    else:
        col='-price'
    p=Product.objects.order_by(col)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def range(request):
    min=request.GET['min']
    max=request.GET['max']
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=Product.objects.filter(q1&q2&q3)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def addtocart(request,pid):
    if request.user.is_authenticated:
        userid=request.user.id
        u=User.objects.filter(id=userid) 
        p=Product.objects.filter(id=pid) 

        q1=Q(uid=u[0])
        q2=Q(pid=p[0])
        c=Cart.objects.filter(q1 & q2) 
        n=len(c)   # 1
        context={}
        if n == 1: 
            context['msg']="Product Already Exist in cart!!"
        else:
            c=Cart.objects.create(uid=u[0],pid=p[0])
            c.save()
            context['success']="Product Added Successfully to Cart!!"
        context['products']=p
        return render(request,'product_details.html',context)
    else:
        return redirect('/login')
    
def viewcart(request):
    c=Cart.objects.filter(uid=request.user.id)   
    np=len(c)    
    s=0
    for x in c:
        s=s + x.pid.price * x.qty
    print(s)
    context={}
    context['data']=c
    context['total']=s
    context['n']=np
    return render(request,'cart.html',context)

def remove(request,cid):
    c=Cart.objects.filter(id=cid) 
    
    c.delete()
    return redirect('/viewcart')

def updateqty(request,qv,cid):
    c=Cart.objects.filter(id=cid)
    print(c)
    print(c[0])
    print(c[0].qty)
    if qv=='1':
        t=c[0].qty + 1
        c.update(qty=t)
    else:
        if c[0].qty>1:
            t=c[0].qty - 1
            c.update(qty=t)
    return redirect('/viewcart')

def placeorder(request):
    userid=request.user.id
    c=Cart.objects.filter(uid=userid) 
    oid=random.randrange(1000,9999)
    for x in c:
        o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()
        x.delete()  
    context={}
    orders=Order.objects.filter(uid=request.user.id)
    np=len(orders) #2
    context['data']=orders
    context['n']=np
    s=0
    for x in orders:
        s= s + x.pid.price * x.qty
    context['total']=s
    return render(request,'placeorder.html',context)

def makepayment(request):
    orders=Order.objects.filter(uid=request.user.id)
    s=0
    for x in orders:
        s= s + x.pid.price * x.qty
        oid=x.order_id  
    client = razorpay.Client(auth=("rzp_test_zE7fJnXA4ipvvS", "RugUl4kibyHtfZsxSjtna8xy"))
    data = { "amount": s*100, "currency": "INR", "receipt": oid }
    payment = client.order.create(data=data)
    print(payment)
    context={}
    context['data']=payment
    uemail=request.user.email
    print(uemail)
    context['uemail']=uemail
    return render(request,'pay.html',context)



def sendusermail(request,uemail):
    # print(uemail)
    msg="Order detail are:---"
    send_mail(
        "Ekart-Order placed successfully",
        msg,
        "aleemshoeb3@gmail.com", 
        [uemail],  
        fail_silently=False,
    )
    return render(request,'index.html')