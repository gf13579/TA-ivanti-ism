# encoding = utf-8

import os
import sys
import time
import datetime
import requests
import json
from urllib import unquote
import ism
import time

def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # global_account = definition.parameters.get('global_account', None)
    # tenant = definition.parameters.get('tenant', None)
    pass

def collect_events(helper, ew):

    loglevel = helper.get_log_level()
    opt_global_account = helper.get_arg('global_account')
    input_stanza = helper.get_input_stanza()
    account = helper.get_user_credential_by_username(opt_global_account['username'])
    opt_username = account['username']
    opt_password = account['password']
    opt_role = helper.get_global_setting("role")
    opt_tenant = helper.get_global_setting("tenant")
    opt_parameters = unquote(helper.get_arg('parameters'))

    base_url = 'https://' + opt_tenant

    helper.log_debug("ISM TA input called with base_url: " + base_url)
    auth_token = ism.authenticate(opt_tenant,opt_username,opt_password,opt_role)

    values = ism.get_servicereqs(auth_token, base_url, opt_parameters)

    t =  "%.3f" % time.time()

    for v in values:
        event = helper.new_event(time=t, source=helper.get_input_type(), index=helper.get_output_index(), sourcetype=helper.get_sourcetype(), data=json.dumps(v))
        ew.write_event(event)
