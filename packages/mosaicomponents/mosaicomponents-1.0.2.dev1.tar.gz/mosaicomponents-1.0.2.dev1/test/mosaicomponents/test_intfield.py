#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
from mosaicomponents.intfield import IntField

class TestIntField(TestCase):

    def setUp(self):
        """Do the test basic setup."""
        data = {"label": _("Type"), "name":"type", "value": 13}
        self.field = IntField(data, self.callback)
        value = self.field.get_value()
        assert response == 13
        value = 65590
        selt.field.set_value(value)
        assert value == self.field.get_value()
        value = -65590
        selt.field.set_value(value)
        assert value == self.field.get_value()
        value = 6.5
        selt.field.set_value(value)
        assert value == self.field.get_value()

    # ----------------------------------------------------------------------
    def callback(self, widget=None, data=None):
        pass
