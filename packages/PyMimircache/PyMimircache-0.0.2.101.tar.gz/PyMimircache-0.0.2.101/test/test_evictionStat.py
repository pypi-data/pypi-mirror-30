# # coding=utf-8
# import unittest
#
# from PyMimircache import *
# from PyMimircache.profiler.evictionStat import *
#
# DAT_FOLDER = "../data/"
# import os
# if not os.path.exists(DAT_FOLDER):
#     if os.path.exists("data/"):
#         DAT_FOLDER = "data/"
#     elif os.path.exists("../PyMimircache/data/"):
#         DAT_FOLDER = "../PyMimircache/data/"
#
# class evictionStat_test(unittest.TestCase):
#     def test_eviction_stat_reuse_dist(self):
#         reader = CsvReader("{}/trace.csv".format(DAT_FOLDER),
#                            init_params={"header": True, 'label': 5, 'real_time': 2})
#
#         eviction_stat_reuse_dist_plot(reader, "Optimal", 1000, 'r', 10000000)
#         eviction_stat_reuse_dist_plot(reader, "Optimal", 200, 'v', 1000)
#
#     def test_eviction_stat_freq(self):
#         reader = CsvReader("{}/trace.csv".format(DAT_FOLDER),
#                            init_params={"header": True, 'label': 5, 'real_time': 2})
#         eviction_stat_reuse_dist_plot(reader, "Optimal", 1000, 'r', 10000000)
#         eviction_stat_freq_plot(reader, "Optimal", 200, 'v', 1000, accumulative=True)
#         eviction_stat_freq_plot(reader, "Optimal", 200, 'v', 1000, accumulative=False)
#
#
#
# if __name__ == "__main__":
#     unittest.main()
#
#
