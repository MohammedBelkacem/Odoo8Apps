# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
from openerp import models, fields, api, exceptions,_
from openerp.exceptions import except_orm, Warning, RedirectWarning
from random import *

class MRPRoutinWorkCenterSecond(models.Model):
    _inherit = 'mrp.routing.workcenter'

    time_milli_second = fields.Float('Temps en millisecondes')
