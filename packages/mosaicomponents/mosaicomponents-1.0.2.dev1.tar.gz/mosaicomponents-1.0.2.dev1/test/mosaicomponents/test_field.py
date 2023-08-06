#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
from mosaicomponents.field import Field

class TestField(TestCase):

    def setUp(self):
        """Do the test basic setup."""
        data = {"label": _("Type"), "name":"type", "value": "Test"}
        self.field = StringField(data, self.callback)
        value = self.field.get_value()
        assert response == 0
        value = "Atenção"
        selt.field.set_value(value)
        assert 0 == self.field.get_value()

    # ----------------------------------------------------------------------
    def callback(self, widget=None, data=None):
        pass
