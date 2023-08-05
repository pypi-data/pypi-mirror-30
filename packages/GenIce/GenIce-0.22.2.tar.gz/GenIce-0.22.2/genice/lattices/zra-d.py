# coding: utf-8
"""
Data source: Dutour Sikirić, Mathieu, Olaf Delgado-Friedrichs, and Michel Deza. “Space Fullerenes: a Computer Search for New Frank-Kasper Structures” Acta Crystallographica Section A Foundations of Crystallography 66.Pt 5 (2010): 602–615.

Cage composition:
 (12,14,15,16) = (14,4,4,4,)
"""

pairs="""
140 69
105 76
99 11
38 31
82 114
107 29
90 73
6 137
76 118
50 1
146 61
30 25
82 43
144 129
77 78
77 79
71 17
84 33
87 34
5 58
145 139
19 16
71 54
67 143
50 12
71 129
69 121
146 40
18 96
82 57
140 130
111 124
23 13
113 127
19 119
13 104
72 58
70 59
92 77
13 113
110 22
25 133
38 12
115 137
92 112
50 11
101 61
135 55
21 46
8 68
18 53
19 53
3 34
80 38
111 10
120 64
127 54
123 66
39 73
137 105
13 4
14 63
93 57
116 53
102 63
85 35
44 79
87 81
146 112
119 33
19 85
17 143
67 35
5 131
38 46
91 70
125 145
124 145
32 56
138 4
86 74
90 112
139 36
2 110
2 87
3 88
0 99
89 10
103 101
60 15
8 45
66 101
80 68
84 133
15 44
7 20
72 105
48 60
110 98
84 18
109 26
119 4
56 42
57 42
1 65
74 42
27 134
136 93
5 86
6 86
46 11
51 68
114 137
47 36
116 147
33 47
141 57
122 121
109 108
69 70
125 14
127 16
8 97
130 100
146 78
136 32
27 117
61 44
144 51
59 36
121 107
27 97
124 40
73 132
24 139
25 139
7 35
95 73
140 102
24 52
26 35
0 105
88 22
115 12
91 100
88 132
34 94
21 74
79 14
67 119
0 131
95 28
144 141
95 142
43 115
0 31
131 12
3 76
9 130
6 3
55 51
99 86
142 118
120 52
128 51
7 55
131 65
85 54
94 1
47 116
62 66
7 136
62 37
147 10
121 75
123 75
96 17
45 42
43 106
2 39
132 98
92 15
23 20
114 31
62 60
2 126
113 26
90 48
30 18
102 75
9 40
21 58
96 85
111 25
101 110
90 126
41 63
106 56
41 103
9 107
30 147
14 29
70 52
117 32
108 120
16 64
93 135
6 50
8 31
56 68
83 75
37 126
23 71
123 15
72 11
22 118
100 133
83 29
41 112
48 61
21 106
29 10
81 142
94 39
45 99
122 44
142 60
109 4
136 54
92 95
104 117
26 64
77 37
5 34
103 79
37 28
81 65
27 106
117 20
80 141
78 66
100 47
87 28
88 28
134 141
89 24
96 109
89 69
53 120
76 65
124 83
72 94
144 20
111 130
98 48
104 135
1 132
113 55
97 135
30 59
91 147
23 67
128 32
46 134
134 45
114 74
102 145
62 22
138 16
138 17
81 98
123 41
108 33
49 128
49 129
39 118
122 40
133 52
64 143
103 126
49 138
82 97
91 107
9 63
84 143
140 36
129 93
127 128
80 43
58 115
78 83
125 122
49 104
108 59
116 24
89 125
"""

waters="""
0.54285 0.0857 0.33295
0.08334 0.66667 0.25
0.12618 0.25237 0.16705
0.58333 0.66667 0.25
0.87382 0.12618 0.66705
0.3357 0.29285 0.29909
0.70715 0.6643 0.29909
0.33333 0.66667 0.57914
0.54285 0.0857 0.44273
0.0857 0.54285 0.94273
0.54049 0.45952 0.88868
0.91431 0.45715 0.33295
0.12618 0.87382 0.33295
0.79049 0.20951 0.61132
0.29285 0.3357 0.97136
0.54285 0.0857 0.05728
0.25236 0.12618 0.66705
0.87382 0.74764 0.66705
0.66667 0.58333 0.75
0.29285 0.3357 0.70091
0.0857 0.54285 0.55728
0.20951 0.41903 0.38868
0.74764 0.87382 0.16705
0.91904 0.45952 0.61132
0.25236 0.12618 0.83295
0.87382 0.74764 0.83295
0.45715 0.9143 0.66705
0.95715 0.29285 0.47136
0.54285 0.45715 0.16705
0.45715 0.54285 0.94273
0.6643 0.70715 0.79909
0.45951 0.91904 0.38868
0.29285 0.3357 0.52864
0.91667 0.33333 0.75
0.33333 0.41667 0.25
0.33333 0.66667 0.64841
0.87382 0.12618 0.83295
0.45952 0.54048 0.11132
0.20951 0.79049 0.38868
0.95715 0.29285 0.20091
0.04285 0.70715 0.97136
0.95715 0.29285 0.02864
0.54285 0.45715 0.44273
0.0 0.0 0.41409
0.3357 0.04285 0.02864
0.66667 0.33333 0.42086
0.08097 0.54049 0.38868
0.04285 0.3357 0.79909
0.20952 0.79049 0.11132
0.0 0.0 0.58591
0.95715 0.6643 0.29909
0.29285 0.95716 0.52864
0.29285 0.95715 0.79909
0.41667 0.33333 0.75
0.54049 0.45952 0.61132
0.45715 0.9143 0.55728
0.3357 0.29285 0.47136
0.70715 0.6643 0.47136
0.12618 0.25237 0.33295
0.6643 0.95715 0.79909
0.45951 0.91904 0.11132
0.12618 0.87382 0.06405
0.58097 0.79049 0.11132
0.04285 0.3357 0.97136
0.29285 0.95715 0.70091
0.33333 0.91666 0.25
0.74764 0.87382 0.06405
0.0857 0.54285 0.66705
0.3357 0.04285 0.47136
0.54049 0.08097 0.88868
0.45715 0.9143 0.83295
0.79049 0.58097 0.61132
0.95716 0.29285 0.29909
0.91431 0.45715 0.16705
0.45951 0.54048 0.38868
0.6643 0.95715 0.97136
0.58333 0.91666 0.25
0.54285 0.45715 0.05728
0.70715 0.6643 0.02864
0.3357 0.29285 0.02864
0.12618 0.87382 0.43596
0.3357 0.04285 0.20091
0.74764 0.87382 0.43596
0.6643 0.70715 0.97136
0.91667 0.58333 0.75
0.45715 0.54285 0.66705
0.54285 0.45715 0.33295
0.3357 0.29285 0.20091
0.70715 0.6643 0.20091
0.41903 0.20951 0.88868
0.08097 0.54049 0.11132
0.33334 0.66667 0.85159
0.66667 0.33333 0.07914
0.6643 0.70715 0.52864
0.08334 0.41667 0.25
0.66667 0.33334 0.14841
0.6643 0.70715 0.70091
0.70715 0.04285 0.47136
0.12618 0.87382 0.16705
0.66667 0.33334 0.35159
0.0857 0.54285 0.83295
0.0 0.0 0.08591
0.87382 0.12618 0.93596
0.12618 0.25237 0.06405
0.87382 0.12618 0.56405
0.70715 0.04285 0.29909
0.12618 0.25237 0.43596
0.33334 0.66667 0.92086
0.66667 0.08333 0.75
0.6643 0.95715 0.70091
0.0 0.0 0.14841
0.79049 0.58097 0.88868
0.91431 0.45715 0.05728
0.54049 0.08097 0.61132
0.58097 0.79049 0.38868
0.0 0.0 0.35159
0.29285 0.3357 0.79909
0.04285 0.3357 0.52864
0.70715 0.04285 0.20091
0.04285 0.3357 0.70091
0.41667 0.08333 0.75
0.45715 0.9143 0.94273
0.29285 0.95715 0.97136
0.70715 0.04285 0.02864
0.87382 0.74764 0.93596
0.25236 0.12618 0.93596
0.20951 0.41903 0.11132
0.41903 0.20951 0.61132
0.25236 0.12618 0.56405
0.87382 0.74764 0.56405
0.91904 0.45952 0.88868
0.3357 0.04285 0.29909
0.95716 0.6643 0.20091
0.04285 0.70715 0.79909
0.9143 0.45715 0.44273
0.6643 0.95715 0.52864
0.45715 0.54285 0.55728
0.74764 0.87382 0.33295
0.0 0.0 0.64841
0.0 0.0 0.85159
0.79049 0.20951 0.88868
0.95715 0.6643 0.47136
0.54285 0.0857 0.16705
0.04285 0.70715 0.70091
0.04285 0.70715 0.52864
0.0 0.0 0.91409
0.95716 0.6643 0.02864
0.45715 0.54285 0.83295
"""

coord= "relative"

cages="""
16 0.66667 0.33333 -0.02708
12 0.34279 0.1714 0.11455
14 -0.33333 -0.66667 0.6891
12 0.17139 0.34279 0.61455
12 -0.34279 -0.1714 0.61455
15 0.66667 0.33333 0.25
12 0.34279 0.1714 -0.61455
16 -0.66667 -0.33333 -0.52708
12 0.0 0.0 0.0
14 0.33333 0.66667 0.1891
12 -0.17139 -0.34279 0.11455
12 -0.1714 0.17139 0.11455
15 0.0 0.0 0.75
12 0.17139 -0.1714 -0.11455
12 -0.17139 0.1714 -0.61455
14 0.66667 0.33333 -0.1891
16 0.33333 0.66667 0.02708
15 -0.66667 -0.33333 0.75
16 -0.33333 -0.66667 0.52708
15 0.0 0.0 0.25
14 -0.66667 -0.33333 -0.6891
12 0.1714 -0.17139 0.61455
12 0.1714 0.34279 -0.11455
12 -0.34279 -0.1714 -0.11455
12 0.0 0.0 0.5
12 -0.1714 -0.34279 -0.61455
"""

bondlen = 3

celltype = 'triclinic'

cell = """
12.74668553361935 0.0 0.0
-6.373342766809673 11.038953486165962 0.0
2.8888262590074906e-15 5.003593854840102e-15 47.17811308564729
"""

density = 0.6663888581464387


