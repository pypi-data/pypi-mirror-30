# coding: utf-8

import os
import io
import argparse
import logging
import subprocess
import urllib
import unicodedata
import string

from crossref.restful import Works
from lxml import etree as ET

logger = logging.getLogger(__name__)

APP_PATH = os.path.dirname(os.path.realpath(__file__))
CERMINE_PATH = '%s/deps/cermine-impl-1.13-jar-with-dependencies.jar' % APP_PATH


def cleanup_string(text):

    nfd_form = unicodedata.normalize('NFD', text)

    cleaned_str = u''.join(x for x in nfd_form if x in string.ascii_letters or x == ' ')

    return cleaned_str


def _config_logging(logging_level='INFO'):

    allowed_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.setLevel(allowed_levels.get(logging_level, 'INFO'))

    hl = logging.StreamHandler()

    hl.setFormatter(formatter)
    hl.setLevel(allowed_levels.get(logging_level, 'INFO'))

    logger.addHandler(hl)


def extract_refs(cermine_xml_file):

    with open(cermine_xml_file, 'rb') as xmlfile:
        parser = ET.XMLParser(remove_blank_text=True)
        xmlio = ET.parse(io.BytesIO(xmlfile.read()), parser)

    with open(APP_PATH + '/xsl/refs_to_txt.xsl', 'rb') as xslfile:
        xsl = ET.parse(xslfile, parser)
        transform = ET.XSLT(xsl)

    refs = transform(xmlio)

    references = []
    for line in str(refs).split('LINEBREAK'):
        try:
            metadata, ref = line.split('METADATABREAK')
        except ValueError:
            continue
        metadata = metadata.split('METADATAITEM')
        metadata.append('')  # Incluind DOI slot.
        references.append([metadata, strip_spaces(ref)])

    return references


def fecth_doi(ref):
    logger.info('Query Crossref API for DOI')
    author = cleanup_string(' '.join([ref[0], ref[1]])).strip()
    title = cleanup_string(ref[2]).strip()
    source = cleanup_string(ref[3]).strip()

    skip_query = False
    if len(author) == 0 or len(title) == 0 or len(source) == 0:
        skip_query = True

    try:
        pub_date = int(ref[4])
    except ValueError:
        skip_query = True

    if skip_query is True:
        return ''

    query = Works().query(author=author, title=title).filter(container_title=source, from_pub_date=pub_date, until_pub_date=pub_date).sort('score')
    logger.debug('Quering crossref API for DOI: %s', urllib.parse.unquote(query.url))
    doi = b''
    try:
        for item in query:
            try:
                doi = 'https://doi.org/%s' % item['DOI']
            except IndexError:
                doi = ''
            break  # Only the first result should be returned
    except:
        doi = ''

    return doi


def append_doi(refs):

    for ndx, ref in enumerate(refs, 0):
        doi = fecth_doi(ref[0])
        ref[0][5] = doi
        if len(doi) != 0:
            ref[1] = '%s DOI (%s)' % (ref[1], doi)

    return refs


def files(directory):
    directory = directory[:-1] if directory[-1] == '/' else directory

    try:
        return [('%s/%s' % (directory, i.replace('.cermxml', '.txt')), '%s/%s' % (directory, i)) for i in os.listdir(directory) if i.endswith('.cermxml')]
    except FileNotFoundError:
        logger.error('Directory not found: %s', directory)
        return []


def strip_spaces(text):
    text = text.replace(' .', '.')
    text = text.replace(' ,', ',')
    text = text.replace(' ;', ';')
    text = text.replace('« ', '«')
    text = text.replace(' »', '»')
    text = text.replace('< ', '<')
    text = text.replace(' >', '>')
    text = text.replace(' -', '-')
    text = text.replace('- ', '-')
    text = text.replace('( ', '(')
    text = text.replace(' )', ')')
    text = text.replace('[ ', '[')
    text = text.replace(' ]', ']')

    return text


def write_file(file_name, references):
    logger.info('Writing file: %s' % file_name)

    with open(file_name, 'w') as fl:
        for line in references:
            fl.write('%s\n\n\n' % line[1])


def cermine_parse(directory):
    logger.info('Running cermine parsing through directory: %s' % directory)
    env = dict(os.environ)
    subprocess.call([
        'java',
        '-cp',
        CERMINE_PATH,
        'pl.edu.icm.cermine.ContentExtractor',
        '-outputs',
        'jats',
        '-path',
        directory
    ], env=env)


def run(directory, cermine=False, doi=False):
    logger.info('Starting to scrapy refs from file in: %s', directory)

    if cermine is True:
        cermine_parse(directory)

    for refs_as_text_file, cermine_xml_file in files(directory):
        refs = extract_refs(cermine_xml_file)
        if doi is True:
            refs = append_doi(refs)
        write_file(refs_as_text_file, refs)
    logger.info('Processing Finished')


def main():

    parser = argparse.ArgumentParser(
        description='Process some Cermine files to extract references.')

    parser.add_argument(
        '--directory',
        '-d',
        default='.',
        help='Directory where the .cermxml files are stored.')

    parser.add_argument(
        '--cermine',
        '-c',
        action='store_true',
        help='Parse existing PDF files in the selected directory with Cermine.')

    parser.add_argument(
        '--doi',
        '-x',
        action='store_true',
        help='Try to retrieve DOI from crossref for each reference.')

    parser.add_argument(
        '--logging_level',
        '-l',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logggin level'
    )

    args = parser.parse_args()
    _config_logging(args.logging_level)

    run(args.directory, args.cermine, args.doi)
