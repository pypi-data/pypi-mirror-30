from flask_mail import Mail
from flask_mail import Message

class Emailer:

    msg = ""
    mail = ""
    app = ""

    def __init__(self,flask_app, mail_server, mail_port, username, password, ssl=True):
        '''This class will send an email'''

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

    def send(self, message, file_name, filetype="text/plain"):
        try:
            with self.app.open_resource(file_name) as fp:
                message.attach(file_name, filetype, fp.read())
            return self.mail.send(message)
        except Exception, e:
            return (str(e))