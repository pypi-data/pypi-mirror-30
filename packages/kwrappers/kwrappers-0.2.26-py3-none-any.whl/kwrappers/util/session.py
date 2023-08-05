import os
import boto3


class Session(boto3.session.Session):

    def __init__(self, region=None, profile='default', role=None, mfa_serial=None, mfa_token=None):
        """Returns an AWS session instance.  If no parameters are provided, keys from `.aws/credentials` 'default' profile are used.

            Kwargs (all optional):
                region (str): An AWS region
                profile (str): A profile with API keys as configured in ~/.aws/credentials file. Not to be used with roles.
                role (str): AWS Arn of the role the user is assuming. If None, the users identity is used.
                mfa_serial (str): AWS Arn of the users Multi-Factor authentication device.
                mfa_token (str): 6 digit Multi-Factor Authentication code.

            Example:
                session = Session()
                s3client = session.client('s3')
        """

        if profile and role:
            raise AttributeError("Either a profile should be used OR a role assumed. Not both.")

        if (mfa_serial and not mfa_token) or (mfa_token and not mfa_serial):
            raise AttributeError("If using MFA, provide both a serial and a token.")

        params = {
            'profile_name': profile,
            'region_name': region,
        }

        if role:
            creds = _get_creds(role, mfa_serial, mfa_token)
            params.update({
                'aws_access_key_id': creds['AccessKeyId'],
                'aws_secret_access_key': creds['SecretAccessKey'],
                'aws_session_token': creds['SessionToken'],
            })

        boto3.session.Session.__init__(self, **{k: v for k, v in params.items() if v})


def _get_creds(role, mfa_serial, mfa_token):
    # TODO: Check for HTTP fail
    params = {
        "RoleArn": role,
        "RoleSessionName": 'ecs-deploy-session',
        "DurationSeconds": 3600,
        "SerialNumber": mfa_serial,
        "TokenCode": mfa_token
    }
    return boto3.client('sts').assume_role(**{k: v for k, v in params.items() if v})['Credentials']
