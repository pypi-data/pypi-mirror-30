"""Reader methods for mzIdentML, tsv as generated by MSGF+"""

from app.readers import xml as basereader
from app.readers import ml

P_SVM = ('percolator:score', 'percolator svm-score')
P_PSMP = ('percolator:psm_p_value', 'PSM p-value')
P_PSMQ = ('percolator:psm_q_value', 'PSM q-value')
P_PSMPEP = ('percolator:psm_pep', 'PSM-PEP')
P_PEPTIDEQ = ('percolator:peptide_q_value', 'peptide q-value')
P_PEPTIDEPEP = ('percolator:peptide_pep', 'peptide PEP')

PERCO_ORDER = [P_SVM, P_PSMP, P_PSMQ, P_PSMPEP, P_PEPTIDEQ, P_PEPTIDEPEP]
PERCO_HEADERMAP = {x[0]: x[1] for x in PERCO_ORDER}


def get_mzid_namespace(mzidfile):
    return basereader.get_namespace_from_top(mzidfile, None)


def mzid_spec_result_generator(mzidfile, namespace):
    return basereader.generate_tags_multiple_files(
        [mzidfile],
        'SpectrumIdentificationResult',
        ['cvList',
         'AnalysisSoftwareList',
         'SequenceCollection',
         'AnalysisProtocolCollection',
         'AnalysisCollection',
         ],
        namespace)


def generate_mzid_peptides(mzidfile, namespace):
    return basereader.generate_tags_multiple_files(
        [mzidfile],
        'Peptide',
        ['cvList',
         'AnalysisSoftwareList',
         'DataCollection',
         'AnalysisProtocolCollection',
         'AnalysisCollection',
         ],
        namespace)


def get_mzid_peptidedata(peptide, xmlns):
    pep_id = peptide.attrib['id']
    sequence = peptide.find('{}PeptideSequence'.format(xmlns)).text
    mods = {}
    for mod in peptide.findall('{}Modification'.format(xmlns)):
        modweight = round(float(mod.attrib['monoisotopicMassDelta']), 3)
        if modweight > 0:
            modweight = '+{}'.format(modweight)
        else:
            modweight = str(modweight)
        location = int(mod.attrib['location'])
        try:
            mods[location] += modweight
        except KeyError:
            mods[location] = modweight
    outseq = []
    for pos, aa in enumerate(sequence):
        if pos in mods:
            outseq.append('{}'.format(mods[pos]))
        outseq.append(aa)
    if pos + 1 in mods:
            outseq.append('{}'.format(mods[pos + 1]))
    return pep_id, ''.join(outseq)


def generate_mzid_spec_id_items(mzidfile, namespace, xmlns, specfn_idmap):
    specid_tag = '{0}SpectrumIdentificationItem'.format(xmlns)
    for specresult in mzid_spec_result_generator(mzidfile, namespace):
        scan = get_specresult_scan_nr(specresult)
        mzmlid = get_specresult_mzml_id(specresult)
        mzmlfn = specfn_idmap[mzmlid]
        for spec_id_item in specresult.findall(specid_tag):
            pep_id = spec_id_item.attrib['peptide_ref']
            yield (scan, mzmlfn, pep_id, spec_id_item)


def mzid_specdata_generator(mzidfile, namespace):
    return basereader.generate_tags_multiple_files(
        [mzidfile],
        'SpectraData',
        ['cvList',
         'AnalysisSoftwareList',
         'SequenceCollection',
         'AnalysisProtocolCollection',
         'AnalysisCollection',
         ],
        namespace)


def get_mzid_specfile_ids(mzidfn, namespace):
    """Returns mzid spectra data filenames and their IDs used in the
    mzIdentML file as a dict. Keys == IDs, values == fns"""
    sid_fn = {}
    for specdata in mzid_specdata_generator(mzidfn, namespace):
        sid_fn[specdata.attrib['id']] = specdata.attrib['name']
    return sid_fn


def get_specresult_scan_nr(result):
    """Returns scan nr of an mzIdentML PSM as a str. The PSM is given
    as a SpectrumIdentificationResult element."""
    return ml.get_scan_nr(result, 'spectrumID')


def get_specresult_mzml_id(specresult):
    return specresult.attrib['spectraData_ref']


def get_specidentitem_percolator_data(item, xmlns):
    """Loop through SpecIdentificationItem children. Find
    percolator data by matching to a dict lookup. Return a
    dict containing percolator data"""
    percomap = {'{0}userParam'.format(xmlns): PERCO_HEADERMAP, }
    percodata = {}
    for child in item:
        try:
            percoscore = percomap[child.tag][child.attrib['name']]
        except KeyError:
            continue
        else:
            percodata[percoscore] = child.attrib['value']
    outkeys = [y for x in list(percomap.values()) for y in list(x.values())]
    for key in outkeys:
        try:
            percodata[key]
        except KeyError:
            percodata[key] = 'NA'
    return percodata
