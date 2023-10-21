'''
    This module is used to get the first set, follow set and ps set of a grammar.
'''
from typing import Any
import yaml

class LL1Scanner():
    '''
        Context-free grammar system.
    '''
    def __init__(self) -> None:
        self.symbol_s = None        # Start symbol
        self.symbol_t = []          # [list] SymbolTerm
        self.symbol_nt = []         # [list] SymbolNonTerm
        self.production_suf = []    # [list] ProductionSuffix
        self.production = []        # [list] Production
        self.first = {}             # [dict] str -> set(str)
        self.follow = {}            # [dict] str -> set(str)
        self.ps = {}                # [dict] str -> set(str)


class Symbol:
    '''
        Base class of SymbolTerm and SymbolNonTerm.
    '''
    def __init__(self) -> None:
        pass


class SymbolTerm(Symbol):
    '''
        Terminal symbol.
    '''
    def __init__(self, attr: str) -> None:
        super().__init__()
        self.attr = str(attr)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SymbolTerm):
            return self.attr == other.attr
        return False

    def __str__(self) -> str:
        return self.attr


class SymbolNonTerm(Symbol):
    '''
        Nonterminal symbol.
    '''
    def __init__(self, attr: str) -> None:
        super().__init__()
        self.attr = str(attr)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SymbolNonTerm):
            return self.attr == other.attr
        return False

    def __str__(self) -> str:
        return self.attr


class ProductionSuffix:
    '''
        Suffix of a production.
    '''
    def __init__(self, attr: list[Symbol]) -> None:
        self.symbol_list = list(attr)
        self.attr_list = list(map(lambda symbol: symbol.attr, self.symbol_list))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ProductionSuffix):
            return self.attr_list == other.attr_list
        return False

    def __str__(self) -> str:
        return "".join(self.attr_list)


class Production:
    '''
        Production of a grammar.
    '''
    def __init__(self, left: str, right: list[str]) -> None:
        self.left = SymbolNonTerm(left)

        self.right = []
        if right:
            for right_symbol in right:
                if SymbolTerm(right_symbol) in Scanner.symbol_t:
                    self.right.append(SymbolTerm(right_symbol))
                else:
                    self.right.append(SymbolNonTerm(right_symbol))

        else:
            self.right = [EPSILON]

    def __str__(self) -> str:
        return self.left.attr + " -> " + "".join([symbol.attr for symbol in self.right])


EPSILON = SymbolTerm("\u03B5")
Scanner = LL1Scanner()

def parse_params() -> None:
    '''
        Get the params from input.
    '''
    with open('input.yml', 'r', encoding='utf-8') as f:
        params = yaml.load(f.read(), Loader=yaml.FullLoader)

    param_symbol_s = params['symbol_s']
    param_production = params['production']
    param_symbol_nt = set()
    param_symbol_t = set()
    param_symbol = set()

    for pro in param_production:
        param_symbol_nt.add(pro[0])
        param_symbol = param_symbol.union(set(pro))
    param_symbol_t = param_symbol - param_symbol_nt

    for attr in param_symbol_t:
        Scanner.symbol_t.append(SymbolTerm(attr))

    for attr in param_symbol_nt:
        Scanner.symbol_nt.append(SymbolNonTerm(attr))

    Scanner.symbol_s = SymbolNonTerm(param_symbol_s)

    for pro in param_production:
        left = pro[0]
        right = pro[1:]
        Scanner.production.append(Production(left, right))

    for pro in Scanner.production:
        if len(pro.right) > 1:
            symbol_list = []
            for symbol in reversed(pro.right):
                symbol_list.append(symbol)
                if len(symbol_list) > 1:
                    pro_suf = ProductionSuffix(reversed(symbol_list))
                    if pro_suf not in Scanner.production_suf:
                        Scanner.production_suf.append(pro_suf)


def print_productions() -> None:
    '''
        Print the productions.
    '''
    print("------------------Productions------------------")
    print()
    for pro in Scanner.production:
        print(pro)


def init_sets() -> None:
    '''
        Initialize the [First] and [Follow] sets.
    '''
    Scanner.first[str(EPSILON)] = {EPSILON.attr}
    for symbol in Scanner.symbol_t:
        Scanner.first[str(symbol)] = {symbol.attr}
    for symbol in Scanner.symbol_nt:
        Scanner.first[str(symbol)] = set()
        if symbol == Scanner.symbol_s:
            Scanner.follow[str(symbol)] = {"#"}
        else:
            Scanner.follow[str(symbol)] = set()
    for pro_suf in Scanner.production_suf:
        Scanner.first[str(pro_suf)] = set()
    for pro in Scanner.production:
        Scanner.ps[str(pro)] = set()

    Scanner.first = dict(sorted(Scanner.first.items(), key=lambda item: (len(item[0]), item[0])))
    Scanner.follow = dict(sorted(Scanner.follow.items(), key=lambda item: item[0]))

def first_set() -> None:
    '''
        Get the [First] set of the grammar.
    '''
    rounds = 0
    success = False
    print()
    print("-----------------First Set-----------------")
    while not success:
        success = True
        rounds = rounds + 1
        print()
        print(f"------------------Round {rounds}------------------")
        print()
        for key, value in Scanner.first.items():
            print(f"[First] {key} ====> {str(value).replace('set()', '{}')}")

        # Rule 1
        for pro_suf in Scanner.production_suf:
            update_set = set()
            for symbol in pro_suf.symbol_list:
                update_set = update_set.union(Scanner.first[str(symbol)])
                if EPSILON.attr not in Scanner.first[str(symbol)]:
                    if EPSILON.attr in update_set:
                        update_set.remove(EPSILON.attr)
                    break

            if Scanner.first[str(pro_suf)] != update_set:
                success = False
                Scanner.first[str(pro_suf)] = update_set

        # Rule 2
        for pro in Scanner.production:
            update_set = set()
            if len(pro.right) > 1:
                pro_suf = ProductionSuffix(pro.right)
                update_set = Scanner.first[str(pro.left)].union(Scanner.first[str(pro_suf)])
            else:
                update_set = Scanner.first[str(pro.left)].union(Scanner.first[str(pro.right[0])])

            if Scanner.first[str(pro.left)] !=  update_set:
                success = False
                Scanner.first[str(pro.left)] = update_set


def follow_set() -> None:
    '''
        Get the [Follow] set of the grammar.
    '''
    rounds = 0
    success = False
    print()
    print("-----------------Follow Set-----------------")
    while not success:
        success = True
        rounds = rounds + 1
        print()
        print(f"------------------Round {rounds}------------------")
        print()
        for key, value in Scanner.follow.items():
            print(f"[Follow] {key} ====> {str(value).replace('set()', '{}')}")

        for pro in Scanner.production:
            for index, symbol in enumerate(pro.right):
                if isinstance(symbol, SymbolNonTerm):
                    update_set = Scanner.follow[str(symbol)]
                    if index == len(pro.right) - 1:
                        suffix = ProductionSuffix([EPSILON])
                    else:
                        suffix = ProductionSuffix(pro.right[index + 1:])
                    update_set = update_set.union(Scanner.first[str(suffix)])
                    if EPSILON.attr in Scanner.first[str(suffix)]:
                        update_set.remove(EPSILON.attr)
                        update_set = update_set.union(Scanner.follow[str(pro.left)])

                    if Scanner.follow[str(symbol)] != update_set:
                        success = False
                        Scanner.follow[str(symbol)] = update_set


def ps_set() -> None:
    '''
        Get the [PS] set of the grammar.
    '''
    print()
    print("-----------------PS Set-----------------")
    print()
    for pro in Scanner.production:
        suffix = ProductionSuffix(pro.right)
        Scanner.ps[str(pro)] = Scanner.ps[str(pro)].union(Scanner.first[str(suffix)])
        if EPSILON.attr in Scanner.first[str(suffix)]:
            Scanner.ps[str(pro)].remove(EPSILON.attr)
            Scanner.ps[str(pro)] = Scanner.ps[str(pro)].union(Scanner.follow[str(pro.left)])

    for key, value in Scanner.ps.items():
        print(f"[PS] {key} ====> {str(value).replace('set()', '{}')}")


if __name__ == "__main__":
    parse_params()
    print_productions()
    init_sets()
    first_set()
    follow_set()
    ps_set()
