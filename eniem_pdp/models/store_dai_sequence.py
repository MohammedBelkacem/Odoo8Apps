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
from openerp import models, fields, api, exceptions,_
from openerp.exceptions import except_orm, Warning, RedirectWarning
from random import *


class StoreDaiSequence (models.Model):

    _inherit = 'res.store'

##    @api.multi
##    def _get_operating_unit_id(self):
##        return self.env.user.default_operating_unit_id.id


    sequence_dai_id = fields.Many2one('ir.sequence', 'Sequence de DAI', copy=False)

##
##    def _get_picking_in_ub(self,cr,uid,context):
##        cr = self.env.cr
##        uid = self.env.uid
##        context = self.env.context
##        context = self._context
##        current_uid = context.get('uid')
##        user = self.pool.get('res.users').browse(cr,uid,uid,context)
##        warehouse=self.pool.get("stock.warehouse").browse(cr,uid,self.pool.get("stock.warehouse").search(cr, uid, [('operating_unit', 'in', [user.default_operating_unit_id.id])], context=context),context)
##        picking_type_id=self.pool.get("stock.picking.type").search(cr, uid, [('warehouse_id', 'in', [warehouse.id]),('code', 'in', ['incoming']),('default_location_src_id', 'in', [8])], context=context)
##        #=self.pool.get("stock.warehouse").browse(cr,uid,self.pool.get("stock.warehouse").search(cr, uid, [('operating_unit', 'in', [user.default_operating_unit_id.id])], context=context),context)
##        return warehouse.id,picking_type_id
##
##        obj_data = self.pool.get('ir.model.data')
##        return obj_data.get_object_reference(cr, uid, 'stock', 'picking_type_in')