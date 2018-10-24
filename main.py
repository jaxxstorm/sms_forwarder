# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os

from twilio import rest
from twilio.twiml import messaging_response, voice_response

TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_NUMBER = os.environ['TWILIO_NUMBER']
DESTINATION_NUMBER = os.environ['DESTINATION_NUMBER']

def receive_sms(request):
    """Receives an SMS message and forwards to a number"""
    sender = request.values.get('From')
    body = request.values.get('Body')

    message = 'Message from: {} - {}'.format(sender, body)

    client = rest.Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    rv = client.messages.create(
        to=DESTINATION_NUMBER,
        from_=TWILIO_NUMBER,
        body=message
    )

    return str(message), 200, {'Content-Type': 'application/xml'}
