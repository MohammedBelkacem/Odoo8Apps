# -*- coding: utf-8 -*-
##############################################################################

{
    'name' : 'Notification sur store, BU, user, role',
    'version' : '0.1',
    'author' : 'Belkacem Mohammed',
    'sequence': 110,
    'category': 'Technique',
    'website' : 'belkacemmohammed.com',
    'summary' : 'Ajout de notifications diverses pour controler les modifications',

    'depends' : [
        'base',
        'mail',

         "insidjam_multi_store_ou",
         "operating_unit"


    ],
    'data' : [
    'views/restore_view.xml',


    ],
    'installable' : True,
    'application' : True,
}
