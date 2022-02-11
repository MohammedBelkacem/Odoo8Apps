# -*- coding: utf-8 -*-
##############################################################################

{
    'name' : 'Workflow pour nomenclature et gamme de production',
    'version' : '0.1',
    'author' : 'ENIEM',
    'sequence': 110,
    'category': 'Workflow pour nomenclature et gamme de production',
    'website' : 'eniem.dz',
    'summary' : 'Définir un workflow pour les gammes et production',

    'depends' : [
        'base',
        'mail',
        'mrp',
        'eniem_bom_eclate_report',

    ],
    'data' : [
    'views/bom_view.xml',
    'views/routing_view.xml',
    'views/mrp_production_view.xml'
    #'views/pdp_view.xml','views/cbn_view.xml','views/dai_view.xml','views/forecast.xml','reports/raw_needs.xml',
    #'reports/report_pdp.xml','data/data.xml','data/sequence.xml'

    ],
    'installable' : True,
    'application' : True,
}
