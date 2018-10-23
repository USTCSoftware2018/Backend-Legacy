import requests

NLP_SERVER = 'http://nlp.biohub.tech'

def resolve(text):
    r = requests.post(NLP_SERVER, json={'text', text}, timeout=3)
    return r.json()

def parse(text):
    """
    return (start: string, end: string, match: [string])
    """
    res = resolve(text)
    if len(res) == 0:
        return (None, None, None)
    if len(res) == 1:
        t0 = res[0]
        return (t0.get("resolved"), None, [t0.get("original")])
    if len(res) >= 2:
        t0 = res[0]
        t1 = res[1]
        return (t0.get("resolved"), t1.get("resolved"), [t0.get("original"), t1.get("original")])


if __name__ == "__main__":
    print(parse("yesterday"))