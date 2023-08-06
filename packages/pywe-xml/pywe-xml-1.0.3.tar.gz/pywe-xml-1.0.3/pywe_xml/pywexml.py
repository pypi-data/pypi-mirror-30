# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from xml.parsers.expat import ExpatError

import six
import xmltodict
from pywe_utils import to_text


__all__ = ['dict_to_xml', 'xml_to_dict']


def dict_to_xml(d, ignore=True, isdigit=True):
    xml = ['<xml>\n']
    for k, v in d.items():
        if (ignore and v) or (not ignore):
            if isinstance(v, six.integer_types) or (isdigit and v.isdigit()):
                xml.append('<{0}>{1}</{0}>\n'.format(to_text(k), to_text(v)))
            else:
                xml.append('<{0}><![CDATA[{1}]]></{0}>\n'.format(to_text(k), to_text(v)))
    xml.append('</xml>')
    return ''.join(xml)


def xml_to_dict(x):
    try:
        return xmltodict.parse(x)['xml']
    except (xmltodict.ParsingInterrupted, ExpatError):
        return x
