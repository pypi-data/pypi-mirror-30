#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
from mosaicomponents.colorfield import ColorField

class TestColorField(TestCase):

    def setUp(self):
        """Do the test basic setup."""
        data = {"label": _("Type"), "name":"type", "value": "255:255:255:255"}
        self.field = ColorField(data, self.callback)
        value = self.field.get_value()
        assert response == "#FFFFFF"
        value = "#FF0000"
        selt.field.set_value(value)
        assert value == self.field.get_value()
        value = "#FF0000FF"
        selt.field.set_value(value)
        assert "#FF0000" == self.field.get_value()

    # ----------------------------------------------------------------------
    def callback(self, widget=None, data=None):
        pass
