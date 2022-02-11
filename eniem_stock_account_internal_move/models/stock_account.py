from openerp.osv import fields, osv
from openerp.tools import float_compare, float_round
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, api
import logging
_logger = logging.getLogger(__name__)


class stockquant(osv.osv):
    _inherit = "stock.quant"


    # @override
    def _account_entry_move(self, cr, uid, quants, move, context=None):
        super(stockquant, self)._account_entry_move(cr, uid, quants, move, context=context)
        if context is None:
            context = {}
        location_obj = self.pool.get('stock.location')
        location_from = move.location_id
        location_to = quants[0].location_id
        company_from = location_obj._location_owner(cr, uid, location_from, context=context)
        company_to = location_obj._location_owner(cr, uid, location_to, context=context)
        if (move.location_id.usage == 'internal' and move.location_dest_id.usage == 'internal') \
            and (move.location_id.force_accounting_entries == True or move.location_dest_id.force_accounting_entries==True):
            ctx = context.copy()
            ctx['force_company'] = company_from.id
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, context=ctx)
            self._create_account_move_line(cr, uid, quants, move, acc_valuation, acc_dest, journal_id, context=ctx)

    # @override
    def _get_accounting_data_for_valuation(self, cr, uid, move, context=None):
        journal_id, acc_src, acc_dest, acc_valuation=super(stockquant, self)._get_accounting_data_for_valuation(cr, uid, move, context=context)
        if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'internal' \
                and (move.location_id.force_accounting_entries == True or move.location_dest_id.force_accounting_entries==True):
                #raise osv.except_osv(_('Invalid Action!'), _(str(move.location_id.force_accounting_entries) + str(move.location_dest_id.force_accounting_entries)))
                #raise osv.except_osv(_('Invalid Action!'), _(move.location_id.valuation_out_account_id.name))
                # retreive the aacont input and account output
                #cas source est activee et destination# est pas activee debiter la valorisation du produit et crediter le compte de l emplacement
                if move.location_id.force_accounting_entries == True and move.location_dest_id.force_accounting_entries==False:
                    acc_src=""
                    acc_dest=acc_valuation
                    acc_valuation=move.location_id.valuation_in_account_id.id
                    #raise osv.except_osv(_('Invalid Action!'), _('1'))

                #cas source est non activee et destination est  activee
                if  move.location_id.force_accounting_entries == False and move.location_dest_id.force_accounting_entries==True:
                    acc_src=""
                    acc_dest=move.location_dest_id.valuation_in_account_id.id
                    #raise osv.except_osv(_('Invalid Action!'), _('2'))

                #cas source est activee et destination est  activee
                if  move.location_id.force_accounting_entries == True and move.location_dest_id.force_accounting_entries==True:
                    acc_src=""
                    acc_dest=move.location_dest_id.valuation_in_account_id.id
                    acc_valuation=move.location_id.valuation_in_account_id.id


                    #raise osv.except_osv(_('Invalid Action!'), _('3'))


        return journal_id, acc_src, acc_dest, acc_valuation
    def _get_accounting_data_for_valuation(self, cr, uid, move, context=None):
        """
        Return the accounts and journal to use to post Journal Entries for the real-time
        valuation of the quant.

        :param context: context dictionary that can explicitly mention the company to consider via the 'force_company' key
        :returns: journal_id, source account, destination account, valuation account
        :raise: osv.except_osv() is any mandatory account or journal is not defined.
        """
        product_obj = self.pool.get('product.template')
        accounts = product_obj.get_product_accounts(cr, uid, move.product_id.product_tmpl_id.id, context)
        if move.location_id.valuation_out_account_id and (move.location_id.usage != 'internal' or (move.location_id.usage == 'internal' and move.location_id.force_accounting_entries==True )) :
            acc_src = move.location_id.valuation_out_account_id.id
        else:
            acc_src = accounts['stock_account_input']

        if move.location_dest_id.valuation_in_account_id and (move.location_dest_id.usage != 'internal' or (move.location_dest_id.usage == 'internal' and move.location_dest_id.force_accounting_entries==True )) :
            acc_dest = move.location_dest_id.valuation_in_account_id.id
        else:
            acc_dest = accounts['stock_account_output']

        acc_valuation = accounts.get('property_stock_valuation_account_id', False)
        journal_id = accounts['stock_journal']
        return journal_id, acc_src, acc_dest, acc_valuation