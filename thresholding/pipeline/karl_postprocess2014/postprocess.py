#!/usr/bin/env python
''' This takes in a non-postprocessed system-output file and an input xml file
    with queries; this script will ensure that the output conforms to spec.

    Call as follows:

    ./postprocess.py
      --queries=query_file.xml
      --infile=nonconforming_output_file
      --extractor=extractor_output_file_with_same_format_as_infile
      --thresholds=thresholds_file
      --outfile=output_filename

    and this will write to a file called "output_filename.postprocessed"

    thresholds should be a file with one line per relation type of the format
      per:alternative_names list 0.3
      per:age single 0.8
    that is, each line should be space-delimited and have three fields.
    The first should be the relation name, the second should be one of "list"
    or "single", describing whether relations are list-valued or not, and
    the last should be a confidence.

    written Karl Pichotta, August 2013 & July 2014. pichotta@cs.utexas.edu
'''

import collections
import optparse
import pprint
import re
import sys
import xml.etree.ElementTree as ET

PERSON_TYPES = [
  'per:alternate_names',
  'per:date_of_birth',
  'per:age',
  'per:country_of_birth',
  'per:stateorprovince_of_birth',
  'per:city_of_birth',
  'per:origin',
  'per:date_of_death',
  'per:country_of_death',
  'per:stateorprovince_of_death',
  'per:city_of_death',
  'per:cause_of_death',
  'per:countries_of_residence',
  'per:statesorprovinces_of_residence',
  'per:cities_of_residence',
  'per:schools_attended',
  'per:title',
  'per:employee_or_member_of',
  'per:religion',
  'per:spouse',
  'per:children',
  'per:parents',
  'per:siblings',
  'per:other_family',
  'per:charges',
]

ORG_TYPES = [
  'org:alternate_names',
  'org:political_religious_affiliation',
  'org:top_members_employees',
  'org:number_of_employees_members',
  'org:members',
  'org:member_of',
  'org:subsidiaries',
  'org:parents',
  'org:founded_by',
  'org:date_founded',
  'org:date_dissolved',
  'org:country_of_headquarters',
  'org:stateorprovince_of_headquarters',
  'org:city_of_headquarters',
  'org:shareholders',
  'org:website',
]

class Threshold(object):
  def __init__(self, rel_name, rel_type, confidence):
    assert rel_type == 'list' or rel_type == 'single', (rel_name, rel_type)
    self.rel_name = rel_name
    self.rel_type = rel_type
    self.confidence = float(confidence)

def get_thresholds_map(thresholdsfile):
  res = dict()
  for line in open(thresholdsfile, 'r'):
    line = line.strip()
    if len(line) == 0:
      continue
    fields = line.split(' ')
    assert len(fields) == 3, line
    res[fields[0]] = Threshold(*fields)
  return res


class Query(object):
  def __init__(self, qid, enttype):
    assert enttype == 'ORG' or enttype == 'PER', 'weird enttype %s' % enttype
    assert isinstance(qid, basestring)
    self.enttype = enttype
    self.qid = qid
  def __repr__(self):
    return 'query(%s,%s)' % (self.qid, self.enttype)


class OutputLine(object):
  def __init__(self, qid, slotname, runid, relprovenance, slotfiller,
               fillerprovenance, confidence):
    assert isinstance(qid, basestring)
    assert isinstance(slotname, basestring)
    assert isinstance(runid, basestring)
    assert isinstance(relprovenance, basestring)
    assert isinstance(slotfiller, basestring) or \
           (relprovenance == 'NIL' and slotfiller is None), \
           (relprovenance, slotfiller)
    assert isinstance(fillerprovenance, basestring) or \
           (relprovenance == 'NIL' and fillerprovenance is None), \
           (relprovenance, fillerprovenance)
    assert isinstance(confidence, basestring) or \
           (relprovenance == 'NIL' and confidence is None), \
           (relprovenance, confidence)
    self.qid = qid
    self.slotname = slotname
    self.runid = runid
    self.relprovenance = relprovenance
    self.slotfiller = slotfiller
    self.fillerprovenance = fillerprovenance
    self.confidence = confidence
  def __str__(self):
    if self.relprovenance== 'NIL':
      return '\t'.join([self.qid, self.slotname, self.runid,
                        self.relprovenance])
    else:
      return '\t'.join([self.qid, self.slotname, self.runid, self.relprovenance,
                        self.slotfiller, self.fillerprovenance,
                        self.confidence])
  def __repr__(self):
    return str(self)


def main(infile, outfile, queryfile, extractorfile, thresholdsfile):
  query_map = get_query_map(queryfile)
  thresholds_map = get_thresholds_map(thresholdsfile)
  outline_map = get_output_line_map(infile)
  remove_outlines_with_unknown_queries(query_map, outline_map)
  run_id = get_run_id(outline_map)
  n_outlines_0 = sum([len(x) for x in outline_map.values()])
  n_nonempty_queries_0 = len(outline_map)
  print '%d output lines in original file' % n_outlines_0
  print '====================================================='

  if extractorfile is not None:
    extractor_map = get_output_line_map(extractorfile)
    remove_outlines_with_unknown_queries(query_map, extractor_map)
    extractor_run_id = get_run_id(extractor_map)
    if extractor_run_id is not None:
      assert run_id == extractor_run_id, (run_id, extractor_run_id)

      augment_outfiles_with_extractor(extractor_map, outline_map)

      n_outlines_e = sum([len(x) for x in outline_map.values()])
      n_nonempty_queries_e = len(outline_map)
      print 'added %d backoff slotfillers (some may be removed later)' % \
            (n_outlines_e - n_outlines_0)
      print 'added backoffs for %d queries that had no slot fillers' % \
            (n_nonempty_queries_e - n_nonempty_queries_0)
      print '====================================================='
      n_outlines_0 = n_outlines_e
      n_nonempty_queries_0 = n_nonempty_queries_e

  add_nil_slotfillers(run_id, query_map, outline_map)

  n_outlines_1 = sum([len(x) for x in outline_map.values()])
  n_nonempty_queries_1 = len(outline_map)
  print 'added %d NIL slotfillers' % \
        (n_outlines_1 - n_outlines_0)
  print 'added NIL slotfillers for %d queries that had no slot fillers' % \
        (n_nonempty_queries_1 - n_nonempty_queries_0)
  print '====================================================='

  satisfy_per_relation_constraints(outline_map, thresholds_map)
  remove_nils_in_presence_of_non_nil(outline_map)

  n_outlines_2 = sum([len(x) for x in outline_map.values()])
  n_nonempty_queries_2 = len(outline_map)
  print 'removed %d slotfillers during constraint satisfaction.' % \
        (n_outlines_1 - n_outlines_2)
  print 'removed %d queries that now have no slot fillers (should be 0)' % \
        (n_nonempty_queries_1 - n_nonempty_queries_2)
  print '====================================================='

  add_nil_slotfillers(run_id, query_map, outline_map)

  n_outlines_3 = sum([len(x) for x in outline_map.values()])
  n_nonempty_queries_3 = len(outline_map)
  print 'added %d NIL slotfillers' % \
        (n_outlines_3 - n_outlines_2)
  print 'added NIL slotfillers for %d queries that had no slot fillers' % \
        (n_nonempty_queries_3 - n_nonempty_queries_2)
  print '====================================================='

  remove_invalid_relations(query_map, outline_map)

  n_outlines_4 = sum([len(x) for x in outline_map.values()])
  n_nonempty_queries_4 = len(outline_map)
  print 'removed %d slotfillers with slotnames not in spec' % \
        (n_outlines_3 - n_outlines_4)
  print 'removed %d queries that now have no slot fillers (should be 0)' % \
        (n_nonempty_queries_3 - n_nonempty_queries_4)
  print '====================================================='

  print 'writing %d output lines for %d queries.' % (n_outlines_4,
                                                     n_nonempty_queries_4)
  write_output_file(outline_map, outfile)


def write_output_file(outline_map, outfile):
  f = open('%s.postprocessed' % outfile, 'w')
  for outlines in outline_map.values():
    for li in outlines:
      f.write('%s\n' % str(li))
  f.close()

def remove_outlines_with_unknown_queries(query_map, outline_map):
  ''' this removes anything from outline_map with a query id not found in
      query_map.
  '''
  todel = [qid for qid in outline_map.keys()if qid not in query_map]
  print 'removing %d output lines for %d unknown query IDs...' % \
        (sum([len(v) for k,v in outline_map.iteritems() if k in todel]),
         len(todel))
  print '====================================================='
  for d in todel:
    del outline_map[d]

def augment_outfiles_with_extractor(extractor_map, outline_map):
  ''' adds ALL lines from extractor_map to outline_map. Note that this could
      add multiple redundant entries, and may add entries taht should be
      ignored; those must be removed later.
  '''
  for qid, extractor_outlines in extractor_map.iteritems():
    outlines = outline_map[qid]
    # slotnames present in outlines with at least one non-NIL entry:
    #slotnames = set([x.slotname for x in outlines if x.confidence is not None])
    for extractor_outline in extractor_outlines:
      outlines.append(extractor_outline)
      #if extractor_outline.confidence is not None:
      #  if extractor_outline.slotname not in slotnames:
      #    outlines.append(extractor_outline)


def remove_invalid_relations(query_map, outline_map):
  ''' (4) if we have a relation type in the submission file we give you that is
          not in that PDF, do not output it
  '''
  for qid,outlines in outline_map.items():
    query = query_map[qid]
    # list of indices
    new_outlines = []
    for i,outline in enumerate(outlines):
      if query.enttype == 'ORG':
        if outline.slotname not in ORG_TYPES:
          print 'removing slotfiller with slot name %s in query %s (%s)' % \
                (outline.slotname, query.qid, query.enttype)
        else:
          new_outlines.append(outline)
      elif query.enttype == 'PER':
        if outline.slotname not in PERSON_TYPES:
          print 'removing slotfiller with slot name %s in query %s (%s)' % \
                (outline.slotname, query.qid, query.enttype)
        else:
          new_outlines.append(outline)
    outline_map[qid] = new_outlines
  trim_outline_map_of_empty_querylists(outline_map)

def satisfy_per_relation_constraints(outline_map, thresholds_map):
  '''Ensure 'single' relations have one fact (pick the one with highest
     confidence), and that
     'list' relations don't have multiple facts wiht the same slot fill value.
  '''
  for k,outlines in outline_map.items():
    slotnames = set([x.slotname for x in outlines])
    outline_map[k] = []
    for slotname in slotnames:
      assert slotname in thresholds_map, \
          'Slot name % not found in thresholds file!' % slotname
      threshold_info = thresholds_map[slotname]
      if threshold_info.rel_type == 'list':
        # add anything in outlines with either NIL confidence or sufficiently
        # high confidence.
        for outline in [x for x in outlines if x.slotname == slotname]:
          if (outline.confidence is None or
              float(outline.confidence) > threshold_info.confidence):
            outline_map[k].append(outline)
      elif threshold_info.rel_type == 'single':
        max_outline = get_max_outline(outlines, slotname)
        if (max_outline.confidence is None or
            float(max_outline.confidence) > threshold_info.confidence):
          outline_map[k].append(max_outline)
        else:
          # it's ok if we don't add a 'NIL' entry here for the removed things,
          # because we'll call add_nil_slotfillers() after this method in main.
          pass
          #print 'removing %s' % str(max_outline)
      else:
        raise Exception('Thresholds file has weird reltype for %s' % slotname)
  remove_duplicate_outlines_from_map(outline_map, thresholds_map)

def remove_nils_in_presence_of_non_nil(outline_map):
  ''' if there's a slotname in a query with a NIL entry but there is also a
      non-NIL entry of that type, removes the nil entry
  '''
  for qid,outlines in outline_map.items():
    line_indices_by_slotname = get_line_indices_by_slotname(outlines)
    to_del = []
    for line_indices in line_indices_by_slotname.values():
      for line_index in line_indices:
        if is_conflicting_nil(line_index, line_indices, outlines):
          to_del.append(line_index)
    outline_map[qid] = [x for i,x in enumerate(outlines) if i not in to_del]

def is_conflicting_nil(line_index, lin_indices, outlines):
  this_line = outlines[line_index]
  if this_line.confidence is not None:
    return False
  return any([outlines[index].confidence is not None for index in lin_indices])


def get_line_indices_by_slotname(outlines):
  res = dict()
  for i,outline in enumerate(outlines):
    slotname = outline.slotname
    lines = res.setdefault(slotname, [])
    lines.append(i)
  return res

def remove_duplicate_outlines_from_map(outline_map, thresholds_map):
  ''' if there are outlines with the same reltype and same slotfiller, remove
  the one with lower confidence.
  '''
  for k,outlines in outline_map.items():
    slotnames = set([x.slotname for x in outlines])
    pair_to_outline_map = dict()
    for outline in outlines:
      key = (outline.slotname, outline.slotfiller)
      cur_outline = pair_to_outline_map.get(key)
      if cur_outline is None:
        pair_to_outline_map[key] = outline
      else:
        cur_confidence = cur_outline.confidence
        confidence = outline.confidence
        if confidence is not None:
          if cur_confidence is None:
            # replace:
            pair_to_outline_map[key] = outfile
          else:
            if float(confidence) > float(cur_confidence):
              #replace:
              pair_to_outline_map[key] = outfile
        else:
          # if confidence is None, we're never preferring it over whatever was
          # in there before, so do nothing.
          pass
    outline_map[k] = pair_to_outline_map.values()


def get_max_outline(outlines, slotname):
  ''' takes list of outlines; returns the outline object with slotname that
      has maximum weight value; if all have "NIL" docids, returns one
      arbitrarily
  '''
  winner = None
  for outline in outlines:
    if outline.slotname == slotname:
      if winner is None:
        winner = outline
      else:
        if outline.confidence is not None:
          if (winner.confidence is None or \
              float(outline.confidence) > float(winner.confidence)):
            winner = outline
  return winner

def trim_outline_map_of_empty_querylists(outline_map):
  ''' hopefully never does anything. this removes any entry from outline_map,
      mapping from query ids to lists of outlines, that maps to an empty list.
  '''
  to_del = [k for k,v in outline_map.iteritems() if len(v) == 0]
  for d in to_del:
    del outline_map[d]

def get_run_id(outline_map):
  for outlines in outline_map.values():
    if len(outlines) > 0:
      return outlines[0].runid

def add_nil_slotfillers(run_id, query_map, outline_map):
  ''' (1) ensure that there is a response for every slot filler that is
          required, substituting in NIL if no response is available.
      a slot filler is required for each slot type that matches the query
      entity type (ie, ORG or PER) and that is not in the ignore list.

      Destructively modifies outline_map
  '''
  for query in query_map.values():
    outlines = outline_map[query.qid]
    already_filled_slotnames = set([x.slotname for x in outlines])
    for slotname in get_slotnames(query):
      if slotname not in already_filled_slotnames:
        outlines.append(OutputLine(query.qid, slotname, run_id, 'NIL', None,
                                   None, None))

def get_slotnames(query):
  if query.enttype == 'ORG':
    return ORG_TYPES
  else:
    return PERSON_TYPES

def get_query_map(queryfile):
  ''' returns a map from query ID strings to Query objects
  '''
  root = ET.parse(open(queryfile, 'r')).getroot()
  return dict([(q.get('id'), query_node_to_object(q)) for q in root])

def get_output_line_map(infile):
  ''' takes a nonconforming system output file, returns a defaultdict from
      query IDs to OutputLine objects
  '''
  res = collections.defaultdict(list)
  for line in open(infile, 'r'):
    outline = get_output_line_obj(line)
    res[outline.qid].append(outline)
  return res

def get_output_line_obj(line):
  fields = [x.strip() for x in line.split('\t')]
  assert len(fields) == 4 or len(fields) == 7, line
  if len(fields) == 4:
    fields.extend([None, None, None])
  assert len(fields) == 7
  #del(fields[6])
  #del(fields[6])
  return OutputLine(*fields)

def query_node_to_object(querynode):
  ''' takes an ET object representing a <query> node, returns Query object
  '''
  qid = querynode.get('id')
  enttype = querynode.find('enttype').text
  return Query(qid, enttype)

def get_parser():
  p = optparse.OptionParser()
  p.add_option("--infile", action="store", type="string", dest="infile",
               help="input filename, tab-delimited KBP-output format",
               default=None)
  p.add_option("--extractor", action="store", type="string", dest="extractor",
               help="tab-delimited KBP-output fallback extractor output",
               default=None)
  p.add_option("--outfile", action="store", type="string", dest="outfile",
               help="where the postprocessed file goes, with .postprocessed " +
               "appended", default=None)
  p.add_option("--thresholds", action="store", type="string", dest="thresholds",
               help="File wth relation types and thresholds (see code for " +
               "details on format)", default=None)
  p.add_option("--queries", action="store", type="string", dest="queries",
               help="XML file containing KBP queries", default=None)
  return p

if __name__ == '__main__':
  op = get_parser()
  (opts, args) = op.parse_args()
  if (opts.infile is None or opts.outfile is None or opts.queries is None or
      opts.thresholds is None):
    sys.stderr.write('More Options required. Call with --help for info.\n')
    sys.exit(1)
  main(opts.infile, opts.outfile, opts.queries, opts.extractor, opts.thresholds)

