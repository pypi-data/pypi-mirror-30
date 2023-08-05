
import logging
import requests
from pycountry import countries
import datetime

log = logging.getLogger(__name__)

class Hatchbuck():
    """
    Class to interact with the Hatchbuck.com API
    """
    url = "https://api.hatchbuck.com/api/v1/"
    key = None
    noop = False

    def __init__(self, key, noop=False):
        """
            Initialize API session with settings for the whole session
        :param key: Hatchbuck API key token,
        :param noop: dry-run-mode, no not call the API
        """
        self.key = key
        self.noop = noop
    
    def search_email(self, email):
        """
        Search for profiles, and search for email addresses within them
        :param email:The email address we're looking for
        :return:Return profile if it contains the email address or return None
        """
        query = {'emails': [{'address': email}]}
        log.debug("searching for {0}".format(query))
        r = requests.post(self.url + 'contact/search' + '?api_key=' + self.key, json=query)
        if r.status_code == 200:
            result = r.json()
            for profile in result:
                if self.profile_contains(profile, 'emails', 'address', email):
                    log.debug("found: {0}".format(profile))
                    return profile
                else:
                    log.debug("found profile without matching address: {0}".format(profile))
                    continue
            # if none of the returned profiles actually contain the email address return None
            return None
        else:
            log.debug("not found")
            return None



    def search_name(self, first, last):
        """
        Search for profiles, and search for first and last within them
        :param first:The first name we're looking for
        :param last:The last name we're looking for
        :return:Return profile or return None
        """
        query = {'firstName': first, 'lastName': last}
        log.debug("searching for {0}".format(query))
        r = requests.post(self.url + 'contact/search' + '?api_key=' + self.key, json=query)
        if r.status_code == 200:
            value = r.json()
            log.debug("found: {0}".format(value[0]))
            return value[0]
        else:
            log.debug("not found")
            return None

    def search_email_multi(self, emails):
        """
        Search for email addresses in the email address list
        :param emails:A list of email addresses
        :return:Return the first user profile that matches
        """
        if type(emails) == type(str()):
            emails = [emails]
        for email in emails:
            if email == None:
                continue
            profile = self.search_email(email)
            if profile != None:
                return profile
        return None

    def update(self, contactId, profile):
        """
        Update an existing contact
        :param contactId:The contact ID we want to update
        :param profile:The profile information we want the contactID to have
        :return:Return profile with updates if successful or None if fail
        """
        profile['contactId'] = contactId
        log.debug("updating {0}".format(profile))
        if self.noop:
            return None
        r = requests.put(self.url + 'contact' + '?api_key=' + self.key, json=profile)
        if r.status_code == requests.codes.ok:
            value = r.json()
            log.debug("success: {0}".format(value))
            return value
        else:
            # this happens e.g. when trying to add an email address that already belongs to another contact
            log.debug("fail: {0}".format(r.text))
            return None


    def create(self, profile):
        """
        Create a new profile
        :param profile:The profile we want to create
        :return:Return the new profile with the new contactID if successful or None if fail
        """
        log.debug("creating {0}".format(profile))
        if self.noop:
            profile['contactId'] = None
            return profile
        r = requests.post(self.url + 'contact' + '?api_key=' + self.key, json=profile)
        if r.status_code == 200:
            value = r.json()
            log.debug("success: {0}".format(value))
            return value
        else:
            log.debug("fail: {0}".format(r.text))
            return None


    def profile_add_address(self, profile, address, addresstype):
        """
        :param profile: The profile we want to add the address to
        :param address: The address we want to add
        :param addresstype: The type of address we want to add
        :return: Return the profile after adding the address to it

        """
        try:
            country = countries.get(alpha2=address['country']).name
        except:
            country = address['country']

        update = {
            'street': address['street'],
            'zip': address['zip_code'],
            'city': address['city'],
            'country': country,
            'type': addresstype,
        }

        # check that there is at least one field that is not empty
        notempty = False
        for key in ['street', 'zip', 'city', 'country']:
            if update[key] != None and update[key] != "":
                notempty = True
        if not notempty:
            return profile

        if 'addresses' not in profile:
            profile['addresses'] = []

        addressfound = False
        for item in profile['addresses']:
            thisisit = True
            for key in update:
                if not (item[key] == update[key] or (item[key] == "" and update[key] == None)):
                    thisisit = False
            if thisisit:
                # all fields matched
                addressfound = True
                break
        if not addressfound:
            updated = self.update(profile['contactId'],{'addresses': [update]})
            if updated == None:
                # update failed or noope'd
                return profile
            else:
                return updated

        return profile

    def profile_contains(self, profile, dictname, attributename, value):
        """

        :param profile:hatchbuck contact profile
        :param dictname:the information in the profile dictionary
        :param attributename:A attribut that shows address(email, phone, ...)
        :param value:Values of attributename (email, phone, ...)
        :return:Return true when get a value matching the values in the dictionary, or flase In the opposite case
        """
        # check if a certain email/phone/website address is already in the hatchbuck contact profile
        # the hatchbuck profile is built up like:
        # profile = {
        #   dictname: (e.g. 'emails')
        #     [
        #       {
        #         attributename: value, (e.g. 'address': 'me@example.com'), the attributename and value are used for matching
        #         ... (more attributes, e.g. 'type': 'Work', added here)
        #       },
        #     ],
        #   next dict name....
        # }
        # returns False if it's not there and the dict containing the value if found
        if dictname not in profile:
            return False
        elif attributename == None:
            return profile[dictname].lower() == value.lower()
        for element in profile[dictname]:
            if dictname == "phones":
                # ignore spaces in phone numbers when comparing
                if element[attributename].lower().replace(' ','') == value.lower().replace(' ',''):
                    return True
            else:
                if element[attributename].lower() == value.lower():
                    return True
        return False

    def profile_add(self, profile, dictname, attributename, valuelist, moreattributes={}):
        """
        Add a new fields to the profile if it does not exist, or update the field if it exists
        :param profile: The profile we want to add or modify fields
        :param dictname: The name of the field we're looking for to add or edit
        :param attributename: The name of the attribute we're looking for to add or edit
        :param valuelist: The valus of the attribute
        :param moreattributes: More attributes that we want to add or modify
        :return: Return profile after adding or editing fields
        """
        # add a certain email/phone/website field to the hatchbuck contact profile if it's not there already
        # the hatchbuck profile is built up like:
        # profile = {
        #   dictname: (e.g. 'emails')
        #     [
        #       {
        #         attributename: value, (e.g. 'address': 'me@example.com'), the attributename and value are used for matching
        #         ... (more attributes, e.g. 'type': 'Work', added here)
        #       },
        #     ],
        #   next dict name....
        # }
        if type(valuelist) != type([]):
            valuelist = [valuelist]
        for value in valuelist:
            if attributename == None:
                updateprofile = {dictname: value}
            else:
                updateprofile = {dictname: [{attributename: value}]}
            if not value == None and not value == '' and not self.profile_contains(profile, dictname, attributename, value):
                if dictname == 'emails' and attributename == 'address':
                    lookup = self.search_email(value)
                    if not lookup == None:
                        # uh-oh there is already another contact with this email address, possible duplicate
                        log.warn("uh-oh trying to add email address {0} to {2} already belonging to another contact {1}, not adding".format(value, lookup, profile))
                        return profile
                for key in moreattributes:
                    updateprofile[dictname][0][key] = moreattributes[key]
                # TODO updating the profile through the API right now instead of batching them, can be optimized later if necessary
                updated = self.update(profile['contactId'], updateprofile)
                if updated != None:
                    # update not failed or noop'ed
                    profile = updated
                else:
                    log.debug("update failed or nooped")
            else:
                log.debug("skipping update because value empty or there already: {0}".format(updateprofile))
        return profile


    def add_tag(self, contactId, tagname):
        """
        Add tags by contact id
        :param contactId: A contact ID to which the tag should be added
        :param tagname: Tag that we want to add to contactId
        :return: Return Add the tag if success or the Tag does not add if fail
        """
        log.debug("adding tag {0} to contact {1}".format(tagname, contactId))
        profile = [{'name': tagname}]
        if self.noop:
            return None
        r = requests.post(self.url + 'contact/' + contactId + '/Tags?api_key=' + self.key, json=profile)
        if r.status_code == 201:
            log.debug("success: {0}".format(r.text))
        else:
            log.debug("fail: {0}".format(r.text))


    def profile_add_birthday(self, profile, date):
        """
        Add birthday to profile
        :param profile: A profile to which the birthday should be added
        :param date: The birthday should be added to the file
        :return:Return profile after adding the birthday
        """
        if not date.get('day',0) or not date.get('month',0):
            log.debug("no day/month in birthday {0}, skipping".format(date))
            return profile
        if not date.get('year',0):
            # set year 1000 for unknown year, year 0 is not supported by python datetime.date
            date['year'] = 1000
        oldbirthday = ''
        for field in profile.get('customFields',[]):
            if field['name'] == 'Birthday':
                oldbirthday = field['value']
                break
        if oldbirthday:
            oldbirthday = datetime.datetime.strptime(oldbirthday, '%m/%d/%Y').date()
            log.debug("found old birthday: {0}".format(oldbirthday))
            if oldbirthday.year != 1000 and date['year'] == 1000:
                # if there is a proper year already lets not overwrite that
                date['year'] = oldbirthday.year
        return self.profile_add(profile, 'customFields', 'value', str(date['month']) + '/' + str(date['day']) + '/' + str(date['year']), {'name': 'Birthday'})
