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

def mail(**kwargs):
    # Optional metadata first
    mta = kwargs.get('host', 'mail.apache.org:2025')
    sender = kwargs.get('sender', "Apache Infrastructure <users@infra.apache.org>")
    message_id = kwargs.get('messageid', email.utils.make_msgid("asfpy"))
    date = email.utils.formatdate()
    
    # Now the required bits
    recipients = kwargs.get('recipient', kwargs.get('recipients')) # Allow both names
    if not recipients:
        raise Exception("No recipients specified for email, can't send!")
    # We want this as a list
    if type(recipients) is str:
        recipients = [recipients]
    
    subject = kwargs.get('subject', 'No subject')
    subject_encoded = email.header.Header(subject, 'utf-8').encode()
    
    message = kwargs.get('body')
    if not message:
        raise Exception("No message body provided!")
    # py 2 vs 3 conversion
    if type(message) is bytes:
        message = message.decode('utf-8', errors='replace')
    
    # Construct the email
    msg = u"""From: %s
To: %s
Subject: %s
Message-ID: %s
Date: %s
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit

%s
""" % (sender, ", ".join(recipients), subject_encoded, message_id , date, message)
    msg = msg.encode('utf-8', errors='replace')
    
    # Try to dispatch message, do a raw fail if stuff happens.
    smtpObj = smtplib.SMTP(mta)
    smtpObj.sendmail(sender, recipients, msg)



def hipchat(message, **kwargs):
    """ HipChat messaging """
    room_id = kwargs.get('room', '669587')
    token = kwargs.get('token')
    if not token:
        raise Exception("No HipChat token provided!")
    sender = kwargs.get('from', 'ASF Infra')
    color = kwargs.get('color', 'green')
    notify = kwargs.get('notify', False)
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
    


def stride(message, **kwargs):
    """ Stride messaging """
    cloud_id = kwargs.get('cloud', '0d705148-c1b1-45ac-ac1e-54545f954526')
    room_id = kwargs.get('room', 'aa1d7946-4474-4f64-a5ca-6ea1298cb745')
    token = kwargs.get('token')
    if not token:
        raise Exception("No Stride bearer token provided!")
    sender = kwargs.get('from', 'ASF Infra')
    
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
