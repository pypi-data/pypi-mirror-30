""" 
Regenerate the models and documentation from the .csv files.
Use the standardizer and documentizer to feed data. 
""" 
import os
import re
import unidecode

from .standardizer import Documentizer
from .settings import KNOWN_SCHEDULES, METADATA_DIRECTORY
from .irs_type_utils import get_django_type, get_sqlalchemy_type

FILENAME = "django_models_auto.py"
OUTFILE = os.path.join(METADATA_DIRECTORY, FILENAME)
SOFT_TAB = '    '
BRACKET_RE = re.compile(r'\[.*?\]')


def debracket(string):
    """ Eliminate the bracketed var names in doc, line strings """
    result = re.sub(BRACKET_RE, ';', string)
    result = unidecode.unidecode(result)
    return result

def most_recent(semicolon_delimited_string):
    result = semicolon_delimited_string.split(";")[-1]
    return result

class ModelRegenerator(object):

    def __init__(self, django=True):

        self.run_django = django
        self.run_sqlalchemy = not django

        self.documentizer = Documentizer()

        self.sked_parts = self.documentizer.get_schedule_parts()
        self.variables = self.documentizer.get_variables()
        self.outfile = open(OUTFILE, 'w')
        self.table_name_dict = {}
        for var in self.variables.keys():
            vardata = self.variables[var]
            #print(vardata['db_table'])
            try:
                self.table_name_dict[vardata['db_table']].append(vardata)
            except KeyError:
                print("Table: %s" % vardata['db_table'])
                self.table_name_dict[vardata['db_table']] = [vardata]


    def write_model_top(self, sked_name, full_name, parent_sked_name, repeating_group_part=None, repeating_group_description=None):

        if self.run_django:

            result = "\n#######\n#\n# %s - %s\n" % (parent_sked_name, full_name)
            if repeating_group_description:
                result += "# Description: %s\n" % (repeating_group_description)
            if repeating_group_part:
                result += "# A repeating structure from %s\n" % (repeating_group_part)
            result += "#\n#######\n"
            ## write the start of the first group:
            result += "\nclass %s(models.Model):\n" % sked_name
            result +=  SOFT_TAB +  "object_id = models.CharField(max_length=31, blank=True, null=True, help_text=\"unique xml return id\")\n"
            result +=  SOFT_TAB +  "ein = models.CharField(max_length=15, blank=True, null=True, help_text=\"filer EIN\")\n"
            if parent_sked_name=='IRS990ScheduleK':
                # It's not clear what the max length is; Return.xsd is unclear
                result +=  SOFT_TAB +  "documentId = models.TextField(blank=True, null=True, help_text=\"documentID attribute\")"


            return result

        elif self.run_sqlalchemy:

            result = "\n#######\n#\n# %s - %s\n" % (parent_sked_name, full_name)
            if repeating_group_description:
                result += "# Description: %s\n" % (repeating_group_description)
            if repeating_group_part:
                result += "# A repeating structure from %s\n" % (repeating_group_part)
            result += "#\n#######\n"
            ## write the start of the first group:
            result += "\nclass %s(Base):\n%s__tablename__='%s'\n" % (sked_name,SOFT_TAB, sked_name)
            result +=  SOFT_TAB +  "object_id = Column(String(31))\n"
            result +=  SOFT_TAB +  "ein = Column(String(15))\n"
            if parent_sked_name=='IRS990ScheduleK':
                result +=  SOFT_TAB +  "documentId = Column(String(15))\n"

            result +=  SOFT_TAB +  "id = Column(Integer, primary_key=True)\n" # Add a primary key explicitly

            return result



    def write_top_matter(self):
        if self.run_django:
            self.outfile.write("# -*- coding: latin-1 -*-\n")   # latin1 chars keep getting in from editor        
            self.outfile.write("from django.db import models\n")
        elif self.run_sqlalchemy:
            self.outfile.write("from sqlalchemy import Column, Integer, String, BigInteger, Text, Numeric\n")
            self.outfile.write("from sqlalchemy.ext.declarative import declarative_base\n\n")
            self.outfile.write("Base = declarative_base()\n\n")


    def write_variable(self, variable):
        """
        We fallback to a text field, but we expect the types to be filled in where missing
        """
        #print("write_var %s" % variable)

        if self.run_django:
            variable_output = get_django_type(variable['irs_type'])
            if not variable_output:
                variable_output = "TextField(null=True, blank=True)"
            result =  "\n" + SOFT_TAB + "%s = models.%s" % (variable['db_name'], variable_output)

        elif self.run_sqlalchemy:
            variable_output = get_sqlalchemy_type(variable['irs_type'])
            if not variable_output:
                variable_output = "Text"
            result =  "\n" + SOFT_TAB + "%s = Column(%s)" % (variable['db_name'], variable_output)

        # add newline and documentation regardless of where it's going
        result += "\n" + SOFT_TAB + "#"
        if variable['line_number']:
            result += " Line number: %s " % most_recent(debracket(variable['line_number']))
        if variable['description']:
            result += " Description: %s " % most_recent(debracket(variable['description']))
        result += " xpath: %s \n" % variable['xpath']

        return result


    def regenerate(self):

        self.write_top_matter()

        for sked in KNOWN_SCHEDULES:
            print("Schedule %s" % sked)
            sked_parts = self.documentizer.get_parts_by_sked(sked)
            print("Num sked parts %s " % len(sked_parts))
            for part in sked_parts:
                if part['is_shell']==True:
                    continue
                    print("Skipping shell %s" % part['name'])

                model_top = self.write_model_top(part['parent_sked_part'], part['name'], part['parent_sked'], repeating_group_part=None)
                self.outfile.write(model_top)
                vars = None
                try:
                    vars = self.table_name_dict[part['parent_sked_part']]
                    print("+++ not a keyerror %s" % part['parent_sked_part'])

                except KeyError:
                    print("--- keyerror %s" % part['parent_sked_part'])
                    continue

                for var in vars:

                    self.outfile.write(self.write_variable(var))
                    pass


            groups_in_this_sked = self.documentizer.get_groups_by_sked(sked)
            for group in groups_in_this_sked:
                print("\tgroup:%s" % group['db_name'])

                model_top = self.write_model_top(group['db_name'], group['db_name'], group['parent_sked'], repeating_group_part=group['parent_sked_part'], repeating_group_description=group['description'])
                self.outfile.write(model_top)
                vars = None
                try:
                    vars = self.table_name_dict[group['db_name']]
                except KeyError:
                    print(">>>> keyerror %s" % part['parent_sked_part'])
                    continue
                for var in vars:
                    self.outfile.write(self.write_variable(var))
                    pass

        self.outfile.close()


if __name__ == '__main__':
    R = ModelRegenerator()
    R.regenerate()