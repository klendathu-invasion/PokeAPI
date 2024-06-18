from datetime import datetime

import boto3
from fastapi import UploadFile
from fastapi.logger import logger
from pydantic import BaseModel

from ..config.env import settings
from ..errors.topic_error import CreateTopicError


class AWS(BaseModel):
    @classmethod
    def s3_upload_file(
        cls,
        file: UploadFile,
        bucket_name: str,
        filename: str,
        extra_args: dict | None = None,
    ) -> str | None:
        """This function send a file into a bucket in s3.

        :param file: the file to send
        :param bucket_name: the name of the source bucket
        :param filename: the name of the file in the bucket
        :param extra_args: extra args to send in the s3
        :type file: UploadFile
        :type bucket_name: str
        :type filename: str
        :type extra_args: dict
        :returns: None or the details of the error

        """
        s3_client = boto3.client("s3")
        try:
            s3_client.upload_fileobj(
                file.file, bucket_name, filename, ExtraArgs=extra_args
            )
        except Exception as e:
            return e.__repr__()

    @classmethod
    def s3_download_file(
        cls, bucket_name: str, bucket_key: str, file_path: str
    ) -> str | None:
        s3_client = boto3.client("s3")
        try:
            s3_client.download_file(bucket_name, bucket_key, file_path)
        except Exception as e:
            return e.__repr__()

    @classmethod
    def dynamodb_put_item(cls, table_name: str, item: dict) -> str | None:
        """This function send an item into a table in dynamodb.

        :param table_name: the name of the source table
        :param item: the item to send
        :type table_name: str
        :type item: dict
        :returns: None or the details of the error

        """
        dynamodb_client = boto3.client("dynamodb")
        try:
            dynamodb_client.put_item(TableName=table_name, Item=item)
        except Exception as e:
            return e.__repr__()

    @classmethod
    def dynamodb_scan(cls, table_name: str, scan: dict) -> str | None:
        """This function scan a table in dynamodb.

        :param table_name: the name of the source table
        :param scan: the scan
        :type table_name: str
        :type scan: dict
        :returns: None or the details of the error

        """
        dynamodb_client = boto3.client("dynamodb")
        try:
            result = dynamodb_client.scan(TableName=table_name, **scan)
        except Exception as e:
            return e.__repr__(), []
        return None, result["Items"]

    @classmethod
    def sns_publish(cls, topic_arn: str, subject: str, body: str, client=None) -> None:
        if not client:
            client = boto3.client("sns")

        if not body:
            body = f"""le critère *criteria* de l'objet {subject} a déclenché cette notification.
            Cordialement,
            """
        client.publish(
            TopicArn=topic_arn, Subject=subject, Message=body, MessageStructure="json"
        )

    @classmethod
    def sns_subscribe(cls, topic_arn: str, email: str, client=None) -> None | str:
        if not client:
            client = boto3.client("sns")

        subscription = client.subscribe(
            TopicArn=topic_arn,
            Protocol="email",
            Endpoint=email,
        )
        return subscription["SubscriptionArn"]

    @classmethod
    def sns_get_subscriptions_status(cls, topic_arn):
        client = boto3.client("sns")
        return client.list_subscriptions_by_topic(TopicArn=topic_arn)["Subscriptions"]

    @classmethod
    def sns_create_alert(cls, alert) -> None | str:
        sns_client = boto3.client("sns")

        try:
            topic = sns_client.create_topic(
                Name=datetime.today().strftime(f"%Y%m%d_%H-%M-%S-%f_{alert.subject}")
            )
        except sns_client.exceptions.AuthorizationErrorException as err:
            raise CreateTopicError(alert.subject) from err
        return topic["TopicArn"]

    @classmethod
    def sns_delete_alert(cls, alert) -> None:
        sns_client = boto3.client("sns")
        sns_client.delete_topic(TopicArn=alert.topic_arn)

    @classmethod
    def ses_create_alert(cls, topic_arn):
        ses_client = boto3.client("ses")
        set_name = cls._ses_id_from_sns_arn(topic_arn)
        configuration_set = {"Name": set_name}
        ses_client.create_configuration_set(ConfigurationSet=configuration_set)

    @classmethod
    def ses_delete_alert(cls, alert):
        ses_client = boto3.client("ses")
        ses_client.delete_configuration_set(
            ConfigurationSetName=cls._ses_id_from_sns_arn(alert.topic_arn)
        )

    @classmethod
    def send_notification_email(cls, alert, subscribers_email, body):
        ses_client = boto3.client("ses")
        email = settings.notification_email
        ses_client.send_email(
            Source=email,
            Destination={"ToAddresses": subscribers_email},
            Message={
                "Subject": {"Data": alert.subject},
                "Body": {"Html": {"Data": body}},
            },
            ConfigurationSetName=cls._ses_id_from_sns_arn(alert.topic_arn),
        )

    @classmethod
    def _ses_id_from_sns_arn(cls, topic_arn):
        return topic_arn.split(":")[-1]

    @classmethod
    def ses_verify_email(cls, email, client=None):
        if not client:
            client = boto3.client("ses")
        verification = client.verify_email_address(EmailAddress=email)
        return verification, client

    @classmethod
    def ses_get_verified_email_addresses(cls):
        client = boto3.client("ses")
        return client.list_verified_email_addresses()["VerifiedEmailAddresses"]
