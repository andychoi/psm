from threading import Thread
from django.core.mail import send_mail


def send_mail_async(subject, message, from_email, recipient_list,
                     fail_silently=False, auth_user=None, auth_password=None,
                     connection=None, html_message=None):

    Thread(target=send_mail, args=(subject, message, from_email, recipient_list,
                                   fail_silently, auth_user, auth_password,
                                   connection, html_message)).start()

# EmailMultiAlternatives is a subclass of EmailMessage. You can specify bcc and cc when you initialise the message.
# EmailMessage now supports cc and bcc:

# https://stackoverflow.com/questions/36690146/python-retrieve-email-addresses
import email.utils
import re

def split_combined_addresses(addresses):
    #remove special chars
    addresses = re.sub("\n|\r|\t", "",  addresses)
    
    # addrs = re.findall(r'(.*?)\s<(.*?)>,?', addresses)    #colon separated
    addrs = re.findall(r'(.*?)\s<(.*?)>;?', addresses)    #semicolon separated
    
    # remove leading space in name  .strip()
    # remove double-quote in name
    addrs_clean = [(i.replace('"','').strip(), j) for i,j in addrs]

    # add missing emails without name
    emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", addresses)
    for email in emails:
        if (not email in list(zip(*addrs_clean))[1]):
            addrs_clean.append(('', email))

    return addrs_clean

    # not working... with name.. without quote   
    # parts = email.utils.getaddresses([addresses])
    # return [email.utils.formataddr(name_addr) for name_addr in parts]

# print(split_combined_addresses(email_to))

"""
This is working...
-----------------
addresses='"Johnny Test" <johnny@test.com>, Jack <another@test.com>, "Scott Summers" <scotts@test.com>, noname@test.com'
addresses='"Johnny, Test" <johnny@test.com>; Jack <another@test.com>; "Scott Summers" <scotts@test.com>; noname@test.com'
addresses = re.sub("\n|\r|\t", "",  addresses)
addrs = re.findall(r'(.*?)\s<(.*?)>,?', addresses)

single email extract with regex ( test: https://regex101.com/ )
-------------------------------
(.*?)\s<(.*?)>,?
Scott, Summers <scotts@test.com>

https://docs.python.org/3/library/email.utils.html
email.utils.parseaddr('Smith, Joe A. <smithja@yahoo.com>')  # Fails

"""
from email.utils import formataddr

def combine_to_addresses(addresses):
    return ', '.join([formataddr(address) for address in addresses])

"""
> from email.utils import formataddr
> addresses = [("John Doe", "john@domain.com"), ("Jane Doe", "jane@domain.com")]
> ', '.join([formataddr(address) for address in addresses])
'John Doe <john@domain.com>, Jane Doe <jane@domain.com>'
"""