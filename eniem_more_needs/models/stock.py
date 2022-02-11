# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
from openerp import models, fields, api, exceptions,_
from openerp.exceptions import except_orm, Warning, RedirectWarning
from random import *

class Reception(models.Model):
    _inherit = 'stock.transfer.insidjam'

    dt = fields.Char('DT')
    @api.multi
    def get_next_number(self):
##        cr = self.env.cr
##        uid = self.env.uid
##        context = self.env.context
        user=self.env['res.users'].search([('id','=',self.env.uid)])
        for i in user:
            operating_unit_id=i.default_operating_unit_id.id
        #raise osv.except_osv(_("Attention!"), _(operating_unit_id))
        recept = self.env['stock.transfer.insidjam'].search([('operating_unit_id','=',operating_unit_id)])
        #raise osv.except_osv(_("Attention!"), _("Le DT est déjà affecté"))
        dts = list(map(int,recept.mapped('dt')))
        #raise osv.except_osv(_("Attention!"), _(dts))

        if not self.dt:
         if len(dts)==0:
            self.dt=1
         else:
            self.dt=max(dts)+1
        else:
         raise osv.except_osv(_("Attention!"), _("Le DT est déjà affecté"))


        #self.dt=self.name
        return True



