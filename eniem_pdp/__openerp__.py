# -*- coding: utf-8 -*-
##############################################################################

{
    'name' : 'Programme général d\'approvisionnement',
    'version' : '0.1',
    'author' : 'Belkacem Mohammed',
    'sequence': 110,
    'category': 'Plan général d\'approvisionnemet',
    'website' : 'eniem.dz',
    'summary' : 'PGA, PDP, CBN,DAI, Consultation, Programme de Production, Celcul des besoins nets, demande d''achat interne, approvisionnements',

    'depends' : [
        'base',
        'mail',
        'stock',
        'procurement',
        'purchase',
         'operating_unit',
         'purchase_requisition',
         'eniem_purchase',
         'insidjam_product_kit',
         'mrp',
         "insidjam_multi_store_ou"


    ],
    'data' : [
    'views/pdp_view.xml',
    'views/product_product_view.xml',
    'views/cbn_view.xml',
    'wizard/dai_change_view.xml',
    'views/dai_view.xml',
    'views/purchase_requisition.xml',
    'views/purchase_requisition_partners.xml',
    'views/res_store_view.xml',
    'reports/report_pdp.xml',
    'reports/report_dai.xml',
    'reports/report_pdp_besoins.xml',
    ##'report/report_stockpicking.xml',
    'data/data.xml',
    'data/sequence.xml',
    'security/pdp_security.xml',
    'security/ir.model.access.csv',
    'workflow/dai_workflow.xml',
    'workflow/pdp_workflow.xml',

    ],
    'installable' : True,
    'application' : True,
}
