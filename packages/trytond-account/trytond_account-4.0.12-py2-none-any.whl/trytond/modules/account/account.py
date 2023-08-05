# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from decimal import Decimal
import datetime
from functools import wraps

from sql import Column, Null, Window, Literal
from sql.aggregate import Sum, Max
from sql.conditionals import Coalesce, Case

from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.wizard import Wizard, StateView, StateAction, StateTransition, \
    Button
from trytond.report import Report
from trytond.tools import reduce_ids, grouped_slice
from trytond.pyson import Eval, PYSONEncoder
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond import backend

__all__ = ['TypeTemplate', 'Type', 'OpenType', 'AccountTemplate', 'Account',
    'AccountDeferral', 'OpenChartAccountStart', 'OpenChartAccount',
    'GeneralLedgerAccount', 'GeneralLedgerAccountContext',
    'GeneralLedgerLine', 'GeneralLedgerLineContext',
    'GeneralLedger', 'TrialBalance',
    'BalanceSheetContext', 'IncomeStatementContext',
    'AgedBalanceContext', 'AgedBalance', 'AgedBalanceReport',
    'CreateChartStart', 'CreateChartAccount', 'CreateChartProperties',
    'CreateChart', 'UpdateChartStart', 'UpdateChartSucceed', 'UpdateChart']


def inactive_records(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Transaction().set_context(active_test=False):
            return func(*args, **kwargs)
    return wrapper


class TypeTemplate(ModelSQL, ModelView):
    'Account Type Template'
    __name__ = 'account.account.type.template'
    name = fields.Char('Name', required=True)
    parent = fields.Many2One('account.account.type.template', 'Parent',
            ondelete="RESTRICT")
    childs = fields.One2Many('account.account.type.template', 'parent',
        'Children')
    sequence = fields.Integer('Sequence')
    balance_sheet = fields.Boolean('Balance Sheet')
    income_statement = fields.Boolean('Income Statement')
    display_balance = fields.Selection([
        ('debit-credit', 'Debit - Credit'),
        ('credit-debit', 'Credit - Debit'),
        ], 'Display Balance', required=True)

    @classmethod
    def __setup__(cls):
        super(TypeTemplate, cls).__setup__()
        cls._order.insert(0, ('sequence', 'ASC'))

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        table = TableHandler(cls, module_name)

        super(TypeTemplate, cls).__register__(module_name)

        # Migration from 2.4: drop required on sequence
        table.not_null_action('sequence', action='remove')

    @classmethod
    def validate(cls, records):
        super(TypeTemplate, cls).validate(records)
        cls.check_recursion(records, rec_name='name')

    @staticmethod
    def order_sequence(tables):
        table, _ = tables[None]
        return [Case((table.sequence == Null, 0), else_=1), table.sequence]

    @staticmethod
    def default_balance_sheet():
        return False

    @staticmethod
    def default_income_statement():
        return False

    @staticmethod
    def default_display_balance():
        return 'debit-credit'

    def get_rec_name(self, name):
        if self.parent:
            return self.parent.get_rec_name(name) + '\\' + self.name
        else:
            return self.name

    def _get_type_value(self, type=None):
        '''
        Set the values for account creation.
        '''
        res = {}
        if not type or type.name != self.name:
            res['name'] = self.name
        if not type or type.sequence != self.sequence:
            res['sequence'] = self.sequence
        if not type or type.balance_sheet != self.balance_sheet:
            res['balance_sheet'] = self.balance_sheet
        if not type or type.income_statement != self.income_statement:
            res['income_statement'] = self.income_statement
        if not type or type.display_balance != self.display_balance:
            res['display_balance'] = self.display_balance
        if not type or type.template != self:
            res['template'] = self.id
        return res

    def create_type(self, company_id, template2type=None):
        '''
        Create recursively types based on template.
        template2type is a dictionary with template id as key and type id as
        value, used to convert template id into type. The dictionary is filled
        with new types.
        '''
        pool = Pool()
        Type = pool.get('account.account.type')
        assert self.parent is None

        if template2type is None:
            template2type = {}

        def create(templates):
            values = []
            created = []
            for template in templates:
                if template.id not in template2type:
                    vals = template._get_type_value()
                    vals['company'] = company_id
                    if template.parent:
                        vals['parent'] = template2type[template.parent.id]
                    else:
                        vals['parent'] = None
                    values.append(vals)
                    created.append(template)

            types = Type.create(values)
            for template, type_ in zip(created, types):
                template2type[template.id] = type_.id

        childs = [self]
        while childs:
            create(childs)
            childs = sum((c.childs for c in childs), ())


class Type(ModelSQL, ModelView):
    'Account Type'
    __name__ = 'account.account.type'
    name = fields.Char('Name', size=None, required=True)
    parent = fields.Many2One('account.account.type', 'Parent',
        ondelete="RESTRICT", domain=[
            ('company', '=', Eval('company')),
            ], depends=['company'])
    childs = fields.One2Many('account.account.type', 'parent', 'Children',
        domain=[
            ('company', '=', Eval('company')),
        ], depends=['company'])
    sequence = fields.Integer('Sequence',
        help='Use to order the account type')
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
            'get_currency_digits')
    amount = fields.Function(fields.Numeric('Amount',
        digits=(16, Eval('currency_digits', 2)), depends=['currency_digits']),
        'get_amount')
    balance_sheet = fields.Boolean('Balance Sheet')
    income_statement = fields.Boolean('Income Statement')
    display_balance = fields.Selection([
        ('debit-credit', 'Debit - Credit'),
        ('credit-debit', 'Credit - Debit'),
        ], 'Display Balance', required=True)
    company = fields.Many2One('company.company', 'Company', required=True,
            ondelete="RESTRICT")
    template = fields.Many2One('account.account.type.template', 'Template')

    @classmethod
    def __setup__(cls):
        super(Type, cls).__setup__()
        cls._order.insert(0, ('sequence', 'ASC'))

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        table = TableHandler(cls, module_name)

        super(Type, cls).__register__(module_name)

        # Migration from 2.4: drop required on sequence
        table.not_null_action('sequence', action='remove')

    @classmethod
    def validate(cls, types):
        super(Type, cls).validate(types)
        cls.check_recursion(types, rec_name='name')

    @staticmethod
    def order_sequence(tables):
        table, _ = tables[None]
        return [Case((table.sequence == Null, 0), else_=1), table.sequence]

    @staticmethod
    def default_balance_sheet():
        return False

    @staticmethod
    def default_income_statement():
        return False

    @staticmethod
    def default_display_balance():
        return 'debit-credit'

    def get_currency_digits(self, name):
        return self.company.currency.digits

    @classmethod
    def get_amount(cls, types, name):
        pool = Pool()
        Account = pool.get('account.account')
        GeneralLedger = pool.get('account.general_ledger.account')

        res = {}
        for type_ in types:
            res[type_.id] = Decimal('0.0')

        childs = cls.search([
                ('parent', 'child_of', [t.id for t in types]),
                ])
        type_sum = {}
        for type_ in childs:
            type_sum[type_.id] = Decimal('0.0')

        start_period_ids = GeneralLedger.get_period_ids('start_%s' % name)
        end_period_ids = GeneralLedger.get_period_ids('end_%s' % name)
        period_ids = list(
            set(end_period_ids).difference(set(start_period_ids)))

        with Transaction().set_context(periods=period_ids):
            accounts = Account.search([
                    ('type', 'in', [t.id for t in childs]),
                    ('kind', '!=', 'view'),
                    ])
        for account in accounts:
            type_sum[account.type.id] += (account.debit - account.credit)

        for type_ in types:
            childs = cls.search([
                    ('parent', 'child_of', [type_.id]),
                    ])
            for child in childs:
                res[type_.id] += type_sum[child.id]
            res[type_.id] = type_.company.currency.round(res[type_.id])
            if type_.display_balance == 'credit-debit':
                res[type_.id] = - res[type_.id]
        return res

    def get_rec_name(self, name):
        if self.parent:
            return self.parent.get_rec_name(name) + '\\' + self.name
        else:
            return self.name

    @classmethod
    def delete(cls, types):
        types = cls.search([
                ('parent', 'child_of', [t.id for t in types]),
                ])
        super(Type, cls).delete(types)

    def update_type(self, template2type=None):
        '''
        Update recursively types based on template.
        template2type is a dictionary with template id as key and type id as
        value, used to convert template id into type. The dictionary is filled
        with new types
        '''
        if template2type is None:
            template2type = {}

        values = []
        childs = [self]
        while childs:
            for child in childs:
                if child.template:
                    vals = child.template._get_type_value(type=child)
                    if vals:
                        values.append([child])
                        values.append(vals)
                    template2type[child.template.id] = child.id
            childs = sum((c.childs for c in childs), ())
        if values:
            self.write(*values)


class OpenType(Wizard):
    'Open Type'
    __name__ = 'account.account.open_type'
    start_state = 'open_'
    open_ = StateAction('account.act_account_list2')

    def do_open_(self, action):
        action['pyson_domain'] = PYSONEncoder().encode([
                ('type', '=', Transaction().context['active_id']),
                ('kind', '!=', 'view'),
                ])
        action['pyson_context'] = PYSONEncoder().encode({
                'date': Transaction().context.get('date'),
                'posted': Transaction().context.get('posted'),
                'cumulate': Transaction().context.get('cumulate'),
                })
        return action, {}


class AccountTemplate(ModelSQL, ModelView):
    'Account Template'
    __name__ = 'account.account.template'
    name = fields.Char('Name', size=None, required=True, select=True)
    code = fields.Char('Code', size=None, select=True)
    type = fields.Many2One('account.account.type.template', 'Type',
        ondelete="RESTRICT",
        states={
            'invisible': Eval('kind') == 'view',
            'required': Eval('kind') != 'view',
            }, depends=['kind'])
    parent = fields.Many2One('account.account.template', 'Parent', select=True,
            ondelete="RESTRICT")
    childs = fields.One2Many('account.account.template', 'parent', 'Children')
    reconcile = fields.Boolean('Reconcile',
        states={
            'invisible': Eval('kind') == 'view',
            }, depends=['kind'])
    kind = fields.Selection([
            ('other', 'Other'),
            ('payable', 'Payable'),
            ('revenue', 'Revenue'),
            ('receivable', 'Receivable'),
            ('expense', 'Expense'),
            ('stock', 'Stock'),
            ('view', 'View'),
            ], 'Kind', required=True)
    deferral = fields.Boolean('Deferral', states={
            'invisible': Eval('kind') == 'view',
            }, depends=['kind'])
    party_required = fields.Boolean('Party Required',
        states={
            'invisible': Eval('kind') == 'view',
            },
        depends=['kind'])
    general_ledger_balance = fields.Boolean('General Ledger Balance',
        states={
            'invisible': Eval('kind') == 'view',
            },
        depends=['kind'],
        help="Display only the balance in the general ledger report")

    @classmethod
    def __setup__(cls):
        super(AccountTemplate, cls).__setup__()
        cls._order.insert(0, ('code', 'ASC'))
        cls._order.insert(1, ('name', 'ASC'))

    @classmethod
    def validate(cls, templates):
        super(AccountTemplate, cls).validate(templates)
        cls.check_recursion(templates)

    @staticmethod
    def default_kind():
        return 'view'

    @staticmethod
    def default_reconcile():
        return False

    @staticmethod
    def default_deferral():
        return True

    @staticmethod
    def default_party_required():
        return False

    @staticmethod
    def default_general_ledger_balance():
        return False

    def get_rec_name(self, name):
        if self.code:
            return self.code + ' - ' + self.name
        else:
            return self.name

    @classmethod
    def search_rec_name(cls, name, clause):
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        return [bool_op,
            ('code',) + tuple(clause[1:]),
            (cls._rec_name,) + tuple(clause[1:]),
            ]

    def _get_account_value(self, account=None):
        '''
        Set the values for account creation.
        '''
        res = {}
        if not account or account.name != self.name:
            res['name'] = self.name
        if not account or account.code != self.code:
            res['code'] = self.code
        if not account or account.kind != self.kind:
            res['kind'] = self.kind
        if not account or account.reconcile != self.reconcile:
            res['reconcile'] = self.reconcile
        if not account or account.deferral != self.deferral:
            res['deferral'] = self.deferral
        if not account or account.party_required != self.party_required:
            res['party_required'] = self.party_required
        if (not account
                or account.general_ledger_balance !=
                self.general_ledger_balance):
            res['general_ledger_balance'] = self.general_ledger_balance
        if not account or account.template != self:
            res['template'] = self.id
        return res

    def create_account(self, company_id, template2account=None,
            template2type=None):
        '''
        Create recursively accounts based on template.
        template2account is a dictionary with template id as key and account id
        as value, used to convert template id into account. The dictionary is
        filled with new accounts
        template2type is a dictionary with type template id as key and type id
        as value, used to convert type template id into type.
        '''
        pool = Pool()
        Account = pool.get('account.account')
        assert self.parent is None

        if template2account is None:
            template2account = {}

        if template2type is None:
            template2type = {}

        def create(templates):
            values = []
            created = []
            for template in templates:
                if template.id not in template2account:
                    vals = template._get_account_value()
                    vals['company'] = company_id
                    if template.parent:
                        vals['parent'] = template2account[template.parent.id]
                    else:
                        vals['parent'] = None
                    if template.type:
                        vals['type'] = template2type.get(template.type.id)
                    else:
                        vals['type'] = None
                    values.append(vals)
                    created.append(template)

            accounts = Account.create(values)
            for template, account in zip(created, accounts):
                template2account[template.id] = account.id

        childs = [self]
        while childs:
            create(childs)
            childs = sum((c.childs for c in childs), ())

    def update_account_taxes(self, template2account, template2tax,
            template_done=None):
        '''
        Update recursively account taxes based on template.
        template2account is a dictionary with template id as key and account id
        as value, used to convert template id into account.
        template2tax is a dictionary with tax template id as key and tax id as
        value, used to convert tax template id into tax.
        template_done is a list of template id already updated. The list is
        filled.
        '''
        Account = Pool().get('account.account')

        if template2account is None:
            template2account = {}
        if template2tax is None:
            template2tax = {}
        if template_done is None:
            template_done = []

        def update(templates):
            to_write = []
            for template in templates:
                if template.id not in template_done:
                    if template.taxes:
                        tax_ids = [template2tax[x.id] for x in template.taxes]
                        to_write.append([Account(template2account[template.id])])
                        to_write.append({
                                'taxes': [
                                    ('add', tax_ids)],
                                })
                    template_done.append(template.id)
            if to_write:
                Account.write(*to_write)

        childs = [self]
        while childs:
            update(childs)
            childs = sum((c.childs for c in childs), ())


class Account(ModelSQL, ModelView):
    'Account'
    __name__ = 'account.account'
    name = fields.Char('Name', size=None, required=True, select=True)
    code = fields.Char('Code', size=None, select=True)
    active = fields.Boolean('Active', select=True)
    company = fields.Many2One('company.company', 'Company', required=True,
            ondelete="RESTRICT")
    currency = fields.Function(fields.Many2One('currency.currency',
        'Currency'), 'get_currency')
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
            'get_currency_digits')
    second_currency = fields.Many2One('currency.currency',
        'Secondary Currency', help='Force all moves for this account \n'
        'to have this secondary currency.', ondelete="RESTRICT")
    type = fields.Many2One('account.account.type', 'Type', ondelete="RESTRICT",
        states={
            'invisible': Eval('kind') == 'view',
            'required': Eval('kind') != 'view',
            },
        domain=[
            ('company', '=', Eval('company')),
            ], depends=['kind', 'company'])
    parent = fields.Many2One('account.account', 'Parent', select=True,
        left="left", right="right", ondelete="RESTRICT",
        domain=[('company', '=', Eval('company'))],
        depends=['company'])
    left = fields.Integer('Left', required=True, select=True)
    right = fields.Integer('Right', required=True, select=True)
    childs = fields.One2Many('account.account', 'parent', 'Children')
    balance = fields.Function(fields.Numeric('Balance',
        digits=(16, Eval('currency_digits', 2)), depends=['currency_digits']),
        'get_balance')
    credit = fields.Function(fields.Numeric('Credit',
        digits=(16, Eval('currency_digits', 2)), depends=['currency_digits']),
        'get_credit_debit')
    debit = fields.Function(fields.Numeric('Debit',
        digits=(16, Eval('currency_digits', 2)), depends=['currency_digits']),
        'get_credit_debit')
    reconcile = fields.Boolean('Reconcile',
        help='Allow move lines of this account \nto be reconciled.',
        states={
            'invisible': Eval('kind') == 'view',
            }, depends=['kind'])
    note = fields.Text('Note')
    kind = fields.Selection([
            ('other', 'Other'),
            ('payable', 'Payable'),
            ('revenue', 'Revenue'),
            ('receivable', 'Receivable'),
            ('expense', 'Expense'),
            ('stock', 'Stock'),
            ('view', 'View'),
            ], 'Kind', required=True)
    deferral = fields.Boolean('Deferral', states={
            'invisible': Eval('kind') == 'view',
            }, depends=['kind'])
    deferrals = fields.One2Many('account.account.deferral', 'account',
        'Deferrals', readonly=True, states={
            'invisible': Eval('kind') == 'view',
            }, depends=['kind'])
    party_required = fields.Boolean('Party Required',
        states={
            'invisible': Eval('kind') == 'view',
            },
        depends=['kind'])
    general_ledger_balance = fields.Boolean('General Ledger Balance',
        states={
            'invisible': Eval('kind') == 'view',
            },
        depends=['kind'],
        help="Display only the balance in the general ledger report")
    template = fields.Many2One('account.account.template', 'Template')

    @classmethod
    def __setup__(cls):
        super(Account, cls).__setup__()
        cls._error_messages.update({
                'delete_account_containing_move_lines': ('You can not delete '
                    'account "%s" because it has move lines.'),
                })
        cls._sql_error_messages.update({
                'parent_fkey': ('You can not delete accounts that have '
                    'children.'),
                })
        cls._order.insert(0, ('code', 'ASC'))
        cls._order.insert(1, ('name', 'ASC'))

    @classmethod
    def validate(cls, accounts):
        super(Account, cls).validate(accounts)
        cls.check_recursion(accounts)

    @staticmethod
    def default_left():
        return 0

    @staticmethod
    def default_right():
        return 0

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_company():
        return Transaction().context.get('company') or None

    @staticmethod
    def default_reconcile():
        return False

    @staticmethod
    def default_deferral():
        return True

    @staticmethod
    def default_party_required():
        return False

    @staticmethod
    def default_general_ledger_balance():
        return False

    @staticmethod
    def default_kind():
        return 'view'

    def get_currency(self, name):
        return self.company.currency.id

    def get_currency_digits(self, name):
        return self.company.currency.digits

    @classmethod
    def get_balance(cls, accounts, name):
        pool = Pool()
        MoveLine = pool.get('account.move.line')
        FiscalYear = pool.get('account.fiscalyear')
        cursor = Transaction().connection.cursor()

        table_a = cls.__table__()
        table_c = cls.__table__()
        line = MoveLine.__table__()
        ids = [a.id for a in accounts]
        balances = dict((i, 0) for i in ids)
        line_query, fiscalyear_ids = MoveLine.query_get(line)
        for sub_ids in grouped_slice(ids):
            red_sql = reduce_ids(table_a.id, sub_ids)
            cursor.execute(*table_a.join(table_c,
                    condition=(table_c.left >= table_a.left)
                    & (table_c.right <= table_a.right)
                    ).join(line, condition=line.account == table_c.id
                    ).select(
                    table_a.id,
                    Sum(Coalesce(line.debit, 0) - Coalesce(line.credit, 0)),
                    where=red_sql & line_query & (table_c.active == True),
                    group_by=table_a.id))
            result = cursor.fetchall()
            balances.update(dict(result))

        # SQLite uses float for SUM
        for account_id, balance in balances.iteritems():
            if isinstance(balance, Decimal):
                break
            balances[account_id] = Decimal(str(balance))

        for account in accounts:
            balances[account.id] = account.company.currency.round(
                balances[account.id])

        fiscalyears = FiscalYear.browse(fiscalyear_ids)
        func = lambda accounts, names: \
            {names[0]: cls.get_balance(accounts, names[0])}
        return cls._cumulate(fiscalyears, accounts, {name: balances},
            func)[name]

    @classmethod
    def get_credit_debit(cls, accounts, names):
        '''
        Function to compute debit, credit for accounts.
        If cumulate is set in the context, it is the cumulate amount over all
        previous fiscal year.
        '''
        pool = Pool()
        MoveLine = pool.get('account.move.line')
        FiscalYear = pool.get('account.fiscalyear')
        cursor = Transaction().connection.cursor()

        result = {}
        ids = [a.id for a in accounts]
        for name in names:
            if name not in ('credit', 'debit'):
                raise Exception('Bad argument')
            result[name] = dict((i, 0) for i in ids)

        table = cls.__table__()
        line = MoveLine.__table__()
        line_query, fiscalyear_ids = MoveLine.query_get(line)
        columns = [table.id]
        for name in names:
            columns.append(Sum(Coalesce(Column(line, name), 0)))
        for sub_ids in grouped_slice(ids):
            red_sql = reduce_ids(table.id, sub_ids)
            cursor.execute(*table.join(line, 'LEFT',
                    condition=line.account == table.id
                    ).select(*columns,
                    where=red_sql & line_query,
                    group_by=table.id))
            for row in cursor.fetchall():
                account_id = row[0]
                for i, name in enumerate(names, 1):
                    # SQLite uses float for SUM
                    if not isinstance(row[i], Decimal):
                        result[name][account_id] = Decimal(str(row[i]))
                    else:
                        result[name][account_id] = row[i]
        for account in accounts:
            for name in names:
                result[name][account.id] = account.company.currency.round(
                    result[name][account.id])

        if not Transaction().context.get('cumulate'):
            return result
        else:
            fiscalyears = FiscalYear.browse(fiscalyear_ids)
            return cls._cumulate(fiscalyears, accounts, result,
                cls.get_credit_debit)

    @classmethod
    def _cumulate(cls, fiscalyears, accounts, values, func):
        """
        Cumulate previous fiscalyear values into values
        func is the method to compute values
        """
        pool = Pool()
        FiscalYear = pool.get('account.fiscalyear')
        Deferral = pool.get('account.account.deferral')
        names = values.keys()

        youngest_fiscalyear = None
        for fiscalyear in fiscalyears:
            if (not youngest_fiscalyear
                    or (youngest_fiscalyear.start_date
                        > fiscalyear.start_date)):
                youngest_fiscalyear = fiscalyear

        fiscalyear = None
        if youngest_fiscalyear:
            fiscalyears = FiscalYear.search([
                    ('end_date', '<', youngest_fiscalyear.start_date),
                    ('company', '=', youngest_fiscalyear.company),
                    ], order=[('end_date', 'DESC')], limit=1)
            if fiscalyears:
                fiscalyear, = fiscalyears

        if not fiscalyear:
            return values

        if fiscalyear.state == 'close':
            id2deferral = {}
            ids = [a.id for a in accounts]
            for sub_ids in grouped_slice(ids):
                deferrals = Deferral.search([
                    ('fiscalyear', '=', fiscalyear.id),
                    ('account', 'in', list(sub_ids)),
                    ])
                for deferral in deferrals:
                    id2deferral[deferral.account.id] = deferral

            for account in accounts:
                if account.id in id2deferral:
                    deferral = id2deferral[account.id]
                    for name in names:
                        values[name][account.id] += getattr(deferral, name)
        else:
            with Transaction().set_context(fiscalyear=fiscalyear.id,
                    date=None, periods=None):
                previous_result = func(accounts, names)
            for name in names:
                vals = values[name]
                for account in accounts:
                    vals[account.id] += previous_result[name][account.id]

        return values

    def get_rec_name(self, name):
        if self.code:
            return self.code + ' - ' + self.name
        else:
            return self.name

    @classmethod
    def search_rec_name(cls, name, clause):
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        return [bool_op,
            ('code',) + tuple(clause[1:]),
            (cls._rec_name,) + tuple(clause[1:]),
            ]

    @classmethod
    def copy(cls, accounts, default=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('template')
        default.setdefault('deferrals', [])
        new_accounts = super(Account, cls).copy(accounts, default=default)
        cls._rebuild_tree('parent', None, 0)
        return new_accounts

    @classmethod
    def write(cls, *args):
        pool = Pool()
        MoveLine = pool.get('account.move.line')
        actions = iter(args)
        args = []
        for accounts, values in zip(actions, actions):
            if not values.get('active', True):
                childs = cls.search([
                        ('parent', 'child_of', [a.id for a in accounts]),
                        ])
                if MoveLine.search([
                            ('account', 'in', [a.id for a in childs]),
                            ]):
                    values = values.copy()
                    del values['active']
            args.extend((accounts, values))
        super(Account, cls).write(*args)

    @classmethod
    def delete(cls, accounts):
        MoveLine = Pool().get('account.move.line')
        childs = cls.search([
                ('parent', 'child_of', [a.id for a in accounts]),
                ])
        lines = MoveLine.search([
                ('account', 'in', [a.id for a in childs]),
                ])
        if lines:
            cls.raise_user_error('delete_account_containing_move_lines', (
                    lines[0].account.rec_name,))
        super(Account, cls).delete(accounts)

    def update_account(self, template2account=None, template2type=None):
        '''
        Update recursively accounts based on template.
        template2account is a dictionary with template id as key and account id
        as value, used to convert template id into account. The dictionary is
        filled with new accounts.
        template2type is a dictionary with type template id as key and type id
        as value, used to convert type template id into type.
        '''
        if template2account is None:
            template2account = {}

        if template2type is None:
            template2type = {}

        values = []
        childs = [self]
        while childs:
            for child in childs:
                if child.template:
                    vals = child.template._get_account_value(account=child)
                    current_type = child.type.id if child.type else None
                    if child.template.type:
                        template_type = template2type.get(
                            child.template.type.id)
                    else:
                        template_type = None
                    if current_type != template_type:
                        vals['type'] = template_type
                    if vals:
                        values.append([child])
                        values.append(vals)
                    template2account[child.template.id] = child.id
            childs = sum((c.childs for c in childs), ())
        if values:
            self.write(*values)

    def update_account_taxes(self, template2account, template2tax):
        '''
        Update recursively account taxes base on template.
        template2account is a dictionary with template id as key and account id
        as value, used to convert template id into account.
        template2tax is a dictionary with tax template id as key and tax id as
        value, used to convert tax template id into tax.
        '''
        if template2account is None:
            template2account = {}

        if template2tax is None:
            template2tax = {}

        values = []
        childs = [self]
        while childs:
            for child in childs:
                if not child.template:
                    continue
                if not child.template.taxes:
                    continue
                tax_ids = [template2tax[x.id] for x in child.template.taxes
                    if x.id in template2tax]
                old_tax_ids = [x.id for x in child.taxes]
                for tax_id in tax_ids:
                    if tax_id not in old_tax_ids:
                        values.append([child])
                        values.append({
                                'taxes': [
                                    ('add', template2tax[x.id])
                                    for x in self.template.taxes
                                    if x.id in template2tax],
                                })
                        break
            childs = sum((c.childs for c in childs), ())
        if values:
            self.write(*values)


class AccountDeferral(ModelSQL, ModelView):
    '''
    Account Deferral

    It is used to deferral the debit/credit of account by fiscal year.
    '''
    __name__ = 'account.account.deferral'
    account = fields.Many2One('account.account', 'Account', required=True,
            select=True)
    fiscalyear = fields.Many2One('account.fiscalyear', 'Fiscal Year',
            required=True, select=True)
    debit = fields.Numeric('Debit', digits=(16, Eval('currency_digits', 2)),
        required=True, depends=['currency_digits'])
    credit = fields.Numeric('Credit', digits=(16, Eval('currency_digits', 2)),
        required=True, depends=['currency_digits'])
    balance = fields.Function(fields.Numeric('Balance',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']), 'get_balance')
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
            'get_currency_digits')

    @classmethod
    def __setup__(cls):
        super(AccountDeferral, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('deferral_uniq', Unique(t, t.account, t.fiscalyear),
                'Deferral must be unique by account and fiscal year'),
        ]
        cls._error_messages.update({
            'write_deferral': 'You can not modify Account Deferral records',
            })

    def get_balance(self, name):
        return self.debit - self.credit

    def get_currency_digits(self, name):
        return self.account.currency_digits

    def get_rec_name(self, name):
        return '%s - %s' % (self.account.rec_name, self.fiscalyear.rec_name)

    @classmethod
    def search_rec_name(cls, name, clause):
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        return [bool_op,
            ('account.rec_name',) + tuple(clause[1:]),
            ('fiscalyear.rec_name',) + tuple(clause[1:]),
            ]

    @classmethod
    def write(cls, deferrals, values, *args):
        cls.raise_user_error('write_deferral')


class OpenChartAccountStart(ModelView):
    'Open Chart of Accounts'
    __name__ = 'account.open_chart.start'
    fiscalyear = fields.Many2One('account.fiscalyear', 'Fiscal Year',
            help='Leave empty for all open fiscal year')
    posted = fields.Boolean('Posted Moves', help='Show posted moves only')

    @staticmethod
    def default_posted():
        return False


class OpenChartAccount(Wizard):
    'Open Chart of Accounts'
    __name__ = 'account.open_chart'
    start = StateView('account.open_chart.start',
        'account.open_chart_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('account.act_account_tree2')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({
            'fiscalyear': (self.start.fiscalyear.id
                    if self.start.fiscalyear else None),
            'posted': self.start.posted,
            })
        if self.start.fiscalyear:
            action['name'] += ' - %s' % self.start.fiscalyear.rec_name
        if self.start.posted:
            action['name'] += '*'
        return action, {}

    def transition_open_(self):
        return 'end'


class GeneralLedgerAccount(ModelSQL, ModelView):
    'General Ledger Account'
    __name__ = 'account.general_ledger.account'

    # TODO reuse rec_name of Account
    name = fields.Char('Name')
    code = fields.Char('Code')
    active = fields.Boolean('Active')
    company = fields.Many2One('company.company', 'Company')
    start_debit = fields.Function(fields.Numeric('Start Debit',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']), 'get_account')
    debit = fields.Function(fields.Numeric('Debit',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']), 'get_debit_credit')
    end_debit = fields.Function(fields.Numeric('End Debit',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']), 'get_account')
    start_credit = fields.Function(fields.Numeric('Start Credit',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']), 'get_account')
    credit = fields.Function(fields.Numeric('Credit',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']), 'get_debit_credit')
    end_credit = fields.Function(fields.Numeric('End Credit',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']), 'get_account')
    start_balance = fields.Function(fields.Numeric('Start Balance',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']), 'get_account')
    end_balance = fields.Function(fields.Numeric('End Balance',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']), 'get_account')
    lines = fields.One2Many('account.general_ledger.line', 'account', 'Lines',
        readonly=True)
    general_ledger_balance = fields.Boolean('General Ledger Balance')
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
        'get_currency_digits')

    @classmethod
    def __setup__(cls):
        super(GeneralLedgerAccount, cls).__setup__()
        cls._order.insert(0, ('code', 'ASC'))
        cls._order.insert(1, ('name', 'ASC'))

    @classmethod
    def table_query(cls):
        pool = Pool()
        context = Transaction().context
        Account = pool.get('account.account')
        account = Account.__table__()
        columns = []
        for fname, field in cls._fields.iteritems():
            if not hasattr(field, 'set'):
                columns.append(Column(account, fname).as_(fname))
        return account.select(*columns,
            where=(account.company == context.get('company'))
            & (account.kind != 'view'))

    @classmethod
    def get_period_ids(cls, name):
        pool = Pool()
        Period = pool.get('account.period')
        context = Transaction().context

        period = None
        if name.startswith('start_'):
            period_ids = [0]
            if context.get('start_period'):
                period = Period(context['start_period'])
        elif name.startswith('end_'):
            period_ids = []
            if context.get('end_period'):
                period = Period(context['end_period'])

        if period:
            periods = Period.search([
                    ('fiscalyear', '=', context.get('fiscalyear')),
                    ('end_date', '<=', period.start_date),
                    ])
            if period.start_date == period.end_date:
                periods.append(period)
            if periods:
                period_ids = [p.id for p in periods]
            if name.startswith('end_'):
                # Always include ending period
                period_ids.append(period.id)
        return period_ids

    @classmethod
    def get_account(cls, records, name):
        pool = Pool()
        Account = pool.get('account.account')

        period_ids = cls.get_period_ids(name)
        with Transaction().set_context(periods=period_ids):
            accounts = Account.browse(records)
        fname = name
        for test in ['start_', 'end_']:
            if name.startswith(test):
                fname = name[len(test):]
                break
        return {a.id: getattr(a, fname) for a in accounts}

    @classmethod
    def get_debit_credit(cls, records, name):
        pool = Pool()
        Account = pool.get('account.account')

        start_period_ids = cls.get_period_ids('start_%s' % name)
        end_period_ids = cls.get_period_ids('end_%s' % name)
        periods_ids = list(
            set(end_period_ids).difference(set(start_period_ids)))
        with Transaction().set_context(periods=periods_ids):
            accounts = Account.browse(records)
        return {a.id: getattr(a, name) for a in accounts}

    def get_currency_digits(self, name):
        return self.company.currency.digits

    def get_rec_name(self, name):
        # TODO add start/end balance
        return self.name


class GeneralLedgerAccountContext(ModelView):
    'General Ledger Account Context'
    __name__ = 'account.general_ledger.account.context'
    fiscalyear = fields.Many2One('account.fiscalyear', 'Fiscal Year',
        required=True)
    start_period = fields.Many2One('account.period', 'Start Period',
        domain=[
            ('fiscalyear', '=', Eval('fiscalyear')),
            ('start_date', '<=', (Eval('end_period'), 'start_date')),
            ], depends=['fiscalyear', 'end_period'])
    end_period = fields.Many2One('account.period', 'End Period',
        domain=[
            ('fiscalyear', '=', Eval('fiscalyear')),
            ('start_date', '>=', (Eval('start_period'), 'start_date'))
            ],
        depends=['fiscalyear', 'start_period'])
    company = fields.Many2One('company.company', 'Company', required=True)
    posted = fields.Boolean('Posted Move', help='Show only posted move')

    @classmethod
    def default_fiscalyear(cls):
        pool = Pool()
        FiscalYear = pool.get('account.fiscalyear')
        context = Transaction().context
        return context.get(
            'fiscalyear',
            FiscalYear.find(context.get('company'), exception=False))

    @classmethod
    def default_start_period(cls):
        return Transaction().context.get('start_period')

    @classmethod
    def default_end_period(cls):
        return Transaction().context.get('end_period')

    @classmethod
    def default_company(cls):
        return Transaction().context.get('company')

    @classmethod
    def default_posted(cls):
        return Transaction().context.get('posted', False)

    @fields.depends('fiscalyear', 'start_period', 'end_period')
    def on_change_fiscalyear(self):
        if (self.start_period
                and self.start_period.fiscalyear != self.fiscalyear):
            self.start_period = None
        if (self.end_period
                and self.end_period.fiscalyear != self.fiscalyear):
            self.end_period = None


class GeneralLedgerLine(ModelSQL, ModelView):
    'General Ledger Line'
    __name__ = 'account.general_ledger.line'

    move = fields.Many2One('account.move', 'Move')
    date = fields.Date('Date')
    account = fields.Many2One('account.general_ledger.account', 'Account')
    party = fields.Many2One('party.party', 'Party',
        states={
            'invisible': ~Eval('party_required', False),
            },
        depends=['party_required'])
    party_required = fields.Boolean('Party Required')
    company = fields.Many2One('company.company', 'Company')
    debit = fields.Numeric('Debit',
        digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits'])
    credit = fields.Numeric('Credit',
        digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits'])
    balance = fields.Numeric('Balance',
        digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits'])
    origin = fields.Reference('Origin', selection='get_origin')
    description = fields.Char('Description')
    move_description = fields.Char('Move Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ], 'State')
    state_string = state.translated('state')
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
        'get_currency_digits')

    @classmethod
    def __setup__(cls):
        super(GeneralLedgerLine, cls).__setup__()
        cls._order.insert(0, ('date', 'ASC'))

    @classmethod
    def table_query(cls):
        pool = Pool()
        Line = pool.get('account.move.line')
        Move = pool.get('account.move')
        LedgerAccount = pool.get('account.general_ledger.account')
        Account = pool.get('account.account')
        context = Transaction().context
        line = Line.__table__()
        move = Move.__table__()
        account = Account.__table__()
        columns = []
        for fname, field in cls._fields.iteritems():
            if hasattr(field, 'set'):
                continue
            field_line = getattr(Line, fname, None)
            if fname == 'balance':
                # TODO replace the test by a generic one on backend
                if backend.name() == 'postgresql':
                    w_columns = [line.account]
                    if context.get('party_cumulate', False):
                        w_columns.append(line.party)
                    column = Sum(line.debit - line.credit,
                        window=Window(w_columns,
                            order_by=[move.date.asc, line.id])).as_('balance')
                else:
                    column = (line.debit - line.credit).as_('balance')
            elif fname == 'move_description':
                column = Column(move, 'description').as_(fname)
            elif fname == 'party_required':
                column = Column(account, 'party_required').as_(fname)
            elif (not field_line
                    or fname == 'state'
                    or isinstance(field_line, fields.Function)):
                column = Column(move, fname).as_(fname)
            else:
                column = Column(line, fname).as_(fname)
            columns.append(column)
        start_period_ids = set(LedgerAccount.get_period_ids('start_balance'))
        end_period_ids = set(LedgerAccount.get_period_ids('end_balance'))
        period_ids = list(end_period_ids.difference(start_period_ids))
        with Transaction().set_context(periods=period_ids):
            line_query, fiscalyear_ids = Line.query_get(line)
        return line.join(move, condition=line.move == move.id
            ).join(account, condition=line.account == account.id
                ).select(*columns, where=line_query)

    def get_party_required(self, name):
        return self.account.party_required

    def get_currency_digits(self, name):
        return self.company.currency.digits

    @classmethod
    def get_origin(cls):
        Line = Pool().get('account.move.line')
        return Line.get_origin()


class GeneralLedgerLineContext(GeneralLedgerAccountContext):
    'General Ledger Line Context'
    __name__ = 'account.general_ledger.line.context'

    party_cumulate = fields.Boolean('Cumulate per Party')

    @classmethod
    def default_party_cumulate(cls):
        return False


class GeneralLedger(Report):
    __name__ = 'account.general_ledger'

    @classmethod
    def get_context(cls, records, data):
        pool = Pool()
        Company = pool.get('company.company')
        Fiscalyear = pool.get('account.fiscalyear')
        Period = pool.get('account.period')
        context = Transaction().context

        report_context = super(GeneralLedger, cls).get_context(records, data)

        report_context['company'] = Company(context['company'])
        report_context['fiscalyear'] = Fiscalyear(context['fiscalyear'])

        for period in ['start_period', 'end_period']:
            if context.get(period):
                report_context[period] = Period(context[period])
            else:
                report_context[period] = None

        report_context['accounts'] = records
        return report_context


class TrialBalance(Report):
    __name__ = 'account.trial_balance'

    @classmethod
    def get_context(cls, records, data):
        pool = Pool()
        Company = pool.get('company.company')
        Fiscalyear = pool.get('account.fiscalyear')
        Period = pool.get('account.period')
        context = Transaction().context

        report_context = super(TrialBalance, cls).get_context(records, data)

        report_context['company'] = Company(context['company'])
        report_context['fiscalyear'] = Fiscalyear(context['fiscalyear'])

        for period in ['start_period', 'end_period']:
            if context.get(period):
                report_context[period] = Period(context[period])
            else:
                report_context[period] = None

        report_context['accounts'] = records
        report_context['sum'] = cls.sum
        return report_context

    @classmethod
    def sum(cls, accounts, field):
        return sum((getattr(a, field) for a in accounts), Decimal('0'))


class BalanceSheetContext(ModelView):
    'Balance Sheet Context'
    __name__ = 'account.balance_sheet.context'
    date = fields.Date('Date', required=True)
    company = fields.Many2One('company.company', 'Company', required=True)
    posted = fields.Boolean('Posted Move', help='Show only posted move')

    @staticmethod
    def default_date():
        Date_ = Pool().get('ir.date')
        return Date_.today()

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_posted():
        return False


class IncomeStatementContext(ModelView):
    'Income Statement Context'
    __name__ = 'account.income_statement.context'
    fiscalyear = fields.Many2One('account.fiscalyear', 'Fiscal Year',
        required=True)
    start_period = fields.Many2One('account.period', 'Start Period',
        domain=[
            ('fiscalyear', '=', Eval('fiscalyear')),
            ('start_date', '<=', (Eval('end_period'), 'start_date'))
            ],
        depends=['end_period', 'fiscalyear'])
    end_period = fields.Many2One('account.period', 'End Period',
        domain=[
            ('fiscalyear', '=', Eval('fiscalyear')),
            ('start_date', '>=', (Eval('start_period'), 'start_date')),
            ],
        depends=['start_period', 'fiscalyear'])
    company = fields.Many2One('company.company', 'Company', required=True)
    posted = fields.Boolean('Posted Move', help='Show only posted move')

    @staticmethod
    def default_fiscalyear():
        FiscalYear = Pool().get('account.fiscalyear')
        return FiscalYear.find(
            Transaction().context.get('company'), exception=False)

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_posted():
        return False

    @fields.depends('fiscalyear')
    def on_change_fiscalyear(self):
        self.start_period = None
        self.end_period = None


class AgedBalanceContext(ModelView):
    'Aged Balance Context'
    __name__ = 'account.aged_balance.context'
    type = fields.Selection([
            ('customer', 'Customers'),
            ('supplier', 'Suppliers'),
            ('customer_supplier', 'Customers and Suppliers'),
            ],
        "Type", required=True)
    date = fields.Date('Date', required=True)
    term1 = fields.Integer("First Term", required=True)
    term2 = fields.Integer("Second Term", required=True,
        domain=[
            ('term2', '>', Eval('term1', 0)),
            ],
        depends=['term1'])
    term3 = fields.Integer("Third Term", required=True,
        domain=[
            ('term3', '>', Eval('term2', 0)),
            ],
        depends=['term2'])
    unit = fields.Selection([
            ('day', 'Days'),
            ('month', 'Months'),
            ], "Unit", required=True)
    company = fields.Many2One('company.company', 'Company', required=True)
    posted = fields.Boolean('Posted Move', help='Show only posted move')

    @classmethod
    def default_type(cls):
        return 'customer'

    @classmethod
    def default_posted(cls):
        return False

    @classmethod
    def default_date(cls):
        return Pool().get('ir.date').today()

    @staticmethod
    def default_term1():
        return 30

    @staticmethod
    def default_term2():
        return 60

    @staticmethod
    def default_term3():
        return 90

    @staticmethod
    def default_unit():
        return 'day'

    @staticmethod
    def default_company():
        return Transaction().context.get('company')


class AgedBalance(ModelSQL, ModelView):
    'Aged Balance'
    __name__ = 'account.aged_balance'

    party = fields.Many2One('party.party', 'Party')
    company = fields.Many2One('company.company', 'Company')
    term0 = fields.Numeric('Now',
        digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits'])
    term1 = fields.Numeric('First Term',
        digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits'])
    term2 = fields.Numeric('Second Term',
        digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits'])
    term3 = fields.Numeric('Third Term',
        digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits'])
    balance = fields.Numeric('Balance',
        digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits'])
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
        'get_currency_digits')

    @classmethod
    def __setup__(cls):
        super(AgedBalance, cls).__setup__()
        cls._order.insert(0, ('party', 'ASC'))

    @classmethod
    def table_query(cls):
        pool = Pool()
        context = Transaction().context
        MoveLine = pool.get('account.move.line')
        Move = pool.get('account.move')
        Reconciliation = pool.get('account.move.reconciliation')
        Account = pool.get('account.account')

        line = MoveLine.__table__()
        move = Move.__table__()
        reconciliation = Reconciliation.__table__()
        account = Account.__table__()

        company_id = context.get('company')
        date = context.get('date')
        with Transaction().set_context(date=None):
            line_query, _ = MoveLine.query_get(line)
        kind = cls.get_kind()
        columns = [
            line.party.as_('id'),
            Literal(0).as_('create_uid'),
            Max(line.create_date).as_('create_date'),
            Literal(0).as_('write_uid'),
            Max(line.write_date).as_('write_date'),
            line.party.as_('party'),
            move.company.as_('company'),
            (Sum(line.debit) - Sum(line.credit)).as_('balance'),
            ]

        terms = cls.get_terms()
        factor = cls.get_unit_factor()
        term_values = sorted(terms.values(), key=lambda x: x or 0)

        for name, value in terms.iteritems():
            if value is None or factor is None or date is None:
                columns.append(Literal(None).as_(name))
                continue
            cond = line.maturity_date <= (date - value * factor)
            idx = term_values.index(value)
            if idx + 1 < len(terms):
                cond &= line.maturity_date > (
                    date - term_values[idx + 1] * factor)
            else:
                cond |= line.maturity_date == Null
            columns.append(
                Sum(Case((cond, line.debit - line.credit), else_=0)).as_(name))

        return line.join(move, condition=line.move == move.id
            ).join(account, condition=line.account == account.id
            ).join(reconciliation, 'LEFT',
                condition=reconciliation.id == line.reconciliation
            ).select(*columns,
                where=(line.party != Null)
                & (account.active == True)
                & account.kind.in_(kind)
                & ((line.reconciliation == Null)
                    | (reconciliation.date > date))
                & (move.date <= date)
                & (account.company == company_id)
                & line_query,
                group_by=(line.party, move.company))

    @classmethod
    def get_terms(cls):
        context = Transaction().context
        return {
            'term0': 0,
            'term1': context.get('term1'),
            'term2': context.get('term2'),
            'term3': context.get('term3'),
            }

    @classmethod
    def get_unit_factor(cls):
        context = Transaction().context
        unit = context.get('unit', 'day')
        if unit == 'month':
            return datetime.timedelta(days=30)
        elif unit == 'day':
            return datetime.timedelta(days=1)

    @classmethod
    def get_kind(cls):
        context = Transaction().context
        type_ = context.get('type', 'customer')
        if type_ == 'customer_supplier':
            return ['payable', 'receivable']
        elif type_ == 'supplier':
            return ['payable']
        elif type_ == 'customer':
            return ['receivable']
        else:
            return []

    def get_currency_digits(self, name):
        return self.company.currency.digits


class AgedBalanceReport(Report):
    __name__ = 'account.aged_balance'

    @classmethod
    def get_context(cls, records, data):
        pool = Pool()
        Company = pool.get('company.company')
        Context = pool.get('account.aged_balance.context')
        AgedBalance = pool.get('account.aged_balance')
        context = Transaction().context

        report_context = super(AgedBalanceReport, cls).get_context(
            records, data)

        context_fields = Context.fields_get(['type', 'unit'])

        report_context['company'] = Company(context['company'])
        report_context['date'] = context['date']
        report_context['type'] = dict(
            context_fields['type']['selection'])[context['type']]
        report_context['unit'] = dict(
            context_fields['unit']['selection'])[context['unit']]
        report_context.update(AgedBalance.get_terms())
        report_context['sum'] = cls.sum
        return report_context

    @classmethod
    def sum(cls, records, field):
        return sum((getattr(r, field) for r in records), Decimal('0'))


class CreateChartStart(ModelView):
    'Create Chart'
    __name__ = 'account.create_chart.start'


class CreateChartAccount(ModelView):
    'Create Chart'
    __name__ = 'account.create_chart.account'
    company = fields.Many2One('company.company', 'Company', required=True)
    account_template = fields.Many2One('account.account.template',
            'Account Template', required=True, domain=[('parent', '=', None)])

    @staticmethod
    def default_company():
        return Transaction().context.get('company')


class CreateChartProperties(ModelView):
    'Create Chart'
    __name__ = 'account.create_chart.properties'
    company = fields.Many2One('company.company', 'Company')
    account_receivable = fields.Many2One('account.account',
            'Default Receivable Account',
            domain=[
                ('kind', '=', 'receivable'),
                ('company', '=', Eval('company')),
            ],
            depends=['company'])
    account_payable = fields.Many2One('account.account',
            'Default Payable Account',
            domain=[
                ('kind', '=', 'payable'),
                ('company', '=', Eval('company')),
            ],
            depends=['company'])


class CreateChart(Wizard):
    'Create Chart'
    __name__ = 'account.create_chart'
    start = StateView('account.create_chart.start',
        'account.create_chart_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'account', 'tryton-ok', default=True),
            ])
    account = StateView('account.create_chart.account',
        'account.create_chart_account_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Create', 'create_account', 'tryton-ok', default=True),
            ])
    create_account = StateTransition()
    properties = StateView('account.create_chart.properties',
        'account.create_chart_properties_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Create', 'create_properties', 'tryton-ok', default=True),
            ])
    create_properties = StateTransition()

    def transition_create_account(self):
        pool = Pool()
        TaxCodeTemplate = pool.get('account.tax.code.template')
        TaxTemplate = pool.get('account.tax.template')
        TaxRuleTemplate = pool.get('account.tax.rule.template')
        TaxRuleLineTemplate = \
            pool.get('account.tax.rule.line.template')
        Config = pool.get('ir.configuration')

        with Transaction().set_context(language=Config.get_language(),
                company=self.account.company.id):
            account_template = self.account.account_template
            company = self.account.company

            # Create account types
            template2type = {}
            account_template.type.create_type(
                company.id,
                template2type=template2type)

            # Create accounts
            template2account = {}
            account_template.create_account(
                company.id,
                template2account=template2account,
                template2type=template2type)

            # Create tax codes
            template2tax_code = {}
            TaxCodeTemplate.create_tax_code(
                account_template.id, company.id,
                template2tax_code=template2tax_code)

            # Create taxes
            template2tax = {}
            TaxTemplate.create_tax(
                account_template.id, company.id,
                template2tax_code=template2tax_code,
                template2account=template2account,
                template2tax=template2tax)

            # Update taxes on accounts
            account_template.update_account_taxes(template2account,
                template2tax)

            # Create tax rules
            template2rule = {}
            TaxRuleTemplate.create_rule(
                account_template.id, company.id,
                template2rule=template2rule)

            # Create tax rule lines
            template2rule_line = {}
            TaxRuleLineTemplate.create_rule_line(
                account_template.id, template2tax, template2rule,
                template2rule_line=template2rule_line)
        return 'properties'

    def default_properties(self, fields):
        return {
            'company': self.account.company.id,
            }

    def transition_create_properties(self):
        pool = Pool()
        Property = pool.get('ir.property')
        ModelField = pool.get('ir.model.field')

        with Transaction().set_context(company=self.properties.company.id):
            account_receivable_field, = ModelField.search([
                    ('model.model', '=', 'party.party'),
                    ('name', '=', 'account_receivable'),
                    ], limit=1)
            properties = Property.search([
                    ('field', '=', account_receivable_field.id),
                    ('res', '=', None),
                    ('company', '=', self.properties.company.id),
                    ])
            Property.delete(properties)
            if self.properties.account_receivable:
                Property.create([{
                            'field': account_receivable_field.id,
                            'value': str(
                                self.properties.account_receivable),
                            'company': self.properties.company.id,
                            }])

            account_payable_field, = ModelField.search([
                    ('model.model', '=', 'party.party'),
                    ('name', '=', 'account_payable'),
                    ], limit=1)
            properties = Property.search([
                    ('field', '=', account_payable_field.id),
                    ('res', '=', None),
                    ('company', '=', self.properties.company.id),
                    ])
            Property.delete(properties)
            if self.properties.account_payable:
                Property.create([{
                            'field': account_payable_field.id,
                            'value': str(self.properties.account_payable),
                            'company': self.properties.company.id,
                            }])
        return 'end'


class UpdateChartStart(ModelView):
    'Update Chart'
    __name__ = 'account.update_chart.start'
    account = fields.Many2One('account.account', 'Root Account',
            required=True, domain=[('parent', '=', None)])


class UpdateChartSucceed(ModelView):
    'Update Chart'
    __name__ = 'account.update_chart.succeed'


class UpdateChart(Wizard):
    'Update Chart'
    __name__ = 'account.update_chart'
    start = StateView('account.update_chart.start',
        'account.update_chart_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Update', 'update', 'tryton-ok', default=True),
            ])
    update = StateTransition()
    succeed = StateView('account.update_chart.succeed',
        'account.update_chart_succeed_view_form', [
            Button('OK', 'end', 'tryton-ok', default=True),
            ])

    @inactive_records
    def transition_update(self):
        pool = Pool()
        TaxCode = pool.get('account.tax.code')
        TaxCodeTemplate = pool.get('account.tax.code.template')
        Tax = pool.get('account.tax')
        TaxTemplate = pool.get('account.tax.template')
        TaxRule = pool.get('account.tax.rule')
        TaxRuleTemplate = pool.get('account.tax.rule.template')
        TaxRuleLine = pool.get('account.tax.rule.line')
        TaxRuleLineTemplate = \
            pool.get('account.tax.rule.line.template')

        account = self.start.account
        company = account.company

        # Update account types
        template2type = {}
        account.type.update_type(template2type=template2type)
        # Create missing account types
        if account.type.template:
            account.type.template.create_type(
                company.id,
                template2type=template2type)

        # Update accounts
        template2account = {}
        account.update_account(template2account=template2account,
            template2type=template2type)
        # Create missing accounts
        if account.template:
            account.template.create_account(
                company.id,
                template2account=template2account,
                template2type=template2type)

        # Update tax codes
        template2tax_code = {}
        TaxCode.update_tax_code(
            company.id,
            template2tax_code=template2tax_code)
        # Create missing tax codes
        if account.template:
            TaxCodeTemplate.create_tax_code(
                account.template.id, company.id,
                template2tax_code=template2tax_code)

        # Update taxes
        template2tax = {}
        Tax.update_tax(
            company.id,
            template2tax_code=template2tax_code,
            template2account=template2account,
            template2tax=template2tax)
        # Create missing taxes
        if account.template:
            TaxTemplate.create_tax(
                account.template.id, account.company.id,
                template2tax_code=template2tax_code,
                template2account=template2account,
                template2tax=template2tax)

        # Update taxes on accounts
        account.update_account_taxes(template2account, template2tax)

        # Update tax rules
        template2rule = {}
        TaxRule.update_rule(company.id, template2rule=template2rule)
        # Create missing tax rules
        if account.template:
            TaxRuleTemplate.create_rule(
                account.template.id, account.company.id,
                template2rule=template2rule)

        # Update tax rule lines
        template2rule_line = {}
        TaxRuleLine.update_rule_line(
            company.id, template2tax, template2rule,
            template2rule_line=template2rule_line)
        # Create missing tax rule lines
        if account.template:
            TaxRuleLineTemplate.create_rule_line(
                account.template.id, template2tax, template2rule,
                template2rule_line=template2rule_line)
        return 'succeed'
