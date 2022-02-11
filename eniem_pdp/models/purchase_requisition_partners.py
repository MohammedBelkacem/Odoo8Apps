# -*- encoding: utf-8 -*-
import json
from datetime import datetime
from openerp.osv import fields, osv
from openerp import models, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import api, modules


class purchase_requisition_partner(models.Model):
    _inherit = 'purchase.requisition.partner'

    def get_approved_suppliers_by_products (self):
        active_id = self.env.context.get('active_id', []) or []

        cr = self.env.cr
        uid = self.env.uid
        context = self.env.context

        supplier_ids=[]
        #raise osv.except_osv(_('Invalid Action!'), _(active_id))

        purchase_requisition = self.pool.get('purchase.requisition')

        purchase_requisition_ids = purchase_requisition.browse(cr, uid, active_id, context)
        #raise osv.except_osv(_('Invalid Action!'), _(purchase_requisition_ids))
        suppliers=[]
        ids_part=[]
        produits=[]
        domain=[]
        for line in purchase_requisition_ids: #les requisitions
            if line.type_consultation=="tous":
             domain=[('supplier','=',True)]
            else:


                for product in line.line_ids: # lignes des requisitions

                    product1=self.env['product.product'].sudo().search([('id', 'in', [product.product_id.id])])
                    produits.append(product1)

                    product_supplier_info=self.pool.get('product.supplierinfo').search(cr, uid, [('product_tmpl_id', 'in', [product1.product_tmpl_id.id])], context=context)
                    suppliers=self.pool.get('product.supplierinfo').browse(cr, uid, product_supplier_info, context=context)
                    #raise osv.except_osv(_('Invalid Action!'), _(suppliers))
                    for i in suppliers:
                        #raise osv.except_osv(_('Invalid Action!'), _(i.name.id))
                     if i.name.approved_supplier and i.name.supplier :
                        ids_part.append(i.name.id)
                domain=[('id','in',ids_part)]
                self.write({'flter_domaine': [(4, ids_part)] })
                #self.flter_domaine =  [(6,0, ids_part)]
        #raise osv.except_osv(_('Invalid Action!'), _(ids_part))
        return  domain

    def get_filter (self):
        self.get_approved_suppliers_by_products()
        return str(self.get_approved_suppliers_by_products()[0][2])

    @api.multi
    def get_education_domain(self):
        active_id = self.env.context.get('active_id', []) or []

        cr = self.env.cr
        uid = self.env.uid
        context = self.env.context

        if True:

            supplier_ids=[]
            purchase_requisition = self.pool.get('purchase.requisition')

            purchase_requisition_ids = purchase_requisition.browse(cr, uid, active_id, context)
            suppliers=[]
            ids_part=[]
            produits=[]
            domain=[]
            for line in purchase_requisition_ids: #les requisitions
             if line.type_consultation=="tous":
              domain=[('supplier','=',True)]
             else:


                for product in line.line_ids: # lignes des requisitions

                    product1=self.env['product.product'].sudo().search([('id', 'in', [product.product_id.id])])
                    produits.append(product1)

                    product_supplier_info=self.pool.get('product.supplierinfo').search(cr, uid, [('product_tmpl_id', 'in', [product1.product_tmpl_id.id])], context=context)
                    suppliers=self.pool.get('product.supplierinfo').browse(cr, uid, product_supplier_info, context=context)
                    #raise osv.except_osv(_('Invalid Action!'), _(suppliers))
                    for i in suppliers:
                        #raise osv.except_osv(_('Invalid Action!'), _(i.name.id))
                     if i.name.approved_supplier and i.name.supplier :
                        ids_part.append(i.name.id)
                domain=[('id','in',ids_part)]


                #self.flter_domaine =  [(6,0, )]
            raise osv.except_osv(_('Invalid Action!'), _(self.id))
            self.write({'flter_domaine': [(4, ids_part)] })


    partner_id = fields.Many2one('res.partner', 'Supplier', required=False, domain=lambda self: self.get_approved_suppliers_by_products())
   # flter_domaine = fields.Char('Domaine',default=get_filter)
    #flter_domaine = fields.Many2many('res.partner',store=True,compute=lambda self: self.get_education_domain())
