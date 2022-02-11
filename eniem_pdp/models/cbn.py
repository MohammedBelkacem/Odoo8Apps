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

class cbn (osv.Model):

    _inherit = 'mail.thread'


    _name = 'cbn'
    _description = 'Calcul des besoin nets'
    #_order= 'pdp_id asc'
    _columns = {
        'name': fields.char('Plan', required=True, copy=False,
            readonly=True, default='/', select=True),
        'pdp_id': fields.many2one('pdp', 'PDP', domain=[('state', '=', 'freezed')]),
        'line_ids': fields.one2many('cbn.line', 'cbn_id', 'Quantités brutes', copy=True,ondelete='cascade', select=True, readonly=False),
        'line_brut_bom_ids': fields.one2many('cbn.raw.bom', 'cbn_id', 'Produits intermédiare', copy=True,ondelete='cascade', select=False, readonly=False, states={'draft':[('readonly',False)]}),

        'line_stock_ids': fields.one2many('cbn.stock', 'cbn_id', 'Quantité en Stock', copy=True,ondelete='cascade', select=True, readonly=False),
        'line_recept_ids': fields.one2many('cbn.recept', 'cbn_id', 'En réception', copy=True,ondelete='cascade', select=True, readonly=False),
        'line_definitive_ids': fields.one2many('cbn.definitive', 'cbn_id', 'A approvisionner', copy=True,ondelete='cascade', select=True, readonly=False),
        'line_definitive_common_ids': fields.one2many('cbn.definitive.common', 'cbn_id', 'Produits communs', copy=True,ondelete='cascade', select=True, readonly=False),
        'state' : fields.selection([('draft', "Brouillon"),('confirmed', "Confirmée"),('freezed', "Gelé"),('canceled', "Annulé")], 'Etat',default='draft')
        }

    _defaults = {
      'name': lambda obj, cr, uid, context: '/',}


##    _sql_constraints = [
##        ('name_uniq', 'unique(name, company_id)', 'Plan must be unique per Company!'),
##        ('pdp_uniq', 'unique(pdp_id, company_id)', 'Plan must be unique per Company!'),
##    ]

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

    def unlink(self, cr, uid, ids, context=None):
        CBNS = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in CBNS:
            if s['state'] in ['draft', 'canceled']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('Vous ne pouvez pas supprimer un CBN non brouillon ou non annulé!'))

        return super(cbn, self).unlink(cr, uid, unlink_ids, context=context)

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cbn', context=context) or '/'
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cbn', context=context) or '/'

        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(cbn, self).create(cr, uid, vals, context=ctx)
        self.message_post(cr, uid, [new_id], body=_("CBN created"), context=ctx)
        return new_id

    def action_load_stock(self, cr, uid, ids, context=None):
        cbn_stockc_obj = self.pool.get('cbn.stock')
        a=cbn_stockc_obj.search(cr, uid, [('cbn_id', 'in', ids)], context=context)
        cbn_stockc_obj.unlink(cr, uid, a, context)

        for record in self.browse(cr, uid, ids, context):

            for product in record.line_ids:

                cbn_stockc_obj_id=cbn_stockc_obj.create(cr,uid,{
                    'product_id': product.product_id.id,
                    'cbn_id':record.id,
                    'product_uom_id':product.product_id.uom_id.id,
                    'stock_available':product.product_id.qty_available,
                    'needed_quantity':product.needed_quantity,
                })
                #raise osv.except_osv(_("Error!"), _(cbn_stockc_obj_id))
        return True

    def action_load_recepr(self, cr, uid, ids, context=None):
        sql="select product_id, sum(product_qty) as product_qty   from purchase_order_line group by product_id "
        cr.execute(sql)
        products=[]
        quantities=[]
        for t in cr.dictfetchall():
            products.append (t['product_id'])
            quantities.append (t['product_qty'])
        recept_obj = self.pool.get('cbn.recept')
        a=recept_obj.search(cr, uid, [('cbn_id', 'in', ids)], context=context)
        recept_obj.unlink(cr, uid, a, context)
        for record in self.browse(cr, uid, ids, context):

            for product in record.line_stock_ids:
                recept=0
                if product.product_id.id in products:

                    recept=quantities[products.index(product.product_id.id)]
                recept_obj_id=recept_obj.create(cr,uid,{
                    'product_id': product.product_id.id,
                    'cbn_id':record.id,
                    'product_uom_id':product.product_id.uom_id.id,
                    'commanded':recept,
                    #'douane': recept, #todo
                    #'reception': recept, #todo
                    #'total_reception':
                    'stock_available': product.stock_available,
                    'needed_quantity':product.needed_quantity,


                })


    def action_load_defitive_needs(self, cr, uid, ids, context=None):
##        sql="select product_id, sum(product_qty) as product_qty   from purchase_order_line group by product_id "
##        cr.execute(sql)
##        products=[]
##        quantities=[]
##        for t in cr.dictfetchall():
##            products.append (t['product_id'])
##            quantities.append (t['product_qty'])

        self.pool.get('cbn.definitive').unlink(cr, uid, self.pool.get('cbn.definitive').search(cr, uid, [('cbn_id', 'in', ids)], context=context), context)
        self.pool.get('cbn.definitive.common').unlink(cr, uid, self.pool.get('cbn.definitive.common').search(cr, uid, [('cbn_id', 'in', ids)], context=context), context)
        for record in self.browse(cr, uid, ids, context):

            for product in record.line_recept_ids:
                if product.product_id.is_shared:

                 self.pool.get('cbn.definitive.common').create(cr,uid,{
                    'product_id': product.product_id.id,
                    'cbn_id':record.id,
                    'product_uom_id':product.product_id.uom_id.id,
                    'needed_quantity': product.needed_quantity,
                    'total_reception': product.total_reception,
                    'stock_available': product.stock_available,
                    'purchaser_id': product.product_id.product_manager.id,
                    'categ_id': product.product_id.categ_id.id,

                    #'total_to_supply': fields.float(string='To supply',compute='_get_total_supply',readonly=True,store=True),
                })
                else:
                    self.pool.get('cbn.definitive').create(cr,uid,{
                    'product_id': product.product_id.id,
                    'cbn_id':record.id,
                    'product_uom_id':product.product_id.uom_id.id,
                    'needed_quantity': product.needed_quantity,
                    'total_reception': product.total_reception,
                    'stock_available': product.stock_available,
                    #'total_to_supply': fields.float(string='To supply',compute='_get_total_supply',readonly=True,store=True),
                })
    def exists_in_lines(self, cr, uid, ids,acheteur,categ,dai,context=None):
        for i in dai:
            if acheteur==i[0] and categ==i[2]:
                return True, i[1]

        return False, None
    def generate_dai(self, cr, uid, ids, context=None):
       #dai_purchaser=[]
       #cbn_stockc_obj = self.pool.get('cbn.stock')
       dais=self.pool.get('dai').browse(cr, uid, self.pool.get('dai').search(cr, uid, [('cbn_id', 'in', ids)], context=context), context)
       process_begin=False
       for i in dais:
        if i.state!='draft':
            process_begin=True
       if process_begin:
        raise osv.except_osv(_("Error!"), _("Vous ne pouvez pas regénérer les DAI car au moins une a subi un changement"))
       else:
        self.pool.get('dai').unlink(cr, uid, self.pool.get('dai').search(cr, uid, [('cbn_id', 'in', ids)], context=context), context)

       acheteur_exist=False
       dai_purchaser=[]
       dai_obj = self.pool.get('dai')
       dai_line_obj=self.pool.get('dai.line')
       for record in self.browse(cr, uid, ids, context):



        for product in record.line_definitive_ids:
            #if (product.product_id.product_manager):
             if  (self.exists_in_lines(cr, uid, ids,product.product_id.product_manager.id,product.product_id.categ_id.id,dai_purchaser,context=context)[0]==True) and product.total_to_supply>=0:
                dai_raw=dai_line_obj.create(cr,uid,{
                    'product_id': product.product_id.id,
                    'dai_id':self.exists_in_lines(cr, uid, ids,product.product_id.product_manager.id,product.product_id.categ_id.id,dai_purchaser,context=context)[1],
                    'product_uom_id':product.product_uom_id.id,
                    'requested_quantity':product.total_to_supply,
                    'modified_quantity':product.total_to_supply,

                    #'purchaser_id':product.product_id.product_manager,


                })
             else:

              ub=product.product_id.product_manager.default_operating_unit_id.id
              dai_id = dai_obj.create(cr,uid,{'cbn_id':record.id, 'request_user_id':uid,'purchaser_id':product.product_id.product_manager.id,'organization_unit_id':ub,'categ_id':product.product_id.categ_id.id,'type_demande':'Automatique'})
              dai_purchaser.append([product.product_id.product_manager.id,dai_id,product.product_id.categ_id.id])
              #insert acheteur, dai
              if product.total_to_supply>=0:
               dai_raw=dai_line_obj.create(cr,uid,{
                    'product_id': product.product_id.id,
                    'dai_id':dai_id,
                    'product_uom_id':product.product_uom_id.id,
                    'requested_quantity':product.total_to_supply,
                    'modified_quantity':product.total_to_supply,


                })
        for product in record.line_definitive_common_ids:
            #if (product.product_id.product_manager):
             if  (self.exists_in_lines(cr, uid, ids,product.purchaser_id.id,product.product_id.categ_id.id,dai_purchaser,context=context)[0]==True) and product.total_to_supply>=0:
                dai_raw=dai_line_obj.create(cr,uid,{
                    'product_id': product.product_id.id,
                    'dai_id':self.exists_in_lines(cr, uid, ids,product.purchaser_id.id,product.product_id.categ_id.id,dai_purchaser,context=context)[1],
                    'product_uom_id':product.product_uom_id.id,
                    'requested_quantity':product.total_to_supply,
                    'modified_quantity':product.total_to_supply,

                    #'purchaser_id':product.purchaser_id.id,


                })
             else:
              ub=product.product_id.product_manager.default_operating_unit_id.id
              dai_id = dai_obj.create(cr,uid,{'cbn_id':record.id, 'request_user_id':uid,'purchaser_id':product.purchaser_id.id,'organization_unit_id':ub,'categ_id':product.product_id.categ_id.id,'type_demande':'Automatique'})
              dai_purchaser.append([product.product_id.product_manager.id,dai_id,product.product_id.categ_id.id])
              #insert acheteur, dai
              if  product.total_to_supply>=0:
               dai_raw=dai_line_obj.create(cr,uid,{
                    'product_id': product.product_id.id,
                    'dai_id':dai_id,
                    'product_uom_id':product.product_uom_id.id,
                    'requested_quantity':product.total_to_supply,
                    'modified_quantity':product.total_to_supply,


                })
            #else:
                #raise osv.except_osv(_('Invalid Action!'), _("Le produit "+str(product.product_id.default_code)+" n'a pas d'acheteur"))
        return True
    @api.multi
    def button_confirm(self):
        self.state = 'confirmed'
    @api.multi
    def button_freeze(self):
        self.state = 'freezed'
    @api.multi
    def button_cancel(self):
        self.state = 'canceled'




class cbn_line (osv.osv):
    _name = "cbn.line"
    _description = "Raw of Material lines"
    _rec_name = 'product_id'

    _columns = {
        'product_id': fields.many2one('product.product', string= 'Product', domain=[('purchase_ok', '=', False)],readonly=True),
        'product_uom_id': fields.many2one('product.uom', string='Product Unit of Measure',readonly=True),
        'cbn_id': fields.many2one('cbn',string='CBN', ondelete='cascade'),
        'needed_quantity': fields.float(string='Needed Quantity',readonly=True)

        }

class cbn_stock (osv.osv):
    _name = "cbn.stock"
    _description = "Raw of Material lines"
    _rec_name = 'product_id'

    _columns = {
        'product_id': fields.many2one('product.product', string= 'Produit', domain=[('purchase_ok', '=', False)],readonly=True),
        'product_uom_id': fields.many2one('product.uom', string='Unité de mesure',readonly=True),
        'cbn_id': fields.many2one('cbn',string='CBN', ondelete='cascade'),
        'stock_available': fields.float(string='Quantité disponible',readonly=True),
        'needed_quantity':fields.float(string='Quantité requise',readonly=True),
        }

class cbn_recept (osv.osv):
    _name = "cbn.recept"
    _description = "Raw of Material lines"
    _rec_name = 'product_id'
    @api.depends('commanded', 'douane','reception')
    def _get_total_command(self):
        for record in self:
            record.total_reception=record.commanded+record.douane+record.reception



    _columns = {
        'product_id': fields.many2one('product.product', string= 'Produit', domain=[('purchase_ok', '=', False)],readonly=True),
        'product_uom_id': fields.many2one('product.uom', string='Unité de mesure',readonly=True),
        'cbn_id': fields.many2one('cbn',string='CBN', ondelete='cascade'),
        'commanded': fields.float(string='Commandée',readonly=True),
        'douane': fields.float(string='Douane',readonly=True),
        'reception': fields.float(string='Réception',readonly=True),
        'total_reception': fields.float(string='Total commande',compute='_get_total_command',readonly=True,store=True),
        'stock_available': fields.float(string='Quantité disponible',readonly=True),
        'needed_quantity':fields.float(string='Quantité requise',readonly=True),


        }

class cbn_definitve (osv.osv):
    _name = "cbn.definitive"
    _description = "Definitive CBN"
    _rec_name = 'product_id'

    @api.depends('needed_quantity', 'total_reception','stock_available')
    def _get_total_supply(self):
        for record in self:
            record.total_to_supply=record.needed_quantity-record.total_reception-record.stock_available

    _columns = {
        'product_id': fields.many2one('product.product', string= 'Produit', domain=[('purchase_ok', '=', False)],readonly=True),
        'product_uom_id': fields.many2one('product.uom', string='Unité de mesure',readonly=True),
        'cbn_id': fields.many2one('cbn',string='CBN', ondelete='cascade'),
        'needed_quantity': fields.float(string='Qty brute',readonly=True),
        'total_reception': fields.float(string='En reception',readonly=True),
        'stock_available': fields.float(string='En stock',readonly=True),
        'total_to_supply': fields.float(string='Qty fournir',compute='_get_total_supply',readonly=True,store=True),

        }

class cbn_definitve_common (osv.osv):
    _name = "cbn.definitive.common"
    _description = "Produits communs"
    _rec_name = 'product_id'

    @api.depends('needed_quantity', 'total_reception','stock_available')
    def _get_total_supply(self):
        for record in self:
            record.total_to_supply=record.needed_quantity-record.total_reception-record.stock_available

    _columns = {
        'product_id': fields.many2one('product.product', string= 'Produit', domain=[('purchase_ok', '=', False)]),
        'product_uom_id': fields.many2one('product.uom', string='Unité de mesure'),
        'purchaser_id': fields.many2one('res.users', string='Acheteur'),
        'categ_id': fields.many2one('product.category', string='Catégorie'),
        'cbn_id': fields.many2one('cbn',string='CBN', ondelete='cascade'),
        'needed_quantity': fields.float(string='quantité brute'),
        'total_reception': fields.float(string='En reception'),
        'stock_available': fields.float(string='En stock'),
        'total_to_supply': fields.float(string='Qty à fournir',compute='_get_total_supply',store=True),

        }


class cbn_raw_bom(osv.osv):
    _name = "cbn.raw.bom"
    _description = "Semis finis"
    _rec_name = 'product_id'






    _columns = {
        'product_id': fields.many2one('product.product', string= 'Produit', domain=[('purchase_ok', '=', False)],readonly=False),
        'product_uom_id': fields.many2one('product.uom', string='Unité de mesure',readonly=False),
        'cbn_id': fields.many2one('cbn',string='CBN', ondelete='cascade'),
        'disponible': fields.float(string='Disponible',readonly=False),

         #'parent_product_id': fields.many2many('product.product', 'pdp_raw_group_lines', 'pdp_raw_group_id', 'product_id', 'Nomenclatures', readonly=True),

        }
