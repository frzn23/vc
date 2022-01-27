from email import message
from django import http
from django.shortcuts import redirect, render
from django.http import HttpResponse, request
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls.conf import path
from home.models import Services, Order, dry_clean_services, deleted_orders
from django.contrib import messages
from datetime import datetime
import smtplib
from email.message import EmailMessage
import pytz
from twilio.rest import Client
import random
import requests


def send_mail(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "farzeen7999ghaus@gmail.com"
    msg['from'] = user
    password = "bjhpnnpmvhwjscgd"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)

    server.send_message(msg)
    server.quit()



# Create your views here.
def index(request):


    service = Services.objects.filter(pr="true")
    params = {'service':service}

    return render(request,'home/home.html', params)

def about(request):
    return render(request, 'home/about.html')

def order(request):
    service = Services.objects.filter(pr="true")
    params = {'service':service}
    return render(request, 'home/pricing.html', params)

def contact(request):
    if request.method=="POST":
        name = request.POST.get('name','')
        phone = request.POST.get('phone','')
        email = request.POST.get('email','No email provided')
        content = request.POST.get('msg','')
        mail_content = f"Name - {name} | Phone - {phone} | Email - {email} | Message - {content}"
        send_mail("Query Recieved For HANZO",mail_content,"farzeenghaus23@gmail.com")
        messages.success(request,"Your Query Has Reached Us And We Will Be In Touch Shortly")
        return render(request, "home/contact.html")

    return render(request, "home/contact.html")



def dry_clean(request):
    
    

    allProds = []
    catprods = dry_clean_services.objects.values('s_parent', 's_no')
    cats = {item['s_parent'] for item in catprods}
    for cat in cats:
        prod = dry_clean_services.objects.filter(s_parent=cat)
        allProds.append(prod)

    params = {'allProds':allProds}
    return render(request, 'home/dry_clean.html', params)

def dc(request):
    if request.method=="POST":
        name = request.POST.get('name', '')
        phone = request.POST.get('phone','')
        flat = request.POST.get('flat', '')
        floor = request.POST.get('floor', '')
        location = request.POST.get('location', '')
        landmark = request.POST.get('landmark','')
        # service = Services.objects.filter(s_no=id)[0]
        service = request.POST.get('order_info','')
        price = request.POST.get('order_price','') # to be used while sending msgs
        address = f"{flat}, {floor} Floor, {location}, Near {landmark}"

        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        timing = now.strftime("%d/%m/%Y %I:%M %p")
        

        try:

            if len(phone)!=10:
                messages.error(request, "Order Not Placed. Your Phone Number Should be 10 digits")
    
            else:
                
                # params = {'name':name, 'phone':phone, 'service':service, 'address':address, 'now':now}
                order = Order(name=name, phone=phone, order_name=service, address=address, timing=timing, status="Order Placed", f_stat=0, comment="")
                order.save()
            
                
                msg_for_client = f"Thank You {name} for placing the order of {service}. Our executives will reach you within 20 minutes. Track your order at hanzo.co.in/track using Track ID - {order.order_id}"     
                msg_us = f"Order Recieved of {service}. Name- {name}, Phone-{phone}, address - {address}, ID- {order.order_id}"
                msg_us = msg_us.replace("&","And")
                to_client =f"+91{phone}"
                to_us = ['+919874368148','+917678117021','+918750850454']
                
                # account_sid = "AC956c0481a1259cf06686130dce2679df"
                # auth_token  = "b168342293e80d3a0c7bfcf04f574ea5"
                
                # client = Client(account_sid, auth_token)
                # message = client.messages.create(
                #     to=to_client, 
                #     from_="+17067603908",
                #     body=msg_for_client)
                    
                    
                url_link = f"https://api.telegram.org/bot5024072839:AAFNSeUF9cZXiB3DPlwoKbiNgNo8-c8xD_c/sendMessage?chat_id=-721344690&text={msg_us}"
                # for i in to_us:
                #     message = client.messages.create(
                #         to=i, 
                #         from_="+17067603908",
                #         body=msg_us)

                for i in range(3):
                    requests.get(url_link)
                        
                messages.success(request,f"Your Order Has Been Placed. <br> &darr; <br>   Our executives will pick your clothes within 20 Minutes.  <br> &darr; <br>    You Can Track It Using Track ID - {order.order_id}")




        except Exception as e:
            messages.error(request, "Sorry For The Inconvinence but your order could not be placed. Please Check Your Phone number and try again")            


    return render(request, 'home/dc_form.html')



def feedback(request, id):
    order_list = list(Order.objects.filter(order_id=id, f_stat=0))
    if len(order_list) !=0:
    
        if request.method=="POST":
            change_order = Order.objects.get(order_id=id)
            msg = request.POST.get('feedback', '')
            mail_content = f"Feedback -->  {msg} Feedback Sent by order no -{id}"
            change_order.f_stat = 1
            change_order.save()
            send_mail("Feedback Recieved For HANZO",mail_content,"farzeenghaus23@gmail.com")
            messages.success(request,"Thanks for your feedback, It means a lot to us. We will keep your opinion in our minds")
            return redirect("/")

        return render(request, "home/feedback.html")
    
    else:
        return redirect('/')


def order_info(request, id):
    
    if request.method=="POST":
        name = request.POST.get('name', '')
        phone = request.POST.get('phone','')
        flat = request.POST.get('flat', '')
        floor = request.POST.get('floor', '')
        location = request.POST.get('location', '')
        landmark = request.POST.get('landmark','')
        iron_need = request.POST.get('iron_needed','off')
        service = Services.objects.filter(s_no=id)[0]
        address = f"{flat}, {floor} Floor, {location}, Near {landmark}"

        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        timing = now.strftime("%d/%m/%Y %I:%M %p")
        

        try:

            if len(phone)!=10:
                messages.error(request, "Order Not Placed. Your Phone Number Should be 10 digits. Please Try Again")
                return redirect(f'/place-order-phone/{id}')
    
            else:
                
                # params = {'name':name, 'phone':phone, 'service':service, 'address':address, 'now':now}
                order = Order(name=name, phone=phone, order_name=service, address=address, timing=timing, status="Order Placed", f_stat=0, comment="")
                order.save()
                
                if iron_need=="on":
                    msg_for_client = f"Thank You {name} for placing the order of {service} and ironing of some clothes. Our executives will reach you within 20 minutes. Track your order at hanzo.co.in/track using Track ID - {order.order_id}"     
                    msg_us = f"Order Recieved of {service}+Ironing some clothes. Name- {name}, Phone-{phone}, address - {address}, order id - {order.order_id}"
                else:
                    msg_for_client = f"Thank You {name} for placing the order of {service}. Our executives will reach you within 20 minutes. Track your order at hanzo.co.in/track using Track ID - {order.order_id}"     
                    msg_us = f"Order Recieved of {service} Name- {name}, Phone-{phone}, address - {address}, order id - {order.order_id}"
                                    
                msg_us = msg_us.replace("&","And")
                to_client =f"+91{phone}"
                to_us = ['+919874368148','+917678117021','+918750850454']

                # account_sid = "AC956c0481a1259cf06686130dce2679df"
                # auth_token  = "b168342293e80d3a0c7bfcf04f574ea5"
                
                # client = Client(account_sid, auth_token)
                # message = client.messages.create(
                #     to=to_client, 
                #     from_="+17067603908",
                #     body=msg_for_client)
                    
                url_link = f"https://api.telegram.org/bot5024072839:AAFNSeUF9cZXiB3DPlwoKbiNgNo8-c8xD_c/sendMessage?chat_id=-721344690&text={msg_us}"
                # for i in to_us:
                #     message = client.messages.create(
                #         to=i, 
                #         from_="+17067603908",
                #         body=msg_us)

                # for i in range(3):
                #     requests.get(url_link)

                messages.success(request,f"Your Order Has Been Placed. <br> &darr; <br>   Our executives will pick your clothes within 20 Minutes.  <br> &darr; <br>    You Can Track It Using Track ID - {order.order_id}")
                return redirect('signup')


        except Exception as e:
            messages.error(request, "Sorry For The Inconvinence but your order could not be placed. Please Check Your Phone number and try again")            



    if id==1 or id==2 or id==3 or id==4:
        try:
            phone_get = request.GET['p']
        except:
            phone_get = False
        print(phone_get)
        service = Services.objects.filter(s_no=id)
        if phone_get==False:
            params = {'id':id, 'service':service,'otp_sent':True}
        else:
            params = {'id':id, 'service':service,'otp_sent':True,'phone_get':phone_get}
        return render(request, "home/order_form.html", params)
    else:
        return redirect('/')


def take_phone(request, id):
    if request.method == "POST":
        phone_no = request.POST['phone']
        try:
            user_exists = User.objects.get(username=phone_no)
            return render(request, 'home/take_pass.html', {'auth':True, 'phone':phone_no})

        except User.DoesNotExist:
            service = Services.objects.filter(s_no=id)
            params = {'id':id, 'service':service,'otp_sent':True}
            page_change = f'/place-order/{id}?p={phone_no}'
            # return render(request, page_change, params)
            return redirect(page_change)

    if id==1 or id==2 or id==3:
        service = Services.objects.filter(s_no=id)
        params = {'id':id, 'service':service,'otp_sent':True}
        return render(request, "home/phone.html", params)
    else:
        return redirect('/')



def new_pass(request):
    return render(request, 'home/order_pass.html')


def take_pass(request):
    if request.method=="POST":
        user_name = request.POST['phone']
        password = request.POST['password']
        user = authenticate(username=user_name, password=password)
        if user is not None:
            login(request, user)
            return redirect('/place-auth/1')
        else:
            return render(request, "home/take_pass.html", {'phone':user_name, "no_user":True})
    return render(request, 'home/take_pass.html')

def signup(request):
    pass

def track(request):

    if request.method=="POST":
        id = request.POST.get('id','')
        phone = request.POST.get('phone','')

        if len(phone) != 10:
            msg="Invalid Phone No, Enter Phone No. With 10 Digits And Try Again"
            params={'msg':msg}
            return render(request, 'home/track.html', params)
        
        else:
            order = Order.objects.filter(order_id=id,phone=phone)
            if len(order) != 0:
                stat = order[0].status
                stat = stat.split(',')
                time = order[0].timing
                time = time.split(',')
                mylist=zip(stat,time)
                params={'order':order,'mylist':mylist}
                return render(request, 'home/track.html',params)
            
            else:
                msg = "Wrong Track Id / Phone No, Please Check And Try Again"
                params = {'msg':msg}
                return render(request, 'home/track.html', params)

    else:
        return render(request, 'home/track.html')



def cancel(request):
    if request.method=="POST":
        id = request.POST.get('id','')
        phone = request.POST.get('phone','')

        if len(phone) != 10:
            msg="Invalid Phone No, Enter Phone No. With 10 Digits And Try Again"
            params={'msg':msg}
            return render(request, 'home/cancel.html', params)
        
        else:
            order = Order.objects.filter(order_id=id,phone=phone)
            if len(order) != 0:
                if "Laundry" not in order[0].status:
                    or_id = order[0].order_id
                    name = order[0].name
                    phone = order[0].phone
                    order_name = order[0].name
                    address = order[0].address
                    query = deleted_orders(original_id=or_id, name=name, phone=phone, order_name=order_name, address=address)
                    query.save()
                    order.delete()
                    messages.success(request,"We Are Sorry To See You Go. Your Order Has Been Cancelled.")
                    # return render(request, 'home/home.html')
                    return redirect('/')
                else:
                    msg = "Your Order Is Being Washed In The Laundry Or is already Delivered, You cannot cancel it now"
                    params = {'msg':msg}
                    return render(request, 'home/cancel.html',params)

            
            else:
                msg = "Wrong Track Id / Phone No, Please Check And Try Again"
                params = {'msg':msg}
                return render(request, 'home/cancel.html', params)

    else:
        return render(request, 'home/cancel.html')



