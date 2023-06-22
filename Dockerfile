FROM ubuntu

# update system
RUN apt update -y
RUN apt upgrade -y

# Setup python
RUN apt install python3 libexpat1 -y
RUN ln /usr/bin/python3 /usr/bin/python
RUN apt install python3-pip -y
RUN pip install --upgrade pip

# Install apache and mod_wsgi
RUN apt install apache2 apache2-utils ssl-cert libapache2-mod-wsgi-py3 systemctl -y

# Setup wsgi with apache
COPY wsgitest.py /var/www/html/wsgitest.py
RUN chown www-data:www-data /var/www/html/wsgitest.py
RUN chmod 775 /var/www/html/wsgitest.py

RUN rm /etc/apache2/sites-enabled/000-default.conf
COPY site-config.conf /etc/apache2/sites-enabled/000-default.conf

# utilities
RUN apt install nano -y