"""Exercise Flask request parsing and the real Twilio SDK without sending SMS."""
import importlib
import json
import os
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs

from flask import Flask, request
from requests import Response
from twilio.base.exceptions import TwilioRestException


class ForwarderTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {
            "TWILIO_ACCOUNT_SID": "AC" + "0" * 32,
            "TWILIO_AUTH_TOKEN": "test-only-not-a-real-credential",
            "TWILIO_NUMBER": "+15005550006",
            "DESTINATION_NUMBER": "+15005550009",
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.main = importlib.reload(importlib.import_module("main"))
        self.app = Flask(__name__)
        self.app.add_url_rule("/", view_func=lambda: self.main.receive_sms(request), methods=["POST"])
        self.transport = patch("requests.sessions.Session.send")
        self.send = self.transport.start()
        self.addCleanup(self.transport.stop)
        response = Response()
        response.status_code = 201
        response._content = json.dumps({"sid": "SM" + "0" * 32}).encode()
        response.headers["Content-Type"] = "application/json"
        self.send.return_value = response

    def test_form_message_is_serialized_by_twilio_and_response_is_preserved(self):
        response = self.app.test_client().post("/", data={"From": "+15005550001", "Body": "Hello & goodbye ☃"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/xml")
        self.assertEqual(response.get_data(as_text=True), "Message from: +15005550001 - Hello & goodbye ☃")
        self.send.assert_called_once()
        prepared = self.send.call_args.args[0]
        self.assertEqual(prepared.method, "POST")
        self.assertEqual(prepared.url, "https://api.twilio.com/2010-04-01/Accounts/AC" + "0" * 32 + "/Messages.json")
        self.assertEqual(parse_qs(prepared.body), {
            "To": ["+15005550009"], "From": ["+15005550006"],
            "Body": ["Message from: +15005550001 - Hello & goodbye ☃"],
        })
        self.assertTrue(prepared.headers["Authorization"].startswith("Basic "))

    def test_query_parameters_remain_supported(self):
        response = self.app.test_client().post("/", query_string={"From": "+15005550001", "Body": "query"})
        self.assertEqual(response.get_data(as_text=True), "Message from: +15005550001 - query")
        self.assertEqual(self.send.call_count, 1)

    def test_missing_fields_preserve_existing_behavior(self):
        response = self.app.test_client().post("/")
        self.assertEqual(response.get_data(as_text=True), "Message from: None - None")
        self.assertEqual(self.send.call_count, 1)

    def test_twilio_failure_is_not_reported_as_success(self):
        self.send.return_value.status_code = 400
        self.send.return_value._content = b'{"code": 21211, "message": "Invalid destination"}'
        with self.app.test_request_context("/", method="POST", data={"From": "sender", "Body": "message"}):
            with self.assertRaises(TwilioRestException):
                self.main.receive_sms(request)
        self.assertEqual(self.send.call_count, 1)


if __name__ == "__main__":
    unittest.main()
