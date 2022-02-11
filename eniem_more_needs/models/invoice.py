# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api,_


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def name_get(self):
        if 'purchase_cost_distribution' in self._context and self._context.get('purchase_cost_distribution')==1:
            TYPES = {
                'out_invoice': _('Invoice'),
                'in_invoice': _('Supplier Invoice'),
                'out_refund': _('Refund'),
                'in_refund': _('Supplier Refund'),
            }
            result = []
            for inv in self:
                supplier_number = '('+inv.supplier_invoice_number+')' if inv.supplier_invoice_number else inv.dt
                result.append((inv.id, "%s %s %s" % (inv.number or TYPES[inv.type], inv.name or '', supplier_number)))
            return result
        else:
            res = super(AccountInvoice,self).name_get()
            return res