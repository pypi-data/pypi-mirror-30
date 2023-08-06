import yaml
from .S3Access import S3Access


def to_dict(o, remove_fields=None):
    import inspect
    if remove_fields is None:
        remove_fields = []
    return {
        f: getattr(o, f)
        for f in o.__class__.__dict__.keys()
        if f not in remove_fields and
            not f.startswith('_') and
            hasattr(o, f) and
            not inspect.ismethod(getattr(o, f))
    }


class DatasetFunctions(object):
    def register_dataset_with_metadata(self, description, files, s3_prefix,
                                       keywords=[], tags={}, package_id=None, account_id=None):
        info = {
            'metadata': {
                'description': description,
                'format': 'csv',
                'keywords': keywords,
                'tags': tags,
                'version': 1,
                'lineage': {
                    'generatedBy': 'SDK upload',
                    'sources': ['internet']
                }
            },
            'uploads': [
                {
                    'files': files,
                    'target': {'s3': {'prefix': s3_prefix}}
                }
            ]
        }
        return self.register_dataset(info, package_id=package_id, account_id=account_id)

    def register_dataset_with_config_file(self, path, package_id=None, account_id=None):
        with open(path, 'r') as stream:
            try:
                info = yaml.load(stream)
                return self.register_dataset(info, package_id, account_id)
            except yaml.YAMLError as exc:
                print("Error: {}.".format(exc))

    def update_dataset(self, metadata, dataset_id=None, account_id=None):
        if not dataset_id:
            if "packageId" in metadata:
                dataset_id = metadata["datasetId"]

        if not dataset_id:
            raise Exception("Dataset Id must be provided as a parameter, or as part of metadata")

        if not account_id:
            if "accountId" in metadata:
                account_id = metadata["accountId"]

        if not account_id:
            raise Exception("Account Id must be provided as a parameter, or as part of metadata")

        dataset = self.get_dataset(dataset_id)
        dataset_as_dict = to_dict(dataset, ['self', 'id'])

        dataset_as_dict['datasetId'] = dataset_id
        if 'id' in dataset_id:
            del dataset_as_dict['id']
        dataset_as_dict.update(metadata)
        print(dataset_as_dict)
        response = dataset.update_dataset(__json=dataset_as_dict)
        print('response')
        print(response)
        return self.get_dataset(dataset_id)

    def register_dataset(self, info, package_id=None, account_id=None):
        uploaded_files = []
        metadata = info['metadata']

        if not package_id:
            if "packageId" in metadata:
                package_id = metadata["packageId"]

        if not package_id:
            raise Exception("Package Id must be provided as a parameter, or as part of metadata")

        if not account_id:
            if "accountId" in metadata:
                account_id = metadata["accountId"]

        if not account_id:
            raise Exception("Account Id must be provided as a parameter, or as part of metadata")

        package = self.get_package(package_id)

        if not hasattr(package, 's3Bucket'):
            raise Exception("There is no bucket associated with the package {}".format(package.id))

        s3_bucket = package.s3Bucket
        # s3_bucket = "ihsmarkit-dl-test-package"

        if 'uploads' in info:
            for upload in info['uploads']:
                uploaded_files.append(self._process_upload(upload, package_id, account_id, s3_bucket))

            flattened = [item for sublist in uploaded_files for item in sublist]
            metadata['files'] = ["s3://{}".format(f) for f in flattened]

        dataset = package.add_dataset(__json=metadata)

        return dataset

    def _process_upload(self, upload, package_id, account_id, s3_bucket):
        files = upload['files']
        target = upload['target']

        if 's3' in target:
            prefix = target['s3']['prefix']
            keys = self.get_s3_access_keys_for_package(package_id, account_id)
            s3_access = S3Access(keys['accessKeyId'], keys['secretAccessKey'], keys['sessionToken'])
            s3_location = "{}/{}".format(s3_bucket, prefix)
            uploaded_files = s3_access.upload_files_to_s3(files, s3_location)

            return uploaded_files
        else:
            raise Exception("Only S3 uploads are currently supported")

    def get_dataset(self, dataset_id):
        return self.get_root_siren().get_dataset(dataset_id=dataset_id)
