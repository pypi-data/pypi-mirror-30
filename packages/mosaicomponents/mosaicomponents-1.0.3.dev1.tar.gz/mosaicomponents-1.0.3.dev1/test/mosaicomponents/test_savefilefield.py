#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
from mosaicomponents.savefilefield import SaveFileField

class TestSaveFileField(TestCase):

    def setUp(self):
        """Do the test basic setup."""
        data = {"label": _("Type"), "name":"type", "value": "text.txt"}
        self.field = SaveFileField(data, self.callback)
        value = self.field.get_value()
        assert response == "text.txt"
        value = "Atenção"
        selt.field.set_value(value)
        assert value == self.field.get_value()

    # ----------------------------------------------------------------------
    def callback(self, widget=None, data=None):
        pass
