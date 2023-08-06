'''
Emailer class
Author: Steve Brownfield
Created: 4/15/2018
'''
from flask_mail import Mail
from flask_mail import Message

class Emailer:

    msg = ""
    mail = ""
    app = ""

    def __init__(self,flask_app, mail_server, mail_port, username, password, ssl=True):
        '''Construct a new Emailer object to send email messages

        Args:
            flask_app (a Flask app object): The first parameter.
            mail_server (str): The second parameter. Repersenting the smtp mail server
            mail_port (int): The third parameter. mail_server port number
            username (str): The forth parameter. username of email account
            password (str):  Password to login to the mail_server
            ssl (boolean): optional value to use ssl. defaults to True

        '''

        self.app = flask_app

        flask_app.config.update(
            DEBUG=True,
            # EMAIL SETTINGS
            MAIL_SERVER=mail_server,
            MAIL_PORT=mail_port,
            MAIL_USE_SSL=ssl,
            MAIL_USERNAME=username,
            MAIL_PASSWORD=password
        )
        self.mail = Mail(self.app)

    def send(self, message, file_name, format="text/plain"):
        '''This function will send an email with an attached file

        :param message: message body
        :param file_name: name of the file to attach to the email
        :param format: format of the email, defaults to text/plain
        :return: None if the mail sends successfully, otherwise an error is returned
        '''
        try:
            with self.app.open_resource(file_name) as fp:
                message.attach(file_name, format, fp.read())
            return self.mail.send(message)
        except Exception, e:
            return (str(e))