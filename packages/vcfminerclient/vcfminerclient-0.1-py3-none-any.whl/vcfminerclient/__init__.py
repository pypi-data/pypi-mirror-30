import os
import requests
import json
import re
import urllib
import subprocess


class VCFMinerClient:
    commands = dict(
        app=dict(
            base='securityuserapp/api',
            get_token='login',
            get_users='users',
            create_group='groups/add',
            get_groups='groups/foruser',
            delete_group='groups/delete',
            add_user_to_group='groups/addusertogroup',
            remove_user_from_group='groups/removeuserfromgroup',
            get_users_in_group='groups/usersingroup',
            set_permissions='permissions/set',
            get_permissions_for_group='resources/forgroup',
            get_vcf_for_user='resources/foruser',
            get_vcf_for_group='resources/forgroup',
            delete_vcf='resources/delete/$WORKSPACEID',
        ),
        db=dict(
            base='mongo_svr',
            upload_vcf='uploadvcf/user/$USERID/alias/$ALIASID',
            delete_vcf='ve/delete_workspace/$WORKSPACEID'),
        server=dict(
            create_user='java -jar bcrypt_test.jar /local2/tmp/app_VcfMiner/users.csv $USERNAME $PASSWORD',
        )
    )

    appkey = 'VcfMiner'

    def __init__(self, conf=dict(host='http://localhost:8888',
                                 username='Admin',
                                 password='temppass',
                                 server_host=None,
                                 server_user=None
                                 ),
                 logger=None):

        self.conf = conf
        self.logger = logger
        self.url = self.conf.get('host')

        self.logger.info('Connecting to {}'.format(self.url))

        auth = self.get_authentication()

        self.is_authenticate = auth.get('result').get('isAuthenticated') if auth.get('result') else False
        self.user_token = auth.get('result').get('userToken') if auth.get('result') else None
        self.headers = dict(usertoken=self.user_token)

        if auth.get('errors'):
            self.logger.error(auth.get('errors'))

        else:
            if self.is_authenticate:
                self.logger.info("User {} is authenticated".format(self.conf.get('username')))
            else:
                self.logger.info("User {} is not authenticated. Access Denied".format(self.conf.get('username')))

    def get_authentication(self):
        url = self.__build_url(cmd='get_token')
        data = dict(username=self.conf.get('username'),
                    password=self.conf.get('password'),
                    appkey=self.__class__.appkey)

        response = self.__curl(url=url, data=data)

        return response

    def create_user(self, new_username, new_password):
        params = {'$USERNAME': new_username,
                  '$PASSWORD': new_password}

        cmd = self.__build_cmd(cmd='create_user', params=params)

        response = self.__remote_cmd(user=self.conf.get('server_user'),
                                     host=self.conf.get('server_host'),
                                     cmd=cmd)

        return response

    def get_users(self):
        url = self.__build_url(cmd='get_users')
        response = self.__curl(url=url, headers=self.headers)

        return response

    def user_exists(self, username, delivery=False):
        users = self.get_users().get('result')
        if users:
            exists = True if filter(lambda user: user['username'] == username, users) else False
            return exists if not delivery else filter(lambda user: user['username'] == username, users)
        return False if not delivery else None

    def get_groups(self, username=None):
        url = self.__build_url(cmd='get_groups')
        data = dict(username=username if username else self.conf.get('username'))
        response = self.__curl(url=url, data=data, headers=self.headers)

        return response

    def group_exists(self, groupname, username=None, delivery=False):
        groups = self.get_groups(username=username).get('result')
        if groups:
            exists = True if filter(lambda group: group['groupName'] == groupname, groups) else False
            return exists if not delivery else filter(lambda group: group['groupName'] == groupname, groups)

        return False if not delivery else None

    def create_group(self, groupname):
        if self.group_exists(groupname=groupname):
            msg = "Group '{}' already exists".format(groupname)
            self.logger.warning(msg)

        else:
            url = self.__build_url(cmd='create_group')
            data = dict(groupname=groupname)
            response = self.__curl(url=url, data=data, headers=self.headers)
            return response

        return self.__format_response(warnings=msg)

    def delete_group(self, groupname):
        if not self.group_exists(groupname=groupname):
            msg = "Group '{}' not found".format(groupname)
            self.logger.warning(msg)

        else:
            url = self.__build_url(cmd='delete_group')
            data = dict(groupname=groupname)
            response = self.__curl(url=url, data=data, headers=self.headers, action='delete')
            return response

        return self.__format_response(warnings=msg)

    def add_user_to_group(self, username, groupname):
        if self.user_exists(username=username):
            if not self.group_exists(groupname=groupname, username=username):
                url = self.__build_url(cmd='add_user_to_group')
                data = dict(username=username,
                            groupname=groupname)
                response = self.__curl(url=url, data=data, headers=self.headers)

                return response

            else:
                msg = "User '{}' is already in the group '{}'".format(username, groupname)
                self.logger.warning(msg)

        else:
            msg = "User '{}' not found in server".format(username, self.url)
            self.logger.warning(msg)

        return self.__format_response(warnings=msg)

    def remove_user_from_group(self, username, groupname):
        if self.user_exists(username=username):
            if self.group_exists(groupname=groupname, username=username):
                url = self.__build_url(cmd='remove_user_from_group')
                data = dict(username=username,
                            groupname=groupname)
                response = self.__curl(url=url, data=data, headers=self.headers)

                return response

            else:
                msg = "User '{}' not found in the group '{}'".format(username, groupname)
                self.logger.warning(msg)

        else:
            msg = "User '{}' not found in server".format(username, self.url)
            self.logger.warning(msg)

        return self.__format_response(warnings=msg)

    def get_users_in_group(self, groupname):

        if self.group_exists(groupname=groupname):
            url = self.__build_url(cmd='get_users_in_group')
            data = dict(groupname=groupname)
            response = self.__curl(url=url, data=data, headers=self.headers)

            return response

        else:
            msg = "Group '{}' not found in server '{}'".format(groupname, self.url)
            self.logger.warning(msg)

        return self.__format_response(warnings=msg)

    def get_permissions_for_group(self, groupname):

        if self.group_exists(groupname=groupname):
            url = self.__build_url(cmd='get_permissions_for_group')
            data = dict(groupname=groupname)
            response = self.__curl(url=url, data=data, headers=self.headers)

            return response

        else:
            msg = "Group '{}' not found in server '{}'".format(groupname, self.url)
            self.logger.warning(msg)

        return self.__format_response(warnings=msg)

    def vcf_exists(self, vcfname, delivery=False):
        return self.vcf_belongs_to_user(vcfname,
                                        username=self.conf.get('username'),
                                        delivery=delivery)

    def vcf_belongs_to_user(self, vcfname, username, delivery=False):
        resources = self.get_vcf_for_user(username=username).get('result')
        if resources:
            exists = True if filter(lambda r: "name={},".format(vcfname) in r['description'], resources) else False
            return exists if not delivery else filter(lambda r: "name={},".format(vcfname) in r['description'], resources)

        return False if not delivery else None

    def vcf_belongs_to_group(self, vcfname, groupame, delivery=False):
        resources = self.get_vcf_for_group(groupname=groupame).get('result')
        if resources:
            exists = True if filter(lambda r: "name={},".format(vcfname) in r['description'], resources) else False
            return exists if not delivery else filter(lambda r: "name={},".format(vcfname) in r['description'], resources)

        return False if not delivery else None

    def get_vcf_for_group(self, groupname):

        if self.group_exists(groupname=groupname):
            url = self.__build_url(cmd='get_vcf_for_group')
            data = dict(groupname=groupname)
            response = self.__curl(url=url, data=data, headers=self.headers)

            return response

        else:
            msg = "Group '{}' not found in server '{}'".format(groupname, self.url)
            self.logger.warning(msg)

        return self.__format_response(warnings=msg)

    def get_vcf_for_user(self, username):

        if self.user_exists(username=username):
            url = self.__build_url(cmd='get_vcf_for_user')
            data = dict(username=username)
            response = self.__curl(url=url, data=data, headers=self.headers)

            return response

        else:
            msg = "User '{}' not found in server '{}'".format(username, self.url)
            self.logger.warning(msg)

        return self.__format_response(warnings=msg)

    def upload_vcf(self, vcfpath, vcfname=None):

        def is_compressed(filename):
            extension = os.path.splitext(filename)[1]
            return extension == 'gz' or extension == 'tgz' or extension == 'bgz'

        if os.path.isfile(vcfpath):

            vcfname = vcfname if vcfname else os.path.basename(vcfpath)
            if not self.vcf_exists(vcfname):
                params = {'$USERID': self.conf.get('username'), '$ALIASID': vcfname}
                url = self.__build_url(cmd='upload_vcf', dest='db', params=params)
                files = {'file': open(vcfpath, 'rb')}
                headers = {'file-compression': '.gz' if is_compressed(vcfpath) else 'none'}
                headers.update(self.headers)

                response = self.__curl(url=url, headers=headers, files=files)

                return response

            else:
                return self.__format_response(success=False,
                                              errors='Vcf {} already exists.'.format(vcfname))
        else:
            return self.__format_response(success=False,
                                          errors='{} does not exist. Please specify the full path '
                                                 'to the VCF file.'.format(vcfpath))

    def add_vcf_to_group(self, vcfname, groupname):
        if self.group_exists(groupname=groupname):
            vcf_obj = self.vcf_exists(vcfname=vcfname, delivery=True)
            if vcf_obj:
                if not self.vcf_belongs_to_group(vcfname=vcfname, groupname=groupname):
                    group_obj = self.group_exists(groupname=groupname, delivery=True)
                    url = self.__build_url(cmd='set_permissions')
                    data = dict(
                        resourceId=vcf_obj[0].get('id'),
                        userOrGroupId=group_obj[0].get('id'),
                        isUser=False,
                        isReadAuthority=True,
                        isWriteAuthority=True,
                        isExecuteAuthority=True,
                        actions=[]
                    )
                    headers = {'Content-Type': 'application/json'}
                    headers.update(self.headers)

                    response = self.__curl(url=url, data=data, headers=headers, isjson=True)

                    return response
                else:
                    msg = "VCF '{} already in Group '{}'".format(vcfname, groupname)
                    self.logger.warning(msg)
            else:
                msg = "VCF '{} not found in server '{}'".format(vcfname, self.url)
                self.logger.warning(msg)
        else:
            msg = "Group '{}' not found in server '{}'".format(groupname, self.url)
            self.logger.warning(msg)

        return self.__format_response(warnings=msg)

    def add_vcf_to_user(self, vcfname, username):

        if self.user_exists(username=username):
            vcf_obj = self.vcf_exists(vcfname=vcfname, delivery=True)
            if vcf_obj:
                if not self.vcf_belongs_to_user(vcfname=vcfname, username=username):
                    group_obj = self.user_exists(username=username, delivery=True)
                    url = self.__build_url(cmd='set_permissions')
                    data = dict(
                        resourceId=vcf_obj[0].get('id'),
                        userOrGroupId=group_obj[0].get('id'),
                        isUser=True,
                        isReadAuthority=True,
                        isWriteAuthority=True,
                        isExecuteAuthority=True,
                        actions=[]
                    )
                    headers = {'Content-Type': 'application/json'}
                    headers.update(self.headers)

                    response = self.__curl(url=url, data=data, headers=headers, isjson=True)

                    return response
                else:
                    msg = "VCF '{} already in User '{}'".format(vcfname, username)
                    self.logger.warning(msg)
            else:
                msg = "VCF '{} not found in server '{}'".format(vcfname, self.url)
                self.logger.warning(msg)
        else:
            msg = "User '{}' not found in server '{}'".format(username, self.url)
            self.logger.warning(msg)

        return self.__format_response(warnings=msg)

    def delete_vcf(self, vcfname):
        vcf_obj = self.vcf_exists(vcfname=vcfname, delivery=True)

        if vcf_obj:

            params = {'$WORKSPACEID': vcf_obj[0].get('key')}
            url = self.__build_url(cmd='delete_vcf', dest='db', params=params)
            response = self.__curl(url=url, action='delete')
            status = response.get('result').get('status') if response.get('result') and response.get('result').get(
                'status') else None

            if status and '{} deleted'.format(vcf_obj[0].get('key')) in status:
                url = self.__build_url(cmd='delete_vcf', dest='app', params=params)
                self.__curl(url=url, headers=self.headers, action='post')

            return response
        else:
            msg = "VCF '{} not found in server '{}'".format(vcfname, self.url)
            self.logger.warning(msg)

        return self.__format_response(warnings=msg)

    def __build_url(self, cmd, dest='app', params=dict()):
        if dest in self.__class__.commands and cmd in self.__class__.commands.get(dest):
            url = os.path.join(self.url,
                               self.__class__.commands.get(dest).get('base'),
                               self.__class__.commands.get(dest).get(cmd))

            for old, new in params.iteritems():
                url = url.replace(old, new)

            return url

    def __build_cmd(self, cmd, dest='server', params=dict()):
        if dest in self.__class__.commands and cmd in self.__class__.commands.get(dest):
            cmd = self.__class__.commands.get(dest).get(cmd)

            for old, new in params.iteritems():
                cmd = cmd.replace(old, new)

            return cmd

    def __curl(self, url, data=None, headers=None, files=None, action='post', isjson=False):
        data = urllib.urlencode(data) if data and not isjson else data
        data = json.dumps(data) if data and isjson else data
        try:
            if 'delete' in action:
                r = requests.delete(url, data=data, headers=headers)
            elif 'post' in action:
                r = requests.post(url, data=data, headers=headers, files=files)

        except Exception as e:
            return self.__format_response(success=False, errors=str(e))
        try:
            return self.__format_response(result=json.loads(r.content))
        except Exception as e:
            result = re.sub(re.compile('<.*?>'), '', r.content) if re.sub(re.compile('<.*?>'), '', r.content) != '' else None
            return self.__format_response(result=result, warnings='No JSON object could be decoded')

    def __remote_cmd(self, user, host, cmd):
        remote = "{}@{}".format(user, host)
        try:
            ssh = subprocess.Popen(["ssh", remote, cmd],
                                   shell=False,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

            result = [line.rstrip('\n') for line in ssh.stdout.readlines()]
            error = ssh.stderr.readlines()

            if error:
                result = self.__format_response(success=False, errors=error)
            else:
                result = self.__format_response(success=True, result=result)
        except Exception as e:
            result = self.__format_response(success=False, errors=str(e))

        return result

    def __format_response(self, success=True, result=None, errors=None, warnings=None):
        return dict(success=success,
                    result=result,
                    errors=errors,
                    warnings=warnings)


