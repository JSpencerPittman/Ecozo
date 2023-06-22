FROM ubuntu

# update system
RUN apt update -y
RUN apt upgrade -y

# Setup python
RUN apt install python3 libexpat1 -y
RUN ln /usr/bin/python3 /usr/bin/python

RUN apt install python3-pip -y

# Install apache and mod_wsgi
RUN apt install apache2 apache2-utils ssl-cert libapache2-mod-wsgi-py3 systemctl -y

# Setup wsgi with apache
COPY wsgitest.py /var/www/html/wsgitest.py
RUN chown www-data:www-data /var/www/html/wsgitest.py
RUN chmod 775 /var/www/html/wsgitest.py

# Set site configurations
RUN rm /etc/apache2/sites-enabled/000-default.conf
COPY site-config.conf /etc/apache2/sites-enabled/000-default.conf

# Setup gdal-config
RUN apt install libgdal-dev -y
RUN export CPLUS_INCLUDE_PATH=/usr/local/gdal
RUN export C_INCLUDE_PATH=/usr/local/gdal

# Install app dependencies
COPY requirements.txt /var/www/html
WORKDIR /var/www/html
RUN pip install --upgrade pip
# RUN pip install -r requirements.txt