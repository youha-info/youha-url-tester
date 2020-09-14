import json
import os
import sys

import boto3
import requests

OK_EMOJI = ":white_check_mark:"
FAIL_EMOJI = ":no_entry_sign:"
BLOCK_QUOTE = ">"
AUTH_PREFIX = "Bearer "


def main():
    base_url = os.environ.get("INPUT_BASE_URL", None)
    target_uris = get_uris_from_comma_separated(os.environ.get("INPUT_URIS", None))
    slack_webhook_url = os.environ.get("INPUT_SLACK_WEB_HOOK", None)
    user_pool_id = os.environ.get("INPUT_USER_POOL_ID", None)
    app_client_id = os.environ.get("INPUT_APP_CLIENT_ID", None)
    test_user_id = os.environ.get("INPUT_TEST_USER_ID", None)
    test_user_password = os.environ.get("INPUT_TEST_USER_PASSWORD", None)

    auth_token = authenticate_and_get_token(test_user_id, test_user_password, user_pool_id, app_client_id)

    webhook_text = "URL testing is done\n"

    for uri in target_uris:
        url = f"{base_url}{uri}"
        status_code = test_url(url, auth_token)
        webhook_text = write_message(url, status_code, webhook_text)

    post_to_slack(webhook_text, slack_webhook_url)

    sys.exit(0)


def get_uris_from_comma_separated(uris):
    if not uris:
        return []
    arr_uris = []
    try:
        if ',' in uris:
            arr_uris = [uri.strip() for uri in uris.split(',')]
        else:
            arr_uris = [uris]
    except IndexError:
        pass

    return arr_uris


def write_message(url, status_code, webhook_text):
    webhook_text += f"{BLOCK_QUOTE} {url}\t`{status_code}`\t"
    if status_code == 200:
        webhook_text += OK_EMOJI
    else:
        webhook_text += FAIL_EMOJI
    webhook_text += "\n"
    return webhook_text


def post_to_slack(webhook_text, webhook_url):
    requests.post(
        webhook_url, data=json.dumps({
            "text": webhook_text
        }),
        headers={'Content-Type': 'application/json'}
    )


def authenticate_and_get_token(username: str, password: str,
                               user_pool_id: str, app_client_id: str):
    auth_token = None
    try:
        client = boto3.client('cognito-idp')
        resp = client.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=app_client_id,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password
            }
        )
        auth_token = f"{AUTH_PREFIX} {resp['AuthenticationResult']['AccessToken']}"
    except Exception as e:
        pass
    return auth_token


def test_url(url, auth_token):
    response = requests.request(
        method='get',
        url=url,
        headers={'authorization': auth_token} if auth_token else None,
    )
    sys.stdout.write(f"::debug::{url} - {response.status_code}\n")
    return response.status_code


if __name__ == "__main__":
    main()
