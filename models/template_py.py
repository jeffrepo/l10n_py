from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('py')
    def _get_py_template_data(self):
        return {
            'name': 'Contabilidad base',
            'code_digits': '6',
            'property_account_receivable_id': 'py_receivable',
            'property_account_payable_id': 'py_payable',
        }

    @template('py', 'res.company')
    def _get_py_res_company(self):
        return {
            self.env.company.id: {
                # The standard loader activates base.PYG through base.py and
                # sets it as the currency for a new company without entries.
                'account_fiscal_country_id': 'base.py',
                'bank_account_code_prefix': '1102',
                'cash_account_code_prefix': '1101',
                'transfer_account_code_prefix': '1103',
                'transfer_account_id': 'py_transfer',
                'account_journal_suspense_account_id': 'py_bank_suspense',
                'account_default_pos_receivable_account_id': 'py_receivable_pos',
                'account_sale_tax_id': 'py_iva_sale_10',
                'account_purchase_tax_id': 'py_iva_purchase_10',
                'income_account_id': 'py_sales_goods',
                'expense_account_id': 'py_cost_of_sales',
                'income_currency_exchange_account_id': 'py_exchange_gain',
                'expense_currency_exchange_account_id': 'py_exchange_loss',
                'default_cash_difference_income_account_id': 'py_cash_gain',
                'default_cash_difference_expense_account_id': 'py_cash_loss',
                'account_journal_early_pay_discount_gain_account_id': 'py_discount_gain',
                'account_journal_early_pay_discount_loss_account_id': 'py_discount_loss',
            },
        }

    @template('py', 'account.journal')
    def _get_py_account_journal(self):
        # Reuse the standard journal identifiers so loading the template does
        # not create a second sales, purchases or bank journal.
        return {
            'sale': {'name': 'Ventas', 'code': 'VEN'},
            'purchase': {'name': 'Compras', 'code': 'COM'},
            'general': {'name': 'Operaciones diversas', 'code': 'VAR'},
            'exch': {'name': 'Diferencias de cambio', 'code': 'DIF'},
            'caba': {'name': 'Impuestos en base a efectivo', 'code': 'ICEF'},
            'bank': {
                'name': 'Banco',
                'code': 'BNK',
                'default_account_id': 'py_bank',
            },
            'cash': {
                'name': 'Caja',
                'code': 'CSH',
                'type': 'cash',
                'default_account_id': 'py_cash',
                'show_on_dashboard': True,
                'sequence': 8,
            },
        }
