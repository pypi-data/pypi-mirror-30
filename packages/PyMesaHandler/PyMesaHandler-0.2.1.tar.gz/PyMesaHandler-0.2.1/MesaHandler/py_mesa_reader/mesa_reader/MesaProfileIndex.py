from os.path import join
import numpy as np

from .exceptions import *

class MesaProfileIndex:

    """Structure containing data from the profile index from MESA output.

    Reads in data from profile index file from MESA, allowing a mapping from
    profile number to model number and vice versa. Mostly accessed via the
    MesaLogDir class.

    Parameters
    ----------
    file_name : str, optional
        Path to the profile index file to be read in. Default is
        'LOGS/profiles.index', which should work when the working directory is
        a standard work directory and the logs directory is of the default
        name.

    Attributes
    ----------
    file_name : str
        path to the profile index file
    index_data : dict
        dictionary containing all index data in numpy arrays.
    model_number_string : str
        header name of the model number column in `file_name`
    profile_number_string : str
        header name of the profile number column in `file_name`
    profile_numbers : numpy.ndarray
        List of all available profile numbers in order of their corresponding
        model numbers (i.e. time-order).
    model_numbers : numpy.ndarray
        Sorted list of all available model numbers.
    """

    index_start_line = 2
    index_end = None
    index_names = ['model_numbers', 'priorities', 'profile_numbers']

    @classmethod
    def set_index_rows(cls, index_start=2, index_end=None):
        cls.index_start_line = index_start
        cls.index_end_line = index_end
        return index_start, index_end

    @classmethod
    def set_index_names(cls, name_arr):
        cls.index_names = name_arr
        return name_arr

    def __init__(self, file_name=join('.', 'LOGS', 'profiles.index')):
        self.file_name = file_name
        self.index_data = None
        self.model_number_string = ''
        self.profile_number_string = ''
        self.profile_numbers = None
        self.model_numbers = None
        self.read_index()

    def read_index(self):
        """Read (or re-read) data from `self.file_name`.

        Read the file into an numpy array, sorting the table in order of
        increasing model numbers and establishes the `profile_numbers` and
        `model_numbers` attributes. Converts data and names into a dictionary.
        Called automatically at instantiation, but may be called again to
        refresh data.

        Returns
        -------
        None
        """
        temp_index_data = np.genfromtxt(
            self.file_name, skip_header=MesaProfileIndex.index_start_line - 1,
            dtype=None)
        self.model_number_string = MesaProfileIndex.index_names[0]
        self.profile_number_string = MesaProfileIndex.index_names[-1]
        self.index_data = temp_index_data[np.argsort(temp_index_data[:, 0])]
        self.index_data = dict(zip(MesaProfileIndex.index_names,
                                   temp_index_data.T))
        self.profile_numbers = self.data(self.profile_number_string)
        self.model_numbers = self.data(self.model_number_string)

    def data(self, key):
        """Access index data and return array of column corresponding to `key`.

        Parameters
        ----------
        key : str
            Name of column to be returned. Likely choices are 'model_numbers',
            'profile_numbers', or 'priorities'.

        Returns
        -------
        numpy.ndarray
            Array containing the data requested.

        Raises
        ------
        KeyError
            If input key is not a valid column header name.
        """
        if key not in self.index_names:
            raise KeyError("'" + str(key) + "' is not a column in " +
                           self.file_name)
        return np.array(self.index_data[key])

    def have_profile_with_model_number(self, model_number):
        """Determines if given `model_number` has a matching profile number.

        Attributes
        ----------
        model_number : int
            model number to be checked for available profile number

        Returns
        -------
        bool
            True if `model_number` has a corresponding profile number. False
            otherwise.
        """
        return model_number in self.data(self.model_number_string)

    def have_profile_with_profile_number(self, profile_number):
        """Determines if given `profile_number` is a valid profile number.

        Attributes
        ----------
        profile_number : int
            profile number to be verified

        Returns
        -------
        bool
            True if `profile_number` has a corresponding entry in the index.
            False otherwise.
        """
        return profile_number in self.data(self.profile_number_string)

    def profile_with_model_number(self, model_number):
        """Converts a model number to a profile number if possible.

        If `model_number` has a corresponding profile number in the index,
        returns it. Otherwise throws an error.

        Attributes
        ----------
        model_number : int
            model number to be converted into a profile number

        Returns
        -------
        int
            profile number corresponding to `model_number`

        Raises
        ------
        ProfileError
            If no profile number can be found that corresponds to
            `model_number`
        """
        if not (self.have_profile_with_model_number(model_number)):
            raise ProfileError("No profile with model number " +
                               str(model_number) + ".")
        indices = np.where(self.data(self.model_number_string) == model_number)
        return np.take(self.data(self.profile_number_string), indices[0])[0]

    def model_with_profile_number(self, profile_number):
        """Converts a profile number to a profile number if possible.

        If `profile_number` has a corresponding model number in the index,
        returns it. Otherwise throws an error.

        Attributes
        ----------
        profile_number : int
            profile number to be converted into a model number

        Returns
        -------
        int
            model number corresponding to `profile_number`

        Raises
        ------
        ProfileError
            If no model number can be found that corresponds to
            `profile_number`
        """
        if not (self.have_profile_with_profile_number(profile_number)):
            raise ProfileError("No Profile with profile number " +
                               str(profile_number) + ".")
        indices = np.where(
            self.data(self.profile_number_string) == profile_number)
        return np.take(self.data(self.model_number_string), indices[0])[0]

    def __getattr__(self, method_name):
        if method_name in self.index_data.keys():
            return self.data(method_name)
        else:
            raise AttributeError(method_name)

