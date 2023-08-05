
import os, sys, csv, time

class FormatHelper(object):

    def __init__(self):
        pass

    def _compute_transitiongroup_from_key(self, key):
        """ Transforms an input chromatogram id to a string of [DECOY]_xx/yy

        Possible Input Formats:

        i) [DECOY_]id_xx/yy_zz
        ii) [DECOY_]id_xx_yy

        Where the DECOY_ prefix is optional, xx is the sequence and yy is the
        charge. zz is an additional, optional annotation.

        We want to return only [DECOY]_xx/yy (ensuring that decoys get a
        different identifier than targets).
        """
        components = key.split("_")
        trgr_nr = str(components[1])
        if components[0].startswith("DECOY"):
            trgr_nr = "DECOY_" + str(components[2])

        # Format ii) (second component doesnt contain a slash)
        if trgr_nr.find("/") == -1:
            trgr_nr += "/" + str(components[-1])

        return trgr_nr

    def _compute_transitiongroup_from_precursor(self, precursor):
        """ Transforms an input precursor to a string of [DECOY]_xx/yy
        """
        charge = "0"
        if precursor.has_key("charge"):
            charge = str(precursor["charge"])

        # Check if there is a user-parameter describing the peptide sequence
        # which would allow us to asseble the SEQ/ch pair.
        if precursor.has_key("userParams"):
            if precursor["userParams"].has_key("peptide_sequence"):
                return precursor["userParams"]["peptide_sequence"] + "/" + charge
            if precursor["userParams"].has_key("PeptideSequence"):
                return precursor["userParams"]["PeptideSequence"] + "/" + charge

        if precursor.has_key("mz"):
            # TODO have some reproducible rounding here
            return str(precursor["mz"]) + "GENERIC/" + charge

    def _has_openswath_format(self, key):
        """
        Checks whether the given key follows a specific format which
        could allow to map chromatograms to precursors without reading the
        whole file.

        Namely, the format is expected to be [DECOY_]\d*_.*_.* from which one
        can infer that it is openswath format.

        possible inputs: 
            DECOY_44736_NVEVIEDDKQGIIR/2_y12
            1002781_TGLC(UniMod:4)QFEDAFTQLSGATPIGAGIDAR_3
        """

        # It is probably not the openswath format with 3 or more entries
        if len(key.split("_")) > 4:
            return False

        print(key)
        if len(key.split("_")) >= 3:
            components = key.split("_")
            # print "split into components", components
            if components[0].startswith("DECOY"):
                components = components[1:]

            # Exactly 3 components are needed: id, sequence, charge/ion qualifier
            if len(components) != 3:
                return False

            charge_is_qualifier = True
            trgr_nr = components[0]
            sequence = components[1]
            if len(sequence.split("/")) > 1:
                sequence = sequence.split("/")[0]
                charge_is_qualifier = False
            qualifier = components[2]

            if not self._is_number(trgr_nr):
                print ("Format determination: Could not convert", trgr_nr, "to int.")
                return False
            if self._is_number(sequence):
                print ("Format determination: Does not look like sequence", sequence)
                return False
            elif sequence.find("UniMod") != -1:
                # Looks like sequence, has UniMod tag in it, should be ok
                pass
            else:
                pass
                # valid = re.match('^[A-Z]+$', sequence) is not None
                # if not valid:
                #     print "Format determination: Does not look like sequence", sequence
                #     return False

            if charge_is_qualifier:
                if not self._is_number(qualifier):
                    print ("Format determination: Does not look like number", qualifier)
                    return False
            elif self._is_number(qualifier):
                print ("Format determination: Does look like number", qualifier)
                return False
            
            return True

        # default is false
        print ("default is false")
        return False

    def _is_number(self, n):
        # Sequence should not be a number
        try:
            x = float(n)
            return True
        except ValueError:
            return False

class SqlDataAccess(object):

    def __init__(self, filename):
        import sqlite3
        self.conn = sqlite3.connect(filename)
        self.c = self.conn.cursor()

    def getDataForChromatograms(self, ids):
        """
        Get data from multiple chromatograms chromatogram

        - compression is one of 0 = no, 1 = zlib, 2 = np-linear, 3 = np-slof, 4 = np-pic, 5 = np-linear + zlib, 6 = np-slof + zlib, 7 = np-pic + zlib
        - data_type is one of 0 = mz, 1 = int, 2 = rt
        - data contains the raw (blob) data for a single data array
        """

        stmt ="SELECT CHROMATOGRAM_ID, COMPRESSION, DATA_TYPE, DATA FROM DATA WHERE CHROMATOGRAM_ID IN ("
        for myid in ids:
            stmt += str(myid) + ","
        stmt = stmt[:-1]
        stmt += ")"

        data = [row for row in self.c.execute(stmt)]
        tmpres = self._returnDataForChromatogram(data)

        res = []
        for myid in ids:
            res.append( tmpres[myid] )
        return res

    def getDataForChromatogram(self, myid):
        """
        Get data from a single chromatogram

        - compression is one of 0 = no, 1 = zlib, 2 = np-linear, 3 = np-slof, 4 = np-pic, 5 = np-linear + zlib, 6 = np-slof + zlib, 7 = np-pic + zlib
        - data_type is one of 0 = mz, 1 = int, 2 = rt
        - data contains the raw (blob) data for a single data array
        """

        data = [row for row in self.c.execute("SELECT CHROMATOGRAM_ID, COMPRESSION, DATA_TYPE, DATA FROM DATA WHERE CHROMATOGRAM_ID = %s" % myid )]
        return self._returnDataForChromatogram(data).values()[0]

    def getDataForChromatogramFromNativeId(self, native_id):
        """
        Get data from a single chromatogram

        - compression is one of 0 = no, 1 = zlib, 2 = np-linear, 3 = np-slof, 4 = np-pic, 5 = np-linear + zlib, 6 = np-slof + zlib, 7 = np-pic + zlib
        - data_type is one of 0 = mz, 1 = int, 2 = rt
        - data contains the raw (blob) data for a single data array
        """

        data = [row for row in self.c.execute("SELECT CHROMATOGRAM_ID, COMPRESSION, DATA_TYPE, DATA FROM DATA INNER JOIN CHROMATOGRAM ON CHROMATOGRAM.ID = CHROMATOGRAM_ID WHERE NATIVE_ID = %s" % native_id )]
        return self._returnDataForChromatogram(data).values()[0]

    def _returnDataForChromatogram(self, data):
        import PyMSNumpress
        import zlib

        # prepare result
        chr_ids = set([chr_id for chr_id, compr, data_type, d in data] )
        res = { chr_id : [None, None] for chr_id in chr_ids }

        rt_array = []
        intensity_array = []
        for chr_id, compr, data_type, d in data:
            result = []
            if compr == 5:
                tmp = [ord(q) for q in zlib.decompress(d)]
                PyMSNumpress.decodeLinear(tmp, result)
            if compr == 6:
                tmp = [ord(q) for q in zlib.decompress(d)]
                PyMSNumpress.decodeSlof(tmp, result)

            if data_type == 1:
                res[chr_id][1] = result
            elif data_type == 2:
                res[chr_id][0] = result
            else:
                raise Exception("Only expected RT or Intensity data for chromatogram")

        return res

class SqlSwathRun():
    """Data Model for a single sqMass file.

    TODO: each file may contain multiple runs!

    Attributes:
        runid: Current run id

    Private Attributes:
       - _run:        A :class:`.SqlDataAccess` object
       - _filename:   Original filename
       - _basename:   Original filename basename
       - _precursor_mapping:   Dictionary { FullPrecursorName : [transition_id, transition_id] }
       - _sequences_mapping:   Dictionary { StrippedSequence : [FullPrecursorName, FullPrecursorName]}

    """

    def __init__(self, runid, filename, load_in_memory=False, precursor_mapping = None, sequences_mapping = None, protein_mapping = {}):
        # print "runid ", runid
        if runid is not None:
            assert len(runid) == 1

        self.runid = runid[0] # TODO 
        self._filename = filename
        self._basename = os.path.basename(filename)

        self._range_mapping = {}
        self._score_mapping = {}
        self._intensity_mapping = {}
        self._assay_mapping = {}

        self._run = SqlDataAccess(filename)

        # Map which holds the relationship between a precursor and its
        # corresponding chromatogram id (transition id).
        self._precursor_mapping = {}
        # Map which holds the relationship between a sequence and its precursors
        self._sequences_mapping = {}
        # Map which holds the relationship between a protein and its sequences 
        self._protein_mapping = protein_mapping
        # Map which holds the relationship between a chromatogram and its id
        self._id_mapping = {}

        self._in_memory = False

        self._id_mapping = dict(self._get_id_mapping())

        if not precursor_mapping is None and not len(precursor_mapping) == 0 \
          and not sequences_mapping is None and not len(sequences_mapping) == 0:
            self._precursor_mapping = precursor_mapping
            self._sequences_mapping = sequences_mapping
            self._id_mapping = dict(self._get_id_mapping())
        else:
            pass
            # self._group_by_precursor()
            # self._group_precursors_by_sequence()

    def get_transitions_for_precursor_display(self, precursor):

        if not self._precursor_mapping.has_key(str(precursor)):
            return [ "NA" ]

        transitions = []
        for chrom_id in self._precursor_mapping[str(precursor)]:
            transitions.append(chrom_id)
        return transitions

    def get_range_data(self, precursor):
        return self._range_mapping.get(precursor, [ [0,0] ])

    def get_assay_data(self, precursor):
        r = self._assay_mapping.get(precursor, None)

        if r is not None and len(r) > 0:
            return r[0]
        return None

    def get_score_data(self, precursor):
        r = self._score_mapping.get(precursor, None)

        if r is not None and len(r) > 0:
            return r[0]
        return None

    def get_intensity_data(self, precursor):
        r = self._intensity_mapping.get(precursor, None)

        if r is not None and len(r) > 0:
            return r[0]
        return None

    #
    ## Initialization
    #

    def _get_id_mapping(self):
        """
        Map SQL ids to transition group identifiers
        """

        import sqlite3
        conn = sqlite3.connect(self._filename)
        c = conn.cursor()

        id_mapping = [row for row in c.execute("SELECT NATIVE_ID, ID FROM CHROMATOGRAM" )]

        return id_mapping

    def _group_by_precursor(self):
        """
        Populate the mapping between precursors and the chromatogram ids.

        The precursor is of type 'PEPT[xx]IDE/3' with an optional (DECOY) tag
        in front. Different modifications will generate different precursors,
        but not different charge states.
        """

        id_mapping = self._get_id_mapping()
        # TODO: could also be done in SQL
        self._id_mapping = dict(id_mapping)

        openswath_format = self._has_openswath_format([m[0] for m in id_mapping])

        result = {}
        ## do we care?? TODO
        if not openswath_format and False:
            raise Exception("Could not parse chromatogram ids ... ")

        f = FormatHelper()
        for key, myid in id_mapping:
            trgr_nr = f._compute_transitiongroup_from_key(key)
            tmp = self._precursor_mapping.get(trgr_nr, [])
            tmp.append(key)
            self._precursor_mapping[trgr_nr] = tmp

    def _has_openswath_format(self, keys):
        f = FormatHelper()
        return all([ f._has_openswath_format(k) for k in keys] )

    def _group_precursors_by_sequence(self):
        """Group together precursors with the same charge state"""
        self._sequences_mapping = {}
        for precursor in self._precursor_mapping.keys():
            seq = precursor.split("/")[0]
            tmp = self._sequences_mapping.get(seq, [])
            tmp.append(precursor)
            self._sequences_mapping[seq] = tmp

    #
    ## Getters (data) -> see ChromatogramTransition.getData
    #

    def getTransitionCount(self):
        """
        Get total number of transitions 
        """
        return sum([ len(v) for v in self._precursor_mapping.values()])

    def get_data_for_precursor(self, precursor):
        """Retrieve raw data for a specific precursor - data will be as list of
        pairs (timearray, intensityarray)"""

        if not self._precursor_mapping.has_key(str(precursor)):
            return [ [ [0], [0] ] ]

        transitions = []
        sql_ids = []
        for chrom_id in self._precursor_mapping[str(precursor)]:
            sql_id = self._id_mapping[ chrom_id ]
            sql_ids.append(sql_id)
        transitions = self._run.getDataForChromatograms(sql_ids)
        return transitions

    def getChromatogram(self, transition_id):
        chromatogram = self.get_data_for_transition(transition_id)
        if chromatogram is None:
            return None

        class Chromatogram: pass
        c = Chromatogram()
        c.peaks = [ (rt, inten) for (rt, inten) in zip( chromatogram[0][0], chromatogram[0][1] ) ]
        return c

    def get_data_for_transition(self, transition_id):
        """
        Retrieve raw data for a specific transition
        """

        if transition_id in self._id_mapping:
            return [self._run.getDataForChromatogram(self._id_mapping[transition_id])]
        else:
            print ("Warning: Found chromatogram identifier '%s' that does not map to any chromatogram in the data." % transition_id)
            print ("Please check your input data")
            # print (self._id_mapping)

    def get_id(self):
        return self._basename

    #
    ## Getters (info)
    #
    def get_transitions_for_precursor(self, precursor):
        """
        Return the transition names for a specific precursor
        """
        return self._precursor_mapping.get(str(precursor), [])

    def get_sequence_for_protein(self, protein):
        return self._protein_mapping.get(protein, [])

    def get_precursors_for_sequence(self, sequence):
        """
        Get all precursors mapping to one stripped sequence
        """
        return self._sequences_mapping.get(sequence, [])

    def get_all_precursor_ids(self):
        """
        Get all precursor ids (full sequence + charge)
        """
        return self._precursor_mapping.keys()

    def get_all_peptide_sequences(self):
        """
        Get all (stripped) sequences
        """
        return self._sequences_mapping.keys()

    def get_all_proteins(self):
        return self._protein_mapping

    # 
    ## Data manipulation
    #
    def remove_precursors(self, toremove):
        """ Remove a set of precursors from the run (this can be done to filter
        down the list of precursors to display).
        """
        for key in toremove:
            self._precursor_mapping.pop(key, None)
        self._group_precursors_by_sequence()

        # Re-initialize self to produce correct mapping
        ## self._initialize()

    def add_peakgroup_data(self, precursor_id, leftWidth, rightWidth, fdrscore, intensity, assay_rt):

        tmp = self._range_mapping.get(precursor_id, [])
        tmp.append( [leftWidth, rightWidth ] )
        self._range_mapping[precursor_id] = tmp

        tmp = self._score_mapping.get(precursor_id, [])
        tmp.append(fdrscore)
        self._score_mapping[precursor_id] = tmp

        tmp = self._intensity_mapping.get(precursor_id, [])
        tmp.append(intensity)
        self._intensity_mapping[precursor_id] = tmp

        tmp = self._assay_mapping.get(precursor_id, [])
        tmp.append(assay_rt)
        self._assay_mapping[precursor_id] = tmp
