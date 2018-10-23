from ..utils import split_punct


class Keyword:
    FUNCTIONAL_WORDS = {'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very',
         'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most',
         'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves',
         'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more',
         'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had',
         'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on',
         'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now',
         'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i',
         'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how',
         'further', 'was', 'here', 'than'}

    @classmethod
    def _convert_underscore(cls, x: str):
        if not x:
            return None

        return '_'.join(part.capitalize() for part in split_punct(x))

    def get_keywords(self):
        """
        usernames, actualnames, location, reports title, #labels/tags ...
        "hejiyan" "Jiyan_He"
        """
        from biohub.accounts.models import User
        from biohub.editor.models import Report, Label

        users = User.objects.values('username', 'actualname', 'location')
        reports = Report.objects.values('title')
        labels = Label.objects.values('label_name')

        results = set()
        for user in users:
            results.add(user['username'])
            results.add('@' + user['username'])

            actualname_parts = split_punct(user['actualname'])
            location_parts = split_punct(user['location'])

            results = results.union(set(actualname_parts))
            results = results.union(set(location_parts))
            results.add('_'.join(actualname_parts))
            results.add('_'.join(location_parts))

        for report in reports:
            for word in split_punct(report['title']):
                if word.lower() in self.FUNCTIONAL_WORDS:
                    results.add(word)

        for label in labels:
            results.add('#' + self._convert_underscore(label['label_name']))

        return {keyword.strip() for keyword in results - self.FUNCTIONAL_WORDS if keyword.strip()}
