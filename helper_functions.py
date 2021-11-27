import re

def mask_this_email(s):
    lo = s.find('@')
    return s[0] + "*****" + s[lo-1:]

def validEmail(email):
    # pass the regular expression
    # and the string into the fullmatch() method
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

def validPhoneNumber(phone):
    regex = r'\b[0-9]+\b'
    if(len(phone) == 10 and re.fullmatch(regex, phone)):
        return True
    else:
        return False
