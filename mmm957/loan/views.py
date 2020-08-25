from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.urls import reverse
from django.views import generic
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from twilio.rest import Client
import string
import random
import re
import datetime

from .models import MyUser, Borrower, Borrowing_Message, Price, Employee, Lender, Paying, Ad_Contact, Ad


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'loan/index.html'
    context_object_name = 'ad_list'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context.update({
            'borrowing_message_list': Borrowing_Message.objects.order_by('-pub_time'),  # 依時間排序, 完成
            'lender_list': Lender.objects.order_by('-update_time'),  # 依時間排序, 新增最新更改時間欄位, 更改貼文時記得改變update_time, 完成
        })
        return context

    def get_queryset(self):
        # random傳回12個VIP廣告
        ids = []
        VIPs = User.objects.filter(groups__name='VIP')
        for VIP in VIPs:
            ids.append(VIP.myuser.lender.ad.pk)

        if len(ids) < 12:
            return Ad.objects.filter(pk__in=random.sample(ids, len(ids)))
        else:
            return Ad.objects.filter(pk__in=random.sample(ids, 12))

class RegisterBorrowerView(View):
    template_name = 'loan/borrower_register.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # register submit後直接加進user, myuser, Borrower or Lender, 驗證過後再更改Group(從unverified移到其他的, 頁面上的decorator要限制存取)
        pattern = r"[1-9]+[0-9]*"  # 檢測money是否為非0正整數
        phone = request.POST['phone']  # 需檢查電話格式, 是否有效(以驗證碼處理), 是否已被註冊, 完成
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        nickname = request.POST['nickname']
        money = request.POST['money']  # 僅限輸入數字
        region = request.POST['region']
        money_usage = request.POST['money_usage']

        message = ''
        if not re.match(r'09\d{8}', phone):
            message = '行動電話號碼格式錯誤'
        if User.objects.filter(username=phone):
            message = '此電話號碼已被註冊'
        # 若三次驗證都沒過，則需聯絡客服，未連絡客服者，一段時間把資料清掉?
        if not re.match(pattern, money):
            message = '借款金額須為數字或不得為0'
        if password1.strip() == "" or password2.strip() == "" or nickname.strip() == "" or money.strip() == "" or region.strip() == "" or money_usage.strip() == "":
            message = '所有欄位不得為空'
        if not message == '':
            return render(request, self.template_name, {'message': message})

        if password1 == password2:
            user = User.objects.create_user(username=phone, password=password1)
            group = Group.objects.get(name='unverified')
            user.groups.add(group)
            user.save()
            myUser = MyUser.objects.create(user=user, is_borrower=True)
            borrower = Borrower.objects.create(user=myUser, nickname=nickname)
            borrower.borrowing_message_set.create(money=money, region=region, money_usage=money_usage)
            login(request, user)
            return HttpResponseRedirect(reverse('loan:verify'))
        else:
            return render(request, self.template_name, {'message': '請檢查密碼是否相同'})

class RegisterLenderView(View):
    template_name = 'loan/lender_register.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        phone = request.POST['phone']  # 需檢查電話格式, 是否有效, 是否已被註冊, 完成
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        nickname = request.POST['nickname']
        line_id = request.POST['line_id']  # 檢查line_id是否有效
        highest_lending = request.POST['highest_lending']
        region = request.POST['region']
        lending_way = request.POST['lending_way']
        lending_title = request.POST['lending_title']
        lending_content = request.POST['lending_content']

        message = ''
        if not re.match(r'09\d{8}', phone):
            message = '行動電話號碼格式錯誤'
        if User.objects.filter(username=phone):
            message = '此電話號碼已被註冊'
        if password1.strip() == "" or password2.strip() == "" or nickname.strip() == "" or highest_lending.strip() == "" or region.strip() == "" or lending_way.strip() == "" or lending_title.strip() == "" or lending_content.strip() == "":
            message = '除Line ID外不可為空'
        if not message == '':
            return render(request, self.template_name, {'message': message})

        if password1 == password2:
            user = User.objects.create_user(username=phone, password=password1)
            group = Group.objects.get(name='unverified')
            user.groups.add(group)
            user.save()
            myUser = MyUser.objects.create(user=user, is_lender=True)
            Lender.objects.create(user=myUser, nickname=nickname, line_id=line_id, highest_lending=highest_lending, region=region, lending_way=lending_way, lending_title=lending_title, lending_content=lending_content)
            login(request, user)
            return HttpResponseRedirect(reverse('loan:verify'))  #如果request不能一起傳過去的話，就在這邊把verify.get的事情做完
        else:
            return render(request, self.template_name, {'message': '請檢查密碼是否相同'})

class VerifyView(LoginRequiredMixin, View):
    login_url = '/loan/login/'
    template_name = 'loan/verify.html'

    def get(self, request, *args, **kwargs):
        if request.user.has_perm('loan.view_myuser'):
            return HttpResponseRedirect(reverse('loan:index'))

        phone = request.user.username
        sendVerification(request, phone)

        return render(request, self.template_name, {'message': '驗證碼已寄送'})

    def post(self, request, *args, **kwargs):
        if 'checking_code' in request.POST:
            checking_code = request.POST['checking_code']
            user = request.user.myuser

            if user.checking_error < 4:
                if checking_code == user.checking_code:
                    user.checking_error = 0
                    user.checking_times = 0
                    baseUser = request.user
                    if user.is_borrower:
                        baseUser.groups.add(Group.objects.get(name='member'))
                        baseUser.groups.add(Group.objects.get(name='borrower'))
                        # 驗證完後在前端說已經發出借款貼文
                    if user.is_lender:
                        baseUser.groups.add(Group.objects.get(name='member'))
                        # 待繳費後才可加進lender group, 取得lender權限
                        baseUser.groups.add(Group.objects.get(name='lender'))
                    baseUser.groups.remove(Group.objects.get(name='unverified'))
                    user.save()
                    baseUser.save()
                    return HttpResponseRedirect(reverse('loan:index'))
                else:
                    user.checking_error = user.checking_error + 1
                    user.save()

                    context = {}
                    context['message'] = "驗證碼輸入錯誤，請重新輸入或重新發送驗證碼"
                    return render(request, self.template_name, {context})
            else:
                context = {}
                context['message'] = "您已輸入錯誤三次，請重新發送驗證碼或聯絡客服"
                return render(request, self.template_name, context)
        else:
            phone = request.user.username
            # sendVerification(request, phone)

            return render(request, self.template_name, {'message': '驗證碼已寄送'})


class ForgotView(View):
    template_name = 'loan/forgot.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'loan/input_phone.html')

    def post(self, request, *args, **kwargs):
        if 'checking_code' in request.POST:
            phone = request.POST['phone']  # 前端要hidden傳phone進來
            checking_code = request.POST['checking_code']
            user = User.objects.get(username=phone).myuser

            if user.checking_error < 4:
                if checking_code == user.checking_code:
                    user.checking_error = 0
                    user.checking_times = 0
                    user.save()
                    baseUser = User.objects.get(username=phone)
                    login(request, baseUser)
                    return HttpResponseRedirect(reverse('loan:resetpassword'))
                else:
                    user.checking_error = user.checking_error + 1
                    user.save()

                    context = {}
                    context['phone'] = phone
                    context['message'] = "驗證碼輸入錯誤，請重新輸入或重新發送驗證碼"
                    return render(request, self.template_name, context)
            else:
                context = {}
                context['phone'] = phone
                context['message'] = "您已輸入錯誤三次，請重新發送驗證碼或聯絡客服"
                return render(request, self.template_name, context)
        else:
            phone = request.POST['phone']
            sendVerification(request, phone)

            context = {}
            context['message'] = "驗證碼已寄送"
            context['phone'] = phone
            return render(request, self.template_name, context)

class LoginView(View):
    template_name = 'loan/login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        phone = request.POST['phone']
        password = request.POST['password']  # 加密
        user = authenticate(request, username=phone, password=password)
        if user is not None:
            login(request, user)
            if user.has_perm('loan.view_myuser'):
                return HttpResponseRedirect(reverse('loan:index'))
            else:
                return HttpResponseRedirect(reverse('loan:verify'))
        else:
            #錯誤太多次要啟動'我不是機器人'機制
            return render(request, self.template_name, {'message': "登入失敗，請檢查電話和密碼是否正確"})

def logout(request):
    django_logout(request)
    return HttpResponseRedirect(reverse('loan:index'))

class ResetpasswordView(LoginRequiredMixin, View):
    login_url = '/loan/login/'
    template_name = 'loan/resetpassword.html'

    def get(self, request, *args, **kwargs):
        user = request.user.myuser
        if user.is_borrower:
            return render(request, 'loan/borrower_resetPS.html')
        elif user.is_lender:
            return render(request, 'loan/lender_resetPS.html')

    def post(self, request, *args, **kwargs):
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        user = request.user

        if password1.strip() == '' or password2.strip() == '':
            return render(request, self.template_name, {'message': '密碼不得為空'})

        if password1 == password2:
            user.set_password(password1)
            user.save()
            login(request, user)
            if user.myuser.is_borrower:
                return render(request, 'loan/borrower_resetPS.html', {'message': '密碼更改成功'})
            elif user.myuser.is_lender:
                return render(request, 'loan/lender_resetPS.html', {'message': '密碼更改成功'})
        else:
            if user.myuser.is_borrower:
                return render(request, 'loan/borrower_resetPS.html', {'message': '密碼不一致'})
            elif user.myuser.is_lender:
                return render(request, 'loan/lender_resetPS.html', {'message': '密碼不一致'})

class SubmitAdView(View):
    template_name = 'loan/ad_register.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # 需檢查號碼是否存在? 好像不用，因為我們會直接連絡他，而且只是填聯絡資料沒必要驗證
        name = request.POST['name']
        phone = request.POST['phone']
        line_id = request.POST['line_id']
        package = request.POST['package']
        region = request.POST['region']
        paying_month_local = request.POST['paying_month_local']
        paying_month_nation = request.POST['paying_month_nation']

        message = ''
        if not re.match(r'09\d{8}', phone):
            message = '行動電話號碼格式錯誤'
        if name.strip() == '' or phone.strip() == '' or package.strip() == '' or region.strip() == '' or paying_month_local.strip() == '' or paying_month_nation.strip() == '':
            message = '除line_id外，資料不得為空'
        if not message == '':
            return render(request, self.template_name, {'message': message})

        Ad_Contact.create_ad_contact(self, name, phone, line_id, package, region, paying_month_local, paying_month_nation)
        return HttpResponseRedirect(reverse('loan:ad_success'))

class AdSuccessView(View):
    template_name = 'loan/ad_success.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class BorrowingMessageView(generic.ListView):
    template_name = 'loan/borrower_request.html'
    context_object_name = 'borrowing_message_list'

    def get_queryset(self):
        return Borrowing_Message.objects.all().order_by('-pub_time')

class BorrowingMessageRegionView(generic.ListView):
    template_name = 'loan/borrower_request.html'
    context_object_name = 'borrowing_message_list'

    #這裡要改，要把小區域一起傳回
    def get_queryset(self):
        query = []
        if self.kwargs.get('region') == '北、北、基（含宜蘭）':
            query = ['台北', '新北', '基隆', '宜蘭']
        elif self.kwargs.get('region') == '桃、竹、苗':
            query = ['桃園', '新竹', '苗栗']
        elif self.kwargs.get('region') == '中、彰、投':
            query = ['台中', '彰化', '南投']
        elif self.kwargs.get('region') == '雲、嘉、南':
            query = ['雲林', '嘉義', '台南']
        elif self.kwargs.get('region') == '高雄、屏東':
            query = ['高雄', '屏東']
        elif self.kwargs.get('region') == '中、彰、投':
            query = ['花蓮', '台東']
        return Borrowing_Message.objects.filter(region__in=query).order_by('-pub_time')

class BorrowingMessageDetailView(generic.DetailView):
    model = Borrowing_Message
    template_name = 'loan/borrower_private_request.html'

    # 傳回隨機的VIP廣告
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ids = []
        VIPs = User.objects.filter(groups__name='VIP')
        for VIP in VIPs:
            ids.append(VIP.id)
        context['lender'] = User.objects.get(pk=random.choice(ids)).myuser.lender
        return context

class AdView(generic.ListView):
    template_name = 'loan/position.html'
    context_object_name = 'ad_list'

    #隨機傳回廣告
    def get_queryset(self):
        ids = []
        ads = User.objects.filter(groups__name='ad')
        for ad in ads:
            ids.append(ad.myuser.lender.ad.pk)
        random.shuffle(ids)
        return Ad.objects.filter(pk__in=ids)

class AdRegionView(generic.ListView):
    template_name = 'loan/position.html'
    context_object_name = 'ad_list'

    # 隨機傳回廣告
    def get_queryset(self):
        ids = []
        ads = Ad.objects.filter(ad_region=self.kwargs.get('region'))
        for ad in ads:
            ids.append(ad.pk)
        random.shuffle(ids)
        return Ad.objects.filter(pk__in=ids)

class LendingMessageView(generic.ListView):
    template_name = 'loan/lender_supply.html'
    context_object_name = 'lending_message_list'

    def get_queryset(self):
        return Lender.objects.all().order_by('-update_time')

class LendingMessageRegionView(generic.ListView):
    template_name = 'loan/lender_supply.html'
    context_object_name = 'lending_message_list'

    def get_queryset(self):
        return Lender.objects.filter(region=self.kwargs.get('region'))

class LendingMessageDetailView(generic.DetailView):
    model = Lender
    template_name = 'loan/lender_paragraph_private.html' #不傳到ad_private，在lender_paragraph_private中判斷有沒有廣告

class UpdateBorrowerView(PermissionRequiredMixin, View):
    permission_required = 'loan.change_borrower'
    login_url = '/loan/login/'
    template_name = 'loan/borrower_private.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'borrower': request.user.myuser.borrower})

    def post(self, request, *args, **kwargs):
        nickname = request.POST['nickname']
        line_id = request.POST['line_id']
        job = request.POST['job']

        if nickname.strip() == "":
            context = {}
            context['borrower'] = request.user.myuser.borrower
            context['message'] = "暱稱不得為空"
            return render(request, self.template_name, context)
        else:
            Borrower.change_borrower(self, request.user, nickname, line_id, job)
            return HttpResponseRedirect(reverse('loan:update_borrower'))

class CreateBorrowerMessageView(PermissionRequiredMixin, View):
    permission_required = 'loan.add_borrowing_message'
    login_url = 'loan/login/'
    template_name = 'loan/borrower_create.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'borrower': request.user.myuser.borrower})

    def post(self, request, *args, **kwargs):
        pattern = r"[1-9]+[0-9]*"  # 檢測money是否為非0正整數

        money_usage = request.POST['money_usage']
        money = request.POST['money']
        region = request.POST['region']
        borrowing_way = request.POST['borrowing_way']

        if money_usage.strip() == "" or region.strip() == "" or borrowing_way.strip() == "":
            return render(request, self.template_name, {'message': '所有資料不得為空'})
        if not re.match(pattern, money):
            return render(request, self.template_name, {'message': '借款金額須為數字或不得為0'})

        Borrowing_Message.create_borrowing_message(self, money, region, money_usage, request.user.myuser.borrower, borrowing_way)

        return HttpResponseRedirect(reverse('loan:index'))


class BorrowingHistoryView(PermissionRequiredMixin, View):
    permission_required = 'loan.view_borrower'
    login_url = '/loan/login/'
    template_name = 'loan/borrower_history.html'

    def get(self, request, *args, **kwargs):
        context = {}
        context['borrower'] = request.user.myuser.borrower
        context['borrowing_message_list'] = request.user.myuser.borrower.borrowing_message_set.all()
        return render(request, self.template_name, context)

class BorrowingCompletedView(PermissionRequiredMixin, View):
    permission_required = 'loan.change_borrowing_message'
    login_url = '/loan/login/'
    template_name = 'loan/borrower_history.html'

    def get(self, request, *args, **kwargs):
        Borrowing_Message.change_borrowing_status(self, self.kwargs.get('id'))
        return HttpResponseRedirect(reverse('loan:borrowing_history'))

class UpdateLenderView(LoginRequiredMixin, View):
    login_url = '/loan/login/'
    template_name = 'loan/lender_private.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'lender': request.user.myuser.lender})

    def post(self, request, *args, **kwargs):
        nickname = request.POST['nickname']
        line_id = request.POST['line_id']
        if nickname.strip() == "":
            context = {}
            context['lender'] = request.user.myuser.lender
            context['message'] = "暱稱不得為空"
            return render(request, self.template_name, context)
        else:
            Lender.change_lender(self, request.user, nickname, line_id)
            return HttpResponseRedirect(reverse('loan:update_lender'))

class CreateLenderMessageView(LoginRequiredMixin, View):
    login_url = '/loan/login/'
    template_name = 'loan/lender_create.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'lender': request.user.myuser.lender})

    def post(self, request, *args, **kwargs):
        region = request.POST['region']
        highest_lending = request.POST['highest_lending']
        lending_way = request.POST['lending_way']
        lending_title = request.POST['lending_title']
        lending_content = request.POST['lending_content']

        if region.strip() == '' or highest_lending.strip() == '' or lending_way.strip() == '' or lending_title.strip() == '' or lending_content.strip() == '':
            context = {}
            context['lender'] = request.user.myuser.lender
            context['message'] = "所有資料不得為空"
            return render(request, self.template_name, context)

        Lender.create_lending_content(self, request.user, region, highest_lending, lending_way, lending_title, lending_content)
        return HttpResponseRedirect(reverse('loan:create_lender_message'))

class PayingHistoryView(LoginRequiredMixin, View):
    login_url = '/loan/login/'
    template_name = 'loan/lender_history.html'

    def get(self, request, *args, **kwargs):
        context = {}
        context['lender'] = request.user.myuser.lender
        context['paying_history_list'] = request.user.myuser.lender.paying_set.all()
        return render(request, self.template_name, context)

class PayingView(LoginRequiredMixin, View):
    login_url = '/loan/login/'
    template_name = 'loan/lender_payment.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        #要看前端是不是會把全部參數傳進來，如果不會的話，要判斷是哪種package再存取資料
        package = request.POST['package']
        ad_type = request.POST['ad_type']
        ad_region = request.POST['ad_region']
        paying_month_lender = request.POST['paying_month_lender']
        paying_month_ad_local = request.POST['paying_month_ad_local']
        paying_month_ad_nation = request.POST['paying_month_ad_nation']
        receivable_money = request.POST['receivable_money']

        request.user.myuser.lender.paying_set.create(package=package, ad_type=ad_type, ad_region=ad_region, paying_month_lender=paying_month_lender, paying_month_ad_local=paying_month_ad_local, paying_month_ad_nation=paying_month_ad_nation, receivable_money=receivable_money)
        return HttpResponseRedirect(reverse('loan:paying_success'))

class PayingSuccessView(View):
    template_name = 'loan/lender_success.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'paying': request.user.myuser.lender.paying_set.order_by('-apply_date')[0]})

class PrivacyPolicyView(View):
    template_name = 'loan/privacy_policy.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class TermsView(View):
    template_name = 'loan/terms.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class BackendView(View):
    template_name = 'loan/backend.html'

    #要設permission, staff only
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            context = {}
            context['ad_contacts'] = Ad_Contact.objects.all().order_by('-pub_date')
            context['lender_payments'] = Paying.objects.all().order_by('-apply_date')
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        #須到settings設定MEDIA_ROOT, MEDIA_URL和mmm957/urls
        #imagefield自動處理好圖片儲存，前端存取時用，ad.ad_photo.url
        phone = request.POST['phone']
        ad_region = request.POST['ad_region']
        ad_photo = request.FILES.get('ad_photo')

        user = User.objects.get(username=phone)
        Ad.objects.create(lender=user.myuser.lender, ad_region=ad_region, ad_photo=ad_photo)
        return HttpResponseRedirect(reverse('loan:backend'))

def sendVerification(request, phone):
    phone_886 = '+886' + phone[1:]

    r = ''.join(random.sample(string.digits, 6))  #驗證碼
    try:
        user = User.objects.get(username=phone).myuser
        if user.checking_times < 5:
            user.checking_code = r
            account_sid = 'ACcbf33f74130b248782062490d1680c83'  # 寄簡訊
            auth_token = '07f645e2725464f9915b83828ba74024'
            client = Client(account_sid, auth_token)
            client.messages.create(
                body='歡迎來到957借貸平台。您的簡訊驗證碼為 : ' + r + '。',
                from_='+13524152876',
                to=phone_886
            )
            user.checking_times = user.checking_times + 1
            user.checking_error = 0
            user.save()
        else:
            if request.user.groups.filter(name='member').exists():
                return render(request, 'loan/verify.html', {'message': '驗證碼寄送次數已達上限，請聯絡客服解鎖'})
            else:
                context = {}
                context['message'] = '驗證碼寄送次數已達上限，請聯絡客服解鎖'
                context['phone'] = phone
                return render(request, 'loan/forgot.html', phone)

    except:
        user = User.objects.get(username=phone).myuser
        if user.checking_times < 5:
            user.checking_code = r
            account_sid = 'ACcbf33f74130b248782062490d1680c83'  # 寄簡訊
            auth_token = '07f645e2725464f9915b83828ba74024'
            client = Client(account_sid, auth_token)
            client.messages.create(
                body='歡迎來到957借貸平台。您的簡訊驗證碼為 : ' + r + '。',
                from_='+13524152876',
                to=phone_886
            )
            user.checking_times = user.checking_times + 1
            user.checking_error = 0
            user.save()
        else:
            if request.user.groups.filter(name='member').exists():
                return render(request, 'loan/verify.html', {'message': '驗證碼寄送次數已達上限，請聯絡客服解鎖'})
            else:
                context = {}
                context['message'] = '驗證碼寄送次數已達上限，請聯絡客服解鎖'
                context['phone'] = phone
                return render(request, 'loan/forgot.html', phone)