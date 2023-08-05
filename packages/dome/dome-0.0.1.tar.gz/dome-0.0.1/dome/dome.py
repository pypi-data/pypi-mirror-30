"""
Dom Element
"""
import json
from typing import overload


from dome.utils import uncapitalize_name


class Node(list):
    def __init__(self, tag, *children, **attrs):
        super().__init__(children)
        self.tag = uncapitalize_name(tag)
        self.attrs = dict(attrs)

    def __call__(self, *children, **attrs):
        self.append(*children)
        self.attrs.update(attrs)
        return self

    def _dump_head(self):
        sb = [self.tag]
        for key, value in self.attrs.items():
            if value is not None:
                sb.append(' {}={}'.format(uncapitalize_name(key), json.dumps(value)))
        return ''.join(sb)

    def dumps(self):
        sb = []
        if len(self):
            sb.append('<{}>'.format(self._dump_head()))
            for child in self:
                if isinstance(child, str):
                    sb.append(child)
                else:
                    sb.append(child.dumps())
            sb.append('</{}>'.format(self.tag))
            return ''.join(sb)
        else:
            return '<{}/>'.format(self._dump_head())


class Html(Node):
    def __init__(self, *children, **attrs):
        super().__init__('html', *children, **attrs)


class Head(Node):
    def __init__(self, *children, **attrs):
        super().__init__('head', *children, **attrs)


class Body(Node):
    def __init__(self, *children, **attrs):
        super().__init__('body', *children, **attrs)


class Div(Node):
    @overload
    def __init__(self, *children, Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('div', *children, **attrs)


class Meta(Node):
    """https://www.w3schools.com/tags/tag_meta.asp"""
    @overload
    def __init__(self, *children, Charset=None, Content=None, HttpEquiv=None, Name=None, Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('meta', *children, **attrs)

