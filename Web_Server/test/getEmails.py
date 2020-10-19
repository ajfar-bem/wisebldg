import poplib
from email import parser
import getToken
import test_settings

def getEmails(subject):
    pop_conn = poplib.POP3_SSL('pop.gmail.com')
    pop_conn.user('bemosstesting@gmail.com')
    pop_conn.pass_('thewalletinthewell')
    #Get messages from server:
    messages = [pop_conn.retr(i) for i in range(1, len(pop_conn.list()[1]) + 1)]
    # Concat message pieces:
    messages = ["\n".join(mssg[1]) for mssg in messages]
    #Parse message intom an email object:
    bodies = []
    messages = [parser.Parser().parsestr(mssg) for mssg in messages]
    for message in messages:
        if message['subject'].lower() == subject.lower():
            for part in message.walk():
                if part.get_content_type() in ['text/html','text/plain']:
                    bodies.append(part.get_payload())
    return bodies

if __name__=="__main__":
    token = getToken.login(test_settings.superusername, test_settings.superuserpassword)