# -*- coding: utf-8 -*-
##############################################################################

{
    'name' : 'BOM detailed',
    'version' : '0.1',
    'author' : 'ENIEM',
    'sequence': 110,
    'category': 'Bill of material detailed',
    'website' : 'eniem.dz',
    'summary' : 'Bill of Material detailed, ',

    'depends' : [
        'base',
        'mail',
        'mrp',

    ],
    'data' : ['views/mrp_bom_view.xml','reports/bom_detailed.xml'],
    'installable' : True,
    'application' : True,
}
