from .parser import PeopleParser, TimeParser, LabelParser

def test(debug=None):
    s = "reports by some_people from 2017/01/23 to 2018/10/28 #some_label"
    time_parser = TimeParser(s)
    people_parser = PeopleParser(s)
    label_parser = LabelParser(s)
    filters = {
        "time": time_parser.parse(),
        "people": people_parser.parse(),
        "label": label_parser.parse()
    }

    data = {
        "users" : [],
        "reports" : [],
    }

    ranks = {
        "users": 1,
        "reports": 2,
        "db": -1,
    }

    return {
        "filters": filters,
        "ranks": ranks,
        "data": data,
        "debug": debug
    }


class Engine:
    def __init__(self):
        pass

    def test(self, debug=None):
        return test(debug=debug)

def main():
    print(test())

if __name__ == "__main__":
    main()