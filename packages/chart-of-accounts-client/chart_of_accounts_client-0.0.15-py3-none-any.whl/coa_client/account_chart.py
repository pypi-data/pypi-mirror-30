from enum import Enum


class Node(object):
    path_delimiter = '/'

    def __init__(self, name, description=''):
        self.name = name
        self.description = description

    def __len__(self):
        return 1


class NodeGroup(Node):
    def __init__(self, name, description=''):
        Node.__init__(self, name, description)
        self.children = ()

    def add_node(self, node):
        self.children += (node,)

    def __getitem__(self, path):
        split_path = path.lower().split(Node.path_delimiter)
        if split_path:
            for child in self.children:
                if split_path[1] == child.name.lower():
                    if len(split_path) > 2:
                        return child['/' + Node.path_delimiter.join(split_path[2::])]
                    else:
                        return child

    def __contains__(self, item):
        if self[item]:
            return True
        else:
            return False

    def __len__(self):
        return sum([len(child) for child in self.children])


class Side(Enum):
    DEBIT = 'debit'
    CREDIT = 'credit'

    def __invert__(self):
        if self is Side.DEBIT:
            return Side.CREDIT
        return Side.DEBIT


class AccountClass(Enum):
    ASSETS = 'assets'
    LIABILITIES = 'liabilities'
    REVENUE = 'revenue'
    EXPENSES = 'expenses'

    def balance_side(self):
        if self in [AccountClass.LIABILITIES, AccountClass.REVENUE]:
            return Side.CREDIT
        return Side.DEBIT


class Ledger(object):
    def __init__(self, code, account_class):
        self.code = code
        self.account_class = account_class


class AccountGroup(NodeGroup, Ledger):
    def __init__(self, name, code, account_class, description=''):
        NodeGroup.__init__(self, name, description)
        Ledger.__init__(self, code, account_class)

    def accounts(self):
        booking_accounts = sum([child.accounts() for child in self.children], [])
        return [account for account in booking_accounts]

    @staticmethod
    def build_group(group_name, account_class, group_dict):
        group = AccountGroup(name=group_name, code=group_dict['code'], account_class=account_class)
        for item in group_dict.get('groups', []):
            group.add_node(AccountGroup.build_group(item['name'], account_class, item))
        for account in group_dict.get('accounts',[]):
            group.add_node(Account(name=account['name'], account_class=account_class, code=account['code']))
        return group


class Account(Node, Ledger):
    """
    Booking account representation
    """
    def __init__(self, name, code, account_class, description=''):
        Node.__init__(self, name, description)
        Ledger.__init__(self, code, account_class)

    def __getitem__(self, path):
        if len(path) == 1 and self.name in path:
            return self.name, self.code

    def accounts(self):
        return [self]

    def balance(self):
        return self.account_class.balance_side()


class AccountChart(NodeGroup):
    def __init__(self, organization, description=''):
        NodeGroup.__init__(self, organization, description)

    def add_account_class(self, account_class, code_prefix):
        if account_class not in AccountClass:
            raise ValueError('{0} is not a valid account class'.format(account_class))
        self.add_node(AccountGroup(name=account_class.name, account_class=account_class, code=code_prefix))

    def accounts(self):
        booking_accounts = sum([child.accounts() for child in self.children], [])
        return set(account.code for account in booking_accounts)

    def account(self, code):
        booking_accounts = sum([child.accounts() for child in self.children], [])
        return [account for account in booking_accounts if account.code == code][0]

    @staticmethod
    def build_chart(organization, chart_dict):
        chart = AccountChart(organization)
        for account_class, item in chart_dict.items():
            chart.add_account_class(AccountClass(account_class), code_prefix=item['code'])
            for group in item.get('groups',[]):
                chart['/' + account_class].add_node(AccountGroup.build_group(group['name'], AccountClass(account_class), group))
        return chart
