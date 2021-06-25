import numpy as np

import qetpy as qp


__all__ = [
    'repack_h5info_dict',
    'SingleChannelExtractors',
]


def repack_h5info_dict(h5info_dict):
    """

    Helper function to repackage the hdf5 file event info (metadata)  dictionaries into a dictionary
    with a format that can be used in the rq dataframe

    Parameters
    ----------
    h5dict : list
        A list of dictionaries (one dictionary per event) with format as output by the pytesdaq
        function read_many_events

    Returns
    -------
    retdict : dict
        A dictionary of numpy arrays containing event metadata (eventnumber, seriesnumber, etc.)

    """

    len_dict = len(h5info_dict)
    eventnumber_arr = np.zeros(len_dict, dtype=np.int32)
    eventindex_arr = np.zeros(len_dict, dtype=np.int16)
    dumpnum_arr = np.zeros(len_dict, dtype=np.int16)
    seriesnumber_arr = np.zeros(len_dict, dtype=np.int64)
    eventtime_arr = np.zeros(len_dict)
    triggertype_arr = np.ones(len_dict)
    triggeramp_arr = np.zeros(len_dict)
    triggertime_arr = np.zeros(len_dict)

    for i in range(len_dict):
        eventnumber_arr[i] = h5info_dict[i]['event_num']
        eventindex_arr[i] = h5info_dict[i]['event_index']
        dumpnum_arr[i] = h5info_dict[i]['dump_num']
        seriesnumber_arr[i] = h5info_dict[i]['series_num']
        eventtime_arr[i] = h5info_dict[i]['event_time']
        if h5info_dict[i]['data_mode'] == 'threshold':
            triggertype_arr[i] = 1
            triggeramp_arr[i] = h5info_dict[i]['trigger_amplitude']
            triggertime_arr[i] = h5info_dict[i]['trigger_time']
        elif h5info_dict[i]['data_mode'] == 'rand':
            triggertype_arr[i] = 0
            triggeramp_arr[i] = h5info_dict[i]['trigger_amplitude']
            triggertime_arr[i] = h5info_dict[i]['trigger_time']
        else:
            triggertype_arr[i] = None
            triggeramp_arr[i] = None
            triggertime_arr[i] = None

    retdict = {
        'eventnumber': eventnumber_arr,
        'eventindex': eventindex_arr,
        'dumpnumber': dumpnum_arr,
        'seriesnumber': seriesnumber_arr,
        'eventtime': eventtime_arr,
        'triggertype': triggertype_arr,
        'triggeramp': triggeramp_arr,
        'triggertime': triggertime_arr,
    }

    return retdict

class SingleChannelExtractors(object):
    """
    A class that contains all of the possible feature extractors
    for a given trace, assuming processing on a single channel.
    Each feature extraction function is a staticmethod for processing
    convenience.

    """

    @staticmethod
    def extract_of_nodelay(trace, template, psd, fs, **kwargs):
        """
        Feature extraction for the no delay Optimum Filter.

        Parameters
        ----------
        trace : ndarray
            An ndarray containing the raw data to extract the feature from.
        template : ndarray
            The template to use for the optimum filter.
        psd : ndarray
            The PSD to use for the optimum filter.

        Returns
        -------
        retdict : dict
            Dictionary containing the various extracted features.

        """

        OF = qp.OptimumFilter(
            trace,
            template,
            psd,
            fs,
        )
        ofamp_nodelay, ofchi2_nodelay = OF.ofamp_nodelay()

        retdict = {
            'ofamp_nodelay': ofamp_nodelay,
            'ofchi2_nodelay': ofchi2_nodelay,
        }
        return of_nodelay


    @staticmethod
    def extract_of_unconstrained(trace, template, psd, fs, **kwargs):
        """
        Feature extraction for the unconstrained Optimum Filter.

        Parameters
        ----------
        trace : ndarray
            An ndarray containing the raw data to extract the feature from.
        template : ndarray
            The template to use for the optimum filter.
        psd : ndarray
            The PSD to use for the optimum filter.

        Returns
        -------
        retdict : dict
            Dictionary containing the various extracted features.

        """

        OF = qp.OptimumFilter(
            trace,
            template,
            psd,
            fs,
        )
        ofamp_unconstrained, oft0_unconstrained, ofchi2_unconstrained = OF.ofamp_withdelay()

        retdict = {
            'ofamp_unconstrained': ofamp_unconstrained,
            'oft0_unconstrained': oft0_unconstrained,
            'ofchi2_unconstrained': ofchi2_unconstrained,
        }

        return retdict


    @staticmethod
    def extract_of_constrained(trace, template, psd, fs, nconstrain, window_center, **kwargs):
        """
        Feature extraction for the constrained Optimum Filter.

        Parameters
        ----------
        trace : ndarray
            An ndarray containing the raw data to extract the feature from.
        template : ndarray
            The template to use for the optimum filter.
        psd : ndarray
            The PSD to use for the optimum filter.
        nconstrain : int
            The constraint window set by the processing file.
        window_center : int
            The window center of the constraint window.

        Returns
        -------
        retdict : dict
            Dictionary containing the various extracted features.

        """

        OF = qp.OptimumFilter(
            trace,
            template,
            psd,
            fs,
        )
        ofamp_constrained, oft0_constrained, ofchi2_constrained = OF.ofamp_withdelay(
            nconstrain=nconstrain,
            windowcenter=windowcenter,
        )

        retdict = {
            'ofamp_constrained': ofamp_constrained,
            'oft0_constrained': oft0_constrained,
            'ofchi2_constrained': ofchi2_constrained,
        }

        return retdict


    @staticmethod
    def extract_baseline(trace, end_index, **kwargs):
        """
        Feature extraction for the trace baseline.

        Parameters
        ----------
        trace : ndarray
            An ndarray containing the raw data to extract the feature from.
        end_index : ndarray
            The index of the trace to average the trace up to.

        Returns
        -------
        retdict : dict
            Dictionary containing the various extracted features.

        """

        baseline = np.mean(trace[:end_index])

        retdict = {
            'baseline': baseline,
        }

        return retdict



    @staticmethod
    def extract_integral(trace, start_index, end_index, fs, **kwargs):
        """
        Feature extraction for the pulse integral.

        Parameters
        ----------
        trace : ndarray
            An ndarray containing the raw data to extract the feature from.
        start_index : ndarray
            The index of the trace to start the integration.
        end_index : ndarray
            The index of the trace to end the integration.

        Returns
        -------
        retdict : dict
            Dictionary containing the various extracted features.

        """

        integral = np.trapz(trace[start_index:end_index]) / fs

        retdict = {
            'integral': integral,
        }

        return retdict


    @staticmethod
    def extract_max(trace, start_index, end_index, **kwargs):
        """
        Feature extraction for the maximum pulse value.

        Parameters
        ----------
        trace : ndarray
            An ndarray containing the raw data to extract the feature from.
        start_index : ndarray
            The index of the trace to start searching for the max.
        end_index : ndarray
            The index of the trace to end searching for the max.

        Returns
        -------
        retdict : dict
            Dictionary containing the various extracted features.

        """

        max_trace = np.amax(trace[start_index:end_index])

        retdict = {
            'max': max_trace,
        }

        return retdict


    @staticmethod
    def extract_min(trace, start_index, end_index, **kwargs):
        """
        Feature extraction for the minimum pulse value.

        Parameters
        ----------
        trace : ndarray
            An ndarray containing the raw data to extract the feature from.
        start_index : ndarray
            The index of the trace to start searching for the min.
        end_index : ndarray
            The index of the trace to end searching for the min.

        Returns
        -------
        retdict : dict
            Dictionary containing the various extracted features.

        """

        min_trace = np.amin(trace[start_index:end_index])

        retdict = {
            'min': min_trace,
        }

        return retdict


