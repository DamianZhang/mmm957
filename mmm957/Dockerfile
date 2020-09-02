# myproject/Dockerfile
# 建立 python3.7 环境
FROM python:3.7

# 设置 python 环境变量
ENV PYTHONUNBUFFERED 1

# 创建 myproject 文件夹
RUN mkdir -p /var/www/html/mmm957

# 将 myproject 文件夹为工作目录
WORKDIR /var/www/html/mmm957

# 将当前目录加入到工作目录中（. 表示当前目录）
ADD . /var/www/html/mmm957

# 利用 pip 安装依赖
RUN pip install Django
RUN pip install uwsgi==2.0.18
RUN pip install mysqlclient
RUN pip install django-redis==4.11.0
RUN pip install redis==3.5.0
RUN pip install twilio
RUN pip install pillow
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install vim