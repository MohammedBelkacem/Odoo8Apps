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
from openerp.osv import fields, osv
from openerp.tools.translate import _

class assign_account_move_lines(osv.osv_memory):
    _name = "validate.account.move.lines"
    _description = "Validate Account Move Lines"

    def assign_move_lines(self, cr, uid, ids, context=None):
        obj_move_line = self.pool.get('account.move.line')

        if context is None:
            context = {}
        data_line = obj_move_line.browse(cr, uid, context['active_ids'], context)
        for line in data_line:
            #if line.move_id.state=='draft':
                prod=line.product_id.categ_id.id
                line.categ_id=line.product_id.categ_id
                #raise osv.except_osv(_('Warning!'), _(prod))
        #obj_move.button_validate(cr, uid, move_ids, context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

