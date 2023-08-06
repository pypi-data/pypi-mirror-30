class PackageFunctions(object):
    def get_s3_access_keys_for_package(self, package_id, account_id):
        key = '{}-{}'.format(account_id, package_id)

        if key in self.ctx.s3_keys:
            return self.ctx.s3_keys[key]

        root = self.ctx.get_root_siren()
        pf = root.package_forms()
        keys = pf.request_access_keys(accountId=account_id, package_id=package_id)

        val = {
            "accessKeyId": keys.accessKeyId,
            "packageId": keys.packageId,
            "secretAccessKey": keys.secretAccessKey,
            "sessionToken": keys.sessionToken
        }

        self.ctx.s3_keys[key] = val

        return val

    def get_package(self, package_id):
        package = self.get_root_siren().get_package(package_id=package_id)
        return package

    def search_packages(self, term):
        packages = self.get_root_siren().list_packages(query=term)
        return packages

