from django.contrib.auth.models import User
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

# choices setting
REGION = (
    ('基隆', '基隆'), ('台北', '台北'),
    ('新北', '新北'), ('桃園', '桃園'),
    ('新竹', '新竹'), ('苗栗', '苗栗'),
    ('台中', '台中'), ('彰化', '彰化'),
    ('南投', '南投'), ('雲林', '雲林'),
    ('嘉義', '嘉義'), ('台南', '台南'),
    ('高雄', '高雄'), ('屏東', '屏東'),
    ('宜蘭', '宜蘭'), ('花蓮', '花蓮'),
    ('台東', '台東'),
)
REGION_COMBINED = (
    ('北、北、基（含宜蘭）', '北、北、基（含宜蘭）'), ('桃、竹、苗', '桃、竹、苗'),
    ('中、彰、投', '中、彰、投'), ('雲、嘉、南', '雲、嘉、南'),
    ('高雄、屏東', '高雄、屏東'), ('花蓮、台東', '花蓮、台東'),
)
PAYING_MONTH = (
    ('20000', '20000'), ('54000', '54000'),
    ('108000', '108000'), ('12000', '12000'),
    ('30600', '30600'), ('100800', '100800'),
    ('30000', '30000'), ('76500', '76500'),
    ('252000', '252000'),
)
PRICE_OF_LENDER = (
    ('local', 0), ('national', 0),
)
PRICE_OF_AD = (
    ('local', 0), ('national', 0),
)
BORROWING_WAY = (
    ('本票', '本票'), ('機車', '機車'),
    ('汽車', '汽車'), ('電話諮詢', '電話諮詢'),
)
JOB = (
    ('農、林、漁、牧業', '農、林、漁、牧業'), ('勞工上班族', '勞工上班族'),
    ('交通運輸業', '交通運輸業'), ('餐旅服務業', '餐旅服務業'),
    ('公家機關', '公家機關'), ('建築業', '建築業'),
    ('娛樂業', '娛樂業'), ('大學生', '大學生'),
    ('其他', '其他'), ('無', '無'),
)

class MyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    checking_code = models.CharField(max_length=6, default=0)
    checking_times = models.IntegerField(default=0)
    checking_error = models.IntegerField(default=0)
    is_borrower = models.BooleanField(default=False)
    is_lender = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_ad = models.BooleanField(default=False)
    is_VIP = models.BooleanField(default=False)
    is_member = models.BooleanField(default=False)


class Borrower(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, primary_key=True)
    nickname = models.CharField(max_length=16, default='先生/小姐')
    line_id = models.CharField(max_length=16, null=True)  # 串接line API查看ID是否存在
    job = models.CharField(max_length=16, choices=JOB, null=True)

    # Borrower先不放employee_id, 但檔案上有

    # def create_borrower(self, myUser, nickname):
    #     myUser.borrower.objects.create(nickname=nickname)

    def change_borrower(self, user, nickname, line_id, job):
        borrower = user.myuser.borrower
        borrower.nickname = nickname
        borrower.line_id = line_id
        borrower.job = job
        borrower.save()


class Borrowing_Message(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    money = models.IntegerField()
    borrowing_way = models.CharField(max_length=16, choices=BORROWING_WAY, default='本票')  # 可用Choices的方式
    region = models.CharField(max_length=2, choices=REGION)
    money_usage = models.CharField(max_length=16)
    pub_time = models.DateTimeField(auto_now_add=True)
    borrowing_status = models.BooleanField(default=False)

    def create_borrowing_message(self, money, region, money_usage, borrower, borrowing_way='本票'):
        borrower.borrowing_message_set.create(money=money, region=region, money_usage=money_usage, borrowing_way=borrowing_way)

    def change_borrowing_status(self, id):
        borrowing_message = Borrowing_Message.objects.get(pk=id)
        borrowing_message.borrowing_status = True
        borrowing_message.save()


class Price(models.Model):
    paying_month = models.CharField(max_length=10, choices=PAYING_MONTH)
    price_of_lender = models.CharField(max_length=10, choices=PRICE_OF_LENDER)
    price_of_ad = models.CharField(max_length=10, choices=PRICE_OF_AD)


class Employee(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=16)
    department = models.CharField(max_length=16)
    position = models.CharField(max_length=16)
    salary = models.IntegerField(default=0)
    phone = models.CharField(max_length=10)
    born_date = models.DateTimeField()


class Lender(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, primary_key=True)
    nickname = models.CharField(max_length=16)
    line_id = models.CharField(max_length=16, null=True)  # 串接line API查看ID是否存在
    region = models.CharField(max_length=10, choices=REGION_COMBINED)
    highest_lending = models.IntegerField()
    lending_way = models.CharField(max_length=16, choices=BORROWING_WAY)  # 可用Choices的方式, 同borrowing_way
    lending_title = models.CharField(max_length=100)
    lending_content = models.CharField(max_length=300)
    update_time = models.DateTimeField(auto_now=True)
    lending_expired_date = models.DateTimeField(null=True)
    ad_expired_date = models.DateTimeField(null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)

    def create_lender(self, myUser, nickname, line_id, highest_lending, region, lending_way, lending_title, lending_content):
        myUser.lender.objects.create(nickname=nickname, line_id=line_id, highest_lending=highest_lending, region=region, lending_way=lending_way, lending_title=lending_title, lending_content=lending_content)

    def change_lender(self, user, nickname, line_id):
        lender = user.myuser.lender
        lender.nickname = nickname
        lender.line_id = line_id
        lender.save()

    def create_lending_content(self, user, region, highest_lending, lending_way, lending_title, lending_content):
        lender = user.myuser.lender
        lender.region = region
        lender.highest_lending = highest_lending
        lender.lending_way = lending_way
        lender.lending_title = lending_title
        lender.lending_content = lending_content
        lender.save()


class Paying(models.Model):
    lender = models.ForeignKey(Lender, on_delete=models.CASCADE)
    package = models.CharField(max_length=20)
    ad_type = models.CharField(max_length=5, null=True)
    ad_region = models.CharField(max_length=10, choices=REGION_COMBINED, null=True)
    paying_month_lender = models.CharField(max_length=10, choices=PAYING_MONTH, null=True)
    paying_month_ad_local = models.CharField(max_length=10, choices=PAYING_MONTH, null=True)
    paying_month_ad_nation = models.CharField(max_length=10, choices=PAYING_MONTH, null=True)
    receivable_money = models.IntegerField(null=True)
    apply_date = models.DateTimeField(auto_now_add=True)
    paying_date = models.DateTimeField(null=True)
    get_money = models.IntegerField(default=0)
    next_lender_expired_date = models.DateTimeField(null=True)
    next_ad_expired_date = models.DateTimeField(null=True)
    # 先不放employee_id, 但檔案上有


class Ad_Contact(models.Model):
    name = models.CharField(max_length=16)
    phone = models.CharField(max_length=10)
    line_id = models.CharField(max_length=20, null=True)
    package = models.CharField(max_length=10)
    region = models.CharField(max_length=10, choices=REGION_COMBINED, null=True)
    paying_month_local = models.CharField(max_length=10, choices=PAYING_MONTH, null=True)
    paying_month_nation = models.CharField(max_length=10, choices=PAYING_MONTH, null=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, null=True)

    def create_ad_contact(self, name, phone, line_id, package, region, paying_month_local, paying_month_nation):
        Ad_Contact.objects.create(name=name, phone=phone, line_id=line_id, package=package, region=region, paying_month_local=paying_month_local, paying_month_nation=paying_month_nation)

    # 一個用來檢測是否已經為lender的方法


class Ad(models.Model):
    lender = models.OneToOneField(Lender, on_delete=models.CASCADE, primary_key=True)
    ad_region = models.CharField(max_length=10, choices=REGION_COMBINED)
    ad_photo = models.ImageField(upload_to='%Y/%m/')