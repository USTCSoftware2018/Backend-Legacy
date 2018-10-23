from .filters import FilterParser

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
        return [{"id":1,"followed":False,"stat":{"star_count":0,"report_count":17,"following_count":10,"follower_count":6,"experience_count":0},"avatar_url":"https://api.biohub.tech/media/2.jpg","last_login":"2018-10-16T22:37:00.808568+08:00","username":"test","actualname":"","organization":"MIT","email":"test@email.com","location":"Boston","site_url":"","description":"description"},
{"id":2,"followed":False,"stat":{"star_count":0,"report_count":0,"following_count":2,"follower_count":3,"experience_count":0},"avatar_url":"https://www.gravatar.com/avatar/94fba03762323f286d7c3ca9e001c541?s=328&r=g&d=identicon","last_login":"2018-10-12T15:55:23.252976+08:00","username":"test1","actualname":"","organization":"","email":"test1@test.com","location":"","site_url":"","description":""}]


class EngineReport(EngineBase):
    type = 'report'

    def _rank(self):
        return 2

    def _result(self):
        return [
{"id":16,"title":"16","author":{"id":1,"avatar_url":"https://api.biohub.tech/media/2.jpg","description":"description","followed":False,"username":"test"},"iscollected":False,"abstract":"WOASN DJFAS\nsanifoanf","commentsnum":13,"labels":[{"id":12,"report_count":1,"name":"hello"},{"id":13,"report_count":1,"name":"babababababa"},{"id":14,"report_count":1,"name":"fhdksjhfkjdsahfkjsadhkjfhsdakj"}],"likesnum":0,"isliked":False},
{"id":4,"title":"asdfbaisdf","author":{"id":1,"avatar_url":"https://api.biohub.tech/media/2.jpg","description":"description","followed":False,"username":"test"},"iscollected":False,"abstract":"fasbdfhjabef","commentsnum":5,"labels":[],"likesnum":2,"isliked":False}]


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
        return self._keyword

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
            "filters": self.filters(),
            "data": self.result(),
            "debug": self.debug()
        }
        return data


def main():
    print(Engine('reports yesterday by jiyan #label').data())


if __name__ == "__main__":
    main()