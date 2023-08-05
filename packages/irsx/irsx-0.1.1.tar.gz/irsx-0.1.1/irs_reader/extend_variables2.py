import csv
from operator import itemgetter


CFILE = '/Users/jfenton/github-whitelabel/concordance/irs-efile-master-concordance-file/efiler_master_concordance.csv'
#VARFILE = '/Users/jfenton/github-whitelabel/irsreader/990-xml-reader/irs_reader/metadata/variables.csv'            
VARFILE = '/Users/jfenton/github-whitelabel/irsreader/990-xml-reader/irs_reader/metadata/variables_uniquefied.csv'            

OUTFILE = 'tobemerged.csv'

def get_year_version_numeric(versionstring):
    #print("VS %s" % versionstring)
    if versionstring:
        try:
            last_version = versionstring.strip(";").replace("V","v").split(";")[-1]
            last_version_year = int(last_version.split("v")[0])
            last_version = float(last_version.split("v")[1])

            return(last_version_year, last_version)
        except: 
            return(0,0.0)    
    else:
        return(0,0.0)

def read_concordance():
    """ returns an array of rows """
    reader = csv.DictReader(open(CFILE))
    xpath_hash = {}
    var_hash = {}
    for row in reader:
        (last_version_year, last_version) = get_year_version_numeric(row['version'])
        if last_version_year < 2009:
            continue

        try:
            xpath_hash[row['xpath']] = xpath_hash[row['xpath']] + [row]
        except KeyError:
            xpath_hash[row['xpath']] = [row]
        try:
            var_hash[row['variable_name']] = var_hash[row['variable_name']] + [row]
        except KeyError:
            var_hash[row['variable_name']] = [row]
    return {'xpath_hash':xpath_hash, 'var_hash':var_hash}

def get_varname_from_var_row(row):
    varname = row['db_table'] + '_' + row['db_name']
    return varname

def read_variables():
    reader = csv.DictReader(open(VARFILE))
    xpath_hash = {}
    var_hash = {}

    for row in reader:
        try:
            xpath_hash[row['xpath']]
        except KeyError:
            xpath_hash[row['xpath']] = [row]

        varname = get_varname_from_var_row(row)
        try:
            var_hash[varname] = var_hash[varname] + [row]
        except KeyError:
            var_hash[varname] = [row]
    return {'xpath_hash':xpath_hash, 'var_hash':var_hash}

def transform_from_jf_to_con(var):
    if var.startswith("/ReturnHeader/"):
        return "/Return" + var
    else:
        return "/Return/ReturnData" + var
    ReturnHeader



if __name__ == '__main__':

    cvars = read_concordance()
    c_xpath_hash = cvars['xpath_hash']
    c_var_hash = cvars['var_hash']

    jvars = read_variables()
    j_xpath_hash = jvars['xpath_hash']
    j_var_hash = jvars['var_hash']

    headers = ['variable_name_original', 'merge_into_variable_name','original_versions', 'merge_into_versions', 'original_xpath','merge_into_xpath']
    outfile = open(OUTFILE, 'wb')
    dw = csv.DictWriter(outfile, fieldnames=headers, extrasaction='ignore')
    dw.writeheader()


    def check_overlap(versions1, versions2):
        version_dict = {}
        for version in versions1.split(";"):
            if version:
                version_dict[version] = 1

        for version in versions2.split(";"):
            if version:
                try:
                    version_dict[version]
                    print("**version overlap %s" % version)
                    return True
                except KeyError:
                    pass
        return False


    def check_related_paths(jvar_xpath, xpath, dw):
        msg = ""
        index = 0

        msg += "\nCheck related %s " % jvar_xpath
        xpaths_from_jf = j_xpath_hash.get(jvar_xpath)
        assert len(xpaths_from_jf) == 1
        #xpaths_from_concordance = c_xpath_hash.get(xpath)
        #msg += "\nxpaths from ccd: %s" % xpaths_from_concordance

        ## get the var from each xpath
        thisvar = get_varname_from_var_row(xpaths_from_jf[0])
        jvars = j_var_hash.get(thisvar)


            
        msg += "\nfor jfvar '%s' found %s vars %s" % (thisvar, len(jvars), ["%s %s" % (i['xpath'], i['versions']) for i in jvars])

        ## check that each of the vars has the same concordance var name:
        this_related_cvars = set()
        for jvar in jvars:
            thisjfvar = get_varname_from_var_row(xpaths_from_jf[0])
            this_c_xpaths = c_xpath_hash.get(transform_from_jf_to_con(jvar['xpath']))
            #msg += "\nFound %s for %s" % ([i['variable_name'] for i in this_c_xpaths], jvar['xpath'])
            for this_c_xpath in this_c_xpaths:
                this_related_cvars.add( this_c_xpath['variable_name'] )


        if len(this_related_cvars) > 1:
            #print("\n\n\t ^^^ \nProblem with %s - %s" % (jvar_xpath, this_related_cvars))
            #print(msg)
            cvar_array = list(this_related_cvars)
            #print("cvar array length: %s -> %s" % (len(cvar_array), cvar_array))
            fullcvars = []
            for cvar in cvar_array:
                fullcvar = c_var_hash.get(cvar)[0]
                if fullcvar['version']:
                    (last_version_year, last_version) = get_year_version_numeric(fullcvar['version'])
                    fullcvar['last_version_year'] = last_version_year
                    fullcvar['last_version'] = last_version
                else:
                    fullcvar['last_version'] = 0
                    fullcvar['last_version_year'] = 0

                fullcvars.append(fullcvar)


            fullcvars_sorted = sorted(fullcvars, key=itemgetter('last_version_year', 'last_version'))
            #   headers = ['variable_name_original', 'original_versions','original_xpath', 'merge_into_variable_name', 'merge_into_versions', 'merge_into_xpath']

            versions = fullcvar['version']

            if not check_overlap(fullcvars_sorted[0]['version'], fullcvars_sorted[1]['version']):
            


                index += 1
                row = {
                     'variable_name_original':fullcvars_sorted[0]['variable_name'],
                     'original_versions':fullcvars_sorted[0]['version'],
                     'original_xpath':fullcvars_sorted[0]['xpath'],
                     'merge_into_variable_name':fullcvars_sorted[1]['variable_name'],
                     'merge_into_versions':fullcvars_sorted[1]['version'],
                     'merge_into_xpath':fullcvars_sorted[1]['xpath']
                }


                dw.writerow(row)

                return 1



        # the concordance var repping all these:
        #cvar_name = this_related_cvars.pop()
        #print("jfvar %s from %s contained in %s" % (thisjfvar, jvar['xpath'], cvar_name))
        return 0



    ## Start by going through the jvars one at a time:
    c_keyerror_count = 0
    prob = 0
    for jvar_xpath in j_xpath_hash.keys():
        xpath = transform_from_jf_to_con(jvar_xpath)

        # ignore ones that end in Grp this is a bug
        if xpath.endswith("Grp"):
            continue

        try:
            c_xpath_hash[xpath]
            result = check_related_paths(jvar_xpath, xpath, dw)
            #print("Result is %s" % result)
        except KeyError:
            #print ("KeyError %s" % xpath)
            c_keyerror_count += 1
    print("\n\nTotal keyerrors in concordance: %s" % c_keyerror_count)
    print("Total problem vars in concordance: %s" % prob)


