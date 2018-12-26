#! /usr/bin/env python
import requests
import json
import sys

alarm_url = sys.argv[1]
profile_url = sys.argv[2]
auth_token = sys.argv[3]
filename = sys.argv[4]
auth_type = sys.argv[5]

HEADERS = {'content-type': 'application/json'}
HEADERS['X-Auth-Token'] = auth_token
HEADERS['X-Auth-Type'] = auth_type

CERT_VERIFY_FLAG = False


def post_alarm(event_rule):
    data = json.dumps(event_rule)
    resp = requests.post(url=alarm_url, data=data,
                         headers=HEADERS, verify=CERT_VERIFY_FLAG)
    if resp.status_code != 200:
        print ("Post fail to alarm_url {}: {}".
               format(alarm_url, resp.text))
        sys.exit(1)


def alarm_exists(rule_id):
    url = alarm_url + '/' + rule_id
    resp = requests.get(url=url, headers=HEADERS, verify=CERT_VERIFY_FLAG)
    if resp.status_code == 404:
        return False
    if resp.status_code == 200:
        return True
    print ("Fail to get alarm with id {}: {}".
           format(rule_id, resp.text))
    sys.exit(1)


with open(filename) as profile_file:
    try:
        profile = json.load(profile_file)
    except Exception as e:
        raise Exception("Exception in open profile json file: {}".format(e))

analytics_rules = profile.get('rules')
if not analytics_rules:
    raise Exception("No analytics rules configured")

for rule in analytics_rules:
    if not alarm_exists(rule['EventRuleId']):
        post_alarm(rule)

profile = profile.get('profile')
if profile is not None:
    # check if this profile is already posted, if yes, we need to delete it
    # first then post it
    scope = profile['CompositeAlarmScope']
    type = profile['CompositeAlarmType']
    url = profile_url + '/{}/{}'.format(type, scope)
    resp = requests.get(url=url, headers=HEADERS,
                        verify=CERT_VERIFY_FLAG)
    if resp.status_code == 200:
        profile_id = json.loads(resp.text)['AnalyticsProfile']['AnalyticsId']
        url = profile_url + '/' + profile_id
        resp = requests.delete(url=url, headers=HEADERS,
                               verify=CERT_VERIFY_FLAG)
        if resp.status_code != 200:
            print ("Delete fail to analytics_profile_url {}: {}".
                   format(profile_url, resp.text))
    data = json.dumps(profile)
    resp = requests.post(url=profile_url, data=data,
                         headers=HEADERS, verify=CERT_VERIFY_FLAG)
    if resp.status_code != 200:
        print ("Post fail to analytics_profile_url {}: {}".
               format(profile_url, resp.text))
