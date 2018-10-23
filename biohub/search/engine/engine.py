from django.db.models import Q
from .filters import FilterParser, FilterItem, FilterRel, FilterType
from ..utils import split_punct


class EngineBase:
    type = 'base'

    def __init__(self, keyword, filters):
        """
        :param keyword: string
        :param filters: [FilterItem]
        """
        self.keyword = keyword
        self.filters = filters

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


class EngineUser(EngineBase):
    type = 'user'

    def _rank(self):
        return 1

    def _result(self):
        from biohub.accounts.models import User
        from biohub.accounts.serializers import UserSerializer

        q = Q()
        for f in self.filters:
            if f.type == FilterType.USER:
                q &= Q(username__icontains=f.value)
            elif f.type == FilterType.ADDR:
                q &= Q(location__icontains=f.value) | Q(organization__icontains=f.value)

        keywords = split_punct(self.keyword)
        q2 = Q()
        for k in keywords:
            q2 |= Q(username__icontains=k)
            q2 |= Q(actualname__icontains=k)

        return UserSerializer(User.objects.filter(q & q2).all(), many=True).data


class EngineReport(EngineBase):
    type = 'report'

    def _rank(self):
        return 2

    def _result(self):
        from biohub.editor.models import Report
        from biohub.editor.serializers import ReportInfoSerializer

        q = Q()
        for f in self.filters:
            if f.type == FilterType.USER:
                q &= Q(author__username__icontains=f.value)

            elif f.type == FilterType.TIME:
                if f.rel == FilterRel.GT:
                    q &= Q(ntime__gt=f.value)
                elif f.rel == FilterRel.LT:
                    q &= Q(ntime__lt=f.value)
                elif f.rel == FilterRel.EQ:
                    q &= Q(ntime=f.value)

            elif f.type == FilterType.TITLE:
                q &= Q(title__icontains=f.value)

            elif f.type == FilterType.LABEL:
                q &= Q(label__label_name__icontains=f.value)

            elif f.type == FilterType.ADDR:
                q &= Q(author__location__icontains=f.value) | Q(author__organization__icontains=f.value)

        keywords = split_punct(self.keyword)
        q2 = Q()
        for k in keywords:
            q2 |= Q(introduction__icontains=k)
            q2 |= Q(title__icontains=k)
            # q |= Q(subroutines__icontains=k)

        return ReportInfoSerializer(Report.objects.filter(q & q2).all(), many=True).data


class EngineDB(EngineBase):
    type = 'db'

    def _rank(self):
        if self._check():
            return 4
        else:
            return -1

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
        return len(self.keyword.split()) == 1 and len(self.keyword) > 100 and set("ATCG") == set(self.keyword.upper())

    def _rank(self):
        if self._check():
            return 0
        else:
            return -1

    def _result(self):
        return []


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
        data.append(EngineUser(self.keyword(), self.filters()).result())
        data.append(EngineReport(self.keyword(), self.filters()).result())
        data.append(EngineDB(self.keyword(), self.filters()).result())
        data.append(EngineBLAST(self.keyword(), self.filters()).result())
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
