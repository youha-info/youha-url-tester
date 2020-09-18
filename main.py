import json
import os
import sys

import boto3
import requests

OK_TEXT = "OK"
FAIL_TEXT = "FAIL"
AUTH_PREFIX = "Bearer "


def main():
    base_url = os.environ.get("INPUT_BASE_URL", None)
    target_uris = get_uris_from_comma_separated(os.environ.get("INPUT_URIS", None))
    user_pool_id = os.environ.get("INPUT_USER_POOL_ID", None)
    app_client_id = os.environ.get("INPUT_APP_CLIENT_ID", None)
    test_user_id = os.environ.get("INPUT_TEST_USER_ID", None)
    test_user_password = os.environ.get("INPUT_TEST_USER_PASSWORD", None)

    auth_token = authenticate_and_get_token(test_user_id, test_user_password, user_pool_id, app_client_id)

    result_message = "URL testing is done\n"
    is_all_pass = True

    for uri in target_uris:
        url = f"{base_url}{uri}"
        status_code = test_url(url, auth_token)
        if status_code != 200:
            is_all_pass = False
        result_message = write_message(url, status_code, result_message)

    write_message_to_stdout(result_message)

    if is_all_pass:
        sys.exit(0)
    else:
        sys.exit(1)


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


def write_message(url, status_code, message_text):
    message_text += f"{url}\t{status_code}\t"
    if status_code == 200:
        message_text += OK_TEXT
    else:
        message_text += FAIL_TEXT
    message_text += "\n"
    return message_text


def write_message_to_stdout(result_message):
    print(f"::set-output name=message::{result_message}")


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
        print(f"::set-output name=token_res::{resp['AuthenticationResult']}")
        auth_token = f"{AUTH_PREFIX} {resp['AuthenticationResult']['IdToken']}"
        print(f"::set-output name=token::{auth_token}")
    except Exception as e:
        print(f"::set-output name=error::{e}")
        pass
    return auth_token


def test_url(url, auth_token):
    response = requests.request(
        method='get',
        url=url,
        headers={'authorization': auth_token} if auth_token else None,
    )
    print(f"::debug::{url} - {response.status_code}\n")
    return response.status_code


if __name__ == "__main__":
    main()
