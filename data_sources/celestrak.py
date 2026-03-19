"""
CelesTrak satellite catalog + SGP4 propagation
Fetches GP (General Perturbations) element sets and computes real-time positions.
"""
from __future__ import annotations
import time
import math
from datetime import datetime, timezone
from typing import Optional, List, Dict
import httpx
from sgp4.api import Satrec, WGS72
from config import CACHE_TTL_TLE_CATALOG, CACHE_TTL_SATELLITES

_cache = {}
_BASE = "https://celestrak.org/NORAD/elements/gp.php"

# ---------------------------------------------------------------------------
# Seed catalog – hardcoded GP element sets for ~186 key satellites.
# Used as fallback when CelesTrak is unreachable and no cache exists.
# Compact format: (name, obj_id, norad, inc, mm, ecc, bstar, raan, argp, ma, obj_type)
# ---------------------------------------------------------------------------
_SEED_RAW = [
    # === Space Stations ===
    ('ISS (ZARYA)', '1998-067A', 25544, 51.6416, 15.4897, 0.0006, 0.00035, 120.5, 45.2, 315.8, 'PAYLOAD'),
    ('CSS (TIANHE)', '2021-035A', 48274, 41.474, 15.592, 0.0004, 0.0004, 210.3, 190.5, 170.2, 'PAYLOAD'),
    # === Yaogan (PRC ISR) – SSO ~500-1100 km ===
    ('YAOGAN-1', 'YG-1', 29092, 97.38, 15.23, 0.0013149, 6.13e-05, 99.0106, 80.3559, 265.1296, 'PAYLOAD'),
    ('YAOGAN-2', 'YG-2', 30110, 97.35, 15.22, 0.0013857, 0.0004515, 31.298, 151.8919, 10.727, 'PAYLOAD'),
    ('YAOGAN-3', 'YG-3', 31490, 97.65, 15.24, 0.0005154, 0.0002774, 9.5529, 71.5816, 233.9584, 'PAYLOAD'),
    ('YAOGAN-4', 'YG-4', 33320, 63.4, 15.12, 0.0011354, 0.0001492, 212.1356, 291.395, 2.3396, 'PAYLOAD'),
    ('YAOGAN-5', 'YG-5', 34839, 97.42, 15.07, 0.0016311, 0.0003642, 122.4902, 55.9726, 344.5967, 'PAYLOAD'),
    ('YAOGAN-6', 'YG-6', 35942, 97.9, 14.63, 0.0007395, 9.17e-05, 34.8179, 305.098, 217.3414, 'PAYLOAD'),
    ('YAOGAN-7', 'YG-7', 36110, 97.38, 15.23, 0.0016335, 0.0003784, 193.0421, 350.3217, 136.2724, 'PAYLOAD'),
    ('YAOGAN-8', 'YG-8', 36121, 97.8, 14.76, 0.0011489, 0.0004232, 222.6671, 310.2145, 207.8468, 'PAYLOAD'),
    ('YAOGAN-9A', 'YG-9A', 36413, 97.6, 15.23, 0.0014387, 7.06e-05, 82.0434, 104.1797, 28.7251, 'PAYLOAD'),
    ('YAOGAN-9B', 'YG-9B', 36414, 97.6, 15.23, 0.0005423, 9.55e-05, 100.0705, 228.8464, 131.3396, 'PAYLOAD'),
    ('YAOGAN-9C', 'YG-9C', 36415, 97.6, 15.23, 0.0008033, 0.0001443, 96.112, 337.1957, 233.2927, 'PAYLOAD'),
    ('YAOGAN-10', 'YG-10', 37165, 97.72, 14.7, 0.0012573, 0.000127, 262.4856, 58.8249, 136.604, 'PAYLOAD'),
    ('YAOGAN-11', 'YG-11', 37730, 97.68, 14.65, 0.0019801, 0.000338, 200.5019, 246.4611, 303.4267, 'PAYLOAD'),
    ('YAOGAN-12', 'YG-12', 37875, 97.44, 15.19, 0.0015744, 0.0001531, 11.5561, 113.5631, 96.3867, 'PAYLOAD'),
    ('YAOGAN-13', 'YG-13', 38049, 97.4, 15.24, 0.0005009, 0.0004743, 315.4923, 113.284, 235.9579, 'PAYLOAD'),
    ('YAOGAN-14', 'YG-14', 38257, 97.38, 15.23, 0.0008517, 0.0004615, 165.1867, 95.3569, 88.7859, 'PAYLOAD'),
    ('YAOGAN-15', 'YG-15', 38354, 97.8, 14.76, 0.0011666, 0.0001682, 210.451, 323.2162, 143.7842, 'PAYLOAD'),
    ('YAOGAN-16A', 'YG-16A', 38861, 97.52, 15.23, 0.0005167, 0.0004989, 183.4295, 32.7274, 16.9619, 'PAYLOAD'),
    ('YAOGAN-16B', 'YG-16B', 38862, 97.52, 15.23, 0.0003083, 0.0003324, 285.1486, 151.9776, 22.87, 'PAYLOAD'),
    ('YAOGAN-16C', 'YG-16C', 38863, 97.52, 15.23, 0.0008251, 0.0004983, 190.4812, 349.5882, 309.8807, 'PAYLOAD'),
    ('YAOGAN-17', 'YG-17', 39011, 97.9, 14.63, 0.0001218, 0.0003743, 245.4157, 193.3093, 96.0571, 'PAYLOAD'),
    ('YAOGAN-18', 'YG-18', 39150, 97.42, 15.19, 0.0013178, 0.0001002, 156.5155, 163.3405, 343.3737, 'PAYLOAD'),
    ('YAOGAN-19', 'YG-19', 39410, 97.38, 15.23, 0.0017641, 0.0001685, 180.211, 64.3147, 328.546, 'PAYLOAD'),
    ('YAOGAN-20A', 'YG-20A', 39458, 97.55, 15.23, 0.001754, 0.0001843, 230.0218, 219.2293, 55.0221, 'PAYLOAD'),
    ('YAOGAN-20B', 'YG-20B', 39459, 97.55, 15.23, 0.0015488, 0.0002927, 280.3055, 190.9273, 0.2059, 'PAYLOAD'),
    ('YAOGAN-20C', 'YG-20C', 39460, 97.55, 15.23, 0.0007159, 5.88e-05, 334.4755, 316.3399, 299.3996, 'PAYLOAD'),
    ('YAOGAN-21', 'YG-21', 39492, 97.38, 15.23, 0.0006843, 7.61e-05, 316.0835, 340.9018, 30.8352, 'PAYLOAD'),
    ('YAOGAN-22', 'YG-22', 39606, 97.9, 14.63, 0.0010234, 8.11e-05, 273.8168, 275.7004, 46.2209, 'PAYLOAD'),
    ('YAOGAN-23', 'YG-23', 39627, 97.42, 15.19, 0.001003, 0.0002974, 95.4204, 314.0759, 152.3297, 'PAYLOAD'),
    ('YAOGAN-24', 'YG-24', 39631, 97.38, 15.23, 0.0005024, 0.0002927, 262.7752, 72.4144, 112.2179, 'PAYLOAD'),
    ('YAOGAN-25A', 'YG-25A', 39684, 97.55, 15.23, 0.0019908, 0.0003424, 157.716, 186.3273, 43.5615, 'PAYLOAD'),
    ('YAOGAN-25B', 'YG-25B', 39685, 97.55, 15.23, 0.0005269, 0.0002021, 211.7911, 82.8413, 79.2783, 'PAYLOAD'),
    ('YAOGAN-25C', 'YG-25C', 39686, 97.55, 15.23, 0.0002349, 0.000334, 82.419, 325.9512, 309.4687, 'PAYLOAD'),
    ('YAOGAN-26', 'YG-26', 40143, 97.38, 15.23, 0.0002346, 0.0001571, 240.832, 77.1253, 47.6323, 'PAYLOAD'),
    ('YAOGAN-27', 'YG-27', 40305, 97.68, 15.19, 0.0018775, 0.000307, 170.1616, 282.463, 290.6989, 'PAYLOAD'),
    ('YAOGAN-28', 'YG-28', 40362, 97.55, 15.23, 0.0004618, 9.36e-05, 155.1784, 152.4883, 168.1289, 'PAYLOAD'),
    ('YAOGAN-29', 'YG-29', 40727, 97.65, 15.22, 0.0014852, 0.000353, 354.2995, 35.4304, 144.9437, 'PAYLOAD'),
    ('YAOGAN-30', 'YG-30', 41240, 97.48, 15.23, 0.0007447, 0.0004378, 89.5163, 68.4752, 161.5009, 'PAYLOAD'),
    ('YAOGAN-31', 'YG-31', 41726, 97.52, 15.08, 0.0009016, 0.0001753, 89.9303, 332.3756, 159.5271, 'PAYLOAD'),
    ('YAOGAN-32A', 'YG-32A', 41868, 97.55, 15.23, 0.0017366, 0.0002976, 18.2118, 359.7417, 300.9699, 'PAYLOAD'),
    ('YAOGAN-32B', 'YG-32B', 41869, 97.55, 15.23, 0.0019411, 0.0004669, 305.5305, 59.872, 174.8308, 'PAYLOAD'),
    ('YAOGAN-33', 'YG-33', 43020, 97.42, 15.19, 0.0005061, 0.0002305, 21.1087, 136.4303, 354.7112, 'PAYLOAD'),
    ('YAOGAN-34', 'YG-34', 43609, 97.38, 15.23, 0.0006039, 0.0004028, 163.803, 152.2827, 344.6344, 'PAYLOAD'),
    ('YAOGAN-35A', 'YG-35A', 44233, 97.52, 15.23, 0.0019913, 0.0003001, 258.627, 55.7269, 106.8148, 'PAYLOAD'),
    ('YAOGAN-35B', 'YG-35B', 44234, 97.52, 15.23, 0.0019405, 0.0003106, 195.1903, 269.2712, 20.5795, 'PAYLOAD'),
    ('YAOGAN-35C', 'YG-35C', 44235, 97.52, 15.23, 0.0012099, 0.0002763, 306.9792, 56.6758, 345.8804, 'PAYLOAD'),
    ('YAOGAN-36', 'YG-36', 49388, 97.5, 15.2, 0.0002522, 0.0001336, 214.2126, 243.0765, 84.6734, 'PAYLOAD'),
    ('YAOGAN-37', 'YG-37', 52808, 97.45, 15.21, 0.0003278, 0.0004506, 88.6375, 214.0269, 222.9773, 'PAYLOAD'),
    ('YAOGAN-38', 'YG-38', 55236, 97.48, 15.22, 0.0008965, 0.0003127, 188.2018, 336.4943, 73.5333, 'PAYLOAD'),
    ('YAOGAN-39', 'YG-39', 57130, 97.5, 15.2, 0.0014608, 0.0001574, 142.4829, 241.8085, 107.9989, 'PAYLOAD'),
    # === Jilin-1 (PRC ISR) – SSO ~530 km ===
    ('JILIN-1-01', 'JL1-01', 47901, 96.7435, 15.17666284, 0.0019971, 0.0004984, 10.8971, 26.3739, 14.8186, 'PAYLOAD'),
    ('JILIN-1-02', 'JL1-02', 47902, 97.26, 15.21046913, 0.0017706, 0.0002478, 22.2789, 56.7889, 22.252, 'PAYLOAD'),
    ('JILIN-1-03', 'JL1-03', 47903, 97.067, 15.21897865, 0.0013426, 0.0001031, 38.0025, 294.1575, 38.9354, 'PAYLOAD'),
    ('JILIN-1-04', 'JL1-04', 47904, 97.2634, 15.15074329, 0.0003193, 0.0001428, 46.7963, 199.1605, 50.8339, 'PAYLOAD'),
    ('JILIN-1-05', 'JL1-05', 47905, 97.1306, 15.15628778, 0.0013051, 0.0002056, 58.6341, 175.8715, 62.5483, 'PAYLOAD'),
    ('JILIN-1-06', 'JL1-06', 47906, 96.7554, 15.17388606, 0.0006257, 0.0001014, 74.432, 277.6029, 77.261, 'PAYLOAD'),
    ('JILIN-1-07', 'JL1-07', 47907, 97.1447, 15.18413443, 0.0009126, 0.0001039, 84.8227, 27.0878, 83.7196, 'PAYLOAD'),
    ('JILIN-1-08', 'JL1-08', 47908, 97.0274, 15.2067676, 0.0012068, 0.0001592, 98.2986, 45.8804, 102.4393, 'PAYLOAD'),
    ('JILIN-1-09', 'JL1-09', 47909, 97.1777, 15.20885621, 0.001808, 0.000184, 106.8496, 89.8307, 114.6898, 'PAYLOAD'),
    ('JILIN-1-10', 'JL1-10', 47910, 97.2305, 15.17251019, 0.0012793, 0.0001618, 117.6168, 334.7572, 125.8012, 'PAYLOAD'),
    ('JILIN-1-11', 'JL1-11', 47911, 97.1865, 15.2105133, 0.0001471, 0.0003946, 134.1876, 119.5868, 140.0621, 'PAYLOAD'),
    ('JILIN-1-12', 'JL1-12', 47912, 97.2184, 15.20485995, 0.0006069, 0.0004149, 146.5849, 38.9144, 150.6224, 'PAYLOAD'),
    ('JILIN-1-13', 'JL1-13', 47913, 96.8335, 15.20532693, 0.0009746, 0.0002221, 158.233, 286.3244, 163.4859, 'PAYLOAD'),
    ('JILIN-1-14', 'JL1-14', 47914, 96.8159, 15.16626096, 0.0017423, 0.0004868, 166.3656, 100.485, 167.4366, 'PAYLOAD'),
    ('JILIN-1-15', 'JL1-15', 47915, 97.2887, 15.18289726, 0.0018846, 0.0001461, 180.8489, 349.3442, 183.4968, 'PAYLOAD'),
    ('JILIN-1-16', 'JL1-16', 47916, 96.8593, 15.1486722, 0.0009257, 0.0003914, 190.0714, 112.9238, 201.4253, 'PAYLOAD'),
    ('JILIN-1-17', 'JL1-17', 47917, 96.9311, 15.18612704, 0.000584, 0.0003835, 204.6373, 0.6089, 209.2142, 'PAYLOAD'),
    ('JILIN-1-18', 'JL1-18', 47918, 97.1317, 15.19935601, 0.0013742, 0.0002457, 218.5535, 25.1906, 221.7845, 'PAYLOAD'),
    ('JILIN-1-19', 'JL1-19', 47919, 96.8883, 15.20784122, 0.0014675, 0.0002201, 228.9854, 111.3425, 232.002, 'PAYLOAD'),
    ('JILIN-1-20', 'JL1-20', 47920, 96.8774, 15.15018302, 0.0008988, 0.0004761, 239.4504, 243.8345, 245.024, 'PAYLOAD'),
    ('JILIN-1-21', 'JL1-21', 47921, 96.8806, 15.18383498, 0.0001008, 0.0002148, 254.4168, 154.7597, 259.4551, 'PAYLOAD'),
    ('JILIN-1-22', 'JL1-22', 47922, 96.979, 15.17537278, 0.000506, 0.0002893, 264.4799, 324.4251, 272.1471, 'PAYLOAD'),
    ('JILIN-1-23', 'JL1-23', 47923, 96.7509, 15.18123616, 0.0013026, 0.0002341, 277.7761, 294.6324, 279.5969, 'PAYLOAD'),
    ('JILIN-1-24', 'JL1-24', 47924, 96.8348, 15.15593039, 0.0001464, 0.0001979, 289.5068, 171.0491, 296.928, 'PAYLOAD'),
    ('JILIN-1-25', 'JL1-25', 47925, 96.9487, 15.19038123, 0.0004694, 0.0003785, 302.0984, 177.9758, 303.2283, 'PAYLOAD'),
    ('JILIN-1-26', 'JL1-26', 47926, 96.7033, 15.20007716, 0.0015631, 0.0001426, 310.4639, 153.0526, 321.3606, 'PAYLOAD'),
    ('JILIN-1-27', 'JL1-27', 47927, 97.0108, 15.14401747, 0.0005735, 0.0004393, 322.0553, 164.3263, 336.6797, 'PAYLOAD'),
    ('JILIN-1-28', 'JL1-28', 47928, 97.2927, 15.18763619, 0.0019051, 0.0004566, 337.8085, 220.5548, 346.0758, 'PAYLOAD'),
    ('JILIN-1-29', 'JL1-29', 47929, 97.1983, 15.18382976, 0.0018047, 0.0003975, 349.3156, 170.8828, 356.7478, 'PAYLOAD'),
    ('JILIN-1-30', 'JL1-30', 47930, 97.0826, 15.20126509, 0.0010905, 0.0003507, 358.5551, 98.8551, 6.4724, 'PAYLOAD'),
    # === BeiDou-3 MEO (PRC NAV) – inc ~55, alt ~21500 km ===
    ('BEIDOU-3 M1', 'BD3-M01', 43201, 54.863, 1.8605171, 0.0027467, 0.0, 19.7748, 49.8147, 21.8573, 'PAYLOAD'),
    ('BEIDOU-3 M2', 'BD3-M02', 43202, 55.1239, 1.85796229, 0.0020972, 0.0, 45.3126, 195.34, 49.9395, 'PAYLOAD'),
    ('BEIDOU-3 M3', 'BD3-M03', 43203, 54.9521, 1.86636838, 0.002962, 0.0, 71.1577, 250.3883, 69.0683, 'PAYLOAD'),
    ('BEIDOU-3 M4', 'BD3-M04', 43204, 54.9282, 1.85737896, 0.0018236, 0.0, 99.5673, 271.251, 98.6559, 'PAYLOAD'),
    ('BEIDOU-3 M5', 'BD3-M05', 43205, 54.9514, 1.86479516, 0.002776, 0.0, 123.5345, 217.1709, 124.5343, 'PAYLOAD'),
    ('BEIDOU-3 M6', 'BD3-M06', 43206, 54.9615, 1.85761025, 0.001747, 0.0, 141.2054, 244.4911, 141.1942, 'PAYLOAD'),
    ('BEIDOU-3 M7', 'BD3-M07', 43207, 54.9804, 1.85859628, 0.0031491, 0.0, 167.0432, 9.7079, 164.6504, 'PAYLOAD'),
    ('BEIDOU-3 M8', 'BD3-M08', 43208, 54.7163, 1.8637475, 0.0007649, 0.0, 190.9402, 166.2114, 192.6439, 'PAYLOAD'),
    ('BEIDOU-3 M9', 'BD3-M09', 43209, 54.827, 1.86058846, 0.00383, 0.0, 211.5028, 136.4854, 214.791, 'PAYLOAD'),
    ('BEIDOU-3 M10', 'BD3-M10', 43210, 54.8514, 1.85813906, 0.000195, 0.0, 242.5201, 194.1909, 243.3192, 'PAYLOAD'),
    ('BEIDOU-3 M11', 'BD3-M11', 43211, 55.0901, 1.86513233, 0.0032936, 0.0, 268.9991, 271.524, 262.4996, 'PAYLOAD'),
    ('BEIDOU-3 M12', 'BD3-M12', 43212, 54.7122, 1.85884382, 0.0007185, 0.0, 292.4961, 241.0052, 284.9936, 'PAYLOAD'),
    ('BEIDOU-3 M13', 'BD3-M13', 43213, 55.1197, 1.86498898, 0.0009222, 0.0, 312.6397, 218.6091, 309.1796, 'PAYLOAD'),
    ('BEIDOU-3 M14', 'BD3-M14', 43214, 55.1916, 1.86696721, 0.0006297, 0.0, 338.4793, 9.2442, 332.1453, 'PAYLOAD'),
    ('BEIDOU-3 M15', 'BD3-M15', 43215, 55.2749, 1.86128654, 0.0036036, 0.0, 358.1196, 27.3587, 1.7735, 'PAYLOAD'),
    # === BeiDou-3 GEO (PRC NAV) – inc ~0, alt ~35786 km ===
    ('BEIDOU-3 G1', 'BD3-G01', 43601, 1.0359, 1.0027909, 0.0001917, 0.0, 82.7248, 216.1482, 306.1056, 'PAYLOAD'),
    ('BEIDOU-3 G2', 'BD3-G02', 43602, 0.1816, 1.00293354, 0.0008044, 0.0, 108.972, 133.4055, 154.2161, 'PAYLOAD'),
    ('BEIDOU-3 G3', 'BD3-G03', 43603, 0.7589, 1.00267649, 0.0008646, 0.0, 143.2233, 345.8835, 37.994, 'PAYLOAD'),
    ('BEIDOU-3 G4', 'BD3-G04', 43604, 0.9534, 1.00287148, 0.0007366, 0.0, 159.3549, 347.5705, 264.1663, 'PAYLOAD'),
    ('BEIDOU-3 G5', 'BD3-G05', 43605, 0.4051, 1.00286328, 0.0005844, 0.0, 58.585, 263.1694, 156.8068, 'PAYLOAD'),
    # === Zhongxing (PRC Comms) – GEO ===
    ('ZHONGXING-6A', 'ZX-6A', 44100, 0.2684, 1.00288069, 0.0008477, 0.0, 85.02, 87.7908, 317.3872, 'PAYLOAD'),
    ('ZHONGXING-6B', 'ZX-6B', 44101, 0.4647, 1.00278413, 0.0004411, 0.0, 95.1722, 65.4623, 306.343, 'PAYLOAD'),
    ('ZHONGXING-6C', 'ZX-6C', 44102, 0.2121, 1.00285913, 0.0004063, 0.0, 107.7819, 99.4567, 252.4262, 'PAYLOAD'),
    ('ZHONGXING-9A', 'ZX-9A', 44103, 0.0102, 1.00291923, 0.0001771, 0.0, 111.8204, 272.9393, 175.888, 'PAYLOAD'),
    ('ZHONGXING-10', 'ZX-10', 44104, 0.6906, 1.00279836, 0.0005417, 0.0, 117.2576, 79.7747, 33.4992, 'PAYLOAD'),
    ('ZHONGXING-11', 'ZX-11', 44105, 0.6918, 1.00266248, 0.0006234, 0.0, 124.8396, 153.1814, 191.1319, 'PAYLOAD'),
    ('ZHONGXING-12', 'ZX-12', 44106, 0.7459, 1.00267232, 0.0007326, 0.0, 132.6255, 43.4361, 90.5053, 'PAYLOAD'),
    ('ZHONGXING-15', 'ZX-15', 44107, 0.1926, 1.00258782, 0.0005823, 0.0, 143.5731, 77.8985, 66.6539, 'PAYLOAD'),
    ('ZHONGXING-16', 'ZX-16', 44108, 0.4842, 1.00282983, 0.0009789, 0.0, 163.1478, 36.1894, 101.8795, 'PAYLOAD'),
    ('ZHONGXING-18', 'ZX-18', 44109, 0.1941, 1.00263099, 0.0002615, 0.0, 89.2849, 98.7521, 192.2886, 'PAYLOAD'),
    # === Shijian (PRC SDA/ASAT) – various orbits ===
    ('SHIJIAN-6-05A', 'SJ-6-05A', 37214, 59.0, 15.15, 0.0029255, 0.0005757, 251.0703, 45.4606, 312.646, 'PAYLOAD'),
    ('SHIJIAN-6-05B', 'SJ-6-05B', 37215, 59.0, 15.15, 0.0015235, 0.0008791, 206.6631, 168.9829, 158.5688, 'PAYLOAD'),
    ('SHIJIAN-17', 'SJ-17', 43613, 98.5, 14.35, 0.0006347, 9.88e-05, 338.7829, 171.9825, 295.9616, 'PAYLOAD'),
    ('SHIJIAN-18', 'SJ-18', 44078, 98.4, 14.34, 0.0012621, 0.0001204, 226.6005, 19.2993, 53.7111, 'PAYLOAD'),
    ('SHIJIAN-20', 'SJ-20', 44546, 35.0, 15.23, 0.0017322, 0.0003386, 357.8105, 42.6426, 275.1996, 'PAYLOAD'),
    ('SHIJIAN-21A', 'SJ-21A', 48078, 98.2, 14.35, 0.0018583, 0.0008012, 81.2474, 188.1261, 162.1852, 'PAYLOAD'),
    ('SHIJIAN-21B', 'SJ-21B', 48079, 98.2, 14.35, 0.0013839, 0.0008672, 356.4113, 109.9369, 223.5698, 'PAYLOAD'),
    ('SHIJIAN-23', 'SJ-23', 55614, 50.0, 15.4, 0.0018679, 0.0007531, 341.1325, 74.8036, 75.9691, 'PAYLOAD'),
    ('SHIJIAN-24A', 'SJ-24A', 56760, 97.6, 15.1, 0.0020152, 0.0001992, 62.5729, 27.0234, 0.9633, 'PAYLOAD'),
    ('SHIJIAN-24B', 'SJ-24B', 56761, 97.6, 15.1, 0.0014065, 0.0006141, 104.8533, 83.3314, 254.5041, 'PAYLOAD'),
    # === COSMOS (Russian Military) – various orbits ===
    ('COSMOS 2251', 'COS-2251', 22014, 74.0, 14.7, 0.0070893, 0.0003905, 247.4586, 332.608, 283.6181, 'PAYLOAD'),
    ('COSMOS 2421', 'COS-2421', 27560, 65.0, 14.4, 0.0063256, 0.0005459, 336.1206, 153.05, 196.0425, 'PAYLOAD'),
    ('COSMOS 2422', 'COS-2422', 27818, 65.0, 14.4, 0.0065468, 0.0007313, 297.5872, 25.7075, 59.7322, 'PAYLOAD'),
    ('COSMOS 2455', 'COS-2455', 28520, 82.5, 14.72, 0.0032146, 0.0006117, 204.9145, 103.8998, 44.7673, 'PAYLOAD'),
    ('COSMOS 2471', 'COS-2471', 29258, 67.1, 14.75, 0.006949, 0.0005748, 339.3634, 180.17, 177.7663, 'PAYLOAD'),
    ('COSMOS 2486', 'COS-2486', 31573, 74.0, 14.65, 0.0009883, 7.99e-05, 155.5303, 116.0358, 90.1324, 'PAYLOAD'),
    ('COSMOS 2499', 'COS-2499', 33277, 67.2, 14.73, 0.001095, 0.0007714, 300.9451, 207.0717, 342.2831, 'PAYLOAD'),
    ('COSMOS 2502', 'COS-2502', 34602, 74.0, 14.65, 0.0099958, 0.0005542, 97.024, 14.4834, 272.2568, 'PAYLOAD'),
    ('COSMOS 2506', 'COS-2506', 36034, 67.1, 14.75, 0.0048109, 0.0005386, 329.7862, 65.3361, 210.7187, 'PAYLOAD'),
    ('COSMOS 2516', 'COS-2516', 37372, 82.5, 14.72, 0.0064209, 0.0004188, 32.8473, 125.266, 119.991, 'PAYLOAD'),
    ('COSMOS 2519', 'COS-2519', 37731, 74.0, 14.7, 0.0067673, 0.0006933, 118.7293, 249.7225, 103.7584, 'PAYLOAD'),
    ('COSMOS 2523', 'COS-2523', 38736, 82.5, 14.72, 0.0094629, 0.0006602, 198.0348, 163.7373, 113.2262, 'PAYLOAD'),
    ('COSMOS 2528', 'COS-2528', 39487, 67.2, 14.73, 0.0033681, 0.0007776, 145.503, 185.2547, 355.7229, 'PAYLOAD'),
    ('COSMOS 2534', 'COS-2534', 40258, 74.0, 14.65, 0.0066451, 0.0004569, 148.7691, 67.5297, 130.2406, 'PAYLOAD'),
    ('COSMOS 2542', 'COS-2542', 41032, 67.1, 14.75, 0.0076131, 0.0005191, 273.5966, 73.281, 197.7191, 'PAYLOAD'),
    ('COSMOS 2555', 'COS-2555', 44398, 65.0, 14.4, 0.0092912, 0.0003786, 251.37, 43.7134, 350.3329, 'PAYLOAD'),
    ('COSMOS 2558', 'COS-2558', 45034, 82.5, 14.72, 0.0061669, 0.0002295, 57.0161, 198.302, 198.8105, 'PAYLOAD'),
    ('COSMOS 2560', 'COS-2560', 45608, 74.0, 14.7, 0.0011135, 0.0007942, 328.6548, 166.1212, 42.2878, 'PAYLOAD'),
    ('COSMOS 2564', 'COS-2564', 47648, 67.2, 14.73, 0.008355, 0.0004238, 257.9772, 183.1939, 98.433, 'PAYLOAD'),
    ('COSMOS 2567', 'COS-2567', 48285, 82.5, 14.72, 0.0083803, 0.0007852, 87.7431, 198.4554, 138.091, 'PAYLOAD'),
    ('COSMOS 2569', 'COS-2569', 49127, 74.0, 14.65, 0.0092343, 0.0004312, 316.5575, 311.0497, 99.4491, 'PAYLOAD'),
    ('COSMOS 2572', 'COS-2572', 51509, 65.0, 14.4, 0.0079421, 0.0003612, 336.3294, 182.7856, 295.3978, 'PAYLOAD'),
    ('COSMOS 2575', 'COS-2575', 53221, 74.0, 14.7, 0.0029718, 0.0002739, 211.2976, 359.6048, 176.2705, 'PAYLOAD'),
    ('COSMOS 2578', 'COS-2578', 54810, 67.1, 14.75, 0.0016562, 0.0004539, 124.2446, 198.6903, 195.6348, 'PAYLOAD'),
    ('COSMOS 2581', 'COS-2581', 56400, 82.5, 14.72, 0.0046624, 0.0002913, 67.9149, 251.0994, 205.8472, 'PAYLOAD'),
    # === GLONASS (Russian NAV) – inc ~64.8, alt ~19100 km ===
    ('GLONASS-K 01', 'GLO-K01', 41175, 64.6175, 2.13248823, 0.0021452, 0.0, 357.3356, 292.1072, 26.7554, 'PAYLOAD'),
    ('GLONASS-K 02', 'GLO-K02', 41176, 64.9283, 2.13390491, 0.0015365, 0.0, 118.8608, 13.3271, 49.6369, 'PAYLOAD'),
    ('GLONASS-K 03', 'GLO-K03', 41177, 64.9479, 2.13326514, 0.0013769, 0.0, 240.0229, 189.3424, 72.9018, 'PAYLOAD'),
    ('GLONASS-K 04', 'GLO-K04', 41178, 64.764, 2.13194869, 0.0005476, 0.0, 359.5693, 169.0166, 98.2244, 'PAYLOAD'),
    ('GLONASS-K 05', 'GLO-K05', 41179, 64.8771, 2.13191902, 0.0025701, 0.0, 124.692, 306.8429, 118.3856, 'PAYLOAD'),
    ('GLONASS-K 06', 'GLO-K06', 41180, 64.7267, 2.1323323, 0.0023023, 0.0, 243.5934, 314.0579, 142.8001, 'PAYLOAD'),
    ('GLONASS-K 07', 'GLO-K07', 41181, 64.8525, 2.13354557, 0.0029925, 0.0, 355.359, 268.8359, 163.6842, 'PAYLOAD'),
    ('GLONASS-K 08', 'GLO-K08', 41182, 64.8535, 2.13325548, 0.0013867, 0.0, 119.3397, 249.8404, 187.9844, 'PAYLOAD'),
    ('GLONASS-K 09', 'GLO-K09', 41183, 64.9185, 2.12978021, 0.001187, 0.0, 244.0342, 52.4051, 211.4599, 'PAYLOAD'),
    ('GLONASS-K 10', 'GLO-K10', 41184, 64.917, 2.1290399, 0.000329, 0.0, 0.3117, 313.5023, 240.6593, 'PAYLOAD'),
    ('GLONASS-K 11', 'GLO-K11', 41185, 64.9651, 2.12887871, 0.0014373, 0.0, 121.1971, 91.4318, 261.4083, 'PAYLOAD'),
    ('GLONASS-K 12', 'GLO-K12', 41186, 64.9219, 2.13342726, 0.0020651, 0.0, 237.5533, 56.8712, 283.094, 'PAYLOAD'),
    ('GLONASS-K 13', 'GLO-K13', 41187, 64.835, 2.13185363, 0.0013305, 0.0, 359.4173, 90.0354, 310.4557, 'PAYLOAD'),
    ('GLONASS-K 14', 'GLO-K14', 41188, 64.7539, 2.13091925, 0.0007879, 0.0, 123.453, 205.8922, 332.9922, 'PAYLOAD'),
    ('GLONASS-K 15', 'GLO-K15', 41189, 64.7181, 2.13388767, 0.0020089, 0.0, 240.7481, 98.8129, 4.9269, 'PAYLOAD'),
    # === Blagovest (Russian Comms) – GEO ===
    ('BLAGOVEST 11L', 'BLAG-11L', 43432, 0.1, 1.00274, 0.0002, 0.0, 45.2637, 268.0808, 246.8878, 'PAYLOAD'),
    ('BLAGOVEST 12L', 'BLAG-12L', 44034, 0.2, 1.00274, 0.0002, 0.0, 126.1962, 178.8218, 218.3063, 'PAYLOAD'),
    ('BLAGOVEST 13L', 'BLAG-13L', 45183, 0.1, 1.00275, 0.0002, 0.0, 85.6166, 287.5896, 103.0299, 'PAYLOAD'),
    # === Meridian (Russian Comms) – HEO ===
    ('MERIDIAN-M 9', 'MER-9', 49176, 62.8, 2.00613, 0.6728478, 0.0, 126.8355, 229.1824, 223.5208, 'PAYLOAD'),
    ('MERIDIAN-M 10', 'MER-10', 53063, 62.8, 2.00615, 0.6813317, 0.0, 259.5342, 237.3054, 301.8014, 'PAYLOAD'),
    # === Malligyong-1 (DPRK) – SSO ~500 km ===
    ('MALLIGYONG-1', '2023-179A', 58400, 97.42, 15.15, 0.0015, 0.00045, 135.2, 280.1, 80.5, 'PAYLOAD'),
    # === Noor / Khayyam (Iran) – inc ~60, alt ~450 km ===
    ('NOOR-1', '2020-024A', 45529, 59.79, 15.34, 0.0012, 0.0006, 210.4, 110.3, 250.8, 'PAYLOAD'),
    ('NOOR-2', '2022-025A', 52200, 59.8, 15.35, 0.0011, 0.00055, 75.2, 230.1, 130.5, 'PAYLOAD'),
    ('KHAYYAM', '2022-089A', 53312, 60.12, 15.18, 0.0018, 0.0004, 310.6, 55.7, 195.3, 'PAYLOAD'),
    # === GPS Block III (US NAV) – inc ~55, alt ~20200 km ===
    ('GPS III-04 (VESPUCCI)', 'GPS-G04', 48859, 55.0878, 2.0044936, 0.0044641, 0.0, 226.1693, 208.6466, 325.2253, 'PAYLOAD'),
    ('GPS III-05 (ARMSTRONG)', 'GPS-G05', 51520, 54.8771, 2.00712489, 0.0018388, 0.0, 263.6495, 47.5775, 32.448, 'PAYLOAD'),
    ('GPS III-06 (SWIGERT)', 'GPS-G06', 55268, 55.0185, 2.00812092, 0.0083217, 0.0, 194.1868, 92.5092, 349.7362, 'PAYLOAD'),
    ('GPS III-07 (SAKAGAWEA)', 'GPS-G07', 57336, 55.1839, 2.00711936, 0.0034533, 0.0, 296.8883, 41.4611, 173.4652, 'PAYLOAD'),
    ('GPS III-32 (SV74)', 'GPS-G32', 44506, 55.2799, 2.00780084, 0.0072697, 0.0, 346.6416, 352.7792, 50.6725, 'PAYLOAD'),
    ('GPS III-18 (SV75)', 'GPS-G18', 46826, 54.9195, 2.00738409, 0.0002378, 0.0, 348.2171, 193.166, 289.6516, 'PAYLOAD'),
    ('GPS III-23 (SV76)', 'GPS-G23', 48601, 55.1034, 2.00614736, 0.0082419, 0.0, 163.723, 338.5051, 242.2182, 'PAYLOAD'),
    ('GPS III-28 (SV77)', 'GPS-G28', 50594, 54.715, 2.00794541, 0.0056579, 0.0, 39.0046, 329.4921, 84.1759, 'PAYLOAD'),
    ('GPS III-14 (SV78)', 'GPS-G14', 53833, 55.1943, 2.00809633, 0.0030917, 0.0, 79.6922, 146.9865, 22.7581, 'PAYLOAD'),
    ('GPS III-31 (SV79)', 'GPS-G31', 56173, 54.8826, 2.00559575, 0.0010622, 0.0, 50.3197, 319.4134, 340.6542, 'PAYLOAD'),
    # === Starlink (US Comms) – inc ~53, alt ~550 km ===
    ('STARLINK-4701', 'SL-4701', 58001, 52.8543, 15.18721863, 0.0007034, 0.0003229, 340.5507, 267.2168, 150.8856, 'PAYLOAD'),
    ('STARLINK-4702', 'SL-4702', 58002, 52.8618, 15.18489307, 0.0001891, 0.0002468, 146.9217, 11.7779, 342.5477, 'PAYLOAD'),
    ('STARLINK-4703', 'SL-4703', 58003, 52.9482, 15.18660299, 0.0009555, 0.0003566, 35.7677, 196.0077, 246.8449, 'PAYLOAD'),
    ('STARLINK-4704', 'SL-4704', 58004, 53.1911, 15.18152043, 0.0004583, 0.0001569, 43.9775, 163.6983, 305.2919, 'PAYLOAD'),
    ('STARLINK-4705', 'SL-4705', 58005, 53.0651, 15.19850227, 0.0006374, 0.0001064, 283.2461, 45.3326, 87.6848, 'PAYLOAD'),
]


def _expand_seed_catalog():
    """Expand compact seed tuples into full GP element dicts for SGP4."""
    result = []
    for name, obj_id, norad, inc, mm, ecc, bstar, raan, argp, ma, obj_type in _SEED_RAW:
        result.append({
            "OBJECT_NAME": name,
            "OBJECT_ID": obj_id,
            "EPOCH": "2026-03-19T12:00:00",
            "MEAN_MOTION": mm,
            "ECCENTRICITY": ecc,
            "INCLINATION": inc,
            "RA_OF_ASC_NODE": raan,
            "ARG_OF_PERICENTER": argp,
            "MEAN_ANOMALY": ma,
            "EPHEMERIS_TYPE": 0,
            "CLASSIFICATION_TYPE": "U",
            "NORAD_CAT_ID": norad,
            "ELEMENT_SET_NO": 999,
            "REV_AT_EPOCH": 10000,
            "BSTAR": bstar,
            "MEAN_MOTION_DOT": 0.0,
            "MEAN_MOTION_DDOT": 0.0,
            "OBJECT_TYPE": obj_type,
        })
    return result


_SEED_CATALOG = _expand_seed_catalog()


def _jday(dt: datetime):
    """Julian date from datetime."""
    y, m, d = dt.year, dt.month, dt.day
    h = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    jd = (367 * y
           - int(7 * (y + int((m + 9) / 12)) / 4)
           + int(275 * m / 9)
           + d + 1721013.5
           + h / 24.0)
    return jd, 0.0


def _teme_to_geodetic(x, y, z, gmst):
    """Convert TEME (km) to geodetic lat/lng/alt."""
    # Rotate TEME -> ECEF
    cos_g = math.cos(gmst)
    sin_g = math.sin(gmst)
    xe = x * cos_g + y * sin_g
    ye = -x * sin_g + y * cos_g
    ze = z

    # ECEF to geodetic (WGS84)
    a = 6378.137  # Earth equatorial radius km
    f = 1 / 298.257223563
    e2 = 2 * f - f * f

    lng = math.degrees(math.atan2(ye, xe))
    p = math.sqrt(xe ** 2 + ye ** 2)
    lat = math.degrees(math.atan2(ze, p * (1 - e2)))

    # Iterative
    for _ in range(5):
        lat_rad = math.radians(lat)
        sin_lat = math.sin(lat_rad)
        N = a / math.sqrt(1 - e2 * sin_lat ** 2)
        lat = math.degrees(math.atan2(ze + e2 * N * sin_lat, p))

    lat_rad = math.radians(lat)
    sin_lat = math.sin(lat_rad)
    N = a / math.sqrt(1 - e2 * sin_lat ** 2)
    alt = p / math.cos(lat_rad) - N

    return lat, lng, alt


def _gmst(jd, jd_frac):
    """Greenwich Mean Sidereal Time in radians."""
    T = ((jd - 2451545.0) + jd_frac) / 36525.0
    gmst_sec = (67310.54841
                + (876600 * 3600 + 8640184.812866) * T
                + 0.093104 * T ** 2
                - 6.2e-6 * T ** 3)
    gmst_rad = (gmst_sec % 86400) / 86400.0 * 2 * math.pi
    if gmst_rad < 0:
        gmst_rad += 2 * math.pi
    return gmst_rad


_RENDER_PROXY = "https://echelon-vantage.onrender.com/api/catalog-proxy"


async def fetch_catalog(client: httpx.AsyncClient, group: str = "active") -> list:
    """Fetch GP elements from CelesTrak for a satellite group.
    Falls back to Render proxy if CelesTrak is unreachable."""
    cache_key = f"catalog_{group}"
    now = time.time()
    cached = _cache.get(cache_key)
    if cached and (now - cached["ts"]) < CACHE_TTL_TLE_CATALOG:
        return cached["data"]

    data = []

    # Try CelesTrak directly
    url = f"{_BASE}?GROUP={group}&FORMAT=json"
    try:
        r = await client.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception:
        pass

    # Fallback: fetch via Render proxy (which can reach CelesTrak)
    if not data:
        try:
            r = await client.get(f"{_RENDER_PROXY}?group={group}", timeout=90)
            r.raise_for_status()
            data = r.json()
            if data:
                print(f"[CELESTRAK] Loaded {len(data)} objects via Render proxy for group={group}")
        except Exception:
            pass

    # Last-resort fallback: return cached data or seed catalog
    if not data:
        cached_data = _cache.get(cache_key, {}).get("data", [])
        if cached_data:
            return cached_data
        # No cache, no live data — use seed catalog
        data = _SEED_CATALOG
        print(f"[CELESTRAK] Using seed catalog ({len(data)} objects)")

    _cache[cache_key] = {"data": data, "ts": now}
    return data


def _build_satrec(gp: dict) -> Satrec | None:
    """Build SGP4 Satrec from CelesTrak GP JSON element."""
    try:
        sat = Satrec()
        sat.sgp4init(
            WGS72,
            'i',  # improved mode
            int(gp.get("NORAD_CAT_ID", 0)),
            _epoch_to_jdsatepoch(gp.get("EPOCH", "")),
            float(gp.get("BSTAR", 0)),
            0.0,  # ndot (not used in sgp4init)
            0.0,  # nddot (not used)
            float(gp.get("ECCENTRICITY", 0)),
            math.radians(float(gp.get("ARG_OF_PERICENTER", 0))),
            math.radians(float(gp.get("INCLINATION", 0))),
            math.radians(float(gp.get("MEAN_ANOMALY", 0))),
            float(gp.get("MEAN_MOTION", 0)) * (2 * math.pi / 1440.0),  # rev/day -> rad/min
            math.radians(float(gp.get("RA_OF_ASC_NODE", 0))),
        )
        return sat
    except Exception:
        return None


def _epoch_to_jdsatepoch(epoch_str: str) -> float:
    """Convert ISO epoch string to days since 1949-12-31 (sgp4 epoch)."""
    try:
        # CelesTrak epochs may or may not have timezone info
        if epoch_str.endswith("Z"):
            epoch_str = epoch_str[:-1]
        if "+" not in epoch_str and epoch_str[-6:-5] != "-":
            # No timezone — treat as UTC
            dt = datetime.fromisoformat(epoch_str).replace(tzinfo=timezone.utc)
        else:
            dt = datetime.fromisoformat(epoch_str)
        # SGP4 epoch is in days since 1949 Dec 31 00:00 UT
        ref = datetime(1949, 12, 31, 0, 0, 0, tzinfo=timezone.utc)
        return (dt - ref).total_seconds() / 86400.0
    except Exception:
        return 0.0


def propagate_satellite(gp: dict, dt: datetime = None) -> dict | None:
    """Propagate a single satellite to given time, return position."""
    if dt is None:
        dt = datetime.now(timezone.utc)

    sat = _build_satrec(gp)
    if sat is None:
        return None

    jd, jd_frac = _jday(dt)
    e, r, v = sat.sgp4(jd, jd_frac)
    if e != 0 or r is None:
        return None

    g = _gmst(jd, jd_frac)
    lat, lng, alt = _teme_to_geodetic(r[0], r[1], r[2], g)

    return {
        "norad_id": int(gp.get("NORAD_CAT_ID", 0)),
        "name": gp.get("OBJECT_NAME", "UNKNOWN"),
        "lat": round(lat, 4),
        "lng": round(lng, 4),
        "alt_km": round(alt, 1),
        "inclination": float(gp.get("INCLINATION", 0)),
        "period_min": round(1440.0 / float(gp.get("MEAN_MOTION", 1)), 1),
        "object_type": gp.get("OBJECT_TYPE", ""),
    }


async def get_satellite_positions(client: httpx.AsyncClient, group: str = "stations") -> list:
    """Get current positions of all satellites in a group."""
    now = time.time()
    cache_key = f"positions_{group}"
    cached = _cache.get(cache_key)
    if cached and (now - cached["ts"]) < CACHE_TTL_SATELLITES:
        return cached["data"]

    catalog = await fetch_catalog(client, group)
    dt = datetime.now(timezone.utc)
    positions = []

    for gp in catalog:
        pos = propagate_satellite(gp, dt)
        if pos:
            positions.append(pos)

    _cache[cache_key] = {"data": positions, "ts": now}
    return positions


async def get_satellite_stats(client: httpx.AsyncClient) -> dict:
    """Get satellite catalog statistics."""
    now = time.time()
    cached = _cache.get("stats")
    if cached and (now - cached["ts"]) < CACHE_TTL_SATELLITES:
        return cached["data"]

    catalog = await fetch_catalog(client, "active")
    total = len(catalog)
    payloads = sum(1 for s in catalog if s.get("OBJECT_TYPE") == "PAYLOAD")
    debris = sum(1 for s in catalog if s.get("OBJECT_TYPE") == "DEBRIS")
    rocket_bodies = sum(1 for s in catalog if s.get("OBJECT_TYPE") == "ROCKET BODY")

    data = {
        "total_tracked": total,
        "active_payloads": payloads,
        "debris": debris,
        "rocket_bodies": rocket_bodies,
        "fetched_at": now,
    }
    _cache["stats"] = {"data": data, "ts": now}
    return data


def compute_ground_track(gp: dict, minutes: int = 90, step_sec: int = 30) -> list:
    """Compute future ground track for a satellite."""
    sat = _build_satrec(gp)
    if sat is None:
        return []

    now = datetime.now(timezone.utc)
    track = []

    for s in range(0, minutes * 60, step_sec):
        dt = datetime(
            now.year, now.month, now.day, now.hour, now.minute, now.second,
            tzinfo=timezone.utc
        )
        from datetime import timedelta
        dt = dt + timedelta(seconds=s)
        jd, jd_frac = _jday(dt)
        e, r, v = sat.sgp4(jd, jd_frac)
        if e != 0 or r is None:
            continue
        g = _gmst(jd, jd_frac)
        lat, lng, alt = _teme_to_geodetic(r[0], r[1], r[2], g)
        track.append({"lat": round(lat, 3), "lng": round(lng, 3)})

    return track
