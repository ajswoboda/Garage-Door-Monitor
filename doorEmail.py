from __future__ import print_function
import pickle
import os.path
from time import sleep
from time import time
from ssl import SSLError
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


from apiclient import errors
from httplib2 import ServerNotFoundError

class EmailError(Exception):
    pass

class email(object):
    def __init__(self):
        # check if you want to use this scope. It provides modify permissions.
        self.SCOPE = ['https://www.googleapis.com/auth/gmail.modify']
        self.sender = 'me'
        # multiple emails you can do emailOne, emailTwo
        self.to = 'youremail@goes.here'
        self.subject = ''
        self.message = ''
        self.after = int(time())
        self.before = int(time())
        self.user_id = 'me'
        self.path = '/door/monitor'
        
        retries = 1
        success = False
        sleep(10)
        while retries and not success:
            try:
                self.service = self.sendCreds()
                success = True
            except IOError, e:
                self.logError(e)
                pass
            except ServerNotFoundError, e:
                self.logError(e)
                pass
            
            if not success:
                self.log.write('Sleeping for 10 seconds.')
                sleep(10)
                retries -= 1

        if not retries and not success:
            self.log.write('Sleeping for 10 seconds.\n')
            raise EmailError

    
    def logError(self, e):
        self.log.write('Error: %s.\n' % e)

    def sendCreds(self):
        creds = None
        path = r'%s/token.pickle' % self.path
        cred = r'%s/credentials.json' % self.path
        if os.path.exists(path):
            with open(path, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    cred, self.SCOPE)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(path, 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def sendMessage(self, file=None):
        try:
            message = (self.service.users().messages().send(userId=self.user_id, body=self.createMessage(file)).execute())
            return message
        except (errors.HttpError, SSLError), error:
            print(error)


    def createMessageText(self):
        message = MIMEText(self.message)
        message['to'] = self.to
        message['from'] = self.sender
        message['subject'] = self.subject
        return {'raw': base64.urlsafe_b64encode(message.as_string())}
    
    def createMessage(self, file=None):
        if not file:
            return self.createMessageText()
        else:
            return self.create_message_with_attachment(file)
    
    def create_message_with_attachment(self, file=None):
        message = MIMEMultipart()
        message['to'] = self.to
        message['from'] = self.sender
        message['subject'] = self.subject
        msg = MIMEText(self.message)
        message.attach(msg)
        content_type, encoding = mimetypes.guess_type(file)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'

        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'image':
            fp = open(file, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()

        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)
        return {'raw': base64.urlsafe_b64encode(message.as_string())}

    #chang fQuery to an email you will send a response from
    def listMessagesMatchingQuery(self, fQuery='from:new@email.goeshere after:%s before:%s'):
        if 'after:' in fQuery and 'before:' in  fQuery:
            self.before = int(time())
            fQuery = fQuery % (self.after, self.before)
        
        try:
            response = self.service.users().messages().list(userId=self.user_id,
                                                     q=fQuery).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(userId=self.user_id, q=fQuery,
                                               pageToken=page_token).execute()
                messages.extend(response['messages'])
            return messages
        except (errors.HttpError, SSLError), e:
            print(e)
            return False
    
    def getMessage(self, msg_id):
        try:
            message = self.service.users().messages().get(userId=self.user_id, id=msg_id).execute()
            return message
        except errors.HttpError:
            return False
    


def checkEmails():
    e = email()
    eList = (e.listMessagesMatchingQuery())
    if eList:
        for message in eList:
            msg_id = message['id']
            message = e.getMessage(msg_id)
            if 'payload' in message:
                if 'parts' in message['payload']:
                    for p in message['payload']['parts']:
                        if 'body' in p:
                            if 'data' in p['body']:
                                data = p['body']['data'].strip()
                                decoded = base64.urlsafe_b64decode(data.encode("ascii")).lower().strip()
                                #looks for close or another phrase in the email.
                                if 'close' in decoded:
                                    return True

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    SendMessage(service, user_id, test)



if __name__ == '__main__':
    main()





