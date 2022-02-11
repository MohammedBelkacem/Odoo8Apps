# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
from openerp import models, fields, api, exceptions,_
from openerp.exceptions import except_orm, Warning, RedirectWarning
from random import *

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    dt = fields.Integer('DT')
    @api.multi
    def get_next_number(self):
        cr = self.env.cr
        uid = self.env.uid
        context = self.env.context

        import_orders = self.env['purchase.order'].search([('type_id', '=', 13)])
        dts = list(map(int,import_orders.mapped('dt')))

        if not self.dt:
         if len(dts)==0:
            self.dt=1
         else:
            self.dt=max(dts)+1
        else:
         raise osv.except_osv(_("Attention!"), _("Le DT est déjà affecté"))


        self.dt=max(dts)+1
        return True

