""" alterative to xml_runner that uses unparsed sked_reader """
import csv
import os

from .filing import Filing
from .standardizer import Standardizer, Documentizer, VersionDocumentizer
from .text_format_utils import debracket
#from .sked_dict_reader import SkedDictReader
from .unparsed_sked_reader import UnparsedSkedReader as SkedDictReader
# from .log_utils import configure_logging
from .type_utils import listType

from .settings import WORKING_DIRECTORY, ALLOWED_VERSIONSTRINGS, METADATA_DIRECTORY

# local override 
# 201303199349310500 is version 2012v2.1
ALLOWED_VERSIONSTRINGS = ALLOWED_VERSIONSTRINGS + ['2010v3.2', '2010v3.4', '2010v3.6', '2010v3.7', '2011v1.2', '2011v1.3', '2011v1.4', '2011v1.5', '2012v2.0', '2012v2.1', '2012v2.2', '2012v2.3', '2012v3.0']
ALLOWED_VERSIONSTRINGS = ALLOWED_VERSIONSTRINGS +  ['2009v1.0', ' 2009v1.1', ' 2009v1.2', ' 2009v1.3', ' 2009v1.4', ' 2009v1.7']

class NDC_Documentizer(object):
    """
    Returns data from NDC concordance to add for hack before datathon
    """

    def __init__(self):
        self.ndc_lines = {}
        self._make_ndc_lines()


    def _make_ndc_lines(self):
        filepath = os.path.join(METADATA_DIRECTORY, 'efiler_master_concordance.csv')
        with open(filepath, 'r') as reader_fh:
            reader = csv.DictReader(reader_fh)
            for row in reader:
                self.ndc_lines[row['xpath']] = row

    def get_ndc_line(self, xpath):
        if xpath.startswith("/IRS990"):
            xpath = "/Return/ReturnData" + xpath
        else:
            xpath = "/Return" + xpath

        try:
            return self.ndc_lines[xpath]
        except KeyError:
            return None



class UnparsedXMLRunner(object):
    """ Load a Standardizer just once while running multiple filings
        Return Filing objects with results, keyerrors set
    """
    def __init__(self, documentation=False, standardizer=None):
        self.documentation = documentation

        if documentation:
            # we need a new standardizer, ignore one if passed in
            self.standardizer = Documentizer()
        else:
            if standardizer:
                self.standardizer = standardizer
            else:
                self.standardizer = Standardizer()
        self.group_dicts = self.standardizer.get_groups()
        self.whole_filing_data = []
        self.filing_keyerr_data = []

    def get_standardizer(self):
        return self.standardizer

    def _run_schedule_k(self, sked, object_id, sked_dict, path_root, ein):
        assert sked == 'IRS990ScheduleK'
        if type(sked_dict) == listType:
            for individual_sked in sked_dict:
                doc_id = individual_sked['@documentId']
                reader = SkedDictReader(
                    self.standardizer,
                    self.group_dicts,
                    object_id,
                    ein,
                    documentId=doc_id,
                    documentation=self.documentation
                )

                result = reader.parse(individual_sked, parent_path=path_root)
                self.whole_filing_data.append({
                    'schedule_name': sked,
                    'groups': result['groups'],
                    'schedule_parts': result['schedule_parts'],
                    'csv_line_array':result['csv_line_array']
                })
        else:
            reader = SkedDictReader(
                self.standardizer,
                self.group_dicts,
                object_id,
                ein,
                documentation=self.documentation)

            result = reader.parse(sked_dict, parent_path=path_root)
            self.whole_filing_data.append({
                'schedule_name': sked,
                'groups': result['groups'],
                'schedule_parts': result['schedule_parts'],
                'csv_line_array':result['csv_line_array']

            })

    def _run_schedule(self, sked, object_id, sked_dict, ein):
        print("_run_schedule %s" % sked)
        path_root = "/" + sked
        # Only sked K (bonds) is allowed to repeat
        if sked == 'IRS990ScheduleK':
            self._run_schedule_k(sked, object_id, sked_dict, path_root, ein)

        else:
            reader = SkedDictReader(
                self.standardizer,
                self.group_dicts,
                object_id,
                ein,
                documentation=self.documentation
            )
            if sked == 'ReturnHeader990x':
                path_root = "/ReturnHeader"
            result = reader.parse(sked_dict, parent_path=path_root)
            self.whole_filing_data.append({
                'schedule_name': sked,
                'groups': result['groups'],
                'schedule_parts': result['schedule_parts'],
                'csv_line_array':result['csv_line_array']

            })

            if len(result['group_keyerrors']) > 0 or len(result['keyerrors'])> 0:
                self.filing_keyerr_data.append({
                    'schedule_name': sked,
                    'group_keyerrors':result['group_keyerrors'],
                    'keyerrors':result['keyerrors']
                })

    def run_filing(self, object_id, verbose=False):
        self.whole_filing_data = []
        self.filing_keyerr_data = []
        this_filing = Filing(object_id)
        this_filing.process(verbose=verbose)
        this_version = this_filing.get_version()
        if verbose:
            print("Filing %s is version %s" % (object_id, this_version))
        if this_version in ALLOWED_VERSIONSTRINGS:
            this_version = this_filing.get_version()
            schedules = this_filing.list_schedules()
            ein = this_filing.get_ein()
            self.whole_filing_data = []
            for sked in schedules:
                sked_dict = this_filing.get_schedule(sked)
                self._run_schedule(sked, object_id, sked_dict, ein)

            this_filing.set_result(self.whole_filing_data)
            this_filing.set_keyerrors(self.filing_keyerr_data)
            if verbose:
                if len(self.filing_keyerr_data)>0:
                    pass
                    #print("In %s keyerrors: %s" % (object_id, self.filing_keyerr_data))
                else:
                    print("No keyerrors found")
            return this_filing
        else:
            return this_filing

    def run_from_filing_obj(self, this_filing, verbose=False):  
        """
         Run from a pre-created filing object.
        """
        self.whole_filing_data = []
        self.filing_keyerr_data = []
        this_filing.process(verbose=verbose)
        object_id = this_filing.get_object_id()
        this_version = this_filing.get_version()
        if this_version in ALLOWED_VERSIONSTRINGS:
            this_version = this_filing.get_version()
            schedules = this_filing.list_schedules()
            ein = this_filing.get_ein()
            for sked in schedules:
                sked_dict = this_filing.get_schedule(sked)
                self._run_schedule(sked, object_id, sked_dict, ein)
            this_filing.set_result(self.whole_filing_data)
            this_filing.set_keyerrors(self.filing_keyerr_data)
            return this_filing
        else:
            return this_filing


    def run_sked(self, object_id, sked, verbose=False):
        """
        sked is the proper name of the schedule:
        IRS990, IRS990EZ, IRS990PF, IRS990ScheduleA, etc.
        """
        self.whole_filing_data = []
        self.filing_keyerr_data = []
        this_filing = Filing(object_id)
        this_filing.process(verbose=verbose)
        this_version = this_filing.get_version()
        if this_version in ALLOWED_VERSIONSTRINGS:
            this_version = this_filing.get_version()
            ein = this_filing.get_ein()
            sked_dict = this_filing.get_schedule(sked)
            self._run_schedule(sked, object_id, sked_dict, ein)

            this_filing.set_result(self.whole_filing_data)
            this_filing.set_csv_result(self.csv_line_array)
            this_filing.set_keyerrors(self.filing_keyerr_data)
            return this_filing
        else:
            return this_filing

if __name__ == '__main__':

    #test_set = ['201511319349301766', '201403179349305520', '201542189349301214', '201530449349302683', '201503159349304000', '201530419349300113', '201613209349309896', '201603549349300640', '201503289349300110', '201623209349310262', '201613509349300606', '201543589349300104', '201633519349301053', '201633579349300718', '201613199349306136', '201533139349300208', '201603149349302590', '201532299349304633', '201603179349200000', '201643199349302309', '201623169349100822', '201543169349101804', '201613139349100776', '201630679349300208', '201621349349101032']
    
    test_set = ['201511319349301766', '201403179349305520', '201542189349301214', '201530449349302683', '201503159349304000', '201530419349300113', '201613209349309896', '201603549349300640', '201503289349300110', '201623209349310262', '201613509349300606', '201543589349300104', '201633519349301053', '201633579349300718', '201613199349306136', '201533139349300208', '201603149349302590', '201532299349304633', '201603179349200000', '201643199349302309', '201623169349100822', '201543169349101804', '201613139349100776', '201630679349300208', '201621349349101032', '201123159349301107', '201113349349300206', '201143189349307054', '201103139349300915', '201133199349100833', '201123199349203627', '201533209349304768', '201533179349307818', '201513089349301656', '201533189349300608', '201103159349304200', '201123129349301977', '201513359349100306', '201630529349200103', '201602259349201355', '201601369349200905']
    #test_set = ['201613509349300606']
    vd = VersionDocumentizer()
    #object_id = '201303199349310500' # v2012v2.1
    #object_id = '201113139349301336' # 2010v3.2
    #object_id = '201533089349301428'  #multiple schedule K's
    #test_set = ['201123159349301107', '201113349349300206', '201143189349307054', '201103139349300915', '201133199349100833', '201123199349203627', '201533209349304768', '201533179349307818', '201513089349301656', '201533189349300608', '201103159349304200', '201123129349301977', '201513359349100306', '201630529349200103', '201602259349201355', '201601369349200905']
    xml_runner = UnparsedXMLRunner(documentation=True)
    standardizer = xml_runner.get_standardizer()
    nd = NDC_Documentizer()

    for object_id in test_set:
        parsed_filing = xml_runner.run_filing(
                    object_id,
                    verbose=True
                )

        #fieldnames = ['location_code', 'value', 'is_error', 'error_description', 'description', 'line_number', 'xpath', 'variable_name', 'in_group', 'group_name', 'group_index']
        fieldnames = ['value', 'description', 'line_number', 'xpath', 'in_group', 'group_index']

        outfilename = '/Users/jfenton/github-whitelabel/validata/createdcsvs/' + object_id + ".csv"
        outfile = open(outfilename, 'w') # 'wb' python 2?
        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames,
            delimiter=',',
            quotechar='"',
            lineterminator='\n',
            quoting=csv.QUOTE_MINIMAL,
            extrasaction='ignore'
        )
        writer.writeheader()

        results = parsed_filing.get_result()

        for result in results:
            for this_result in result['csv_line_array']:


                raw_line_num = vd.get_line_number(this_result['xpath'], parsed_filing.get_version())
                this_result['line_number'] =  debracket(raw_line_num)

                raw_description = vd.get_description(this_result['xpath'], parsed_filing.get_version())
                this_result['description'] =  debracket(raw_description)

                nd_result = nd.get_ndc_line(this_result['xpath'])
                if nd_result:
                    this_result['location_code'] = nd_result['location_code']
                    this_result['variable_name'] = nd_result['variable_name']

                if this_result['group_index']:
                    if this_result['group_index'] > 0:
                        this_result['is_error'] = 'DO NOT VALIDATE'
                        this_result['error_description'] = 'DO NOT VALIDATE'

                writer.writerow(this_result)

