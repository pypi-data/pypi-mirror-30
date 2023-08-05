#! /usr/bin/python3
# -*- coding: utf-8 -*-

from pyadf.adf_object import AdfObject
from pyadf.group_node_children_mixin import GroupNodeChildrenMixin

class Document(AdfObject, GroupNodeChildrenMixin):
    type = 'doc'
    def __init__(self):
        self.content = []
        pass

    def to_doc(self):
        result = super(Document,self).to_doc()
        result['version'] = 1
        result['content'] = [ x.to_doc() for x in self.content ]
        return {'body': result}