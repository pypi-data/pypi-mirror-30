import os
import io
import argparse
import logging
import subprocess

from lxml import etree as ET

logger = logging.getLogger(__name__)

APP_PATH = os.path.dirname(os.path.realpath(__file__))
CERMINE_PATH = '%s/deps/cermine-impl-1.13-jar-with-dependencies.jar' % APP_PATH


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

    return str(refs).encode('utf-8')


def files(directory):

    try:
        return [('%s/%s' % (directory, i.replace('.cermxml', '.txt')), '%s/%s' % (directory, i)) for i in os.listdir(directory) if i.endswith('.cermxml')]
    except FileNotFoundError:
        logger.error('Directory not found: %s', directory)
        return []


def strip_spaces(text):
    text = text.replace(b'LINEBREAK', b'\n\n\n')
    text = text.replace(b' .', b'.')
    text = text.replace(b' ,', b',')
    text = text.replace(b' ;', b';')
    text = text.replace('« '.encode('utf-8'), '«'.encode('utf-8'))
    text = text.replace(' »'.encode('utf-8'), '»'.encode('utf-8'))
    text = text.replace(b' -', b'-')
    text = text.replace(b'- ', b'-')
    text = text.replace(b'( ', b'(')
    text = text.replace(b' )', b')')
    text = text.replace(b'[ ', b'[')
    text = text.replace(b' ]', b']')

    return text


def write_file(file_name, text):

    with open(file_name, 'wb') as fl:
        logger.info('Writing file: %s' % file_name)
        fl.write(text)


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
    logger.info('Cermine parsing finished')


def run(directory, cermine):
    logger.info('Starting to scrapy refs from file in: %s', directory)

    if cermine is True:
        cermine_parse(directory)

    for refs_as_text_file, cermine_xml_file in files(directory):
        refs_as_text = strip_spaces(extract_refs(cermine_xml_file))
        write_file(refs_as_text_file, refs_as_text)
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
        '--logging_level',
        '-l',
        default='DEBUG',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logggin level'
    )

    args = parser.parse_args()
    _config_logging(args.logging_level)

    args.directory = args.directory[:-1] if args.directory[-1] == '/' else args.directory
    run(args.directory, args.cermine)
