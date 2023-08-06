import os
from os.path import join
import numpy as np

from .exceptions import *

class MesaLogDir:

    """Structure providing access to both history and profile output from MESA

    Provides access for accessing the history and profile data of a MESA run
    by linking profiles to the history through model numbers.

    Parameters
    ----------
    log_path : str, optional
        Path to the logs directory, default is 'LOGS'
    profile_prefix : str, optional
        Prefix before profile number in profile file names, default is
        'profile'
    profile_suffix : str, optional
        Suffix after profile number and period for profile file names, default
        is 'data'
    history_file : str, optional
        Name of the history file in the logs directory, default is
        'history.data'
    index_file : str, optional
        Name of the profiles index file in the logs directory, default is
        'profiles.index'
    memoize_profiles : bool, optional
        Determines whether or not profiles will be "memo-ized", default is
        True. If memoized, once a profile is called into existence, it is saved
        so that it need not be read in again. Good for quick, clean, repeated
        access of a profile, but bad for reading in many profiles for one-time
        uses as it will hog memory.

    Attributes
    -----------
    log_path : str
        Path to the logs directory; used (re-)reading data in
    profile_prefix : str
        Prefix before profile number in profile file names
    profile_suffix : str
        Suffix after profile number and period for profile file names
    history_file : str
        Base name (not path) of the history file in the logs directory
    index_file : str
        Base name (not path) of the profiles index file in the logs directory
    memoize_profiles : bool
        Determines whether or not profiles will be "memo-ized". Setting this
        after initialization will not delete profiles from memory. It will
        simply start/stop memoizing them. To clear out memoized profiles,
        re-read the data with `self.read_logs()`
    history_path : str
        Path to the history data file
    index_path : str
        Path to the profile index file
    history : mesa_reader.MesaData
        MesaData object containing history information from `self.history_path`
    history_data : mesa_reader.MesaData
        Alias for `self.history`
    profiles : mesa_reader.MesaProfileIndex
        MesaProfileIndex from profiles in `self.index_path`
    profile_numbers : numpy.ndarray
        Result of calling `self.profiles.profile_numbers`. Just the profile
        numbers of the simulation in order of corresponding model numbers.
    model_numbers : numpy.ndarray
        Result of calling `self.profiles.model_numbers`. Just the model numbers
        of the simulations that have corresponding profiles in ascending order.
    profile_dict : dict
        Stores MesaData objects from profiles. Keys to this dictionary are
        profile numbers, so presumably `self.profile_dict(5)` would yield the
        MesaData object obtained from the file `profile5.data` (assuming
        reasonable defaults) if such a profile was ever accessed. Will remain
        empty if memoization is shut off.
    """

    def __init__(self, log_path='LOGS', profile_prefix='profile',
                 profile_suffix='data', history_file='history.data',
                 index_file='profiles.index', memoize_profiles=True):
        self.log_path = log_path
        self.profile_prefix = profile_prefix
        self.profile_suffix = profile_suffix
        self.history_file = history_file
        self.index_file = index_file

        # Check if log_path and files are dir/files.
        if not os.path.isdir(self.log_path):
            raise BadPathError(self.log_path + ' is not a valid directory.')

        self.history_path = os.path.join(self.log_path, self.history_file)
        if not os.path.isfile(self.history_path):
            raise BadPathError(self.history_file + ' not found in ' +
                               self.log_path + '.')

        self.index_path = os.path.join(self.log_path, self.index_file)
        if not os.path.isfile(self.index_path):
            raise BadPathError(self.index_file + ' not found in ' +
                               self.log_path + '.')

        self.memoize_profiles = memoize_profiles

        self.history = None
        self.history_data = None
        self.profiles = None
        self.profile_numbers = None
        self.model_numbers = None
        self.profile_dict = None
        self.read_logs()

    def read_logs(self):
        """Read (or re-read) data from the history and profile index.

        Reads in `self.history_path` and `self.index_file` for use in getting
        history data and profile information. This is automatically called at
        instantiation, but can be recalled by the user if for some reason the
        data needs to be refreshed (for instance, after changing some of the
        reader methods to read in specially-formatted output.)

        Returns
        -------
        None

        Note
        ----
        This, if called after initialization, will empty `self.profile_dict`,
        erasing all memo-ized profiles.
        """

        self.history = MesaData(self.history_path)
        self.history_data = self.history
        self.profiles = MesaProfileIndex(self.index_path)
        self.profile_numbers = self.profiles.profile_numbers
        self.model_numbers = self.profiles.model_numbers
        self.profile_dict = dict()

    def have_profile_with_model_number(self, m_num):
        """Checks to see if a model number has a corresponding profile number.

        Parameters
        ----------
        m_num : int
            model number to be checked

        Returns
        -------
        bool
            True if the model number is in `self.model_numbers`, otherwise
            False.
        """
        return self.profiles.have_profile_with_model_number(m_num)

    def have_profile_with_profile_number(self, p_num):
        """Checks to see if a given number is a valid profile number.

        Parameters
        ----------
        p_num : int
            profile number to be checked

        Returns
        -------
        bool
            True if profile number is in `self.profile_numbers`, otherwise
            False.
        """
        return self.profiles.have_profile_with_profile_number(p_num)

    def profile_with_model_number(self, m_num):
        """Converts a model number to a corresponding profile number

        Parameters
        ----------
        m_num : int
            model number to be converted

        Returns
        -------
        int
            profile number that corresponds to `m_num`.
        """
        return self.profiles.profile_with_model_number(m_num)

    def model_with_profile_number(self, p_num):
        """Converts a profile number to a corresponding model number

        Parameters
        ----------
        p_num : int
            profile number to be converted

        Returns
        -------
        int
            model number that corresponds to `p_num`.
        """
        return self.profiles.model_with_profile_number(p_num)

    def profile_data(self, model_number=-1, profile_number=-1):
        """Generate or retrieve MesaData from a model or profile number.

        If both a model number and a profile number is given, the model number
        takes precedence. If neither are given, the default is to return a
        MesaData object of the last profile (biggest model number). In either
        case, this generates (if it doesn't already exist) or retrieves (if it
        has already been generated and memoized) a MesaData object from the
        corresponding profile data.

        Parameters
        ----------
        model_number : int, optional
            model number for the profile MesaData object desired. Default is
            -1, corresponding to the last model number.
        profile_number : int, optional
            profile number for the profile MesaData object desired. Default is
            -1, corresponding to the last model number. If both `model_number`
            and `profile_number` are given, `profile_number` is ignored.

        Returns
        -------
        mesa_reader.MesaData
            Data for profile with desired model/profile number.
        """
        if model_number == -1:
            if profile_number == -1:
                to_use = self.profile_numbers[-1]
            else:
                to_use = profile_number
        else:
            to_use = self.profile_with_model_number(model_number)

        if to_use in self.profile_dict:
            return self.profile_dict[to_use]

        file_name = join(self.log_path,
                         (self.profile_prefix + str(to_use) + '.' +
                          self.profile_suffix))
        p = MesaData(file_name)
        if self.memoize_profiles:
            self.profile_dict[to_use] = p
        return p

    def select_models(self, f, *keys):
        """Yields model numbers for profiles that satisfy a given criteria.

        Given a function `f` of various time-domain (history) variables,
        `*keys` (i.e., categories in `self.history.bulk_names`), filters
        `self.model_numbers` and returns all model numbers that satisfy the
        criteria.

        Parameters
        ----------
        f : function
            A function of the same number of parameters as strings given for
            `keys` that returns a boolean. Should evaluate to `True` when
            condition is met and `False` otherwise.
        keys : str
            Name of data categories from `self.history.bulk_names` whose values
            are to be used in the arguments to `f`, in the same order that they
            appear as arguments in `f`.

        Returns
        -------
        numpy.ndarray
            Array of model numbers that have corresponding profiles where the
            condition given by `f` is `True`.

        Raises
        ------
        KeyError
            If any of the `keys` are invalid history keys.

        Examples
        --------
        >>> l = MesaLogDir()
        >>> def is_old_and_bright(age, log_lum):
        >>>     return age > 1e9 and log_lum > 3
        >>> m_nums = l.select_models(is_old_and_bright, 'star_age', 'log_L')

        Here, `m_nums` will contain all model numbers that have profiles where
        the age is greater than a billion years and the luminosity is greater
        than 1000 Lsun, provided that 'star_age' and 'log_L' are in
        `self.history.bulk_names`.
        """

        for key in keys:
            if not self.history.in_data(key):
                raise KeyError("'" + str(key) + "' is not a valid data type.")
        inputs = {}
        for m_num in self.model_numbers:
            this_input = []
            for key in keys:
                this_input.append(
                    self.history.data_at_model_number(key, m_num))
            inputs[m_num] = this_input
        mask = np.array([f(*inputs[m_num]) for m_num in self.model_numbers])
        return self.model_numbers[mask]
