# -*- encoding: utf-8 -*-
from openerp import models, fields, api, exceptions,_
from openerp.exceptions import except_orm, Warning, RedirectWarning

class SupplyerInvoice(models.Model):
    _inherit = 'account.invoice'

    dt = fields.Char('DT')

