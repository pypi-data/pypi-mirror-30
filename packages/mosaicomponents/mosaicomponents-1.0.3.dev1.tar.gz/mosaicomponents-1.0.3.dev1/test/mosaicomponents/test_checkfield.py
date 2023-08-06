#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
from mosaicomponents.checkfield import CheckField

class TestCheckField(TestCase):

    def setUp(self):
        """Do the test basic setup."""
        data = {"label": _("Type"), "name":"type", "value": True}
        self.field = CheckField(data, self.callback)
        value = self.field.get_value()
        assert response == True
        value = False
        selt.field.set_value(value)
        assert value == self.field.get_value()

    # ----------------------------------------------------------------------
    def callback(self, widget=None, data=None):
        pass

