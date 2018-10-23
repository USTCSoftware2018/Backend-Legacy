import re


class FilterType:
    TIME = 'time'
    TITLE = 'title'
    NAME = 'name'
    ADDR = 'addr'
    USER = 'user'
    LABEL = 'label'


class FilterRel:
    # scales & time
    EQ = 'eq'
    GT = 'gt'
    LT = 'lt'
    # like
    LIKE = 'like'
    # in
    IN = 'in'


class FilterItem:
    def __init__(self, type, rel, value):
        self.type = type
        self.rel = rel
        self.value = value

    def data(self):
        return {
            "type": self.type,
            "rel": self.rel,
            "value": self.value
        }


class FilterParser:
    def __init__(self, s):
        self.s = s
        self.__filters = list()

    def add_filter(self, filter):
        if filter: self.__filters.append(filter)

    def rule_user_in_address(self):
        p = re.compile(r'users? in (\w+)', re.I)
        match_obj = p.search(self.s)
        self.s = p.sub('', self.s, 16)
        if match_obj:
            addr = match_obj.group(1)
            self.add_filter(FilterItem(FilterType.ADDR, FilterRel.IN, addr))

    def rule_user_from_address(self):
        p = re.compile(r'users? from (\w+)', re.I)
        match_obj = p.search(self.s)
        self.s = p.sub('', self.s, 16)
        if match_obj:
            addr = match_obj.group(1)
            self.add_filter(FilterItem(FilterType.ADDR, FilterRel.IN, addr))

    def rule_reports_by_user(self):
        p = re.compile(r'by (\w+)', re.I)
        match_obj = p.search(self.s)
        self.s = p.sub('', self.s, 16)
        if match_obj:
            user = match_obj.group(1)
            self.add_filter(FilterItem(FilterType.USER, FilterRel.EQ, user))

    def rule_reports_at_user(self):
        p = re.compile(r'@(\w+)', re.I)
        match_obj = p.search(self.s)
        self.s = p.sub('', self.s, 16)
        if match_obj:
            user = match_obj.group(1)
            self.add_filter(FilterItem(FilterType.USER, FilterRel.EQ, user))

    def rule_label(self):
        p = re.compile(r'#(\w+)', re.I)
        match_obj = p.search(self.s)
        self.s = p.sub('', self.s, 16)
        if match_obj:
            label = match_obj.group(1)
            self.add_filter(FilterItem(FilterType.LABEL, FilterRel.EQ, label))

    def parse_time(self, t):
        import dateutil.parser
        return dateutil.parser.parse(t)

    def rule_time(self):
        if len(self.s.split()) <= 1:
            return None
        try:
            from ..nlp.nlp import parse
            start, end, match = parse(self.s)
            print('parse: ', start, end, match)
            if start:
                self.add_filter(FilterItem(FilterType.TIME, FilterRel.GT, self.parse_time(start)))
            if end:
                self.add_filter(FilterItem(FilterType.TIME, FilterRel.LT, self.parse_time(end)))
            if match:
                for match_str in match:
                    self.s = self.s.replace(match_str, '')
        except:
            return

    def parse(self):
        self.rule_label()
        self.rule_reports_at_user()
        self.rule_reports_by_user()
        self.rule_user_in_address()
        self.rule_user_from_address()
        self.rule_time()
        f = self.__filters

        filter_words = [
            'reports', 'report', 'users', 'user',
            'before', 'after', 'until', 'till', 'since',
            'from', 'to'
        ]

        for filter_word in filter_words:
            self.s = self.s.replace(filter_word, '')

        return (self.s, f)
