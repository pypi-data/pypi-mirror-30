# -*- coding:utf-8 -*-
# Created by qinwei on 2017/11/16
import html
import re

from lxml import etree


class HtmlUtils:
    RE_URL = re.compile(r"""url=(.*)""", re.I)

    @staticmethod
    def get_meta_refresh_url(element):
        """  获取refresh隐藏的刷新URL地址
         <meta http-equiv="refresh" content="0;url=http://www.baidu.com/">
         """
        if HtmlUtils.equal_tag_name(element, "meta"):
            content = element.get("content", "")
            match = HtmlUtils.RE_URL.search(content)
            if match:
                return match.group(1).strip()
        return None

    @staticmethod
    def text(element):
        result = []
        if isinstance(element, (list, tuple)):
            for el in element:
                result.append("".join([x for x in el.itertext()]))
            return "".join(result)

        return "".join([x for x in element.itertext()])

    @staticmethod
    def html(element):
        return etree.tostring(element).decode()

    @staticmethod
    def decode_html(html_str):
        return html.unescape(html_str)

    @staticmethod
    def equal_tag_name(element, tag_name):
        return hasattr(element, "tag") and element.tag == tag_name
