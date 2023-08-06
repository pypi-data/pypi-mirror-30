# -*- coding: utf-8 -*-
import os
import boto3
import jinja2
import re
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


class Email(object):
    """Clase para envio de correos por Amazon SES.
    parametros obligatorios:
        to: email destinatario.
        subject: titulo de correo
    parametros opcionales:
        from_addr: quien envia el correo
        stat: si se desea que el correo pase por monitoreo o no
        (status, tracking de correo, lectura.)
        group: nombre del grupo en caso de tenerlo
        unsubscribe: Se agrega al final del correo un link de desuscribir,
        el cual permitira que no reciba mas correos
            futuros en newsletter"""

    def __init__(self, to, subject='', from_addr='',
                 config={}):
        self._not_valid_emails = []
        email_regex = config.get('email_regex',
            					 "^[A-Za-z0-9\.\+_-]+@[A-Za-"
            					 "z0-9\._-]+\.[a-zA-Z]{2,4}$")
        self._to = to if isinstance(to, list) else re.split("[,;|]+", to)
        self._valid_emails = list(
                filter(lambda x: x if
                       re.match(email_regex, x)!=None \
                       else self._not_valid_emails.append(x), self._to))
        self._subject = subject
        self._from_addr = from_addr if from_addr != '' else config.get("default_sender")
        self._format = 'html'
        self._msg = MIMEMultipart('mixed')
        self._msg['Subject'] = self._subject
        self._msg['From'] = self._from_addr
        self._msg['To'] = ', '.join(self._valid_emails)
        self._attach_cap = config.get('attach_cap', 9999)
        self._config = config

    def config(self):
        return boto3.client('ses',
            region_name=self._config['region_name'],
            aws_access_key_id=self._config['aws_access_key_id'],
            aws_secret_access_key=self._config['aws_secret_access_key'])

    def html(self, html, context={}, charset='utf-8', read=False):
        # charset: The character encoding for the email.
        self._msg_body = MIMEMultipart('alternative')
        if read is True:
            path, filename = os.path.split(html)
            body = jinja2.Environment(
                loader=jinja2.FileSystemLoader(path or './')
            ).get_template(filename).render(context)
        else:
            body = jinja2.Environment(loader=jinja2.BaseLoader) \
                .from_string(html) \
                .render(**context)

        # The email body for recipients with non-HTML email clients.
        # Create a multipart/mixed parent container.

        # Encode the text and HTML content and set the character encoding. This step is
        # necessary if you're sending a message with characters outside the ASCII range.
        #textpart = MIMEText(BODY_TEXT.encode(charset), 'plain', charset)
        htmlpart = MIMEText(body.encode(charset), 'html', charset)

        # Add the text and HTML parts to the child container.
        #self._msg_body.attach(textpart)
        self._msg_body.attach(htmlpart)
        self._msg.attach(self._msg_body)

    def custom_header(self, header, parameter):
        """ 
            For more information
            See https://docs.aws.amazon.com/ses/latest/DeveloperGuide/header-fields.html
        """
        self._msg[header] = parameter

    def attach(self, name=None, file=None, read=True):
        """
            Options:
            name: optional, is the name displayed on the file when delivered,
                    using default will use file name.
            file: File to be delivered, it can also be a binary file
                    but <read> option must be False so wont be readed.
            read: optional, its intended to know if a file is already opened
                    or needs to be read and loaded.

            Aditional note:
                Max size available to deliver according to big enterprises
                is 10mb, its custom and can be change in the settings
                but keep that on mind, this is because maybe we need less 
                than that or a day the size increases and we can easily 
                adjust it.
        """
        if isinstance(read, bool):
            pass
        else:
            raise Exception('Read option must be True or False.')
        self._attach_cap -= os.path.getsize(file) >> 10
        if self._attach_cap > 0:
            if file and read is True:
                att = MIMEApplication(open(file, 'rb').read())
            elif file and read is False:
                att = MIMEApplication(file)
            else:
                raise Exception('No file found or issued, call ignored.')
            att.add_header('Content-Disposition',
                           'attachment',
                           filename=name if name else os.path.basename(file))
            self._msg.attach(att)
        else:
            self._attach_cap += os.path.getsize(file) >> 10
            raise Exception('Size of file %s overreach max capacity, '
                            'file ignored.' % os.path.basename(file))

    def set_paremeters(self):
        p = {"RawMessage": {'Data': self._msg.as_string(), },
             "Source": self._from_addr}
        if 'ConfigurationSetName' in self._config:
            p['ConfigurationSetName'] = self._config['ConfigurationSetName']
        return p

    def send(self):
        try:
            # Provide the contents of the email.
            response = self.config().send_raw_email(
                **self.set_paremeters()
            )
        # Display an error if something goes wrong. 
        except ClientError as e:
            r = {"success": False,
                 "error": e.response['Error']['Message']}
        else:
            # Get request id if everythings ok. 
            r = {"success": True,
                 "RequestId": response['ResponseMetadata']['RequestId']}
        # If an email has an invalid format will be returned in 
        # ignored emails list
        if len(self._not_valid_emails) is not 0:
            r['ignored_emails'] = ','.join(self._not_valid_emails)
        return r
