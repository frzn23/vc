from email import message
from django import http
from django.shortcuts import redirect, render
from django.http import HttpResponse, request
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls.conf import path
from home.models import Services,Cred, Order, dry_clean_services, deleted_orders
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



def dc(request):
    if request.method=="POST":
        if request.user.is_authenticated and request.user.last_name=='c':
            phone = request.user.username
            name = request.user.first_name
            last_order = Order.objects.filter(phone=phone).order_by('-order_id')[0]
            name = last_order.name
            service = request.POST.get('order_info','')
            address = last_order.address
            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)
            timing = now.strftime("%d/%m/%Y %I:%M %p")



        else:
            name = request.POST.get('name', '')
            phone = request.POST.get('phone','')
            phone = request.GET['p']
            if phone=="":
                phone = request.POST.get('phone','')
            flat = request.POST.get('flat', '')
            floor = request.POST.get('floor', '')
            location = request.POST.get('location', '')
            landmark = request.POST.get('landmark','')
            # service = Services.objects.filter(s_no=id)[0]
            service = request.POST.get('order_info','')
            price = request.POST.get('order_price','') # to be used while sending msgs
            address = f"{flat}, {floor} Floor, {location}, Near {landmark}"
            passw = request.POST.get('passw','')
            email = request.POST.get('email','')

            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)
            
            timing = now.strftime("%d/%m/%Y %I:%M %p")

            cred = Cred(name=name, phone=phone, key=passw)
            cred.save()


        try:

            if len(phone)!=10:
                messages.error(request, "Order Not Placed. Your Phone Number Should be 10 digits")
    
            else:

                order = Order(name=name, phone=phone, order_name=service, address=address, timing=timing, status="Order Placed", f_stat=0, comment="")
                order.save()
                
                msg_for_client = f"Thank You {name} for placing the order of {service}. Our executives will reach you within 20 minutes. Track your order at hanzo.co.in/track using Track ID - {order.order_id}"     
                msg_us = f"Order Recieved of {service}. Name- {name}, Phone-{phone}, address - {address}, ID- {order.order_id}"
                msg_us = msg_us.replace("&","And")
                to_client =f"+91{phone}"
                to_us = ['+919874368148','+917678117021','+918750850454']
                
                account_sid = "AC956c0481a1259cf06686130dce2679df"
                auth_token  = "507a5a4fdcee85e75caece9c3c489c65"
                
                # client = Client(account_sid, auth_token)
                # message = client.messages.create(
                #     to=to_client, 
                #     from_="+17067603908",
                #     body=msg_for_client)
                    
                    
                url_link = f"https://api.telegram.org/bot5024072839:AAFNSeUF9cZXiB3DPlwoKbiNgNo8-c8xD_c/sendMessage?chat_id=-721344690&text={msg_us}"
                

                requests.get(url_link)

                myuser = User.objects.create_user(phone, email, passw)
                myuser.first_name= name
                myuser.last_name= 'c'
                myuser.save()
                params = {'user_created':True}
                user = authenticate(username = phone, password = passw)

                if user is not None:
                    login(request, user)
                    messages.success(request,f"Your Order Has Been Placed. <br> &darr; <br>   Our executives will pick your clothes within 20 Minutes.  <br> &darr; <br>    You Can Track It Using Track ID - {order.order_id}")
                    return redirect("/panel")
                    
                else:
                    messages.error(request, "Some error has occured in the server, we are trying to fix it. Please try again in few hours")
                    return redirect("/dry-clean")

                    
        except Exception as e:
            messages.success(request,f"Your Order Has Been Placed. <br> &darr; <br>   Our executives will pick your clothes within 20 Minutes.  <br> &darr; <br>    You Can Track It Using Track ID - {order.order_id}")
            return redirect("/panel")

    if request.user.is_authenticated and request.user.last_name=='c':
        phone = request.user.username
        name = request.user.first_name
        last_order = Order.objects.filter(phone=phone).order_by('-order_id')[0]
        params = {'address':last_order.address}
        return render(request, 'home/dc_form.html',params)

    else:
        
        try:
            phone_get = request.GET['p']
        except:
            phone_get = False
        
        if phone_get==False:
            no_phone_page = '/place-order-phone/3'
            return redirect(no_phone_page)
        else:
            params = {'id':id,'phone_get':phone_get}
        return render(request, "home/dc_form.html", params)
        



def order_info(request, id):
    
    if request.method=="POST":
        name = request.POST.get('name', '')
        phone = request.POST.get('phone','')
        phone = request.GET['p']
        if phone=="":
            phone = request.POST.get('phone','')
        
        flat = request.POST.get('flat', '')
        floor = request.POST.get('floor', '')
        location = request.POST.get('location', '')
        landmark = request.POST.get('landmark','')
        address = f"{flat}, {floor} Floor, {location}, Near {landmark}"
        iron_need = request.POST.get('iron_needed','off')
        service = Services.objects.filter(s_no=id)[0]
        passw = request.POST.get('passw','')
        email = request.POST.get('email','')
        code = request.POST.get('code','-')

        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        timing = now.strftime("%d/%m/%Y %I:%M %p")
        


        try:

            if len(phone)!=10:
                messages.error(request, "Order Not Placed. Your Phone Number Should be 10 digits. Please Try Again")
                return redirect(f'/place-order-phone/{id}')
    
            else:
                
                # params = {'name':name, 'phone':phone, 'service':service, 'address':address, 'now':now}
                order = Order(name=name, phone=phone, order_name=service, address=address, timing=timing, status="Order Placed", f_stat=0, comment="", refer_code=code)
                order.save()
                cred = Cred(name=name, phone=phone, key=passw)
                cred.save()

                
                if iron_need=="on":
                    msg_for_client = f"Thank You {name} for placing the order of {service} and ironing of some clothes. Our executives will reach you within 20 minutes. Track your order at hanzo.co.in/track using Track ID - {order.order_id}"     
                    msg_us = f"Order Recieved of {service}+Ironing some clothes. Name- {name}, Phone-{phone}, address - {address}, order id - {order.order_id}"
                else:
                    msg_for_client = f"Thank You {name} for placing the order of {service}. Our executives will reach you within 20 minutes. Track your order at hanzo.co.in/track using Track ID - {order.order_id}"     
                    msg_us = f"Order Recieved of {service} Name- {name}, Phone-{phone}, address - {address}, order id - {order.order_id}"
                                    
                msg_us = msg_us.replace("&","And")
                to_client =f"+91{phone}"
                to_us = ['+919874368148','+917678117021','+918750850454']

                account_sid = "AC956c0481a1259cf06686130dce2679df"
                auth_token  = "507a5a4fdcee85e75caece9c3c489c65"
                
                # client = Client(account_sid, auth_token)
                # message = client.messages.create(
                #     to=to_client, 
                #     from_="+17067603908",
                #     body=msg_for_client)

                url_link = f"https://api.telegram.org/bot5024072839:AAFNSeUF9cZXiB3DPlwoKbiNgNo8-c8xD_c/sendMessage?chat_id=-721344690&text={msg_us}"
                requests.get(url_link)



                # messages.success(request,f"Your Order Has Been Placed. <br> &darr; <br>   Our executives will pick your clothes within 20 Minutes.  <br> &darr; <br>    You Can Track It Using Track ID - {order.order_id}")

                myuser = User.objects.create_user(phone, email, passw)
                myuser.first_name= name
                myuser.last_name= 'c'
                myuser.save()
                params = {'user_created':True}
                user = authenticate(username = phone, password = passw)

                if user is not None:
                    login(request, user)
                    messages.success(request,f"Your Order Has Been Placed. <br> &darr; <br>   Our executives will pick your clothes within 20 Minutes.  <br> &darr; <br>    You Can Track It Using Track ID - {order.order_id}")
                    return redirect("/panel")
                    
                else:
                    messages.error(request, "Some error has occured in the server, we are trying to fix it. Please try again in few hours")
                    return redirect("/signup")



        except Exception as e:
            messages.success(request,f"Your Order Has Been Placed. <br> &darr; <br>   Our executives will pick your clothes within 20 Minutes.  <br> &darr; <br>    You Can Track It Using Track ID - {order.order_id}")



    if id==1 or id==2 or id==3 or id==4:
        if request.user.is_authenticated and request.user.last_name=='c':
            page = f"/panel#order{id}"
            return redirect(page)
        try:
            phone_get = request.GET['p']
        except:
            phone_get = False
        service = Services.objects.filter(s_no=id)
        if phone_get==False:
            params = {'id':id, 'service':service,'otp_sent':True}
            no_phone_page = f'/place-order-phone/{id}'
            return redirect(no_phone_page)
        else:
            params = {'id':id, 'service':service,'otp_sent':True,'phone_get':phone_get}
        return render(request, "home/order_form.html", params)
    else:
        return redirect('/')



def order_auth(request,id):
    if request.method=="POST":
        
        if id==1 or id==2:
            name=request.POST.get('name','')
            phone=request.POST.get('phone')
            service = Services.objects.filter(s_no=id)[0]
            address = request.POST.get('address','')
            iron_need = request.POST.get('iron_needed','off')
            service = Services.objects.filter(s_no=id)[0]
            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)
            timing = now.strftime("%d/%m/%Y %I:%M %p")
            
            # Retrieve Last Order Code
            last_order = Order.objects.filter(phone=phone).order_by("-order_id")[0]
            code = last_order.refer_code


            try:
                order = Order(name=name, phone=phone, order_name=service, address=address, timing=timing, status="Order Placed", f_stat=0, comment="",refer_code=code)
                order.save()
                
                if iron_need=="on":
                    msg_for_client = f"Thank You {name} for placing the order of {service} and ironing of some clothes. Our executives will reach you within 20 minutes. Track your order at hanzo.co.in/track using Track ID - {order.order_id}"     
                    msg_us = f"Order Recieved of {service}+Ironing some clothes. Name- {name}, Phone-{phone}, address - {address}, order id - {order.order_id}"
                else:
                    msg_for_client = f"Thank You {name} for placing the order of {service}. Our executives will reach you within 20 minutes. Track your order at hanzo.co.in/track using Track ID - {order.order_id}"     
                    msg_us = f"Order Recieved of {service} Name- {name}, Phone-{phone}, address - {address}, order id - {order.order_id}"
                                    
                msg_us = msg_us.replace("&","And")
                to_client =f"+91{phone}"

                account_sid = "AC956c0481a1259cf06686130dce2679df"
                auth_token  = "507a5a4fdcee85e75caece9c3c489c65"
                
                # client = Client(account_sid, auth_token)
                # message = client.messages.create(
                #     to=to_client, 
                #     from_="+17067603908",
                #     body=msg_for_client)
                    
                url_link = f"https://api.telegram.org/bot5024072839:AAFNSeUF9cZXiB3DPlwoKbiNgNo8-c8xD_c/sendMessage?chat_id=-721344690&text={msg_us}"
                requests.get(url_link)


                messages.success(request,f"Your Order Has Been Placed. <br> &darr; <br>   Our executives will pick your clothes within 20 Minutes.  <br> &darr; <br>    You Can Track It Using Track ID - {order.order_id}")
                return redirect('/panel')
            except Exception as e:
                messages.success(request,f"Your Order Has Been Placed. <br> &darr; <br>   Our executives will pick your clothes within 20 Minutes.  <br> &darr; <br>    You Can Track It Using Track ID - {order.order_id}")
                return redirect('/panel')
        else:
            return redirect('/panel')
    else:
        return redirect('/panel')



def take_phone(request, id):
    if request.user.is_authenticated and request.user.last_name=='c':
        if id==1:
            page_redirect="/panel#order1"
        if id==2:
            page_redirect="/panel#order2"
        if id==3:
            page_redirect="/dc"
        return redirect(page_redirect)
    if request.method == "POST":
        phone_no = request.POST['phone']
        try:
            user_exists = User.objects.get(username=phone_no)
            user = User.objects.get(username=phone_no)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            if id==1:
                page_redirect="/panel#order1"
            if id==2:
                page_redirect="/panel#order2"
            if id==3:
                page_redirect="/dc"
            
            return redirect(page_redirect)

            # return render(request, 'home/login/take_pass.html', {'auth':True, 'phone':phone_no})
        except User.DoesNotExist:
            service = Services.objects.filter(s_no=id)
            params = {'id':id, 'service':service,'otp_sent':True}
            page_change = f'/place-order/{id}?p={phone_no}'
            if id==3:
                page_change = f'/dc?p={phone_no}'

            return redirect(page_change)

    if id==1 or id==2 or id==3:
        service = Services.objects.filter(s_no=id)
        params = {'id':id, 'service':service,'otp_sent':True}
        return render(request, "home/login/phone.html", params)
    else:
        return redirect('/')



def take_pass(request):
    if request.user.is_authenticated and request.user.last_name=='c':
        return redirect('/panel')
    if request.method=="POST":
        phone = request.POST['phone']
        password = request.POST['password']
        current_url = request.POST['next_url']
        current_url_end = current_url[-1]
        if current_url_end=="1" or current_url_end=="2" or current_url_end=="3":
            page_change = f'/panel#order{current_url_end}'
        else:
            page_change = '/panel'
        user = authenticate(username = phone, password = password)

        if user is not None:
            login(request, user)
            # messages.success(request, "Logged In Successfully")
            return redirect(page_change)
        else:
            return render(request, 'home/login/take_pass.html',{'no_user':True,'phone':phone})

    return render(request, 'home/login/take_pass.html')


def my_order(request):
    if request.user.is_authenticated and request.user.last_name=='c':
        phone = request.user.username
        name = request.user.first_name
        orders = Order.objects.filter(phone=phone)
        params = {'phone':phone, 'name':name, 'orders':orders}
        return render(request, 'home/login/my_order.html',params)

    else:
        return redirect('/take_pass')


def panel(request):
    if request.user.is_authenticated and request.user.last_name=='c':
        phone = request.user.username
        name = request.user.first_name
        orders = Order.objects.filter(phone=phone).order_by('-order_id')
        service = Services.objects.filter(pr="true")
        total_order = len(orders)
        if total_order>=5:
            loop_range=5
        elif total_order<5:
            loop_range=total_order
        address = orders[0].address
        last_order=orders[0].order_name
        refer_code = orders[0].refer_code

        last_review=orders[0].laundry_review
        if last_review == "No review":
            if "Delivered" in orders[0].status:
                review = True
            else:
                review = False
        else:
            review=False

        stat = orders[0].status
        stat = stat.split(',')
        time = orders[0].timing
        time = time.split(',')
        mylist=zip(stat,time)
        params = {'phone':phone, 'name':name, 'orders':orders,'service':service,
         'address':address,'loop_range':loop_range,'last_order':last_order,
         'review':review,'order':order,'mylist':mylist, 'refer_code':refer_code}
        return render(request, 'home/login/panel.html',params)

    else:
        return redirect('/place-order-phone/1')

def send_otp(c_no, c_otp):

    account_sid = "AC956c0481a1259cf06686130dce2679df"
    auth_token  = "507a5a4fdcee85e75caece9c3c489c65"

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to=c_no, 
        from_="+17067603908",
        body=c_otp)


def change_pass(request):
    if request.method == "POST":
        status = request.POST.get('status')
        if status == "take":
            phone = request.POST.get('phone','')
            try:
                user_exists = User.objects.get(username=phone)
                otp = random.randint(1000,9999)
                otp_body = f"Your OTP for Hanzo Account Is {otp}. Please Login."
                send_otp(f"+91{phone}",otp_body)
                params = {'phone':phone, 'otp':otp, 'otp_true':True}
                return render(request, 'home/login/forget.html',params)

            except User.DoesNotExist:
                params = {'no_user':True}
                return render(request, 'home/login/forget.html',params)


        elif status == "give":
            phone = request.POST.get('phone_val','')
            otp_val = request.POST.get('otp_val','')
            otp_input = request.POST.get('otp_input','')
            if int(otp_val) == int(otp_input):
                user = User.objects.get(username=phone)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                return redirect(panel)         
            
            else:
                params = {'phone':phone, 'otp':otp_val, 'otp_true':True, 'otp_error':True}
                return render(request, 'home/login/forget.html',params)




    return render(request, 'home/login/forget.html')



def review_sep(request, id):
    
    if request.user.is_authenticated and request.user.last_name=='c':

        if request.method=="POST":
            delivery = int(request.POST.get("speed","4"))
            quality = int(request.POST.get("quality","4"))
            order = Order.objects.get(order_id=id)
            order.laundry_review = int(quality)
            order.delivery_review = int(delivery)
            order.save()
            review_text = f'Review Recieved For Order Id - {id}: Laundry - {quality} Stars. Delivery - {delivery} Stars.'
            url_link = f"https://api.telegram.org/bot5172631902:AAG9EUXR_WOF9SY07A36aUKI5lo88o1ZbTc/sendMessage?chat_id=-647444639&text={review_text}"
            requests.get(url_link)

            if delivery<4 and quality<4:
                messages.success(request,"We are sorry for your bad experience with Washing Quality & Delivery Speed. We will be in touch soon & we will compensate for your discomfort. Next time you order from Hanzo, you will recieve the best service.")

            elif delivery<4:
                messages.success(request,"We are sorry for your bad experience with delivery speed. We are already looking into the issue. Next time you order from Hanzo, you will recieve the best service.")
            elif quality<4:
                messages.success(request,"We are sorry for your bad experience with Washing Quality. We will be in touch soon & we will compensate for your discomfort. Next time you order from Hanzo, you will recieve the best service.")
            elif delivery>=4 and quality>=4:
                messages.success(request,"We are thankful for your good review, Please keep using Hanzo and we will be providing you with such luxury service at lowest cost.")
            return redirect('/panel')


        else:
            order_review_check = Order.objects.get(order_id=id).delivery_review
            if order_review_check=="No review":

                return render(request, 'home/login/review.html',{'id':id})
            else:
                return redirect('/panel')

    else:
        return redirect('/take_pass')


def log_out(request):
    logout(request)
    return redirect('/take_pass')



def take_review(request):
    if request.user.is_authenticated and request.user.last_name=='c':

        if request.method=="POST":
            delivery = int(request.POST.get("speed","4"))
            quality = int(request.POST.get("quality","4"))
            order_id = request.POST.get('review_id','')
            order = Order.objects.get(order_id=order_id)
            order.laundry_review = int(quality)
            order.delivery_review = int(delivery)
            order.save()
            
            review_text = f'Review Recieved For Order Id - {order_id}: Laundry - {quality} Stars. Delivery - {delivery} Stars.'
            url_link = f"https://api.telegram.org/bot5172631902:AAG9EUXR_WOF9SY07A36aUKI5lo88o1ZbTc/sendMessage?chat_id=-647444639&text={review_text}"
            requests.get(url_link)

            if delivery<4 and quality<4:
                messages.success(request,"We are sorry for your bad experience with Washing Quality & Delivery Speed. We will be in touch soon & we will compensate for your discomfort. Next time you order from Hanzo, you will recieve the best service.")

            elif delivery<4:
                messages.success(request,"We are sorry for your bad experience with delivery speed. We are already looking into the issue. Next time you order from Hanzo, you will recieve the best service.")
            elif quality<4:
                messages.success(request,"We are sorry for your bad experience with Washing Quality. We will be in touch soon & we will compensate for your discomfort. Next time you order from Hanzo, you will recieve the best service.")
            elif delivery>=4 and quality>=4:
                messages.success(request,"We are thankful for your good review, Please keep using Hanzo and we will be providing you with such luxury service at lowest cost.")
            return redirect('/panel')


        else:
            return redirect('/panel')
    else:
        return redirect('/take_pass')

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
