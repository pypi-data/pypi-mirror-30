#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This is the standardized email library for sending emails.
It handles encoding options and required metadata,
as well as defaulting where bits are missing.

It also contains hipchat and stride integrations
"""

import email.utils
import email.header
import smtplib
import requests

def uniaddr(addr):
    """ Unicode-format an email address """
    bits = email.utils.parseaddr(addr)
    return email.utils.formataddr((email.header.Header(bits[0], 'utf-8').encode(), bits[1]))

def mail(
        host = 'mail.apache.org:2025',
        sender = "Apache Infrastructure <users@infra.apache.org>",
        recipient = None,
        recipients = None,
        subject = 'No subject',
        message = None,
        messageid = None
        ):
    # Optional metadata first
    if not messageid:
        messageid = email.utils.make_msgid("asfpy")
    date = email.utils.formatdate()
    
    # Now the required bits
    recipients = recipient or recipients # We accept both names, 'cause
    if not recipients:
        raise Exception("No recipients specified for email, can't send!")
    # We want this as a list
    if type(recipients) is str:
        recipients = [recipients]
    
    # py 2 vs 3 conversion
    if type(sender) is bytes:
        sender = sender.decode('utf-8', errors='replace')
    if type(message) is bytes:
        message = message.decode('utf-8', errors='replace')
    for i, rec in enumerate(recipients):
        if type(rec) is bytes:
            rec = rec.decode('utf-8', errors='replace')
            recipients[i] = rec
            
    # Recipient, Subject and Sender might be unicode.
    subject_encoded = email.header.Header(subject, 'utf-8').encode()
    sender_encoded = uniaddr(sender)
    recipient_encoded = ", ".join([uniaddr(x) for x in recipients])
    
    if not message:
        raise Exception("No message body provided!")
    
    # Construct the email
    msg = u"""From: %s
To: %s
Subject: %s
Message-ID: %s
Date: %s
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit

%s
""" % (sender_encoded, recipient_encoded, subject_encoded, messageid , date, message)
    msg = msg.encode('utf-8', errors='replace')
    
    # Try to dispatch message, do a raw fail if stuff happens.
    smtpObj = smtplib.SMTP(host)
    # Note that we're using the raw sender here...
    smtpObj.sendmail(sender, recipients, msg)



def hipchat(
    message,
    token = None,
    room_id = '669587',
    sender = 'ASF Infra',
    color = 'green',
    notify = False
    ):
    """ HipChat messaging """
    if not token:
        raise Exception("No HipChat token provided!")
    if notify and notify != '0':
        notify = '1'
    else:
        notify = '0'
    payload = {
            'room_id': str(room_id),
            'auth_token': token,
            'from': sender,
            'message_format': 'html',
            'notify': notify,
            'color': color,
            'message': message
        }
    requests.post('https://api.hipchat.com/v1/rooms/message', data = payload)
    


def stride(
    message,
    token = None,
    cloud_id = '0d705148-c1b1-45ac-ac1e-54545f954526',
    room_id = 'aa1d7946-4474-4f64-a5ca-6ea1298cb745'
    ):
    """ Stride messaging """
    if not token:
        raise Exception("No Stride bearer token provided!")
    
    payload = {
        "body": {
            "version": 1,
            "type": "doc",
            "content": [{
                    "type": "paragraph",
                    "content": [{
                            "type": "text",
                            "text": message
                        }
                    ]
                }
            ]
        }
    }
    headers = {'Authorization': 'Bearer %s' % token}
    requests.post('https://api.atlassian.com/site/%s/conversation/%s/message' % (cloud_id, room_id), headers = headers, json = payload)
