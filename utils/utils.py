import re
import io
import os
import random
import gcsfs
import markdown
import pandas as pd
import numpy as np
from PIL import Image
import streamlit as st
#from utils import utils
#import pydata_google_auth
from seletor import Seletor
from io import BytesIO, StringIO
from google.cloud import storage
from google.oauth2 import service_account
from IPython.core.display import display,HTML

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_auth_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        #if creds and creds.expired and creds.refresh_token:
        #    creds.refresh(Request())
        #else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def CreateMessageHtml(sender, to, subject, msgPlain):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgPlain, 'plain'))
    raw = base64.urlsafe_b64encode(msg.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    return body

def SendMessage(sender, to, subject, msgPlain, attachmentFile=None):
    if attachmentFile:
        message1 = createMessageWithAttachment(sender, to, subject, msgPlain, attachmentFile)
    else: 
        message1 = CreateMessageHtml(sender, to, subject, msgPlain)
    result = SendMessageInternal("me", message1)
    return result


def SendMessageInternal(user_id, message):
    service = get_auth_service()
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"
    return "OK"


def get_bytestring(project: str,
                   bucket: str,
                   path: str,
                   service_account_credentials_path: str = None) -> bytes:
    """
    Retrieve data from a given blob on Google Storage and pass it as a byte-string.
    :param path: path within the bucket
    :param project: name of the project
    :param bucket_name: name of the bucket
    :param service_account_credentials_path: path to credentials.
           TIP: can be stored as env variable, e.g. os.getenv('GOOGLE_APPLICATION_CREDENTIALS_DSPLATFORM')
    :return: byte-string (needs to be decoded)
    """
    blob = _get_blob(bucket, path, project, service_account_credentials_path)
    s = blob.download_as_string()
    return s


def _get_blob(bucket_name, path, project, service_account_credentials_path):
    credentials = service_account.Credentials.from_service_account_file(
        service_account_credentials_path) if service_account_credentials_path else None
    storage_client = storage.Client(project=project, credentials=credentials)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(path)
    return blob

def get_byte_fileobj(project: str,
                     bucket: str,
                     path: str,
                     service_account_credentials_path: str = None) -> BytesIO:
    """
    Retrieve data from a given blob on Google Storage and pass it as a file object.
    :param path: path within the bucket
    :param project: name of the project
    :param bucket_name: name of the bucket
    :param service_account_credentials_path: path to credentials.
           TIP: can be stored as env variable, e.g. os.getenv('GOOGLE_APPLICATION_CREDENTIALS_DSPLATFORM')
    :return: file object (BytesIO)
    """
    blob = _get_blob(bucket, path, project, service_account_credentials_path)
    byte_stream = BytesIO()
    blob.download_to_file(byte_stream)
    byte_stream.seek(0)
    return byte_stream


def path_to_image_html(path):
    return '<img src="'+ path + '" width="60" >'


def createMessageWithAttachment(sender, to, subject, msgPlain, attachmentFile):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      msgHtml: Html message to be sent
      msgPlain: Alternative plain text message for older email clients          
      attachmentFile: The path to the file to be attached.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart('mixed')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    messageA = MIMEMultipart('alternative')
    messageR = MIMEMultipart('related')

    message.attach(MIMEText(msgPlain, 'plain'))
    message.attach(messageR)

    message.attach(messageA)

    print("create_message_with_attachment: file: %s" % attachmentFile)
    content_type, encoding = mimetypes.guess_type(attachmentFile)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(attachmentFile, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    elif main_type == 'image':
        fp = open(attachmentFile, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(attachmentFile, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(attachmentFile, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()

    filename = os.path.basename(attachmentFile)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    return body