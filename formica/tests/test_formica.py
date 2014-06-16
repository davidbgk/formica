# -*- coding: utf-8 -*-
#
# This file is part of Formica released under the FreeBSD license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)
import os.path

from django.template import TemplateSyntaxError
from django.test import TestCase
from django.test.utils import override_settings

try:
    from pyquery import PyQuery as pq
except ImportError:
    raise Exception('You should install pyquery to run tests.')


TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)


@override_settings(TEMPLATE_DIRS=TEMPLATE_DIRS)
class FormicaTestCase(TestCase):
    urls = 'formica.tests.urls'

    def assertTag(self, d, selector, count=1):
        self.assertEqual(count, len(d(selector)))

    def test_simple(self):
        r = self.client.get('/')
        d = pq(r.content)

        self.assertEqual(1, len(d('input#id_email')))
        self.assertEqual(1, len(d('div.field>label[for=id_email]')))
        self.assertEqual(1, len(d('input#id_check')))
        self.assertEqual(1, len(d('div.field>div.field-content>label[for=id_check]')))

    def test_raise(self):
        self.assertRaises(TemplateSyntaxError, self.client.get, '/raises')

    def test_override(self):
        r = self.client.get('/override')
        d = pq(r.content)

        self.assertTag(d, 'input#id_email')
        self.assertTag(d, 'input#id_check')
        self.assertTag(d, 'input#id_other-email')
        self.assertTag(d, 'input#id_other-check')

        self.assertTag(d, '#my_form div.field', 2)
        self.assertTag(d, '#my_form div.field.wrapped')
        self.assertTag(d, '#my_form input[name=csrfmiddlewaretoken]')

        self.assertTag(d, '#other_form div.field', 2)
        self.assertTag(d, '#other_form input#id_other-email[size="40"]')
        self.assertTag(d, '#other_form div.field.wrapped input#id_other-email')
        self.assertTag(d, '#other_form input#id_other-check[class=checkbox]')
        self.assertTag(d, '#other_form input[name=csrfmiddlewaretoken]', 0)

    def test_table(self):
        r = self.client.get('/table')
        d = pq(r.content)

        self.assertTag(d, '#form thead>tr>th>label[for=id_email]')
        self.assertTag(d, '#form thead>tr>th>label[for=id_check]')
        self.assertTag(d, '#form tbody>tr>td.field>input#id_email')
        self.assertTag(d, '#form tbody>tr>td.field>input#id_check')

        self.assertTag(d, '#formset thead')
        self.assertTag(d, '#formset tbody>tr', 2)
        self.assertTag(d, '#formset>div>input#id_form-TOTAL_FORMS[value="2"]')
        self.assertTag(d, '#formset tbody>tr>td.field>input#id_form-0-email')
        self.assertTag(d, '#formset tbody>tr>td.field>input#id_form-1-check')
        self.assertTag(d, '#formset tbody>tr>td.field>input#id_form-1-ORDER')
        self.assertTag(d, '#formset tbody>tr>td.field>input#id_form-1-DELETE')

    def test_custom(self):
        r = self.client.get('/custom')
        d = pq(r.content)

        self.assertEqual(1, len(d('#fields').children()))
        self.assertTag(d, '#fields>div.void')

        self.assertTag(d, '#field div.super-wrapper>div.field input#id_email')
        self.assertTag(d, '#field div.super-wrapper>div.field input#id_check')

    def test_errors(self):
        r = self.client.get('/errors')
        d = pq(r.content)

        self.assertTag(d, 'body>div.messages.error>strong')
        self.assertTag(d, 'div.field>ul.errorlist>li', 2)