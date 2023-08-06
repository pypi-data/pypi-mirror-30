from os.path import join
import re
import numpy as np

from .exceptions import *

class MesaData:

    """Structure containing data from a Mesa output file.

    Reads a profile or history output file from mesa. Assumes a file with
    the following structure:

    - line 1: header names
    - line 2: header data
    - line 3: blank
    - line 4: main data names
    - line 5: main data values

    This structure can be altered by using the class methods
    MesaData.set_header_rows and MesaData.set_data_rows.

    Parameters
    ----------
    file_name : str, optional
        File name to be read in. Default is 'LOGS/history.data', which works
        for scripts in a standard work directory with a standard logs directory
        for accessing the history data.

    Attributes
    ----------
    file_name : str
        Path to file from which the data is read.
    bulk_data : numpy.ndarray
        The main data (line 6 and below) in record array format. Primarily
        accessed via the `data` method.
    bulk_names : tuple of str
        Tuple of all available data column names that are valid inputs for
        `data`. Essentially the column names in line 4 of `file_name`.
    header_data : dict
        Header data (line 2 of `file_name`) in dict format
    header_names : list of str
        List of all available header column names that are valid inputs for
        `header`. Essentially the column names in line 1 of `file_name`.
    """

    header_names_line = 2
    bulk_names_line = 6

    @classmethod
    def set_header_name_line(cls, name_line=2):
        cls.header_names_line = name_line

    @classmethod
    def set_data_rows(cls, name_line=6):
        cls.bulk_names_line = name_line

    def __init__(self, file_name=join('.', 'LOGS', 'history.data'),
                 file_type=None):
        """Make a MesaData object from a Mesa output file.

        Reads a profile or history output file from mesa. Assumes a file with
        the following structure:

        line 1: header names
        line 2: header data
        line 3: blank
        line 4: main data names
        line 5: main data values

        This structure can be altered by using the class methods
        `MesaData.set_header_rows` and `MesaData.set_data_rows`.

        Parameters
        ----------
        file_name : str, optional
            File name to be read in. Default is 'LOGS/history.data'

        file_type : str, optional
            File type of file to be read.  Default is None, which will
            auto-detect the type based on file extension.  Valid values are
            'model' (a saved model) and 'log' (history or profile output).
        """
        self.file_name = file_name
        self.file_type = file_type
        self.bulk_data = None
        self.bulk_names = None
        self.header_data = None
        self.header_names = None
        self.read_data()

    def read_data(self):
        """Decide if data file is log output or a model, then load the data

        Log files and models are structured differently, so different methods
        will be required to read in each. This method figures out which one
        should be called and then punts to that method.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # attempt auto-detection of file_type (if not supplied)
        if self.file_type is None:
            if self.file_name.endswith((".data", ".log")):
                self.file_type = 'log'
            elif self.file_name.endswith(".mod"):
                self.file_type = 'model'
            else:
                raise UnknownFileTypeError("Unknown file type for file {}".format(
                    self.file_name))

        # punt to reading method appropriate for each file type
        if self.file_type == 'model':
            self.read_model_data()
        elif self.file_type == 'log':
            self.read_log_data()
        else:
            raise UnknownFileTypeError("Unknown file type {}".format(
                self.file_type))

    def read_log_data(self):
        """Reads in or update data from the original log (.data or .log) file.

        This re-reads the data from the originally-provided file name. Mostly
        useful if the data file has been changed since it was first read in or
        if the class methods MesaData.set_header_rows or MesaData.set_data_rows
        have been used to alter how the data have been read in.

        Returns
        -------
        None
        """
        self.bulk_data = np.genfromtxt(
            self.file_name, skip_header=MesaData.bulk_names_line - 1,
            names=True, dtype=None)
        self.bulk_names = self.bulk_data.dtype.names
        header_data = []
        with open(self.file_name) as f:
            for i, line in enumerate(f):
                if i == MesaData.header_names_line - 1:
                    self.header_names = line.split()
                elif i == MesaData.header_names_line:
                    header_data = [eval(datum) for datum in line.split()]
                elif i > MesaData.header_names_line:
                    break
        self.header_data = dict(zip(self.header_names, header_data))
        self.remove_backups()

    def read_model_data(self):
        """Read in or update data from the original model (.mod) file.

        Models are assumed to have the following structure:

        - lines of comments and otherwise [considered] useless information
        - one or more blank line
        - Header information (names and values separated by one or more space, one per line)
        - one or more blank lines
        - ONE line of column names (strings separated by one or more spaces)
        - many lines of bulk data (integer followed by many doubles, separated by one or more spaces)
        - a blank line
        - everything else is ignored

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        def pythonize_number(num_string):
            """Convert fotran double [string] to python readable number [string].

            Converts numbers with exponential notation of D+, D-, d+, or d-
            to E+ or E- so that a python interpreter properly understands them.
            Leaves all other strings the untouched.
            """
            num_string = re.sub('(d|D)\+', 'E+', num_string)
            return re.sub('(d|D)-', 'E-', num_string)

        with open(self.file_name, 'r') as f:
            lines = f.readlines()
        # Walk through file until we get to the last blank line, saving
        # relevant data as we go.
        blank_line_matcher = re.compile('^\s*$')
        i = 0
        found_blank_line = False
        while not found_blank_line:
            i += 1
            found_blank_line = (blank_line_matcher.match(lines[i]) is not None)
        # now on blank line 1, advance through one or more lines to get to
        # header data
        while found_blank_line:
            i += 1
            found_blank_line = (blank_line_matcher.match(lines[i]) is not None)
        # now done with blank lines and on to header data
        self.header_names = []
        self.header_data = {}
        while not found_blank_line:
            name, val = [datum.strip() for datum in lines[i].split()]
            self.header_data[name] = eval(pythonize_number(val))
            self.header_names.append(name)
            i += 1
            found_blank_line = (blank_line_matcher.match(lines[i]) is not None)
        # now on blank line 2, advance until we get to column names
        while found_blank_line:
            i += 1
            found_blank_line = (blank_line_matcher.match(lines[i]) is not None)
        self.bulk_names = ['zone']
        self.bulk_names += lines[i].split()
        i += 1
        self.bulk_data = {}
        temp_data = []
        found_blank_line = False
        while not found_blank_line:
            temp_data.append([eval(pythonize_number(datum)) for datum in
                              lines[i].split()])
            i += 1
            found_blank_line = (blank_line_matcher.match(lines[i]) is not None)
        temp_data = np.array(temp_data).T
        for i in range(len(self.bulk_names)):
            self.bulk_data[self.bulk_names[i]] = temp_data[i]
            # self.bulk_data = np.array(temp_data, names=self.bulk_names)

    def data(self, key):
        """Accesses the data and returns a numpy array with the appropriate data

        Accepts a string key, like star_age (for history files) or logRho (for
        profile files) and returns the corresponding numpy array of data for
        that data type. Can also just use the shorthand methods that have the
        same name of the key.

        Parameters
        ----------
        key : str
            Name of data. Must match a main data title in the source file. If it
            is not a data title, will first check for a log_[`key`] or ln[`key`]
            version and return an exponentiated version of that data. If `key`
            looks like a `log_*` or `ln_*` name, searches for a linear
            quantity of the appropriate name and returns the expected
            logarithmic quantity.

        Returns
        -------
        numpy.ndarray
            Array of values for data corresponding to key at various time steps
            (history) or grid points (profile or model).

        Raises
        ------
        KeyError
            If `key` is an invalid key (i.e. not in `self.bulk_names` and no
            fallback logarithmic or linear quantities found)

        Examples
        --------
        You can either call `data` explicitly with `key` as an argument, or get
        the same result by calling it implicitly by treating `key` as an
        attribute.

        >>> m = MesaData()
        >>> x = m.data('star_age')
        >>> y = m.star_age
        >>> x == y
        True

        In this case, x and y are the same because the non-existent method
        MesaData.star_age will direct to to the corresponding MesaData.data
        call.

        Even data categories that are not in the file may still work.
        Specifically, if a linear quantity is available, but the log is asked
        for, the linear quantity will be first log-ified and then returned:

        >>> m = MesaData()
        >>> m.in_data('L')
        False
        >>> m.in_data('log_L')
        True
        >>> x = m.L
        >>> y = 10**m.log_L
        >>> x == y
        True

        Here, `data` was called implicitly with an argument of 'L' to get `x`.
        Since `'L'` was an invalid data category, it first looked to see if a
        logarithmic version existed. Indeed, `'log_L'` was present, so it was
        retrieved, exponentiated, and returned.
        """
        if self.in_data(key):
            return self.bulk_data[key]
        elif self._log_version(key) is not None:
            return 10**self.bulk_data[self._log_version(key)]
        elif self._ln_version(key) is not None:
            return np.exp(self.bulk_data[self._ln_version(key)])
        elif self._exp10_version(key) is not None:
            return np.log10(self.bulk_data[self._exp10_version(key)])
        elif self._exp_version(key) is not None:
            return np.log(self.bulk_data[self._exp_version(key)])
        else:
            raise KeyError("'" + str(key) + "' is not a valid data type.")

    def header(self, key):
        """Accesses the header, returning a scalar the appropriate data

        Accepts a string key, like version_number and returns the corresponding
        datum for that key. Can also just use the shorthand
        methods that have the same name of the key.

        Parameters
        ----------
        key : string
            Name of data. Must match a main data title in the source file.

        Returns
        -------
        int or str or float
            Returns whatever value is below the corresponding key in the header
            lines of the source file.

        Raises
        ------
        KeyError
            If `key` is an invalid key (i.e. not in `self.header_names`)

        Examples
        --------
        Can call `header` explicitly with `key` as argument or implicitly,
        treating `key` as an attribute.

        In this case, x and y are the same because the non-existent method
        MesaData.version_number will first see if it can call
        MesaData.data('version_number'). Then, realizing that this doesn't make
        sense, it will instead call MesaData.header('version_number')

        >>> m = MesaData()
        >>> x = m.data('version_number')
        >>> y = m.version_number
        >>> x == y
        True
        """

        if not self.in_header(key):
            raise KeyError("'" + str(key) + "' is not a valid header name.")
        return self.header_data[key]

    def is_history(self):
        """Determine if the source file is a history file

        Checks if 'model_number' is a valid key for self.data. If it is, return
        True. Otherwise return False. This is used in determining whether or not
        to cleanse the file of backups and restarts in the MesaData.read_data.

        Returns
        -------
        bool
            True if file is a history file, otherwise False
        """
        return 'model_number' in self.bulk_names

    def in_header(self, key):
        """Determine if `key` is an available header data category.

        Checks if string `key` is a valid argument of MesaData.header. Returns
        True if it is, otherwise False

        Parameters
        ----------
        key : str
            Candidate string for accessing header data. This is what you want
            to be able to use as an argument of `MesaData.header`.

        Returns
        -------
        bool
            True if `key` is a valid input to MesaData.header, otherwise False.

        Notes
        -----
        This is automatically called by MesaData.header, so the average user
        shouldn't need to call it.
        """
        return key in self.header_names

    def in_data(self, key):
        """Determine if `key` is an available main data category.

        Checks if string `key` is a valid argument of MesaData.data. Returns
        True if it is, otherwise False

        Parameters
        ----------
        key : str
            Candidate string for accessing main data. This is what you want
            to be able to use as an argument of MesaData.data.

        Returns
        -------
        bool
            True if `key` is a valid input to MesaData.data, otherwise False.

        Notes
        -----
        This is automatically called by MesaData.data, so the average user
        shouldn't need to call it.
        """
        return key in self.bulk_names

    def _log_version(self, key):
        """Determine if the log of the desired value is available and return it.

        If a log_10 version of the value desired is found in the data columns,
        the "logified" name will be returned. Otherwise it will return `None`.

        Parameters
        ----------
        key : str
            Candidate string for accessing main data. This is what you want
            to be able to use as an argument of MesaData.data.

        Returns
        -------
        str or `None`
            The "logified" version of the key, if available. If unavailable,
            `None`.
        """
        log_prefixes = ['log_', 'log', 'lg_', 'lg']
        for prefix in log_prefixes:
            if self.in_data(prefix + key):
                return prefix + key

    def _ln_version(self, key):
        """Determine if the ln of the desired value is available and return it.

        If a log_e version of the value desired is found in the data columns,
        the "ln-ified" name will be returned. Otherwise it will return `None`.

        Parameters
        ----------
        key : str
            Candidate string for accessing main data. This is what you want
            to be able to use as an argument of MesaData.data.

        Returns
        -------
        str or `None`
            The "ln-ified" version of the key, if available. If unavailable,
            `None`.
        """
        log_prefixes = ['ln_', 'ln']
        for prefix in log_prefixes:
            if self.in_data(prefix + key):
                return prefix + key

    def _exp10_version(self, key):
        """Find if the non-log version of a value is available and return it

        If a non-log version of the value desired is found in the data columns,
        the linear name will be returned. Otherwise it will return `None`.

        Parameters
        ----------
        key : str
            Candidate string for accessing main data. This is what you want
            to be able to use as an argument of MesaData.data.

        Returns
        -------
        str or `None`
            The linear version of the key, if available. If unavailable, `None`.
        """
        log_matcher = re.compile('^lo?g_?(.+)')
        matches = log_matcher.match(key)
        if matches is not None:
            groups = matches.groups()
            if self.in_data(groups[0]):
                return groups[0]

    def _exp_version(self, key):
        """Find if the non-ln version of a value is available and return it

        If a non-ln version of the value desired is found in the data columns,
        the linear name will be returned. Otherwise it will return `None`.

        Parameters
        ----------
        key : str
            Candidate string for accessing main data. This is what you want
            to be able to use as an argument of MesaData.data.

        Returns
        -------
        str or `None`
            The linear version of the key, if available. If unavailable, `None`.
        """
        log_matcher = re.compile('^ln_?(.+)')
        matches = log_matcher.match(key)
        if matches is not None:
            groups = matches.groups()
            if self.in_data(groups[0]):
                return groups[0]

    def _any_version(self, key):
        """Determine if `key` can point to a valid data category

        Parameters
        ----------
        key : str
            Candidate string for accessing main data. This is what you want
            to be able to use as an argument of MesaData.data.

        Returns
        -------
        bool
            True if `key` can be mapped to a data type either directly or by
            exponentiating/taking logarithms of existing data types
        """
        return bool(self.in_data(key) or self._log_version(key) or
                    self._ln_version(key) or self._exp_version(key) or
                    self._exp10_version(key))

    def data_at_model_number(self, key, m_num):
        """Return main data at a specific model number (for history files).

        Finds the index i where MesaData.data('model_number')[i] == m_num. Then
        returns MesaData.data(key)[i]. Essentially lets you use model numbers
        to index data.

        Parameters
        ----------
        key : str
            Name of data. Must match a main data title in the source file.

        m_num : int
            Model number where you want to sample the data

        Returns
        -------
        float or int
            Value of MesaData.data(`key`) at the same index where
            MesaData.data('model_number') == `m_num`

        See Also
        --------
        index_of_model_number : returns the index for sampling, not the value
        """
        return self.data(key)[self.index_of_model_number(m_num)]

    def index_of_model_number(self, m_num):
        """Return index where MesaData.data('model_number') is `m_num`.

        Returns the index i where MesaData.data('model_number')[i] == m_num.

        Parameters
        ----------
        m_num : int
            Model number where you want to sample data

        Returns
        -------
        int
            The index where MesaData.data('model_number') == `m_num`

        Raises
        ------
        HistoryError
            If trying to access a non-history file

        ModelNumberError
            If zero or more than one model numbers matching `m_num` are found.

        See Also
        --------
        data_at_model_number : returns the datum of a specific key a model no.
        """
        if not self.is_history():
            raise HistoryError("Can't get data at model number " +
                               "because this isn't a history file")
        index = np.where(self.data('model_number') == m_num)[0]
        if len(index) > 1:
            raise ModelNumberError("Found more than one entry where model " +
                                   "number is " + str(m_num) + " in " +
                                   self.file_name + ". Report this.")
        elif len(index) == 0:
            raise ModelNumberError("Couldn't find any entries with model " +
                                   "number " + str(m_num) + ".")
        elif len(index) == 1:
            return index[0]

    def remove_backups(self, dbg=False):
        """Cleanses a history file of backups and restarts

        If the file is a history file, goes through and ensure that the
        model_number data are monotonically increasing. It removes rows of data
        from all categories if there are earlier ones later in the file.

        Parameters
        ----------
        dbg : bool, optional
            If True, will output how many lines are cleansed. Default is False

        Returns
        -------
        None
        """
        if not self.is_history():
            return None
        if dbg:
            print("Scrubbing history...")
        to_remove = []
        for i in range(len(self.data('model_number')) - 1):
            smallest_future = np.min(self.data('model_number')[i + 1:])
            if self.data('model_number')[i] >= smallest_future:
                to_remove.append(i)
        if len(to_remove) == 0:
            if dbg:
                print("Already clean!")
            return None
        if dbg:
            print("Removing {} lines.".format(len(to_remove)))
        self.bulk_data = np.delete(self.bulk_data, to_remove)

    def __getattr__(self, method_name):
        if self._any_version(method_name):
            return self.data(method_name)
        elif self.in_header(method_name):
            return self.header(method_name)
        else:
            raise AttributeError(method_name)

