import sys
import os
import signal
import argparse
import sqlite3
import random
import time
import re
from datetime import datetime
from math import floor

from lxml import html as etree
from multidict import MultiDict
import requests

import config


def get_tor_session():
    session = requests.Session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    session.headers.update({'User-agent': random_ua_string()})
    return session


def get_form_data_from_form(form):
    form_data = MultiDict()
    for el in form.xpath('.//input[@name]|select[@name]|textarea[@name]|button[@name]'):
        data = {}
        if el.tag == 'input':
            if el.attrib.get('type') == 'radio' or el.attrib.get('type') == 'checkbox':
                if el.attrib.get('checked', None):
                    data[el.attrib['name']] = el.attrib.get('value', '')
            else:
                data[el.attrib['name']] = el.attrib.get('value', '')
        elif el.tag == 'select':
            options = el.xpath('./option[@selected]')
            if options:
                data[el.attrib['name']] = options[0].attrib.get('value', '')
        elif el.tag == 'textarea':
            data[el.sttrib['name']] = el.text or ''
        elif el.tag == 'button':
            if el.attrib.get('type', None) == 'submit':
                data[el.attrib['name']] = el.attrib.get('value', '')
        form_data.extend(data)
    return form_data


def dict_factory(cursor, row):
    """For convenient dict access of sqlite results"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def init():
    """
    Initialize the database 
    """
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE
        IF NOT EXISTS
        jobs
        (num INT)""")
    cursor.execute("""CREATE UNIQUE INDEX
        IF NOT EXISTS
        jobsnum
        ON jobs(num)""")
    cursor.execute("""CREATE TABLE
        IF NOT EXISTS
        organizations
        (
            state TEXT,
            court TEXT,
            register_type TEXT,
            idnum TEXT,
            name TEXT,
            location TEXT,
            last_seen TEXT DEFAULT CURRENT_DATE
        )""")
    cursor.execute("""CREATE UNIQUE INDEX
        IF NOT EXISTS
        orguniq
        ON organizations(court, register_type, idnum)""")
    db.commit()


def empty_jobqueue():
    """Remove all jobs from the queue"""
    cursor = db.cursor()
    cursor.execute("DELETE FROM jobs WHERE 1")
    db.commit()


def empty_orgstable():
    """Delete all organizations"""
    cursor = db.cursor()
    cursor.execute("DELETE FROM organizations WHERE 1")
    db.commit()


def count_jobs():
    """Returns the number of jobs left"""
    cursor = db.cursor()
    cursor.execute("SELECT count(*) AS num_jobs FROM jobs")
    return cursor.fetchone()["num_jobs"]


def has_jobs():
    """Returns true of job queue has jobs"""
    if count_jobs() > 0:
        return True
    return False


def create_jobs():
    """Fills the job queue with jobs"""
    if args.verbose:
        n = config.MAX_REGISTER_NUMBER - config.MIN_REGISTER_NUMBER
        print("Creating %d jobs..." % n)
    cursor = db.cursor()
    for n in range(config.MIN_REGISTER_NUMBER, config.MAX_REGISTER_NUMBER + 1):
        cursor.execute("INSERT INTO jobs (num) VALUES (?)", (n,))
    db.commit()


def get_job():
    """returns a random job"""
    cursor = db.cursor()
    cursor.execute("SELECT num FROM jobs ORDER BY random() LIMIT 1")
    return cursor.fetchone()["num"]


def remove_job(num):
    """Remove the job with the given number from the queue"""
    cursor = db.cursor()
    cursor.execute("DELETE FROM jobs WHERE num=?", (num, ))
    db.commit()


def wait():
    """Wait for a random time interval"""
    t = random.triangular(config.WAIT_MIN, config.WAIT_MAX)
    time.sleep(t)


def duration_string(sec):
    """Formats a time interval to a readable string"""
    sec = float(int(sec))
    if sec > 60 * 60 * 24:
        return "%.1f days" % (sec / float(60 * 60 * 24))
    if sec > 60 * 60:
        return "%.1f hours" % (sec / float(60 * 60))
    if sec > 60:
        return "%.1f minutes" % (sec / float(60))
    return "%d seconds" % sec


def clean_spaces(t):
    """Remove multiple spaces from a string"""
    if t is None:
        return t
    return re.sub('\s+', ' ', t)


def random_ua_string():
    """Returns a randomly selected user agent strings"""
    return random.sample(config.USER_AGENTS, 1)[0]


def save_result_items(html):
    """Retrieves content from search result HTML"""
    html_parts = re.split('<tr>\s*<td\s+colspan="[0-9]"\s+class="RegPortErg_AZ">', html)
    if not len(html_parts):
        return

    cursor = db.cursor()
    count = 0
    html = ("</table>\n\n" + '<table class="scrapableTable"><tr><td class="RegPortErg_AZ">').join(html_parts)
    root = etree.fromstring(html)
    items = root.xpath('.//table[@class="scrapableTable"]')
    for table in items:
        state_field = table.xpath('.//td[@class="RegPortErg_AZ"]')[0].text_content().strip()
        # state_field = table.find("td", {"class": "RegPortErg_AZ"}).contents[0].strip()
        title_field = table.xpath('.//td[@class="RegPortErg_AZ"]/b')[0].text_content().strip()
        state_field = state_field.replace(title_field, '')
        title_field = clean_spaces(title_field)
        # title_field = clean_spaces(table.find("td", {"class": "RegPortErg_AZ"}).find("b").string.strip())
        name_field = table.xpath('.//td[@class="RegPortErg_FirmaKopf"]')[0].text_content().strip()
        # name_field = table.find("td", {"class": "RegPortErg_FirmaKopf"}).contents[0].strip().replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")
        try:
            location_field = table.xpath('.//td[@class="RegPortErg_SitzStatusKopf"]')[0].text_content().strip()
            # location_field = table.find("td", {"class": "RegPortErg_SitzStatusKopf"}).contents[0].strip()
        except IndexError:
            # printtable.find("td", {"class": "RegPortErg_SitzStatusKopf"})
            location_field = ''

        m = re.search(r"Amtsgericht\s+(.+)\s+([GHRBVPAn]{2,3})\s+([0-9]+.*)", title_field)
        court = None
        register_type = None
        idnum = None
        if m is not None:
            count += 1
            court = m.group(1).strip()
            register_type = m.group(2).strip()
            idnum = m.group(3).strip()
        else:
            sys.stderr.write("PROBLEM: title_field has no match: %s" % title_field)
        record = {
            'state': clean_spaces(state_field),
            'court': court,
            'register_type': register_type,
            'idnum': idnum,
            'name': clean_spaces(name_field),
            'location': clean_spaces(location_field),
            'last_seen': datetime.utcnow().strftime("%Y-%m-%d")
        }
        sql = """INSERT OR REPLACE INTO organizations
            (state, court, register_type, idnum, name, location, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (
            record['state'],
            record['court'],
            record['register_type'],
            record['idnum'],
            record['name'],
            record['location'],
            record['last_seen']))

    db.commit()
    return count


def get_num_results(html):
    """Returns None if result size too large or Int if size is known."""
    pattern = re.compile(r'Ihre Suche hat ([0-9]+) Treffer ergeben')
    match = pattern.search(html)
    if match is not None:
        return int(match.group(1))
    match = re.search('Trefferanzahl von 200 wurde', html)
    if match is not None:
        return None


def resolve_job(regnum):
    """
    Perform a search on handelsregister.de for one specific number
    and store the result.

    If anything fails, we immediately return, which mens the job
    will be taken care of with another attempt.
    """
    global error_1_count
    session = get_tor_session()
    wait()
    try:
        response = session.get(config.HANDELSREGISTER_URL)
    except requests.exceptions.RequestException as e:
        if args.verbose:
            sys.stderr.write("Error: %s.\n" % e)
        return

    root = etree.fromstring(response.text)
    allforms = root.xpath('.//form')
    if len(allforms) == 0:
        error_1_count += 1
        sys.stderr.write("Error 1: No form found on initial page.\n")
        if error_1_count >= config.ERROR_1_LIMIT:
            sys.stderr.write("Maximum of %d error 1 occurrences reached. Exiting.\n" % config.ERROR_1_LIMIT)
            sys.exit(1)
        if args.proxypid is not False:
            if args.verbose:
                sys.stderr.write("Restarting proxy process, sleeping %d seconds.\n" % config.SIGHUP_SLEEP)
            os.kill(args.proxypid, signal.SIGHUP)
            time.sleep(config.SIGHUP_SLEEP)
        return
    else:
        # Reset count if everything works fine
        error_1_count = 0

    form = allforms[0]
    form_data = get_form_data_from_form(form)
    form_data['registerNummer'] = str(regnum)
    form_data['ergebnisseProSeite'] = [str(config.ITEMS_PER_PAGE)]

    wait()
    try:
        response = session.post(config.BASE_URL + form.attrib['action'], data=form_data)
    except requests.exceptions.RequestException as e:
        if args.verbose:
            sys.stderr.write("Error: %s.\n" % e)
        return

    html = response.content

    num_results = get_num_results(response.text)
    if num_results is None:
        sys.stderr.write("Error 7: No results on page.\n")
        return
    if args.verbose:
        if num_results == 0:
            pass
        elif num_results == 1:
            print("1 entry found")
        else:
            print("%d entries found" % num_results)

    # while search result is too big, hit "double result" link
    while num_results is None:
        wait()
        response = session.get(url=config.BASE_URL + '/rp_web/search.do?doppelt')
        num_results = get_num_results(response.text)
    html = response.text
    num_found = save_result_items(html)
    current_page = 2
    if num_results > config.ITEMS_PER_PAGE:
        num_pages = int(floor(num_results / config.ITEMS_PER_PAGE) + 1)
        while current_page < num_pages + 1:
            wait()
            root = etree.fromstring(html)
            links = root.xpath('.//a[text()="%s"]' % current_page)
            if not links:
                if args.verbose:
                    sys.stderr.write("Error 3: Pagination link %d not found.\n" % current_page)
                return
            response = session.get(config.BASE_URL + links[0].attrib['href'])
            html = response.text
            num_found += save_result_items(html)
            current_page += 1
    if num_found != num_results:
        if args.verbose:
            sys.stderr.write("Error 2: Number of retrieved entries (%d) does not match indicated number of hits (%d).\n" % (num_found, num_results))
        return

    remove_job(j)
    return True


if __name__ == "__main__":

    # set up command line options
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-j", "--resetjobs", dest="resetjobs",
        action="store_true", default=False,
        help="Empty and recreate the job queue before starting")
    argparser.add_argument("--resetorgs", dest="resetorgs",
        action="store_true", default=False,
        help="Empty the organization table before starting (data loss!)")
    # argparser.add_argument("-s", "--socksproxy", dest="socksproxy", default="",
    #     help="Use this SOCKS5 proxy server (e. g. for use woth Tor)")
    # argparser.add_argument("-p", "--proxyport", dest="proxyport",
    #     type=int, default=config.DEFAULT_PROXY_PORT,
    #     help="Use this SOCKS5 proxy server (e. g. for use woth Tor)")
    argparser.add_argument("--proxypid", dest="proxypid",
        type=int, default=False,
        help="Send SIGUP signal to process with pid on error")
    argparser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
        help="Give verbose output")
    args = argparser.parse_args()

    db = sqlite3.connect(config.DB_PATH)
    db.row_factory = dict_factory

    # set up the database
    init()

    if args.resetorgs:
        empty_orgstable()

    if args.resetjobs:
        empty_jobqueue()

    if not has_jobs():
        create_jobs()

    # counter for certain errors
    error_1_count = 0

    starttime = time.time()
    jobs_done = 0

    # the main loop
    while has_jobs():
        c = count_jobs()
        j = get_job()

        if args.verbose:
            print("Register number: %d" % j)

        if resolve_job(j):
            jobs_done += 1

        # display some progress stats
        if args.verbose:
            if jobs_done > 0 and jobs_done % 10 == 0:
                duration = time.time() - starttime
                seconds_per_job = duration / jobs_done
                print("Resolved %d jobs in %s. %d jobs, %s remaining" % (
                    jobs_done, duration_string(duration), c, duration_string(seconds_per_job * c)))

    db.close()
