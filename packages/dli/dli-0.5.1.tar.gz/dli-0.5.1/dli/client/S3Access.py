import s3fs
import os


class S3Access:
    def __init__(self, key, secret, token):
        self.s3fs = s3fs.S3FileSystem(key=key, secret=secret, token=token)

    def upload_file_to_s3(self, file, s3_location):
        print("......uploading {} to {}".format(file, s3_location))
        file_name = os.path.basename(file)
        target = "{}{}".format(s3_location, file_name)
        self.s3fs.put(file, target)
        print("............done.")
        return target

    def upload_files_to_s3(self, files, s3_location):
        uploaded_files = []

        for f in files:
            print("f: {}, s3: {}".format(f, s3_location))

            if not os.path.exists(f):
                raise Exception("File / directory specified ({}) for upload does not exist.".format(f))

            if os.path.isfile(f):
                print("...detected file: {}".format(f))
                tf = self.upload_file_to_s3(f, s3_location)
                uploaded_files.append(tf)
            elif os.path.isdir(f):
                print("... detected directory: {}".format(f))
                files = [s for s in os.listdir(f) if os.path.isfile("{}/{}".format(f, s))]
                for s in files:
                    uploaded_files.append(self.upload_file_to_s3("{}{}".format(f, s), s3_location))

        return uploaded_files
