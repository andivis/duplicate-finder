import logging
import re

import library.helpers as helpers


def get(item, key):
    return item.get(key, '')


class DuplicateFinder:
    def isDuplicate(self, line, line2):
        result = False

        fields = [
            'name',
            'short_name',
            'website_url',
            'linkedin_url'
        ]

        for field in fields:
            if not get(line, field) or not get(line2, field):
                continue

            value1 = ''
            value2 = ''

            if field == 'name' or field == 'short_name':
                value1 = self.getBasicCompanyName(get(line, field))
                value2 = self.getBasicCompanyName(get(line2, field))
            else:
                value1 = self.getBasicUrl(get(line, field))
                value2 = self.getBasicUrl(get(line2, field))

            if not value1 or not value2:
                continue

            if value1 == value2:
                result = True
                break

        return result

    def getBasicCompanyName(self, s):
        # description or extraneous information usually comes after
        s = helpers.findBetween(s, '', '|')
        s = helpers.findBetween(s, '', ' - ')
        s = helpers.findBetween(s, '', ',')
        s = helpers.findBetween(s, '', '(')

        s = s.lower()

        stringsToIgnore = [
            'limited',
            'ltd',
            'llc',
            'inc',
            'pty',
            'pl',
            'co',
            'corp'
            'incorporated'
        ]

        for string in stringsToIgnore:
            # word with space before and after
            s = re.sub(f' {string} ', ' ', s)
            # ends in the string
            s = re.sub(f' {string}$', '', s)

        s = self.getFuzzyVersion(s)

        return s

    def getFuzzyVersion(self, s):
        result = s.lower()
        return helpers.lettersAndNumbersOnly(result)

    def getBasicUrl(self, s):
        result = helpers.findBetween(s, '://www.', '')
        result = helpers.findBetween(result, '://', '')

        if result.endswith('/'):
            result = result[0:-1]

        return result


class Main:
    def run(self):
        helpers.setUpLogging()
        logging.info('Starting')
        self.duplicateFinder = DuplicateFinder()
        self.ids = {}
        lines = helpers.getCsvFile('input.csv')

        for i, line in enumerate(lines):
            try:
                logging.info(f'On line {i + 1} of {len(lines)}')
                self.checkForDuplicates(i, line, lines)

            except Exception as e:
                helpers.handleException(e)

        logging.info('Done')

    def checkForDuplicates(self, i, line, lines):
        for j, otherLine in enumerate(lines):
            # no need to re-tread rows we already checked
            if j <= i:
                continue

            if get(self.ids, get(otherLine, 'Id')):
                # already found this duplicate
                continue

            if self.duplicateFinder.isDuplicate(line, otherLine):
                logging.info(f'Duplicate: {get(otherLine, "name")} (ID: {get(otherLine, "Id")}) seems to be a duplicate of {get(line, "name")} (ID: {get(line, "Id")})')
                self.ids[get(otherLine, 'Id')] = True


main = Main()
main.run()
