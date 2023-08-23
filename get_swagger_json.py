# -*- coding: utf-8 -*-
# @Time : 2023/7/28 16:37
# @Author : weiliu
# @File : get_swagger_json.py
# @Software: PyCharm
# @Desc: 根据swagger链接，获取swagger中的json数据

import requests
import re
import os
import winreg
import locale
import json
import datetime
locale.setlocale(locale.LC_CTYPE, 'chinese')
from util.config_util import cf
import time

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                         '/107.0.0.0 Safari/537.36',
               'Content-Type': 'application/json'}

RE_PATTERN = re.compile(r'/\d+$|/$|/true|/false|/:[a-zA-Z]+|/{.+}|/[a-zA-Z0-9]+-[a-zA-Z0-9-]+-[a-zA-Z0-9]+[a-zA-Z0-9]$')



class ReadSwaggerApiDocs:
    '''
    获取swagger接口信息，与soso接口信息进行比较
    将比较结果写入excel中
    '''

    def __init__(self, url, project_name):
        #  http://192.168.32.85:9600/swagger-resources传入资源地址获取链接
        self.url = url
        self.resource_url = self.url + '/swagger-resources'
        self.project_name = project_name


    def get_api_resource(self, url):
        '''
        获取接口的返回信息，调用接口返回response
        :param url: 接口地址
        :return:
        '''
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json()
        else:
            print(res.text)
            return "获取接口文档失败"

    def get_swagger_modules(self):
        '''
        获取swagger中的接口模块
        :return:
        '''
        url = self.resource_url
        try:
            # res = ReadSwaggerApiDocs(self.url, self.project_name).get_api_resource(url)
            res = self.get_api_resource(url)
            modules_list = []
            # 循环获取模块信息
            for i in range(len(res)):
                modules_list.append(res[i]['url'])
            return modules_list
        except Exception as error:
            print(f'{error}')

    def get_single_module_res(self, module):
        '''
        获取单个模块的swagger.json文件
        :param module: 传入模块名称
        :return:
        '''

        module_url = self.url + module
        try:
            # 获取单个模块的接口swaggerjson文档信息
            res_module = self.get_api_resource(module_url)
            return res_module
        except Exception as e:
            print(f"获取接口文档失败，失败原因：{e}")

    # 创建文件夹
    def create_file(self):
        '''
        创建桌面文件夹
        :return:
        '''
        # 获取所有文件列表
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        # 选择桌面文件
        desktop = winreg.QueryValueEx(key, "Desktop")[0]
        path = desktop + '\项目接口文件夹'
        if os.path.exists(path):
            pass
        else:
            os.mkdir(path)
        date = str(datetime.datetime.now().strftime('%Y-%m-%d %H时%M分%S秒'))
        # 创建项目文件夹
        path_poject = path + f'\{self.project_name}项目'
        if os.path.exists(path_poject):
            pass
        else:
            os.mkdir(path_poject)
        return path_poject

    def write_json(self, module):
        '''
        写入json数据
        :param res_module:
        :return:
        '''
        path_poject = self.create_file()
        res_module = self.get_single_module_res(module)
        try:
            module_name = res_module['info']['title']
            with open(path_poject + f'\{module_name}' + '.json', mode='w') as f:
                json.dump(res_module, f)
            print(f'获取{self.project_name}的{module_name}模块json文件成功！')
        except Exception as e:
            print(e)

    def write_all_data(self):
        '''
        获取全部数据
        :return:
        '''
        modules = self.get_swagger_modules()
        if modules:
            for i in modules:
                res = self.write_json(i)
        else:
            print('模块不存在！')


if __name__ == '__main__':
    url = cf.get_key('swagger-url', 'url')
    project_name = cf.get_key('swagger-url', 'project_name')
    print(f"=============开始获取{project_name}项目swagger对应json=============")
    res_api = ReadSwaggerApiDocs(url, project_name).write_all_data()
    print('文件路径：桌面\\项目接口文件夹')
    time.sleep(5)
