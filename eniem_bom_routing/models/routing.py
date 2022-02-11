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

class routing (models.Model):

    _inherit =  'mrp.routing'

    state= fields.Selection ([('draft', "Brouillon"),('submitted', "Soumise à validation"),('validated', "Validée"),('canceled', "Annulée")], 'Etat',default='draft')

##    def unlink(self, cr, uid, ids, context=None):
##        routing = self.read(cr, uid, ids, ['state'], context=context)
##        unlink_ids = []
##        for s in routing:
####            if s['state'] in ['draft', 'canceled']:
####                unlink_ids.append(s['id'])
####            else:
##                raise osv.except_osv(_('Invalid Action!'), _('Vou ne pouvez pas supprimer de gammes. Vous pouvez la désactiver en décochant la case Actif.\n Si vous souhaitez la supprimer prière de contacter la DSI'))
##
##        return super(routing, self).unlink(cr, uid, unlink_ids, context=context)

    @api.multi
    def action_draft(self):
        self.state = 'draft'
    @api.multi
    def action_submit(self):
        self.state = 'submitted'
    @api.multi
    def action_validate(self):
        self.state = 'validated'
    @api.multi
    def action_cancel(self):
        self.state = 'canceled'
