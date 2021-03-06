from django.db.models import Q
from haystack.query import SearchQuerySet, SQ
from .filters import FilterParser, FilterItem, FilterRel, FilterType
from ..utils import split_punct, punct_ws_re


class EngineBase:
    type = 'base'

    def __init__(self, keyword, filters, s):
        """
        :param keyword: string
        :param filters: [FilterItem]
        """
        self.keyword = keyword
        self.filters = filters
        self.s = s

    def _result(self):
        return []

    def _rank(self):
        return -1

    def result(self):
        return {
            "type": self.type,
            "rank": self._rank(),
            "data": self._result()
        }


def get_rank(s, type):
    s = s.lower()
    if "report" in s:
        if type == "user":
            return -1
        if type == "report":
            return 1
        if type == "brick":
            return -1
    if "user" in s:
        if type == "user":
            return 1
        if type == "report":
            return -1
        if type == "brick":
            return -1
    if "brick" in s:
        if type == "user":
            return -1
        if type == "report":
            return -1
        if type == "brick":
            return 1
    if len(s.split()) >= 3:
        if type == "user":
            return 3
        if type == "report":
            return 2
    return 3


class EngineUser(EngineBase):
    type = 'user'

    def _rank(self):
        return get_rank(self.s, self.type)

    def _result(self):
        from biohub.accounts.models import User
        from biohub.accounts.serializers import UserSerializer

        q = Q()
        for f in self.filters:
            if isinstance(f.value, str):
                value = f.value.replace('_', punct_ws_re)
            else:
                value = f.value

            if f.type == FilterType.USER:
                q &= Q(username__icontains=value) | Q(actualname__icontains=value)
            elif f.type == FilterType.ADDR:
                q &= Q(location__iregex=value) | Q(organization__iregex=value)

        keywords = split_punct(self.keyword)
        q2 = Q()
        for k in keywords:
            q2 |= Q(username__iregex=k)
            q2 |= Q(actualname__iregex=k)

        return UserSerializer(User.objects.filter(q & q2).all(), many=True).data


class EngineReport(EngineBase):
    type = 'report'

    def _rank(self):
        return get_rank(self.s, self.type)

    def _result(self):
        from biohub.editor.models import Report
        from biohub.editor.serializers import ReportInfoSerializer

        q = Q()
        for f in self.filters:
            if isinstance(f.value, str):
                value = f.value.replace('_', punct_ws_re)
            else:
                value = f.value

            if f.type == FilterType.USER:
                q &= Q(author__username__icontains=value)

            elif f.type == FilterType.TIME:
                if f.rel == FilterRel.GT:
                    q &= Q(ntime__gt=value)
                elif f.rel == FilterRel.LT:
                    q &= Q(ntime__lt=value)
                elif f.rel == FilterRel.EQ:
                    q &= Q(ntime=value)

            elif f.type == FilterType.TITLE:
                q &= Q(title__iregex=value)

            elif f.type == FilterType.LABEL:
                q &= Q(label__label_name__iregex=value)

            elif f.type == FilterType.ADDR:
                q &= Q(author__location__iregex=value) | Q(author__organization__iregex=value)

        keywords = split_punct(self.keyword)
        q2 = Q()
        for k in keywords:
            q2 |= Q(introduction__iregex=k)
            q2 |= Q(title__iregex=k)
            # q |= Q(subroutines__iregex=k)

        return ReportInfoSerializer(Report.objects.filter(q & q2).all(), many=True).data


class EngineDB(EngineBase):
    type = 'db'

    def _rank(self):
        if self._check():
            return 4
        else:
            return 50

    def _check(self):
        return len(self.keyword.split()) == 1 and len(self.keyword) < 50

    def _result(self):
        if not self._check(): return []
        from .db.SpiderMonitor import SpiderMonitor
        result = SpiderMonitor().spiders(keyword=self.keyword, timeout=5)
        return result


class EngineBLAST(EngineBase):
    type = 'blast'

    def _check(self):
        self.keyword = self.keyword.replace(' ', '')
        self.keyword = self.keyword.replace('\t', '')
        return len(self.keyword.split()) == 1 and len(self.keyword) >= 10 and set("ATCG") == set(self.keyword.upper())

    def _rank(self):
        if self._check():
            return 0
        else:
            return 100

    def _result(self):
        return ['blast']


class EngineBrick(EngineBase):
    type = 'brick'

    def _check(self):
        return self.s.lower().startswith('bba_') or self.s.lower().startswith('psb')

    def _rank(self):
        if self._check():
            return 0
        else:
            return get_rank(self.s, self.type)

    def _result(self):
        from biohub.biobrick.serializers import BiobrickSerializer

        qs = SearchQuerySet()
        ordering = ['-weight', '-creation_date']

        # Filter by author
        for f in self.filters:
            if f.type == FilterType.USER:
                # Due to technical limitations, here we can't use regexp
                qs = qs.filter(author__contains=f.value)

        # Filter by part names
        qs_names = qs.filter(part_name__contains=self.keyword).order_by(*ordering)
        qs_names = qs_names.load_all()[:5]

        # Search descriptions
        qs_desc = qs.filter(text__contains=self.keyword).order_by(*ordering)
        qs_desc = qs_desc.load_all()[:25]

        # Merge and Uniquify
        results = list(qs_names)
        for result in qs_desc:
            if result not in results:
                results.append(result)

        return BiobrickSerializer.list_creator()(results, many=True).data


class Engine:
    def __init__(self, s, filters=None):
        self.s = s
        self._filters = filters
        self._keyword = ""

    def keyword(self):
        return self._keyword.strip()

    def filters(self):
        if not self._filters:
            self._keyword, self._filters = FilterParser(self.s).parse()
        return self._filters

    def result(self):
        data = list()
        data.append(EngineUser(self.keyword(), self.filters(), self.s).result())
        data.append(EngineReport(self.keyword(), self.filters(), self.s).result())
        data.append(EngineDB(self.keyword(), self.filters(), self.s).result())
        data.append(EngineBLAST(self.keyword(), self.filters(), self.s).result())
        data.append(EngineBrick(self.keyword(), self.filters(), self.s).result())
        return data

    def debug(self):
        return {
            "s": self.s,
            "keyword": self.keyword()
        }

    def data(self):
        data = {
            "filters": [x.data() for x in self.filters()],
            "data": self.result(),
            "debug": self.debug()
        }
        return data


def main():
    print(Engine('reports yesterday by jiyan #label').data())


if __name__ == "__main__":
    main()
