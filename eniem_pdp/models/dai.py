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

class dai (osv.Model):

    _inherit = 'mail.thread'


    _name = 'dai'
    _description = 'Demande d\'achat'
    _order= 'name asc'

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
                    ids = [ids]
        reads = self.read(cr, uid, ids, ['name'], context=context)
        res = []
        for record in reads:
            name = record['name']
            res.append((record['id'], name))
        return res


    def create(self, cr, uid, vals, context=None):

        if context is None:
            context = {}

        if 'cbn_id' in vals:
            user=self.pool.get('res.users').browse(cr,uid,self.pool.get('res.users').search(cr,uid,[('id', 'in', [vals['purchaser_id']])],context=context),context=context)
            #raise osv.except_osv(_("Error!"), _(user))
            ub=user.default_operating_unit_id.id
            #raise osv.except_osv(_("Error!"), _(ub))
            store=self.pool.get('res.store').browse(cr,uid,self.pool.get('res.store').search(cr,uid,[('operating_unit_id', 'in', [ub])],context=context),context=context)
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, store.sequence_dai_id.code, context=context) or '/'

        else:
            ub=self.get_operating_unit_id(cr,uid,context)
            store=self.pool.get('res.store').browse(cr,uid,self.pool.get('res.store').search(cr,uid,[('operating_unit_id', 'in', [ub])],context=context),context=context)
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, store.sequence_dai_id.code, context=context) or '/'
        #raise osv.except_osv(_("Error!"), _(vals))

        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(dai, self).create(cr, uid, vals, context=context)
        self.message_post(cr, uid, [new_id], body=_("DAI created"), context=context)
        return new_id
    @api.multi
    def get_operating_unit_id(self):
        return self.env.user.default_operating_unit_id.id
    @api.multi
    def get_user_id(self):
        return self.env.user.id

    #operating_unit_id = fields.Many2one('operating.unit', string='Operating unit', default=get_operating_unit_id)

    _columns = {
        'exercice':fields.selection([('2021', "2021"),('2022', "2022"),('2023', "2023"),('2024', "2024"), ('2025', "2025"),('2026', "2026"),('2027', "2027")], 'Exercice',default='2021'),
        'emission_service': fields.char('Service émetteur'),
         'purchase_status': fields.char('Statut d\'achat'),
         'dai_object': fields.char('Objet de l\'achat'),
        'name': fields.char('DAI', required=True, copy=False,
            readonly=True, default='/', select=True),
        'purchaser_id': fields.many2one('res.users', 'Acheteur'),
         'categ_id': fields.many2one('product.category','Catégorie de produit', required=True ,help="Catégorie de produit"),

        'request_user_id': fields.many2one('res.users', 'Demandeur',required=True,default=get_user_id  ),
        'organization_unit_id': fields.many2one('operating.unit', 'Unité d\'organisation', default=get_operating_unit_id,readonly=True),
        'type_demande': fields.selection([('Manuelle', 'Manuelle'),
                                   ('Automatique', 'Automatique'),
                                   ], string="Type de demande",required=True, default='Manuelle'),
        'cbn_id': fields.many2one('cbn', 'CBN', domain=[('state', '=', 'freezed')]),
        'manual_cbn': fields.char('Origine de la demande'),
        'line_ids': fields.one2many('dai.line', 'dai_id', 'Quantities', copy=True,ondelete='cascade', select=True, readonly=True),
        'state' : fields.selection([('draft', "Brouillon"),('submited', "Validation section"),('submited1', "Validation service"),('submited2', "Validation département"),('validated', "Validée"),('approved', "Approuvée"),('in_process', "Encours de traitement"), ('terminate', "Soldée"),('canceled', "Annulée")], 'Status',default='draft')
        }


    _defaults = {
        #'organization_unit_id':self.pool.get('res.user').browse(cr,uid,uid).default_operating_unit.id
        # 'doors': 5,
        # 'odometer_unit': 'kilometers',
        # 'state_id': _get_default_state,
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'La dai doit avoir une numéro unique!'),
        #('pdp_uniq', 'unique(pdp_id, company_id)', 'Plan must be unique per Company!'),
    ]

    @api.multi
    def verify_quantities(self):
        noline=False
        for product in self.line_ids:
            noline=True
            if product.requested_quantity <=0 or product.modified_quantity<0:
               raise osv.except_osv(_("Error!"), _("Vérifiez vos quantités.\nIl existe probablement des quantités nulles ou négatives"))
        if not noline:
            raise osv.except_osv(_("Error!"), _("Aucune ligne. Prière d'en ajouter au moins une"))

    @api.multi
    def button_submit(self):
        self.verify_quantities()
        self.state = 'submited'
        self.message_post(body=_("Status changé à  "+self.state))
    @api.multi
    def button_submit_cser(self):
        self.verify_quantities()
        self.state = 'submited1'
        self.message_post(body=_("Status changé à "+self.state))
    @api.multi
    def button_submit_dep(self):
        self.verify_quantities()

        self.state = 'submited2'
        self.message_post(body=_("Status changé à "+self.state))
    @api.multi
    def button_approve(self):
        self.verify_quantities()
        self.state = 'approved'
        self.message_post(body=_("Status changé à "+self.state))

    @api.multi
    def button_validate(self):
        #if not self.purchaser_id:
         #    raise osv.except_osv(_("Error!"), _("Prière d'indiquer l'acheter"))

        if not self.purchaser_id:
            raise osv.except_osv(_('Invalid Action!'), _('Il faut d\'abord renseigner l\'acheteur'))

        self.verify_quantities()
        self.state = 'validated'
        self.message_post(body=_("Status changé à "+self.state))

    @api.multi
    def button_in_process(self):
        self.state = 'in_process'
        self.message_post(body=_("Status changé à  "+self.state))

    @api.multi
    def button_terminate(self):
        self.state = 'terminate'
        self.message_post(body=_("Status changé à "+self.state))

    @api.multi
    def button_cancel(self):
        self.state = 'canceled'
        self.message_post(body=_("Status changé à "+self.state))

    def unlink(self, cr, uid, ids, context=None):
        DAI = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in DAI:
            if s['state'] in ['draft']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('Vous ne pouvez pas supprimer une DAI dans cet état'))

        return super(dai, self).unlink(cr, uid, unlink_ids, context=context)
    @api.multi
    def benerate_rfq(self):
        cr = self.env.cr
        uid = self.env.uid
        context = self.env.context
        #raise osv.except_osv(_("Error!"), _(self.reference))
        records=[]
        for record in self.line_ids:
            if record.state=='validated' and record.state2=='processed' :
                records.append([record.product_id.id, record.product_uom_id.id, record.modified_quantity,record.id])

        if len(records)>0:
            purchase_requisition=self.pool.get("purchase.requisition")
            warehouse, picking_id= purchase_requisition._get_picking_in_ub(cr,uid,context)

            rfq_id=purchase_requisition.create(cr,uid,{
                        'origin': self.name,
                        'user_id': self.purchaser_id.id,
                        'dai_id': self.id,
                        'type_consultation': "homologue",
                        'picking_type_id': int(picking_id[0])})
                        #'warehouse_id': warehouse

            for product in records:
                self.pool.get('purchase.requisition.line').create(cr,uid,{
                        'product_id': product[0],
                        'requisition_id':rfq_id,
                        'product_uom_id':product[1],
                        'product_qty':product[2],


                    })
                self.pool.get('dai.line').write(cr, uid, product[3], {'state2': 'terminate','rfq_id':rfq_id})
            #self.message_post(cr, uid, [self.id], body=_("Consultation créée "), context=context)
            return  {
        'type': 'ir.actions.client',
        'tag': 'reload',
            }
        return True

class dai_line(osv.Model):
    _name = "dai.line"
    _description = "Lignes de la DAI"
    _rec_name = 'product_id'



    def product_id_change(self, cr, uid, ids, product, uom=False,context=None):
        context = context or {}
        product_uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')


        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context)


        domain = {}
        result['product_uom_id'] = product_obj.uom_id.id
        if (not uom):
            result['product_uom_id'] = product_obj.uom_id.id
        return {'value': result, 'domain': domain}
    @api.depends('requested_quantity')
    def _modified_quantity(self):
        for record in self:
            record.modified_quantity=record.requested_quantity

    _columns = {
        'product_id': fields.many2one('product.product', 'Produit', domain=[('purchase_ok', '=', True)]),
        'product_uom_id': fields.many2one('product.uom', 'Unité de mesure'),
        'dai_id': fields.many2one('dai', 'DAI'),
        'rfq_id': fields.many2one('purchase.requisition', 'Consultation'),
        'requested_quantity': fields.float('Quanitité demandée',store=True),
        #'modified_quantity': fields.float('Quanitité modifiée',store=True),
        'modified_quantity': fields.float('Quantité modifiée',compute='_modified_quantity',store=True),
        'state' : fields.selection([('draft', "Brouillon"),('validated', "Validé"),('canceled', "Annulé")], 'Statut',default='draft',copy=False),
        'state2' : fields.selection([('unprocessed', "Non Traitée"),('processed', "Programmée"),('terminate', "Traitée")], 'Statut de traitement',default='unprocessed',copy=False),



        }
    @api.multi
    def button_cancel(self):
        #raise osv.except_osv(_("Error!"), _(self.dai_id.state))
        if self.dai_id.state not in ['approved','terminate','in_process']:
                  raise osv.except_osv(_("Attention!"), _("Vous n'avez pas le droit de traiter cette DAI avant son approbation"))
        self.state = 'canceled'
        self.state2 = 'processed'
        sold=True
        for line in self.dai_id.line_ids:
            if line.state != 'canceled' and  line.state2 not in ['processed' , 'terminate']:
              sold=False
        if sold==True:
         self.dai_id.state='terminate'
         return {
    'type': 'ir.actions.client',
    'tag': 'reload',
}
        else:
          if  self.dai_id.state!='in_process':
            self.dai_id.state='in_process'
            return {
    'type': 'ir.actions.client',
    'tag': 'reload',
}

    @api.multi
    def button_process(self):
        if self.dai_id.state not in ['approved','terminate','in_process']:
                  raise osv.except_osv(_("Attention!"), _("Vou n'avez pas le droit de traiter cette DAI avant son approbation"))

        #raise osv.except_osv(_("Error!"), _(self.state))
        self.state = 'validated'
        self.state2 = 'processed'
        sold=True
        for line in self.dai_id.line_ids:
            if line.state != 'canceled' and  line.state2 not in ['processed' , 'terminate']:
              sold=False
        if sold==True:
         self.dai_id.state='terminate'
         return {
    'type': 'ir.actions.client',
    'tag': 'reload',
}
        else:
          if  self.dai_id.state!='in_process':
            self.dai_id.state='in_process'
            return {
    'type': 'ir.actions.client',
    'tag': 'reload',
}

    def affect_line_to_new_dai(self,cr, uid,active_ids,dai_id,context):
        #dai_idc'est la dai de destination
        #raise osv.except_osv(_("Error!"), _(self.dai_id))
        dais=self.pool.get('dai').browse(cr,uid,[dai_id],context)
        lines=self.pool.get('dai.line').browse(cr,uid,active_ids,context)
        for line in lines:

          #raise osv.except_osv(_("Error!"), _(line.dai_id.state))
         if line.dai_id.state  in ['canceled','terminate']:
                  raise osv.except_osv(_("Attention!"), _("Vou n'avez pas le droit d'affecter cette ligne"))
        for dai in dais:
            #raise osv.except_osv(_("Attention!"), _(dai.state))
            if dai.state  in ['canceled','terminate']:
                  raise osv.except_osv(_("Attention!"), _("Vou n'avez pas le droit d'affecter cette ligne à cette dai"))

        #self.state = 'validated'
        #self.state2 = 'processed'
##        sold=True
##        for line in self.dai_id.line_ids:
##            if line.state2 != 'processed':
##              sold=False
##        if sold==True:
##         self.dai_id.state='terminate'
        self.write(cr, uid, active_ids, {'dai_id': dai_id}, context=context)
        dais=self.pool.get('dai').browse(cr,uid,[dai_id],context)
        for dai in dais:
            sold=True
            for line in dai.line_ids:
                if line.state != 'canceled' and  line.state2 not in ['processed' , 'terminate']:
                  sold=False
                  break
            if sold==True:
             dai.state='terminate'

        return  True
