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
class account_move_line (osv.osv):

    _inherit = "account.move.line"


    #_name = 'account_move_line'
    #_description = 'PAccount move line'

##    def product_id_change(self, cr, uid, ids, account_move_line,context=None):
##        price=00.00
##        prod = self.pool.get('account.move.line')
##        for record in prod.browse(cr, uid, [product], context):
##            price=record.standard_price
##            values = {'category_id':record.product_id.categ_id.id,
##            #product.standard_price or 00.00,
##            }
    @api.depends('product_id')

    def _compute_categorie(self):
        prod = self.pool.get('account.move.line')

        for record in self:
          if (record.product_id):
            record.category_id=record.product_id.categ_id.id

    _columns = {

        'categ_id': fields.many2one('product.category', 'Category',compute='_compute_categorie',readonly=False,store=True),
        }





    _defaults = {
        # 'doors': 5,
        # 'odometer_unit': 'kilometers',
        # 'state_id': _get_default_state,
    }

