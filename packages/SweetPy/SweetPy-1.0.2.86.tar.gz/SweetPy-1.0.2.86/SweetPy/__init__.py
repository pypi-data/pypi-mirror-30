import os
import platform
from sys import argv

def check_runserver():
    if 'uwsgi' in argv:
        return True
    _argv_count = len(argv)
    if _argv_count > 1:
        for i in range(1, _argv_count):
            _argv = argv[i].lower()
            if _argv.startswith('runserver'):
                return True
    return False


def get_dirs_name_by_path(path):
    result = []
    for dirpath, dirnames, filenames in os.walk(path):
        for dir in dirnames:
            result.append(dir)
        break
    return result
def get_project_setting_path():
    sysstr = platform.system()

    local_path = os.getcwd()
    dirs = get_dirs_name_by_path(local_path)
    for _dir in dirs:
        if sysstr.lower() == 'windows':
            filename = local_path + '\\' + _dir + '\\settings.py'
            if os.path.exists(filename):
                return _dir
        else:
            filename = local_path + '/' + _dir + '/settings.py'
            if os.path.exists(filename):
                return _dir

def set_environ():
    if 'production' in argv:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", get_project_setting_path() + "_production.settings")
        argv.remove('production')
        print('SeetPy启动生产环境配置文件...')
    elif 'uwsgi' in argv:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", get_project_setting_path() + "_production.settings")
        print('SeetPy启动生产环境配置文件...')
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", get_project_setting_path() + ".settings")
        print('SeetPy启动默认配置文件...')
set_environ()

from django.conf import settings

settings.INSTALLED_APPS.append('SweetPy.geely_auth')

settings.MIDDLEWARE.insert(0,'SweetPy.django_middleware.tracker.request_tracker')

#如果是测试 则不连接应用云
import sys
istest = len(sys.argv)>1  and sys.argv[1].lower() == 'test'
if istest:
    settings.SWEET_CLOUD_ENABLED = False

if check_runserver() or istest:
    from rest_framework import response
    import SweetPy.extend.response_plus

    response.Response = SweetPy.extend.response_plus.Response
    from rest_framework import mixins
    import SweetPy.extend.mixins_plus

    mixins.ListModelMixin = SweetPy.extend.mixins_plus.ListModelMixin
    mixins.RetrieveModelMixin = SweetPy.extend.mixins_plus.RetrieveModelMixin
    mixins.DestroyModelMixin = SweetPy.extend.mixins_plus.DestroyModelMixin
    mixins.CreateModelMixin = SweetPy.extend.mixins_plus.CreateModelMixin

    import SweetPy.extend.api_view_plus

    from rest_framework import views
    import SweetPy.extend.view_plus

    views.exception_handler = SweetPy.extend.view_plus.exception_handler
    import SweetPy.extend.swagger_plus
    import SweetPy.setting

    import SweetPy.sweet_framework.sweet_framework_views
    import SweetPy.sweet_framework_cloud.sweet_framework_cloud_views
    import SweetPy.geely_auth.geely_sso

    if os.environ.get("RUN_MAIN") == "true":
        import SweetPy.scheduler