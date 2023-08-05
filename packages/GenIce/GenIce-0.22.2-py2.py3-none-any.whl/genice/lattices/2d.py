# coding: utf-8
"""
A hydrogen-disordered counterpart of ice II.
Note: Due to the technical limitation in the GenIce algorithm, the minimum lattice size is larger than the crystallographic unit cell size.

Data source: Nakamura, Tatsuya et al. “Thermodynamic Stability of Ice II and Its Hydrogen-Disordered Counterpart: Role of Zero-Point Energy.” The Journal of Physical Chemistry B 120.8 (2015): 1843–1848.
"""

density = 1.2     #default density


bondlen = 3     #bond threshold	 
celltype = "rect"

cell="""
13.25 22.9496665056 6.19244244367
"""
coord = "absolute"

waters="""
1.8266 2.4421 0.9143
1.8266 10.0920 5.0426
8.4516 6.2671 2.9784
10.7561 0.4625 0.9143
10.7561 8.1123 5.0426
4.1311 4.2874 2.9784
8.0058 9.1855 0.9143
1.3808 5.3605 5.0426
8.0058 1.5356 2.9784
5.2740 9.4428 0.2553
11.8990 5.6179 4.3836
5.2740 1.7930 2.3194
9.5945 11.4225 0.2553
2.9695 7.5976 4.3836
9.5945 3.7726 2.3194
12.3448 2.6995 0.2553
12.3448 10.3494 4.3836
5.7198 6.5245 2.3194
8.4516 13.9170 0.9143
8.4516 21.5668 5.0426
1.8266 17.7419 2.9784
4.1311 11.9373 0.9143
4.1311 19.5872 5.0426
10.7561 15.7622 2.9784
1.3808 20.6603 0.9143
8.0058 16.8353 5.0426
1.3808 13.0104 2.9784
11.8990 20.9177 0.2553
5.2740 17.0927 4.3836
11.8990 13.2678 2.3194
2.9695 22.8973 0.2553
9.5945 19.0724 4.3836
2.9695 15.2474 2.3194
5.7198 14.1743 0.2553
5.7198 21.8242 4.3836
12.3448 17.9993 2.3194
11.6473 2.3563 3.7643
5.0223 13.8312 3.7643
11.6473 10.0062 1.7001
5.0223 6.1813 5.8284
5.9200 9.0104 3.7643
12.5450 5.1854 1.7001
5.9200 1.3605 5.8284
3.0211 0.7233 3.7643
3.0211 8.3732 1.7001
9.6461 4.5483 5.8284
8.7032 9.5286 3.5978
2.0782 5.7037 1.5336
8.7032 1.8787 5.6619
1.1806 2.8746 3.5978
1.1806 10.5245 1.5336
7.8056 6.6995 5.6619
4.0795 11.1616 3.5978
10.7045 7.3367 1.5336
4.0795 3.5118 5.6619
5.0223 21.4810 1.7001
11.6473 17.6561 5.8284
12.5450 20.4852 3.7643
5.9200 16.6603 1.7001
12.5450 12.8353 5.8284
9.6461 12.1981 3.7643
9.6461 19.8480 1.7001
3.0211 16.0231 5.8284
2.0782 21.0035 3.5978
8.7032 17.1785 1.5336
2.0782 13.3536 5.6619
7.8056 14.3494 3.5978
7.8056 21.9993 1.5336
1.1806 18.1744 5.6619
10.7045 22.6365 3.5978
4.0795 18.8115 1.5336
10.7045 14.9866 5.6619
"""
