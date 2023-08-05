# coding=utf-8
# author:dn_eric(qq:2384363842)
# 动脑学院pythonVip课程
# 创建于: 2018/3/23 15:49
import requests


def main():
    r = requests.get("http://www.baidu.com")
    ret = r.request.url
    return ret


if __name__ == "__main__":
    main()
