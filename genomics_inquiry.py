#!/usr/bin/python

"""Usinf Google Genomics API.
  * Authorization
  * creating genomics/v1 service
  * Making calls to the genomics v1 service for reads and variants
"""

import argparse
from collections import Counter
from apiclient.discovery import build
import httplib2
from oauth2client import tools
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from ensembl_request import MyApp

# For these examples, the client id and client secret are command-line arguments
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])
parser.add_argument('--client_secrets_filename',
                    default='client_secrets.json',
                    help=('The filename of a client_secrets.json file from a '
                          'Google "Client ID for native application" that '
                          'has the Genomics API enabled.'))
flags = parser.parse_args()

# Authorization
storage = Storage('credentials.dat')
credentials = storage.get()
if credentials is None or credentials.invalid:
  flow = flow_from_clientsecrets(
      flags.client_secrets_filename,
      scope='https://www.googleapis.com/auth/genomics',
      message=('You need to copy a client_secrets.json file into this '
               'directory, or pass in the --client_secrets_filename option '
               'to specify where one exists. See the README for more help.'))
  credentials = run_flow(flow, storage, flags)

# Create a genomics API service
http = httplib2.Http()
http = credentials.authorize(http)
service = build('genomics', 'v1', http=http)


# GET https://genomics.googleapis.com/v1/datasets/10473108253681171589?key={YOUR_API_KEY}

thousand_genomes_id = '10473108253681171589'  # This is the 1000 Genomes dataset ID
#sample = 'NA12872'
reference_name = '7'

# Get data from my ensmbl table
#reference_position = 140833972


try:
  test_data = MyApp().get_sequence_location()

except Exception as exc:
  print(exc)


def find_alignment_for_given_location(reference_position):

# 1. First find the read group set ID for the sample
  request = service.readgroupsets().search(
      body={'datasetIds': [thousand_genomes_id]}, #'name': sample},
      fields='readGroupSets(id)')
  read_group_sets = request.execute().get('readGroupSets', [])
  if len(read_group_sets) == 1:
    raise Exception ('Searching for %s didnt return '
                    'the right number of read group sets' %reference_name)

  read_group_set_id = read_group_sets[0]['id']

  # 2. Once we have the read group set ID,
  # lookup the reads at the position we are interested in
  request = service.reads().search(
      body={'readGroupSetIds': [read_group_set_id],
            'referenceName': reference_name,
            'start': reference_position,
            'end': reference_position + 1},
      fields='alignments(alignment,alignedSequence)')
  reads = request.execute().get('alignments', [])

  # Note: This is simplistic - the cigar should be considered for real code
  bases = [
      read['alignedSequence'][
          reference_position - int(read['alignment']['position']['position'])]
      for read in reads]

  output_1 = ''
  for base, count in Counter(bases).items():
    output_1+=('%s: %s' % (base, count))

  output_2 = ('%s bases on %s at %d are' % (reference_position, reference_name, reference_position))

  output = (output_2 +'\n' +  output_1)

  return output


for start_position_unpacked in test_data:
  start_position = start_position_unpacked[0]
  print(find_alignment_for_given_location(start_position))

