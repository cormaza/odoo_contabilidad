# -*- coding: utf-8 -*-
import calendar
import re
from datetime import date, datetime
from odoo import models

class PleUtil(models.AbstractModel):
    _name = "account.ple.util"

    def filterPhrase(self, phrase):
        expression = '[!@#$\n]'
        return " ".join((re.sub(expression,'',phrase)).split())