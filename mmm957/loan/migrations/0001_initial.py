# Generated by Django 3.1 on 2020-08-10 18:55

from django.conf import settings
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checking_code', models.CharField(default=0, max_length=6)),
                ('checking_times', models.IntegerField(default=0)),
                ('checking_error', models.IntegerField(default=0)),
                ('is_borrower', models.BooleanField(default=False)),
                ('is_lender', models.BooleanField(default=False)),
                ('is_employee', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paying_month', models.CharField(choices=[('1', '1'), ('3', '3'), ('12', '12')], max_length=2)),
                ('price_of_lender', models.CharField(choices=[('local', 0), ('national', 0)], max_length=10)),
                ('price_of_ad', models.CharField(choices=[('local', 0), ('national', 0)], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Borrower',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='loan.myuser')),
                ('nickname', models.CharField(default='先生/小姐', max_length=16)),
                ('line_id', models.CharField(max_length=16, null=True)),
                ('job', models.CharField(choices=[('農、林、漁、牧業', '農、林、漁、牧業'), ('勞工上班族', '勞工上班族'), ('交通運輸業', '交通運輸業'), ('餐旅服務業', '餐旅服務業'), ('公家機關', '公家機關'), ('建築業', '建築業'), ('娛樂業', '娛樂業'), ('大學生', '大學生'), ('其他', '其他'), ('無', '無')], max_length=16, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='loan.myuser')),
                ('name', models.CharField(max_length=16)),
                ('department', models.CharField(max_length=16)),
                ('position', models.CharField(max_length=16)),
                ('salary', models.IntegerField(default=0)),
                ('phone', models.CharField(max_length=10)),
                ('born_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Lender',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='loan.myuser')),
                ('nickname', models.CharField(max_length=16)),
                ('line_id', models.CharField(max_length=16, null=True)),
                ('region', models.CharField(choices=[('北、北、基（含宜蘭）', '北、北、基（含宜蘭）'), ('桃、竹、苗', '桃、竹、苗'), ('中、彰、投', '中、彰、投'), ('雲、嘉、南', '雲、嘉、南'), ('高雄、屏東', '高雄、屏東'), ('花蓮、台東', '花蓮、台東')], max_length=10, null=True)),
                ('highest_lending', models.IntegerField(null=True)),
                ('lending_way', models.CharField(choices=[('本票', '本票'), ('機車', '機車'), ('汽車', '汽車'), ('電話諮詢', '電話諮詢')], max_length=16, null=True)),
                ('lending_title', models.CharField(max_length=20, null=True)),
                ('lending_content', models.CharField(max_length=50, null=True)),
                ('update_time', models.DateTimeField(null=True, verbose_name='date published')),
                ('lending_expired_date', models.DateTimeField(null=True)),
                ('ad_expired_date', models.DateTimeField(null=True)),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='loan.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Paying',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paying_date', models.DateTimeField(null=True)),
                ('receivable_money', models.IntegerField()),
                ('get_money', models.IntegerField(null=True)),
                ('next_lender_expired_date', models.DateTimeField(null=True)),
                ('next_ad_expired_date', models.DateTimeField(null=True)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loan.price')),
                ('lender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loan.lender')),
            ],
        ),
        migrations.CreateModel(
            name='Borrowing_Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('money', models.IntegerField()),
                ('borrowing_way', models.CharField(choices=[('本票', '本票'), ('機車', '機車'), ('汽車', '汽車'), ('電話諮詢', '電話諮詢')], default='本票', max_length=16, null=True)),
                ('region', models.CharField(choices=[('基隆', '基隆'), ('台北', '台北'), ('新北', '新北'), ('桃園', '桃園'), ('新竹', '新竹'), ('苗栗', '苗栗'), ('台中', '台中'), ('彰化', '彰化'), ('南投', '南投'), ('雲林', '雲林'), ('嘉義', '嘉義'), ('台南', '台南'), ('高雄', '高雄'), ('屏東', '屏東'), ('宜蘭', '宜蘭'), ('花蓮', '花蓮'), ('台東', '台東')], max_length=2)),
                ('money_usage', models.CharField(max_length=16)),
                ('pub_time', models.DateTimeField(verbose_name='date published')),
                ('borrowing_status', models.BooleanField(default=False)),
                ('borrower', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='loan.borrower')),
            ],
        ),
        migrations.CreateModel(
            name='Ad_Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('phone', models.CharField(max_length=10)),
                ('line_id', models.CharField(max_length=20)),
                ('package', models.CharField(max_length=10)),
                ('region', models.CharField(choices=[('北、北、基（含宜蘭）', '北、北、基（含宜蘭）'), ('桃、竹、苗', '桃、竹、苗'), ('中、彰、投', '中、彰、投'), ('雲、嘉、南', '雲、嘉、南'), ('高雄、屏東', '高雄、屏東'), ('花蓮、台東', '花蓮、台東')], max_length=10, null=True)),
                ('paying_month', models.CharField(choices=[('1', '1'), ('3', '3'), ('12', '12')], max_length=2)),
                ('pub_date', models.DateTimeField()),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='loan.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad_region', models.CharField(choices=[('北、北、基（含宜蘭）', '北、北、基（含宜蘭）'), ('桃、竹、苗', '桃、竹、苗'), ('中、彰、投', '中、彰、投'), ('雲、嘉、南', '雲、嘉、南'), ('高雄、屏東', '高雄、屏東'), ('花蓮、台東', '花蓮、台東')], max_length=10)),
                ('ad_photo', models.ImageField(storage=django.core.files.storage.FileSystemStorage(location='/media/cards'), upload_to='')),
                ('lender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loan.lender')),
            ],
        ),
    ]
