from odoo import Command, fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestParaguayChartTemplate(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env['res.company'].create({
            'name': 'Empresa Paraguay - pruebas',
            'country_id': cls.env.ref('base.py').id,
        })
        cls.env = cls.env(context=dict(cls.env.context, allowed_company_ids=[cls.company.id]))
        cls.company = cls.company.with_env(cls.env)
        cls.chart = cls.env['account.chart.template'].with_context(l10n_check_fields_complete=True)
        cls.chart.try_loading('py', cls.company, install_demo=False)
        cls.partner = cls.env['res.partner'].create({
            'name': 'Cliente / proveedor de prueba Paraguay',
            'country_id': cls.env.ref('base.py').id,
        })

    def _company_records(self, model, company=None):
        company = company or self.company
        company_field = 'company_ids' if model == 'account.account' else 'company_id'
        return self.env[model].with_context(active_test=False).search([
            (company_field, 'in', company.ids),
        ])

    def test_company_currency_and_defaults(self):
        self.assertEqual(self.company.chart_template, 'py')
        self.assertEqual(self.company.account_fiscal_country_id, self.env.ref('base.py'))
        self.assertEqual(self.company.currency_id, self.env.ref('base.PYG'))
        self.assertTrue(self.company.currency_id.active)
        self.assertEqual(self.company.currency_id.rounding, 1.0)
        self.assertEqual(self.company.currency_id.decimal_places, 0)
        self.assertEqual(self.company.account_sale_tax_id, self.chart.ref('py_iva_sale_10'))
        self.assertEqual(self.company.account_purchase_tax_id, self.chart.ref('py_iva_purchase_10'))
        self.assertEqual(self.partner.property_account_receivable_id, self.chart.ref('py_receivable'))
        self.assertEqual(self.partner.property_account_payable_id, self.chart.ref('py_payable'))
        self.assertEqual(self.company.income_account_id, self.chart.ref('py_sales_goods'))
        self.assertEqual(self.company.expense_account_id, self.chart.ref('py_cost_of_sales'))
        self.assertEqual(
            len(self._company_records('account.account').filtered(
                lambda account: account.account_type == 'equity_unaffected'
            )),
            1,
        )

    def test_journals_and_liquidity_accounts(self):
        for xmlid, journal_type, code in (
            ('sale', 'sale', 'VEN'),
            ('purchase', 'purchase', 'COM'),
            ('general', 'general', 'VAR'),
            ('exch', 'general', 'DIF'),
            ('caba', 'general', 'ICEF'),
            ('bank', 'bank', 'BNK'),
            ('cash', 'cash', 'CSH'),
        ):
            with self.subTest(journal=xmlid):
                journal = self.chart.ref(xmlid)
                self.assertEqual(journal.type, journal_type)
                self.assertEqual(journal.code, code)
                self.assertEqual(journal.company_id, self.company)
        self.assertEqual(self.chart.ref('sale').default_account_id, self.chart.ref('py_sales_goods'))
        self.assertEqual(self.chart.ref('purchase').default_account_id, self.chart.ref('py_cost_of_sales'))
        for xmlid, account_id in (('bank', 'py_bank'), ('cash', 'py_cash')):
            journal = self.chart.ref(xmlid)
            self.assertEqual(journal.default_account_id, self.chart.ref(account_id))
            self.assertEqual(journal.suspense_account_id, self.chart.ref('py_bank_suspense'))
            self.assertEqual(journal.profit_account_id, self.chart.ref('py_cash_gain'))
            self.assertEqual(journal.loss_account_id, self.chart.ref('py_cash_loss'))
        self.assertEqual(self.company.currency_exchange_journal_id, self.chart.ref('exch'))
        self.assertTrue(self.company.transfer_account_id.reconcile)

    def test_tax_amounts_and_repartition_accounts(self):
        for use, account_prefix in (('sale', 'debit'), ('purchase', 'credit')):
            for rate, gross, vat in (('10', 110000, 10000), ('5', 105000, 5000), ('exempt', 100000, 0)):
                with self.subTest(use=use, rate=rate):
                    tax = self.chart.ref(f'py_iva_{use}_{rate}')
                    self.assertEqual(tax.type_tax_use, use)
                    self.assertEqual(tax.country_id, self.env.ref('base.py'))
                    self.assertTrue(tax.price_include)
                    self.assertEqual(tax.tax_exigibility, 'on_invoice')
                    self.assertEqual(tax.tax_group_id.country_id, self.env.ref('base.py'))
                    for repartition in (tax.invoice_repartition_line_ids, tax.refund_repartition_line_ids):
                        self.assertEqual(len(repartition), 2)
                        tax_line = repartition.filtered(lambda line: line.repartition_type == 'tax')
                        self.assertEqual(tax_line.factor_percent, 100)
                        if rate != 'exempt':
                            self.assertEqual(tax_line.account_id, self.chart.ref(f'py_iva_{account_prefix}_{rate}'))
                        else:
                            self.assertFalse(tax_line.account_id)
                    for refund in (False, True):
                        totals = tax.compute_all(gross, currency=self.company.currency_id, is_refund=refund)
                        self.assertEqual(totals['total_excluded'], 100000)
                        self.assertEqual(totals['total_included'], gross)
                        self.assertEqual(sum(line['amount'] for line in totals['taxes']), vat)

    def test_post_invoices_and_credit_notes(self):
        for move_type, use, tax_sign in (
            ('out_invoice', 'sale', -1),
            ('out_refund', 'sale', 1),
            ('in_invoice', 'purchase', 1),
            ('in_refund', 'purchase', -1),
        ):
            for rate, gross, vat in (('10', 110000, 10000), ('5', 105000, 5000), ('exempt', 100000, 0)):
                with self.subTest(move_type=move_type, rate=rate):
                    tax = self.chart.ref(f'py_iva_{use}_{rate}')
                    account = self.chart.ref('py_sales_goods' if use == 'sale' else 'py_cost_of_sales')
                    move = self.env['account.move'].create({
                        'move_type': move_type,
                        'company_id': self.company.id,
                        'currency_id': self.company.currency_id.id,
                        'partner_id': self.partner.id,
                        'journal_id': self.chart.ref('sale' if use == 'sale' else 'purchase').id,
                        'invoice_date': fields.Date.today(),
                        'invoice_line_ids': [Command.create({
                            'name': 'Operación de prueba',
                            'quantity': 1,
                            'price_unit': gross,
                            'account_id': account.id,
                            'tax_ids': [Command.set(tax.ids)],
                        })],
                    })
                    move.action_post()
                    self.assertEqual(move.state, 'posted')
                    self.assertEqual(move.amount_untaxed, 100000)
                    self.assertEqual(move.amount_tax, vat)
                    self.assertEqual(move.amount_total, gross)
                    self.assertTrue(self.company.currency_id.is_zero(sum(move.line_ids.mapped('balance'))))
                    tax_lines = move.line_ids.filtered('tax_line_id')
                    self.assertEqual(sum(tax_lines.mapped('balance')), tax_sign * vat)
                    if vat:
                        prefix = 'debit' if use == 'sale' else 'credit'
                        self.assertEqual(tax_lines.account_id, self.chart.ref(f'py_iva_{prefix}_{rate}'))

    def test_reload_preserves_records_and_customized_journals(self):
        models = ('account.account', 'account.tax', 'account.tax.group', 'account.journal', 'account.group')
        before = {model: set(self._company_records(model).ids) for model in models}
        self.chart.ref('bank').name = 'Banco elegido por la empresa'
        self.chart.try_loading('py', self.company, install_demo=False)
        for model in models:
            with self.subTest(model=model):
                self.assertEqual(set(self._company_records(model).ids), before[model])
        self.assertEqual(self.chart.ref('bank').name, 'Banco elegido por la empresa')

    def test_company_isolation(self):
        guatemala = self.env['res.company'].create({
            'name': 'Empresa Guatemala existente',
            'country_id': self.env.ref('base.gt').id,
            'currency_id': self.env.ref('base.GTQ').id,
        })
        gt_journal = self.env['account.journal'].with_company(guatemala).create({
            'name': 'Operaciones Guatemala',
            'code': 'GTOP',
            'type': 'general',
            'company_id': guatemala.id,
        })
        py_before = set(self._company_records('account.account').ids)
        second_company = self.env['res.company'].create({
            'name': 'Segunda empresa Paraguay',
            'country_id': self.env.ref('base.py').id,
        })
        second_chart = self.chart.with_company(second_company)
        second_chart.try_loading('py', second_company, install_demo=False)
        self.assertEqual(second_company.currency_id, self.env.ref('base.PYG'))
        self.assertEqual(guatemala.currency_id, self.env.ref('base.GTQ'))
        self.assertFalse(guatemala.chart_template)
        self.assertEqual(gt_journal.name, 'Operaciones Guatemala')
        self.assertEqual(self._company_records('account.journal', guatemala), gt_journal)
        self.assertEqual(set(self._company_records('account.account').ids), py_before)
        self.assertFalse(py_before & set(self._company_records('account.account', second_company).ids))
        for xmlid in ('py_receivable', 'py_iva_sale_10', 'sale', 'bank', 'cash'):
            self.assertNotEqual(self.chart.ref(xmlid), second_chart.ref(xmlid))
