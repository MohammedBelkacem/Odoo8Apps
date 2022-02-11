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

class dai_purchaser(osv.osv_memory):
    _name = "dai.purchaser"
    _description = "DAI"
    _columns = {
        'dai_id': fields.many2one('dai', 'DAI', required=True, domain=[('state', 'not in', ['canceled','terminate'])]),
    }


    def affect_line_to_dai(self, cr, uid, ids, context=None):
        active_ids = context and context.get('active_ids', [])
        data =  self.browse(cr, uid, ids, context=context)[0]
        #raise osv.except_osv(_("Error!"), _(active_ids))
        #raise osv.except_osv(_("Error!"), _(data.dai_id.id))
        self.pool.get('dai.line').affect_line_to_new_dai(cr, uid, active_ids, data.dai_id.id, context=context)

        ## x"zqt l   nouvelle dai raise osv.except_osv(_("Error!"), _(data.dai_id.id))

        return  {
    'type': 'ir.actions.client',
    'tag': 'reload',
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
