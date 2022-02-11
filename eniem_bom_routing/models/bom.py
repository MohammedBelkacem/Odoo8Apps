# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from openerp.osv import fields, osv
from openerp import models, fields, api, exceptions,_
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import api

class bom (models.Model):

    _inherit =  'mrp.bom'

    state= fields.Selection ([('draft', "Brouillon"),('submitted', "Soumise à validation"),('validated', "Validée"),('canceled', "Annulée")], 'Etat',default='draft')

    def unlink(self, cr, uid, ids, context=None):
        bom = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in bom:
            if s['state'] in ['draft', 'canceled']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('Vou ne pouvez pas supprimer de nomenclatures. Vous pouvez la désactiver en décochant la case Actif.\n Allez sur l\'onglet Propriétés et décochez la case Actif. Si vous souhaitez la supprimer prière de contacter la DSI'))

        return super(bom, self).unlink(cr, uid, unlink_ids, context=context)
    @api.multi
    def retreive_bom(self,product):
        cr = self.env.cr
        uid = self.env.uid
        context = self.env.context
        #raise osv.except_osv(_('Invalid Action!'), _('La quantité de ce produit est nulle.'+line.product_id.default_code+'\nPrière de corriger avant de soumettre'))
        bom=self.pool.get("mrp.bom").search(cr, uid, [('product_id', 'in', [product.id]),('state', 'not in', ['validated'])], context=context)
        if (bom):

            raise osv.except_osv(_('Invalid Action!'), _('Cette sous nomenclature n\'est pas validée: '+product.default_code+' '+product.name+'\nPrière de la valider'))



    @api.multi
    def action_draft(self):
        self.state = 'draft'
    @api.multi
    def action_submit(self):

        for line in self.bom_line_ids:
            self.retreive_bom(line.product_id)
            if line.product_qty == 0:
                raise osv.except_osv(_('Invalid Action!'), _('La quantité de ce produit est nulle: '+line.product_id.default_code+" "+line.product_id.name+'\nPrière de corriger avant de soumettre'))
        self.state = 'submitted'
    @api.multi
    def action_validate(self):
        for line in self.bom_line_ids:
            if line.product_qty == 0:
                raise osv.except_osv(_('Invalid Action!'), _('La quantité de ce produit est nulle.'+line.product_id.default_code+'\nPrière de corriger avant de valider'))
        self.state = 'validated'
    @api.multi
    def action_cancel(self):
        self.state = 'canceled'

class bom_line (models.Model):

    _inherit =  'mrp.bom.line'


    product_qty= fields.Float('Product Quantity', required=True, digits_compute=dp.get_precision('Product Unit of Measure'))




    def _auto_init(self, cr, context=None):


        self._sql_constraints = [
        ('bom_qty_zero', 'CHECK (product_qty>=0)', 'Indiquez des quantités positives 0.')
    ]
        super(bom_line, self)._auto_init(cr,context)
