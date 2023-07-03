import json
import os
import yaml


def read_config() -> dict:
    '''
    读取配置文件
    '''
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        return config


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
            name = json_icon['name']
            # 将icon的名称和unicode添加到icon字典中
            icon_dict[font_class] = {
                'class': font_class,
                'name': name,
                'unicode': icon_unicode,
                'unicode_decimal': icon_unicode_decimal,
            }
        return icon_dict


def read_codesign_font_json_dict(json_path):
    '''
    读取codesign的json文件并生成字典
    '''
    # 读json文件
    with open(json_path, 'r', encoding='utf-8') as f:
        # 装载数据
        json_data = json.load(f)
        # 获取json文件中的icons
        icons = json_data['icons']
        # 构建快速icon字典
        icon_dict = {}
        # 遍历icon列表
        for icon in icons:
            class_name = icon['class_name']
            unicode = icon['unicode']
            unicode_decimal = icon['unicode_decimal']
            name = icon['name']
            icon_dict[class_name] = {
                'class': class_name,
                'name': name,
                'unicode': unicode,
                'unicode_decimal': unicode_decimal
            }
        return icon_dict


def write_error_log(error):
    """
    写错误日志
    """
    error_log_path = os.path.join(os.path.dirname(__file__), 'error.log')        
    with open(error_log_path, 'a', encoding='utf-8') as f:
        f.write(error)
        f.write('\n')
        f.close()