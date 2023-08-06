#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
from mosaicomponents.combofield import ComboField

class TestComboField(TestCase):

    def setUp(self):
        """Do the test basic setup."""
        data = {"label": _("Type"), "name":"type",
                "value": "Banana", "values":["Banana", "Apple", "Orange"]}
        self.field = ComboField(data, self.callback)
        value = self.field.get_value()
        assert response == "Banana"
        value = "Orange"
        selt.field.set_value(value)
        assert value == self.field.get_value()

    # ----------------------------------------------------------------------
    def callback(self, widget=None, data=None):
        pass

