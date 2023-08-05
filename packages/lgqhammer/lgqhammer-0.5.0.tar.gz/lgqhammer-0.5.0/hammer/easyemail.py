# -*- coding=utf-8 -*-

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EasyEmail(object):
    def __init__(self, *args, **kwargs):
        self.server = None
        pass

    #
    # kwargs = {
    #     'from_email': 'awolfly9@gmail.com',
    #     'password': '',
    #     'address': 'smtp.gmail.com:587',
    # }
    def login(self, **kwargs):
        '''
        :param kwargs:
        :return: status
        '''
        self.from_email = kwargs.get('from_email')
        password = kwargs.get('password')
        address = kwargs.get('address')

        self.server = smtplib.SMTP(address)

        self.server.ehlo()
        self.server.starttls()
        self.server.login(self.from_email, password)
        return True

    # infos = [
    #     {
    #         'to_email': 'awolfly9@gmail.com',
    #         'subject': 'Test',
    #         'content': 'this is test',
    #     },
    # ]
    def send(self, infos):
        for info in infos:
            to_email = info.get('to_email')
            content = info.get('content')
            subject = info.get('subject')

            try:
                msg = MIMEMultipart()
                msg['From'] = self.from_email
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(content, 'plain'))
                self.server.sendmail(self.from_email, to_email, msg.as_string())
                print('to_email:%s send success' % to_email)
            except Exception as e:
                print('Exception to_email:%s reason:%s' % (to_email, e))

    def quit(self):
        if self.server is not None:
            self.server.quit()
