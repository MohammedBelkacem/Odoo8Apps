# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "ENIEM Others",
    "version" : "1.0",
    "author" : "ENIEM",
    "website" : "http://www.eniem.dz",
    "category" : "Extra",
    "depends" : ['mrp','purchase','account_accountant','stock','insidjam_pack_std','insidjam_purchase_secondary_unit','purchase_landed_cost'],
    "data" : [

       "views/invoice_view.xml",
        "views/stock_reception_view.xml",
        'views/mrp_routing_workcenter.xml',
       "views/purchase_order.xml",
       "wizard/import_invoice_line_view.xml",
    ],
    "demo_xml" : [],
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
