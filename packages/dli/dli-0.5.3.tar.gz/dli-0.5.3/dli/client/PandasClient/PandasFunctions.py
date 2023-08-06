import boto3
import pandas as pd
import io

s3_resource = boto3.resource('s3')


class PandasFunctions(object):
    def load_df(self, dataset, path, account_id=None, *args, **kwargs):
        if account_id is None:
            account_id = self.account_id

        keys = self.get_s3_access_keys_for_package(package_id=dataset.packageId, account_id=account_id)
        s3_client = boto3.client('s3',
                                 aws_access_key_id=keys['accessKeyId'],
                                 aws_secret_access_key=keys['secretAccessKey'],
                                 aws_session_token=keys['sessionToken'])

        path = path.replace("s3://", "")
        bucket, key = path.split('/', 1)
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        return pd.read_csv(io.BytesIO(obj['Body'].read()), *args, **kwargs)

    # Example usage
    # pd_read_csv_s3("s3://my_bucket/my_folder/file.csv", skiprows=2)
