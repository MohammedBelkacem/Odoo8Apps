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
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import api
class mrpBOM (osv.osv):

    _inherit = 'mrp.bom'

    def _get_total_cost(self, cr, uid, ids, context=None):
        for record in self:
            raise osv.except_osv(_("Error!"), _(record.cost_mp))
            record.cost_mp=100.5

    _columns = {

        'mrp_bom_line_detailed_ids': fields.one2many('mrp.bom.line.detailed', 'bom_id', 'Composants', copy=True,ondelete='cascade', select=True, readonly=False),
        'cost_mp':  fields.float('Cout de la MP',compute='_get_total_cost',readonly=True,store=True,digits_compute=dp.get_precision('Factor')),
        }

    def recursive_search_bom(self, cr, uid, ids,raw,record,manuf_prod, quantity_row, context=None):
                 #pdp_obj = self.pool.get('pdp.raw')
                 rawb_obj = self.pool.get('mrp.bom.line.detailed')
                 bom_obj = self.pool.get('mrp.bom')

                 a=bom_obj.pool['mrp.bom'].search(cr, uid, [('product_id', 'in', [ raw.product_id.id])], context=context)
                 raws_ids=self.pool['mrp.bom.line'].search(cr, uid, [('bom_id', 'in', a)], context=context)
                 raws=self.pool['mrp.bom.line'].browse(cr, uid, raws_ids, context=context)

                 if not a:
                  #raise osv.except_osv(_("Error!"), _(a))
                  pdp_raw=rawb_obj.create(cr,uid,{
                    'product_id': raw.product_id.id,
                    'bom_id':record,
                    'product_uom_id':raw.product_id.uom_id.id,
                    'factor':quantity_row,
                    'pmp':raw.product_id.standard_price,
                    'total':raw.product_id.standard_price*quantity_row
                    #'quantity':manuf_prod.total,
                    #'parent_product_id':manuf_prod.product_id.id,
                })
                 else:
                    for raw1 in raws:
                     #raise osv.except_osv(_("Error!"), _('yesy'))
                     product_qty=float(raw1.product_qty*quantity_row)
                     self.recursive_search_bom(cr, uid, ids,raw1,record,manuf_prod,product_qty)


    def action_compute(self, cr, uid, ids, context=None):
        rawb_obj = self.pool.get('mrp.bom.line.detailed')
        a=rawb_obj.pool['mrp.bom.line.detailed'].search(cr, uid, [('bom_id', 'in', ids)], context=context)
        rawb_obj.unlink(cr, uid, a, context)

        product_qty=1.00
        products=[]
        factors=[]

        for record in self.browse(cr, uid, ids, context):

            for product in record:
                #raise osv.except_osv(_("Error!"), _(record.product_id))

                #My_error_Msg=str( record.id)
                #err=str( product.product_id)
                #product_obj = self.pool.get('product.product')
                bom_obj = self.pool.get('mrp.bom')
                a=bom_obj.pool['mrp.bom'].search(cr, uid, [('product_id', 'in', [ product.product_id.id])], context=context)
                raws_ids=self.pool['mrp.bom.line'].search(cr, uid, [('bom_id', 'in', a)], context=context)
                raws=self.pool['mrp.bom.line'].browse(cr, uid, raws_ids, context=context)
                #My_error_Msg=raws

                #raise osv.except_osv(_("Error!"), _(My_error_Msg)+'mm'+_(err))
                #raise osv.except_osv(_("Error!"), _(My_error_Msg))
                for raw in raws: # parcourir les lignes de la nomenclature
                 bom_obj = self.pool.get('mrp.bom')
                 a=bom_obj.pool['mrp.bom'].search(cr, uid, [('product_id', 'in', [ raw.product_id.id])], context=context)
                 raws_ids=self.pool['mrp.bom.line'].search(cr, uid, [('bom_id', 'in', a)], context=context)
                 raws=self.pool['mrp.bom.line'].browse(cr, uid, raws_ids, context=context)
                 My_error_Msg=str(product)
                 #raise osv.except_osv(_("Error!"), _(My_error_Msg))
                 if not a: # si le produit n'a pas de nomenclature
                  rawb_obj_id=rawb_obj.create(cr,uid,{
                    'product_id': raw.product_id.id,
                    'bom_id':record.id,
                    'factor':raw.product_qty,
                    'product_uom_id':raw.product_id.uom_id.id,
                    'pmp':raw.product_id.standard_price,
                    'total':raw.product_id.standard_price*raw.product_qty
                    #'quantity':product.total,
                    #'parent_product_id':product.product_id.id,
                })
                 else:
                    manuf_prod=product
                    product_qty=float( raw.product_qty*product_qty)
                    self.recursive_search_bom( cr, uid, ids,raw,record.id,manuf_prod,product_qty)
        #self._get_total_cost(cr, uid, context)

        return True


class mrp_bom_line_detailed(osv.osv):
    _name = "mrp.bom.line.detailed"
    _description = "Detailed composants"
    _rec_name = 'product_id'

    def product_id_change(self, cr, uid, ids, product,context=None):
        price=00.00
        prod = self.pool.get('product.product')
        for record in prod.browse(cr, uid, [product], context):
            price=record.standard_price

        #raise osv.except_osv(_('Invalid Action!'), _('In order to delete a Plans, you must cancel it before!'))
        values = {'pmp':price,
            #product.standard_price or 00.00,
            }
        return {'value': values}#, 'domain': domain, 'warning': warning}



    _columns = {
        'product_id': fields.many2one('product.product', 'Product', ),
        'pmp': fields.float('Cout unitaire',digits_compute=dp.get_precision('Factor')),
        'product_uom_id': fields.many2one('product.uom', 'Product Unit of Measure'),
        'bom_id': fields.many2one('mrp.bom', 'BOM', ondelete='cascade'),
        'factor': fields.float('Facteur',readonly=True,store=True,digits_compute=dp.get_precision('Factor')),
        'total': fields.float('Total',readonly=True,store=True,digits_compute=dp.get_precision('Factor')),

        }
    def _get_uom_id(self, cr, uid, *args):
        return self.pool["product.uom"].search(cr, uid, [], limit=1, order='id')[0]
    _defaults = {
        'product_uom_id': _get_uom_id,

    }



