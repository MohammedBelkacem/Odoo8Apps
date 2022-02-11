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
class pdp (osv.Model):

    _inherit = 'mail.thread'


    _name = 'pdp'
    _description = 'Prevision de production'
    _order= 'name asc'
    def _compute_brut_quantities (self):
        return true
    #@api.depends('total', 'cession_price')

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
    @api.multi
    def get_cost(self):

        price=0
        for record in self.line_ids:
            price=price+record.total_cession_price
        #raise osv.except_osv(_("Error!"), _(My_error_Msg)+'mm'+_(price))
        self.total_pdp_cost=price
        return  True
    @api.multi
    def get_user_id(self):
        return self.env.user.id

        #return True
##        for record in self:
##            record.total_cession_price=record.total*record.cession_price
    _columns = {

        'name': fields.char('Plan', required=True, copy=False,
            readonly=True, default='/', select=True),

        'line_ids': fields.one2many('pdp.line', 'pdp_id', 'Produits à fabriquer', copy=True,ondelete='cascade', select=True, readonly=False, states={'draft':[('readonly',False)]}),
        'line_brut_ids': fields.one2many('pdp.raw', 'pdp_id', 'Besoins éclatés en MP', copy=True,ondelete='cascade', select=False, readonly=True, states={'draft':[('readonly',False)]}),
        'line_brut_grouped_ids': fields.one2many('pdp.raw.group', 'pdp_id', 'Besoin en MP groupé', copy=True,ondelete='cascade', select=False, readonly=False, states={'draft':[('readonly',False)]}),

        'line_brut_bom_ids': fields.one2many('pdp.raw.bom', 'pdp_id', 'Produits intermediares', copy=True,ondelete='cascade', select=False, readonly=False, states={'draft':[('readonly',False)]}),
        'line_brut_bom_eclate_ids': fields.one2many('pdp.raw.bom.eclate', 'pdp_id', 'Stock SFs eclatés', copy=True,ondelete='cascade', select=False, readonly=False, states={'draft':[('readonly',False)]}),
        'line_brut_bom_grouped_ids': fields.one2many('pdp.raw.bom.grouped', 'pdp_id', 'Stocks MP SFs groupés', copy=True,ondelete='cascade', select=False, readonly=False, states={'draft':[('readonly',False)]}),

        'start_date': fields.date('Date de début', copy=True),
        'end_date': fields.date('Date de fin', copy=True),
        'state' : fields.selection([('draft', "Brouillon"),('confirmed', "Confirmé"),('freezed', "Gelé"),('canceled', "Annulé")], 'Status',default='draft'),
        'total_pdp_cost': fields.float('Total PDP Cost'),
        'request_user_id': fields.many2one('res.users', 'Planificateur',required=True,default=get_user_id  ),
        'cbn_id': fields.many2one('cbn', 'CBN', domain=[('state', '=', 'freezed')]),
        }
    _defaults = {
    'name': lambda obj, cr, uid, context: '/',}
##    _sql_constraints = [
##        ('name_uniq', 'unique(name, company_id)', 'Plan must be unique per Company!'),
##    ]
    def unlink(self, cr, uid, ids, context=None):
        plans = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in plans:
            if s['state'] in ['draft', 'canceled']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('In order to delete a Plans, you must cancel it before!'))

        return super(pdp, self).unlink(cr, uid, unlink_ids, context=context)
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'pdp', context=context) or '/'
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'pdp', context=context) or '/'

        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(pdp, self).create(cr, uid, vals, context=ctx)
        self.message_post(cr, uid, [new_id], body=_("Plan created"), context=ctx)
        return new_id



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
    def recursive_search_bom_semi(self, cr, uid, ids,raw,record,manuf_prod, quantity_row, context=None):

                 a=self.pool.get('mrp.bom').search(cr, uid, [('product_id', 'in', [ raw.product_id.id])], context=context)
                 raws_ids=self.pool('mrp.bom.line').search(cr, uid, [('bom_id', 'in', a)], context=context)
                 raws=self.pool('mrp.bom.line').browse(cr, uid, raws_ids, context=context)


                 if  a:
                    b=self.pool.get('pdp.raw.bom').search(cr, uid, [('pdp_id', '=', record),('product_id','=',raw.product_id.id)], context=context)
                    if not b and raw.product_id.qty_available!=0:
                     pdp_raw_bom=self.pool.get('pdp.raw.bom').create(cr,uid,{
                    'product_id': raw.product_id.id,
                    'pdp_id':record,
                    'product_uom_id':raw.product_id.uom_id.id,
                    'disponible':raw.product_id.qty_available              })
                    for raw in raws:
                     product_qty=float(raw.product_qty*quantity_row)
                     self.recursive_search_bom_semi(cr, uid, ids,raw,record,manuf_prod,product_qty)
    def recursive_search_bom(self, cr, uid, ids,raw,record,manuf_prod, quantity_row, context=None):


                 a=self.pool.get('mrp.bom').search(cr, uid, [('product_id', 'in', [ raw.product_id.id])], context=context)
                 raws_ids=self.pool.get('mrp.bom.line').search(cr, uid, [('bom_id', 'in', a)], context=context)
                 raws=self.pool.get('mrp.bom.line').browse(cr, uid, raws_ids, context=context)

                 if not a:
                  pdp_raw=self.pool.get('pdp.raw').create(cr,uid,{
                    'product_id': raw.product_id.id,
                    'pdp_id':record,
                    'product_uom_id':raw.product_id.uom_id.id,
                    'factor':quantity_row,
                    'quantity':manuf_prod.total,
                    'parent_product_id':manuf_prod.product_id.id,
                })
                 else:
                    for raw in raws:
                     product_qty=float(raw.product_qty*quantity_row)
                     self.recursive_search_bom(cr, uid, ids,raw,record,manuf_prod,product_qty)
    def recursive_search_bom_sf_eclate(self, cr, uid, ids,raw,record,manuf_prod, quantity_row, context=None):
                 a=self.pool.get('mrp.bom').search(cr, uid, [('product_id', 'in', [ raw.product_id.id])], context=context)
                 raws_ids=self.pool.get('mrp.bom.line').search(cr, uid, [('bom_id', 'in', a)], context=context)
                 raws=self.pool.get('mrp.bom.line').browse(cr, uid, raws_ids, context=context)

                 if not a:
                  pdp_raw=self.pool.get('pdp.raw.bom.eclate').create(cr,uid,{
                    'product_id': raw.product_id.id,
                    'pdp_id':record,
                    #'factor':float(raw.product_qty),
                    'product_uom_id':raw.product_id.uom_id.id,
                    'disponible':float(raw.product_qty)*quantity_row,
                    #'parent_product_id':product.product_id.id,
                })
                 else:
                    for raw in raws:
                     product_qty=float(raw.product_qty*quantity_row)
                     self.recursive_search_bom_sf_eclate(cr, uid, ids,raw,record,manuf_prod,product_qty)

    def action_compute_semi(self, cr, uid, ids, context=None):

        a=self.pool.get('pdp.raw.group').search(cr, uid, [('pdp_id', 'in', ids)], context=context)
        self.pool.get('pdp.raw.group').unlink(cr, uid, a, context)
        a=self.pool.get('pdp.raw.bom.eclate').search(cr, uid, [('pdp_id', 'in', ids)], context=context)
        self.pool.get('pdp.raw.bom.eclate').unlink(cr, uid, a, context)

        product_qty=1.00

        a=self.pool.get('pdp.raw').search(cr, uid, [('pdp_id', 'in', ids)], context=context)
        self.pool.get('pdp.raw').unlink(cr, uid, a, context)

        b=self.pool.get('pdp.raw.bom').search(cr, uid, [('pdp_id', 'in', ids)], context=context)
        self.pool.get('pdp.raw.bom').unlink(cr, uid, b, context)

        for record in self.browse(cr, uid, ids, context):

            for product in record.line_ids:

                a=self.pool.get('mrp.bom').search(cr, uid, [('product_id', 'in', [ product.product_id.id])], context=context)
                raws_ids=self.pool.get('mrp.bom.line').search(cr, uid, [('bom_id', 'in', a)], context=context)
                raws=self.pool.get('mrp.bom.line').browse(cr, uid, raws_ids, context=context)
                #My_error_Msg=raws

                #raise osv.except_osv(_("Error!"), _(My_error_Msg)+'mm'+_(err))
                #raise osv.except_osv(_("Error!"), _(My_error_Msg))
                for raw in raws:
                 bom_obj = self.pool.get('mrp.bom')
                 a=self.pool.get('mrp.bom').search(cr, uid, [('product_id', 'in', [ raw.product_id.id])], context=context)
                 raws_ids=self.pool.get('mrp.bom.line').search(cr, uid, [('bom_id', 'in', a)], context=context)
                 raws=self.pool.get('mrp.bom.line').browse(cr, uid, raws_ids, context=context)
                 My_error_Msg=str(product)
                 #raise osv.except_osv(_("Error!"), _(My_error_Msg))
                 if  a:
                    b=self.pool.get('pdp.raw.bom').search(cr, uid, [('pdp_id', '=', record.id),('product_id','=',raw.product_id.id)], context=context)
                    if not b and  raw.product_id.qty_available!=0:

                     pdp_raw_bom=self.pool.get('pdp.raw.bom').create(cr,uid,{
                    'product_id': raw.product_id.id,
                    'pdp_id':record.id,
                    'product_uom_id':raw.product_id.uom_id.id,
                    'disponible':raw.product_id.qty_available                })
                    manuf_prod=product
                    product_qty=float( raw.product_qty*product_qty)
                    self.recursive_search_bom_semi( cr, uid, ids,raw,record.id,manuf_prod,product_qty)

        return True
    #eclate le disponible du SF
    def action_compute_eclate_SF(self, cr, uid, ids, context=None):

        a=self.pool.get('pdp.raw.bom.eclate').search(cr, uid, [('pdp_id', 'in', ids)], context=context)
        self.pool.get('pdp.raw.bom.eclate').unlink(cr, uid, a, context)
        a=self.pool.get('pdp.raw.group').search(cr, uid, [('pdp_id', 'in', ids)], context=context)
        self.pool.get('pdp.raw.group').unlink(cr, uid, a, context)


        a=self.pool.get('pdp.raw').search(cr, uid, [('pdp_id', 'in', ids)], context=context)
        self.pool.get('pdp.raw').unlink(cr, uid, a, context)


        for record in self.browse(cr, uid, ids, context):

            for product in record.line_brut_bom_ids:
                product_qty=product.disponible


                #product_obj = self.pool.get('product.product')

                a=self.pool['mrp.bom'].search(cr, uid, [('product_id', 'in', [ product.product_id.id])], context=context)
                raws_ids=self.pool['mrp.bom.line'].search(cr, uid, [('bom_id', 'in', a)], context=context)
                raws=self.pool['mrp.bom.line'].browse(cr, uid, raws_ids, context=context)
                #My_error_Msg=raws

                #raise osv.except_osv(_("Error!"), _(My_error_Msg)+'mm'+_(err))
                #raise osv.except_osv(_("Error!"), _(My_error_Msg))
                for raw in raws:

                 a=self.pool['mrp.bom'].search(cr, uid, [('product_id', 'in', [ raw.product_id.id])], context=context)
                 raws_ids=self.pool['mrp.bom.line'].search(cr, uid, [('bom_id', 'in', a)], context=context)
                 raws=self.pool['mrp.bom.line'].browse(cr, uid, raws_ids, context=context)
                 My_error_Msg=str(product)
                 #raise osv.except_osv(_("Error!"), _(My_error_Msg))
                 if not a:

                   pdp_raw=self.pool.get('pdp.raw.bom.eclate').create(cr,uid,{
                    'product_id': raw.product_id.id,
                    'pdp_id':record.id,
                    #'factor':float(raw.product_qty),
                    'product_uom_id':raw.product_id.uom_id.id,
                    'disponible':float(raw.product_qty)*product_qty,
                    #'parent_product_id':product.product_id.id,
                })
                 else:
                    manuf_prod=product
                    product_qty=float( raw.product_qty*product_qty)
                    self.recursive_search_bom_sf_eclate( cr, uid, ids,raw,record.id,manuf_prod,product_qty)

        return True

    ## Calcul des besoins bruts en MP sans le disponible en SFs
    def action_compute(self, cr, uid, ids, context=None):

        a=self.pool.get('pdp.raw.group').search(cr, uid, [('pdp_id', 'in', ids)], context=context)
        self.pool.get('pdp.raw.group').unlink(cr, uid, a, context)

        product_qty=1.00
        a=self.pool.get('pdp.raw').search(cr, uid, [('pdp_id', 'in', ids)], context=context)
        self.pool.get('pdp.raw').unlink(cr, uid, a, context)

        for record in self.browse(cr, uid, ids, context):

            for product in record.line_ids:
                My_error_Msg=str( record.id)
                err=str( product.product_id)
                #product_obj = self.pool.get('product.product')
                a=self.pool.get('mrp.bom').search(cr, uid, [('product_id', 'in', [ product.product_id.id])], context=context)
                raws_ids=self.pool.get('mrp.bom.line').search(cr, uid, [('bom_id', 'in', a)], context=context)
                raws=self.pool.get('mrp.bom.line').browse(cr, uid, raws_ids, context=context)
                #My_error_Msg=raws

                #raise osv.except_osv(_("Error!"), _(My_error_Msg)+'mm'+_(err))
                #raise osv.except_osv(_("Error!"), _(My_error_Msg))
                for raw in raws:
                 a=self.pool.get('mrp.bom').search(cr, uid, [('product_id', 'in', [ raw.product_id.id])], context=context)
                 raws_ids=self.pool.get('mrp.bom.line').search(cr, uid, [('bom_id', 'in', a)], context=context)
                 raws=self.pool.get('mrp.bom.line').browse(cr, uid, raws_ids, context=context)

                 #raise osv.except_osv(_("Error!"), _(My_error_Msg))
                 if not a:

                   pdp_raw=self.pool.get('pdp.raw').create(cr,uid,{
                    'product_id': raw.product_id.id,
                    'pdp_id':record.id,
                    'factor':float(raw.product_qty),
                    'product_uom_id':raw.product_id.uom_id.id,
                    'quantity':product.total,
                    'parent_product_id':product.product_id.id,
                })
                 else:
                    manuf_prod=product
                    product_qty=float( raw.product_qty*product_qty)
                    self.recursive_search_bom( cr, uid, ids,raw,record.id,manuf_prod,product_qty)

        return True
    def action_raz(self, cr, uid, ids, context=None):
        brut_bom = self.browse(cr, uid, ids[0], context=context)
        line_brut_bom_ids = [line.id for line in brut_bom.line_brut_bom_ids]
        self.pool.get('pdp.raw.bom').write(cr, uid, line_brut_bom_ids, {'disponible': 0})
        return True

    def product_exist(self, cr, uid, ids,a,rows, context=None):
        Exist=False
        j=0
        for i in rows:
            if a[0]==i[0]:
                return [True, j]
            j=j+1
        return [False,j]
    def action_compute_mp_sf_grouped(self, cr, uid, ids, context=None):
        a=self.pool.get('pdp.raw.bom.grouped').search(cr, uid, [('pdp_id', 'in', ids)], context=context)
        self.pool.get('pdp.raw.bom.grouped').unlink(cr, uid, a, context)

        sql="select product_id, pdp_id,sum(disponible) as total,product_uom_id from pdp_raw_bom_eclate where pdp_id="+str(ids[0])+" group by pdp_id,product_id,product_uom_id;"
        cr.execute(sql)
        res=[]
        for t in cr.dictfetchall():
            #My_error_Msg=str(t)
            a=[]
            a.append(t['product_id'])
            a.append(t['pdp_id'])
            a.append(t['product_uom_id'])
            a.append(t['total'])
            if self.product_exist(cr, uid, ids,a,res)[0]:
                indice=self.product_exist (cr, uid, ids,a,res)[1]
                b=res[indice]
                b[3]=b[3]+ a[3]
                b[4]=str(b[4])+','+str(a[4])
                res[indice]=b
            else:
                #sql="insert into pdp_raw_group_lines values = ("+","+")"
                cr.execute(sql)
                res.append(a)
        #t=res
        for t in res:

            pdp_raw=self.pool.get('pdp.raw.bom.grouped').create(cr,uid,{
                'product_id':t[0],
                'pdp_id':t[1],
                #'factor': t['factor'],
                'product_uom_id': t[2],
                'disponible': t[3],
                #'parent_product_id': t[4],
                 })






        return True

    def action_compute_total_grouped(self, cr, uid, ids, context=None):
        a=self.pool.get('pdp.raw.group').search(cr, uid, [('pdp_id', 'in', ids)], context=context)
        self.pool.get('pdp.raw.group').unlink(cr, uid, a, context)
        products_available=[]
        quantities_available=[]
        for record in self.browse(cr, uid, ids, context):

            for product in record.line_brut_bom_grouped_ids:
                products_available.append(product.product_id.id)
                quantities_available.append(product.disponible)

        #raise osv.except_osv(_('Invalid Action!'), _(products_available))
        sql="select product_id, parent_product_id, pdp_id,sum(total) as total,product_uom_id from pdp_raw where pdp_id="+str(ids[0])+" group by pdp_id,product_id,product_uom_id,parent_product_id;"
        cr.execute(sql)
        res=[]
        for t in cr.dictfetchall():
            #My_error_Msg=str(t)
            a=[]
            a.append(t['product_id'])
            a.append(t['pdp_id'])
            a.append(t['product_uom_id'])
            a.append(t['total'])

            a.append(t['parent_product_id'])

            if self.product_exist(cr, uid, ids,a,res)[0]:
                indice=self.product_exist (cr, uid, ids,a,res)[1]
                b=res[indice]
                b[3]=b[3]+ a[3]
                b[4]=str(b[4])+','+str(a[4])
                res[indice]=b
            else:
                #sql="insert into pdp_raw_group_lines values = ("+","+")"
                cr.execute(sql)
                res.append(a)
        #t=res
        for t in res:
            if t[0] in products_available:

                total_net = t[3]-quantities_available[products_available.index(t[0])]

                #raise osv.except_osv(_('Invalid Action!'), _(t['total']-quantities_available[products_available.index(t['product_id'])]))
            else:
                total_net = t[3]

            pdp_raw=self.pool.get('pdp.raw.group').create(cr,uid,{
                'product_id':t[0],
                'pdp_id':t[1],
                #'factor': t['factor'],
                'product_uom_id': t[2],
                'total': t[3],
                'total_net': total_net,
                 })

            parent=str( t[4]).split(",")
            for k in parent:
                sql = "insert into pdp_raw_group_lines values ("+str( pdp_raw)+","+str( k)+");"
                cr.execute(sql)





        return True



    def generate_cnb (self, cr, uid, ids, context=None):
       cbn_obj = self.pool.get('cbn')
       cbn_line_obj=self.pool.get('cbn.line')
       cbn_raw_bom_obj=self.pool.get('cbn.raw.bom')
       for record in self.browse(cr, uid, ids, context):
        if record.cbn_id:
            raise osv.except_osv(_('Invalid Action!'), _("Le CBNa été déjà généré."))

        else:

            cbn_id = cbn_obj.create(cr,uid,{'pdp_id':record.id,})
            self.write(cr, uid, ids, {'cbn_id': cbn_id})

            for product in record.line_brut_grouped_ids:
                pdp_raw=cbn_line_obj.create(cr,uid,{
                        'product_id': product.product_id.id,
                        'cbn_id':cbn_id,
                        'product_uom_id':product.product_uom_id.id,
                        'needed_quantity':product.total,

                    })
            for product in record.line_brut_bom_ids:
                pdp_raw=cbn_raw_bom_obj.create(cr,uid,{
                        'product_id': product.product_id.id,
                        'cbn_id':cbn_id,
                        'product_uom_id':product.product_uom_id.id,
                        'disponible':product.disponible,

                    })


    _defaults = {
        # 'doors': 5,
        # 'odometer_unit': 'kilometers',
        # 'state_id': _get_default_state,
    }

class pdp_line(osv.osv):
    _name = "pdp.line"
    _description = "Lignes du PDP"
    _rec_name = 'product_id'
    #def product_id_change(self, cr, uid, ids, product,context=None):
        #raise osv.except_osv(_('Invalid Action!'), _(product))
        #values = {'cession_price': product.standard_price}
    #    return {'value': values}#, 'domain': domain, 'warning': warning}

    @api.depends('january', 'february','march','april','mai','june','july','august','september','october','november','december')
    def _get_total(self):
        for record in self:
            record.total=record.january+record.february+record.march+record.april+record.mai+record.june+record.july+record.august+record.september+record.october+record.november+record.december
    @api.depends('total', 'cession_price')
    def _get_total_price(self):
        for record in self:
            record.total_cession_price=record.total*record.cession_price
    @api.depends('product_id')
    def _get_price(self):
        for record in self:
            record.cession_price=record.product_id.standard_price


    _columns = {
        'product_id': fields.many2one('product.product', 'Produit', domain=[('purchase_ok', '=', False),('sale_ok', '=', True)]),
        'cession_price': fields.float('Prix de cession',compute='_get_price'),
        'product_uom_id': fields.many2one('product.uom', 'Unité de mesure'),
        'pdp_id': fields.many2one('pdp', 'PDP', ondelete='cascade'),
        'operating_unit_id': fields.many2one('operating.unit', 'Unite d\'organisation', ondelete='cascade'),
        'january': fields.integer('Janvier',help='Janvier'),
        'february': fields.integer('Fevrier',help='Fevrier'),
        'march': fields.integer('Mars',help='Mars'),
        'april': fields.integer('Avril',help='Avril'),
        'mai': fields.integer('Mai',help='Mai'),
        'june': fields.integer('Juin',help='Juin'),
        'july': fields.integer('Juillet',help='Juillet'),
        'august': fields.integer('Aout',help='Aout'),
        'september': fields.integer('Septembre',help='Septembre'),
        'october': fields.integer('Octobre',help='Octobre'),
        'november': fields.integer('Novembre',help='Novembre'),
        'december': fields.integer('Décembre',help='Decembre'),
        'total': fields.integer('Total',compute='_get_total',readonly=True,store=True),
        'total_cession_price': fields.float('Prix de cession total',compute='_get_total_price',readonly=True,store=True),


        }


class pdp_raw(osv.osv):
    _name = "pdp.raw"
    _description = "Lignes de MP"
    _rec_name = 'product_id'

    @api.depends('factor','quantity')
    def _get_total(self):
        for record in self:
            record.total=record.factor*record.quantity




    _columns = {
        'product_id': fields.many2one('product.product', string= 'Produit', domain=[('purchase_ok', '=', False)],readonly=True),
        'product_uom_id': fields.many2one('product.uom', string='Unité de mesure',readonly=True),
        'pdp_id': fields.many2one('pdp',string='PDP', ondelete='cascade'),
        'factor': fields.float(string='Facteur', required=True,help='Factor'),
        'quantity': fields.float(string='Quantité',help='Quantity'),
        'total': fields.float(string='Quantité totale', compute='_get_total',readonly=True,store=True),
        'parent_product_id': fields.many2one('product.product', 'Nomenclature', domain=[('purchase_ok', '=', False)]),

}

class pdp_raw_group(osv.osv):
    _name = "pdp.raw.group"
    _description = "Lignes de MP groupees"
    _rec_name = 'product_id'

    @api.depends('factor','quantity')
    def _get_total(self):
        for record in self:
            record.total=record.factor*record.quantity





    _columns = {
        'product_id': fields.many2one('product.product', string= 'Produit', domain=[('purchase_ok', '=', False)],readonly=False),
        'product_uom_id': fields.many2one('product.uom', string='Unité de mesure',readonly=False),
        'pdp_id': fields.many2one('pdp',string='PDP', ondelete='cascade'),
        'total': fields.float(string='Quantité brute',readonly=False),
         'parent_product_id': fields.many2many('product.product', 'pdp_raw_group_lines', 'pdp_raw_group_id', 'product_id', 'Nomenclatures', readonly=True),
        'total_net': fields.float(string='Quantité nette',readonly=False),
        }




class pdp_raw_bom(osv.osv):
    _name = "pdp.raw.bom"
    _description = "Semis finis"
    _rec_name = 'product_id'






    _columns = {
        'product_id': fields.many2one('product.product', string= 'Produit', domain=[('purchase_ok', '=', False)],readonly=False),
        'product_uom_id': fields.many2one('product.uom', string='Unité de mesure',readonly=False),
        'pdp_id': fields.many2one('pdp',string='PDP', ondelete='cascade'),
        'disponible': fields.float(string='Disponible',readonly=False),

         #'parent_product_id': fields.many2many('product.product', 'pdp_raw_group_lines', 'pdp_raw_group_id', 'product_id', 'Nomenclatures', readonly=True),

        }


class pdp_raw_bom_eclate(osv.osv):
    _name = "pdp.raw.bom.eclate"
    _description = "Composants des SFs"
    _rec_name = 'product_id'






    _columns = {
        'product_id': fields.many2one('product.product', string= 'Produit', domain=[('purchase_ok', '=', False)],readonly=False),
        'product_uom_id': fields.many2one('product.uom', string='Unité de mesure',readonly=False),
        'pdp_id': fields.many2one('pdp',string='PDP', ondelete='cascade'),
        'disponible': fields.float(string='Disponible',readonly=False),

         #'parent_product_id': fields.many2many('product.product', 'pdp_raw_group_lines', 'pdp_raw_group_id', 'product_id', 'Nomenclatures', readonly=True),

        }


class pdp_raw_bom_eclate(osv.osv):
    _name = "pdp.raw.bom.grouped"
    _description = "Composants des SFs groupes"
    _rec_name = 'product_id'






    _columns = {
        'product_id': fields.many2one('product.product', string= 'Produit', domain=[('purchase_ok', '=', False)],readonly=False),
        'product_uom_id': fields.many2one('product.uom', string='Unite de mesure',readonly=False),
        'pdp_id': fields.many2one('pdp',string='PDP', ondelete='cascade'),
        'disponible': fields.float(string='Disponible',readonly=False),

         #'parent_product_id': fields.many2many('product.product', 'pdp_raw_group_lines', 'pdp_raw_group_id', 'product_id', 'Nomenclatures', readonly=True),

        }




##class product_product(osv.osv):
##  _inherit = 'product.product'
##
##  def has_bom(self, cr, uid, ids, context=None):
##        pdp_obj = self.pool.get('mrp.bom')
##        a=pdp_obj.pool['mrp.bom'].search(cr, uid, [('product_id', 'in', ids)], context=context)
##        return a

