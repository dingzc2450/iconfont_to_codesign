"""
验证iconfont和codesign的关键数据是否一致
"""
from icon_r_util import read_icon_font_json_dict, read_codesign_font_json_dict, read_config
config = read_config()
icon_font_json_path = config['icon_font'].get('json_path')
codesign_json_path = config['codesign'].get('json_path')

if __name__ == "__main__":
    if (icon_font_json_path is None):
        print('icon_font_json_path is None')
        exit(1)
    if (codesign_json_path is None):
        print('codesign_json_path is None')
        exit(1)
    icon_font_dict = read_icon_font_json_dict(icon_font_json_path)
    codesign_dict = read_codesign_font_json_dict(codesign_json_path)
    icon_font_dict_keys = icon_font_dict.keys()
    codesign_dict_keys = codesign_dict.keys()
    # 对比两个keys的差异
    icon_font_dict_keys_diff = set(
        icon_font_dict_keys).difference(set(codesign_dict_keys))
    # 如果有差异则跑错
    if (len(icon_font_dict_keys_diff) > 0):
        print('icon_font_dict_keys_diff:{}'.format(icon_font_dict_keys_diff))
        exit(1)
    # 验证两个字典中各个字段是否一致
    for key in icon_font_dict_keys:
        icon_font_item = icon_font_dict[key]
        codesign_item = codesign_dict[key]
        if (icon_font_item['unicode_decimal'] != codesign_item['unicode_decimal']):
            print('unicode_decimal not equal')
            print('icon_font_item:{}'.format(icon_font_item))
            print('codesign_item:{}'.format(codesign_item))
            exit(1)
        if (icon_font_item['class'] != codesign_item['class']):
            print('class not equal')
            print('icon_font_item:{}'.format(icon_font_item))
            print('codesign_item:{}'.format(codesign_item))
            exit(1)
        if (icon_font_item['name'] != codesign_item['name']):
            print('name not equal')
            print('icon_font_item:{}'.format(icon_font_item))
            print('codesign_item:{}'.format(codesign_item))
            exit(1)
        if (icon_font_item['unicode'] != codesign_item['unicode']):
            print('unicode not equal')
            print('icon_font_item:{}'.format(icon_font_item))
            print('codesign_item:{}'.format(codesign_item))
            exit(1)
    print('verify_sync.py:success')
