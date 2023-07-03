# 实现读取yaml文件的功能
import os
import yaml
import requests
from bs4 import BeautifulSoup
import json
from itertools import islice


def read_config():
    '''
    读取配置文件
    '''
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        return config


config = read_config()
# print(config)
icon_font_config = config['icon_font']
codesign_config = config['codesign']
TOKEN = codesign_config.get('token')
HEADERS = {
    'Origin': 'https://codesign.qq.com',
    'Referer': 'https://codesign.qq.com',
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'Authorization': 'Bearer ' + TOKEN,
}


def read_icon_font_js_to_svg(js_path, icon_font_config):
    '''
    读取iconfont的js拆分出svg文件
    '''
    with open(js_path, 'r', encoding='utf-8') as f:
        js_code = f.read()
        # 提取js代码中 单引号里面的内容
        svg = js_code.split("'")[1]
        # 将svg代码转换成BeautifulSoup对象
        svg = BeautifulSoup(svg, 'lxml')
        # 收集所有 symbol 标签
        symbols = svg.find_all('symbol')
        list1 = []
        # 遍历所有symbol标签
        for symbol in symbols:
            # 获取symbol标签的 id 属性值
            id = symbol.get('id')
            # print(id)
            # 获取symbol标签的 viewBox 属性值
            viewBox = symbol.get('viewbox')
            # 获取symbol标签的 所有属性
            # 获取symbol标签内所有子元素
            content = symbol.contents
            # 将获取到的内容拼接成一个字典
            dict1 = {
                'icon_id': id,
                'viewbox': viewBox,
                'height': icon_font_config['out_svg_height'],
                'width': icon_font_config['out_svg_width'],
                'contents': content
            }

            # 将字典添加到列表中
            list1.append(dict1)
        return list1


def read_icon_font_json_dict(json_path):
    '''
    读取iconfont的json文件并生成字典
    '''
    # 读json文件
    with open(json_path, 'r', encoding='utf-8') as f:
        # 装载数据
        json_data = json.load(f)
        # 获取json文件中的glyphs
        glyphs = json_data['glyphs']
        css_prefix = json_data['css_prefix_text']
        # 构建快速icon字典
        icon_dict = {}
        # 遍历icon列表
        for json_icon in glyphs:
            # 获取icon的class名称
            font_class = json_icon['font_class']
            font_class = '{p}{c}'.format(p=css_prefix, c=font_class)
            # 获取icon的unicode
            icon_unicode = json_icon['unicode']
            # 获取icon unicode_decimal
            icon_unicode_decimal = json_icon['unicode_decimal']
            # 将icon的名称和unicode添加到icon字典中
            icon_dict[font_class] = {
                'unicode': icon_unicode,
                'unicode_decimal': icon_unicode_decimal
            }
        return icon_dict


def create_icon_svg(icon_dict):
    '''
    创建一个icon的svg文件
    '''
    # 获取icon的id
    icon_id = icon_dict['icon_id']
    # 获取icon的viewbox
    viewbox = icon_dict['viewbox']
    # 获取icon的内容
    contents = icon_dict['contents']
    # 获取icon的高度
    height = icon_dict['height']
    # 获取icon的宽度
    width = icon_dict['width']
    # 创建一个svg对象
    svg = BeautifulSoup(features='lxml')
    # 创建一个svg标签
    svg_tag = svg.new_tag('svg')
    # 给svg标签添加 viewBox 属性
    svg_tag['viewBox'] = viewbox
    # 给svg标签添加 xmlns 属性
    svg_tag['xmlns'] = "http://www.w3.org/2000/svg"
    # 给svg标签添加 width height 属性
    svg_tag['width'] = width
    svg_tag['height'] = height
    # svg标签填充内容
    svg_tag.extend(contents)
    # 将svg标签添加到svg对象中
    svg.append(svg_tag)
    # 将svg对象转换成字符串
    svg_str = str(svg)
    return svg_str


def save_icon_svg(icon_str, icon_save_path):
    '''
    保存icon的svg文件
    '''
    with open(icon_save_path, 'w', encoding='utf-8') as f:
        f.write(icon_str)
        f.close()


def update_icon_unicode(icon_id,  class_name):
    '''
    更新icon的unicode
    '''
    update_request_url = codesign_config.get('update_request_url')
    update_request_method = codesign_config.get(
        'update_request_method')
    unicode = json_icon_unicode_dict.get(class_name)
    if unicode is None:
        raise Exception('没有找到{}的unicode'.format(class_name))
    unicode = unicode['unicode_decimal']
    print('更新{}的unicode为{}'.format(class_name, unicode))
    update_json_data = json.dumps({
        'unicode': unicode,
    })
    print(update_json_data)
    response = requests.request(update_request_method.lower(
    ), update_request_url.replace('{icon_id}', icon_id), headers=HEADERS, data=update_json_data)
    return response


def send_icons_to_server(json_data, json_icon_unicode_dict: dict):
    '''
    将icon上传到codeisgn服务器
    '''
    request_url = codesign_config['request_url']
    request_method = codesign_config['request_method']
    request_method = request_method.lower()
    unicode_sync = codesign_config['unicode_sync']

    if unicode_sync is True:
        update_request_url = codesign_config.get('update_request_url', None)
        update_request_method = codesign_config.get(
            'update_request_method', None)
        if update_request_url is None or update_request_method is None:
            # 抛出异常
            raise Exception(
                '同步unicode时，必须配置update_request_url和update_request_method')

    # 发送请求
    response = requests.request(
        request_method, request_url, headers=HEADERS, data=json_data)
    # 获取响应状态码
    status_code = response.status_code
    if status_code == 401:
        return 'token失效无权限访问'
    # 获取响应数据
    response_data = response.json()
    status_code = response.status_code
    # 合并response_data为一个逗号间隔字符串
    class_list_str = ','.join(map(response_data, lambda x: x['class_name']))

    # 判断响应状态码
    if status_code == 200:
        if unicode_sync is True:
            for icon in response_data:
                # print(icon)
                # 获取icon的class名称
                class_name = icon['class_name']
                # 获取icon的id
                icon_id = icon['id']
                # 更新icon的unicode
                update_icon_unicode(icon_id, class_name)

        return '[{}]上传成功'.format(class_list_str)
    else:
        return response_data


def get_icons(icon_list, json_icon_unicode_dict):
    batch_icon_list = []
    # 遍历icon列表
    for icon in icon_list:
        icon_str = create_icon_svg(icon)

        # 获取icon的id
        icon_id = icon['icon_id']
        # 获取icon的unicode
        icon_unicode = json_icon_unicode_dict.get(icon_id)
        if not icon_unicode is None:
            icon_unicode = icon_unicode['unicode_decimal']
        # 构建icon保存路径
        # icon_save_path = os.path.join(codesign_out_path, icon_id + '.svg')

        # 保存icon的svg文件
        # save_icon_svg(icon_str, icon_save_path)
        # 构建icon的json数据
        json_data_dict = {
            'name': icon_id,
            'class_name': icon_id,
            'unicode': icon_unicode,
            'original_svg': icon_str,
            'svg': icon_str
        }
        batch_icon_list.append(json_data_dict)
    return batch_icon_list


def chunk_list(it, limit):
    it = iter(it)
    return iter(lambda: list(islice(it, limit)), [])


if __name__ == '__main__':
    js_path = icon_font_config['js_path']
    icon_list = read_icon_font_js_to_svg(js_path, icon_font_config)
    # codesign输出路径
    codesign_out_path = codesign_config['out_path']
    # codesign输出路径不存在则创建
    if not os.path.exists(codesign_out_path):
        # 支持多级目录创建
        os.makedirs(codesign_out_path)
    json_path = icon_font_config['json_path']
    json_icon_unicode_dict = read_icon_font_json_dict(json_path)
    # 将icon_list列表拆分成20个一组上传
    for i in chunk_list(icon_list, 20):
        batch_icon_list = get_icons(i, json_icon_unicode_dict)
        # 将列表转换为json
        # codesign的proejctid
        project_id = codesign_config['project_id']
        json_data = {
            'project_id': project_id,
            'icons': batch_icon_list
        }
        json_data = json.dumps(json_data)
        # 发送请求

        response = send_icons_to_server(json_data, json_icon_unicode_dict)
        print(response)
