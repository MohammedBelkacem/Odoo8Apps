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
class pdp (osv.osv):

    _inherit = 'mail.thread'


    _name = 'pdp'
    _description = 'Plan directeur de production'
    _order= 'year asc'
    def _compute_brut_quantities (self):
        return true
    _columns = {

        'year': fields.integer('Annee', help='Annee du plan de production'),
        'reference': fields.char('Reference', help='PDP reference'),
        'line_ids': fields.one2many('pdp.line', 'pdp_id', 'Products to manifacture', copy=True,ondelete='cascade', select=True, readonly=False, states={'draft':[('readonly',False)]}),
        'line_brut_ids': fields.one2many('pdp.raw', 'pdp_id', 'Basic raw of metrial', copy=True,ondelete='cascade', select=False, readonly=True, states={'draft':[('readonly',False)]}),
        'start_date': fields.date('Starting date', copy=True),
        'end_date': fields.date('End date', copy=True),
        'state' : fields.selection([('draft', "Draft"),('confirmed', "Confirmed"),('freezed', "Freezed"),('canceled', "Canceled")], 'Status',default='draft')

        }
    @api.multi
    def action_draft(self):
        self.state = 'draft'
    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'
    @api.multi
    def action_freeze(self):
        self.state = 'freezed'
    @api.multi
    def action_canceled(self):
        self.state = 'canceled'
    def recursive_searhc_bom(self, cr, uid, ids,product_id, context=None):
        bom_obj = self.pool.get('mrp.bom')
        a=bom_obj.pool['mrp.bom'].search(cr, uid, [('product_id', 'in', [ product_id])], context=context)
        if (a):
         raws_ids=pdp_obj.pool['mrp.bom.line'].search(cr, uid, [('bom_id', 'in', a)], context=context)
         raws=pdp_obj.pool['mrp.bom.line'].browse(cr, uid, raws_ids, context=context)
                #My_error_Msg=raws

                #raise osv.except_osv(_("Error!"), _(My_error_Msg)+'mm'+_(err))
                #raise osv.except_osv(_("Error!"), _(My_error_Msg))
         for raw in raws:
                self.recursive_searhc_bom(self, cr, uid, raw.product_id.id, context=None)
        else:
              pdp_raw=pdp_obj.create(cr,uid,{
                    'product_id': raw.product_id.id,
                    'pdp_id':record.id,
                    'product_uom_id':raw.product_id.uom_id.id,
                })

    def action_compute(self, cr, uid, ids, context=None):
        pdp_obj = self.pool.get('pdp.raw')
        a=pdp_obj.pool['pdp.raw'].search(cr, uid, [('pdp_id', 'in', ids)], context=context)
        pdp_obj.unlink(cr, uid, a, context)
        for record in self.browse(cr, uid, ids, context):

            for product in record.line_ids:
                My_error_Msg=str( record.id)
                err=str( product.product_id)
                #product_obj = self.pool.get('product.product')
                bom_obj = self.pool.get('mrp.bom')
                a=bom_obj.pool['mrp.bom'].search(cr, uid, [('product_id', 'in', [ product.product_id.id])], context=context)
                raws_ids=pdp_obj.pool['mrp.bom.line'].search(cr, uid, [('bom_id', 'in', a)], context=context)
                raws=pdp_obj.pool['mrp.bom.line'].browse(cr, uid, raws_ids, context=context)
                #My_error_Msg=raws

                #raise osv.except_osv(_("Error!"), _(My_error_Msg)+'mm'+_(err))
                #raise osv.except_osv(_("Error!"), _(My_error_Msg))
                for raw in raws:

                 pdp_raw=pdp_obj.create(cr,uid,{
                    'product_id': raw.product_id.id,
                    'pdp_id':record.id,
                    'product_uom_id':raw.product_id.uom_id.id,
                })
        return True




    _defaults = {
        # 'doors': 5,
        # 'odometer_unit': 'kilometers',
        # 'state_id': _get_default_state,
    }

class pdp_line(osv.osv):
    _name = "pdp.line"
    _description = "PDP lines"
    _rec_name = 'product_id'

    @api.depends('january', 'february','march','april','mai','june','july','august','september','october','november','december')
    def _get_total(self):
        for record in self:
            record.total=record.january+record.february+record.march+record.april+record.mai+record.june+record.july+record.august+record.september+record.october+record.november+record.december





    _columns = {
        'product_id': fields.many2one('product.product', 'Product', domain=[('purchase_ok', '=', False)]),
        'product_uom_id': fields.many2one('product.uom', 'Product Unit of Measure'),
        'pdp_id': fields.many2one('pdp', 'PDP', ondelete='cascade'),
        'january': fields.integer('January',help='January'),
        'february': fields.integer('February',help='february'),
        'march': fields.integer('March',help='January'),
        'april': fields.integer('April',help='January'),
        'mai': fields.integer('Mai',help='January'),
        'june': fields.integer('June',help='January'),
        'july': fields.integer('July',help='January'),
        'august': fields.integer('August',help='January'),
        'september': fields.integer('September',help='January'),
        'october': fields.integer('October',help='January'),
        'november': fields.integer('November',help='January'),
        'december': fields.integer('December',help='January'),
        'total': fields.integer('Total',compute='_get_total',readonly=True,store=True)}





class pdp_raw(osv.osv):
    _name = "pdp.raw"
    _description = "Raw of Material lines"
    _rec_name = 'product_id'

    @api.depends('january', 'february','march','april','mai','june','july','august','september','october','november','december')
    def _get_total(self):
        for record in self:
            record.total=record.january+record.february+record.march+record.april+record.mai+record.june+record.july+record.august+record.september+record.october+record.november+record.december



    _columns = {
        'product_id': fields.many2one('product.product', 'Product', domain=[('purchase_ok', '=', False)],readonly=True),
        'product_uom_id': fields.many2one('product.uom', 'Product Unit of Measure',readonly=True),
        'pdp_id': fields.many2one('pdp','PDP', ondelete='cascade'),
        'january': fields.integer('January',help='January'),
        'february': fields.integer('February',help='January'),
        'march': fields.integer('March',help='January'),
        'april': fields.integer('April',help='January'),
        'mai': fields.integer('Mai',help='January'),
        'june': fields.integer('June',help='January'),
        'july': fields.integer('July',help='January'),
        'august': fields.integer('August',help='January'),
        'september': fields.integer('September',help='January'),
        'october': fields.integer('October',help='January'),
        'november': fields.integer('November',help='January'),
        'december': fields.integer('December',help='January'),
        'total': fields.integer('Total',compute='_get_total',readonly=True,store=True)

        }

##class product_product(osv.osv):
##  _inherit = 'product.product'
##
##  def has_bom(self, cr, uid, ids, context=None):
##        pdp_obj = self.pool.get('mrp.bom')
##        a=pdp_obj.pool['mrp.bom'].search(cr, uid, [('product_id', 'in', ids)], context=context)
##        return a

