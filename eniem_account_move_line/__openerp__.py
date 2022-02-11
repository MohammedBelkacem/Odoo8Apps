# -*- coding: utf-8 -*-
##############################################################################

{
    'name' : 'Amélioration pour analyser les écritures',
    'version' : '0.1',
    'author' : 'ENIEM',
    'sequence': 110,
    'category': 'ENIEM',
    'website' : 'eniem.dz',
    'summary' : 'Ajout de la catégorie de produit sur la ligne d''écriture, ajout du groupage par produit, par catégorie de produit et par liste de prix, ajout d''un wizard pour l''affectation des catégories ',

    'depends' : [
        'base',
        'mail',
        'account',

    ],
    'data' : ['views/account_move_line.xml','reports/report_fiche_imputation.xml','wizard/account_validate_move_view.xml','data/data.xml'

    ],
    'installable' : True,
    'application' : True,
}
