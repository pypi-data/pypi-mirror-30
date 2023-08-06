#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
from mosaicomponents.commentfield import CommentField

class TestCommentField(TestCase):

    def setUp(self):
        """Do the test basic setup."""
        data = {"label": _("Type"), "name":"type", "value": "text"}
        self.field = OpenFileField(data, self.callback)
        value = self.field.get_value()
        assert response == "text"
        value = "Atenção"
        selt.field.set_value(value)
        assert value == self.field.get_value()

    # ----------------------------------------------------------------------
    def callback(self, widget=None, data=None):
        pass
