# coding: utf-8
"""
A continuous random network of Sillium.

Mousseau, N, and G T Barkema. “Fast Bond-Transposition Algorithms for Generating Covalent Amorphous Structures.” Current Opinion in Solid State and Materials … 5.6 (2001): 497–502. Web.
"""

celltype="rect"
cell="""
26.778 26.778 26.778
"""
density=0.96
coord="absolute"
waters="""
-12.18 5.17 12.07
2.86 -7.62 13.36
-0.45 12.45 12.85
-1.12 3.37 -6.19
-8.5 -7.28 -8.15
10.76 -7.58 1.19
-12.15 -8.17 -2.72
-10.18 -11.16 0.74
6.78 -7.32 -1.67
3.55 -0.22 0.57
12.06 3.23 -4.15
-3.42 9.85 5.56
-5.75 0.72 -7.96
10.67 -1.42 2.0
-9.53 11.79 1.1
0.63 -9.66 10.78
-3.53 5.5 -2.85
-11.48 -5.54 7.22
-0.31 -9.91 12.75
-10.81 -0.76 5.63
-7.64 7.96 -10.88
-13.22 -10.39 12.62
2.77 -13.23 11.11
-11.85 -5.75 -12.97
-9.96 3.23 -0.01
-6.43 -3.26 10.64
-11.75 -0.96 -8.24
10.36 -9.17 -2.61
5.32 -13.26 8.42
13.16 0.6 9.21
-5.7 -2.38 -0.52
0.13 11.02 0.06
-10.08 13.26 -13.16
-8.64 -8.03 9.03
-6.17 -12.19 -1.29
5.56 2.84 -3.33
-7.38 6.36 -12.54
10.32 0.71 -1.95
-11.28 -9.33 1.69
10.03 -12.81 -4.03
9.06 -2.04 0.32
-5.69 5.02 -12.21
-10.8 -0.31 -6.22
6.56 -3.56 -6.63
-5.13 -11.72 -5.28
2.2 3.16 -4.66
-9.92 -1.36 7.66
3.94 -6.14 -8.43
-9.87 9.25 12.54
0.48 -10.26 0.74
-10.67 -4.53 -11.43
-8.4 -3.26 3.03
4.4 -11.03 -0.34
-5.87 -12.06 -11.11
6.42 -4.25 2.74
-9.22 0.1 -0.58
-4.1 -1.01 -4.0
2.26 10.41 8.2
-4.87 6.82 11.33
12.16 12.88 9.86
3.88 -2.47 5.89
7.81 2.92 -3.74
-0.87 -7.75 -13.31
9.03 2.79 4.08
11.35 1.03 -3.84
12.78 5.93 2.68
-2.03 12.42 -9.67
5.08 -1.13 -8.54
10.05 12.3 -9.36
-5.22 -4.94 4.28
7.18 -1.12 -11.79
5.6 -8.64 -10.84
0.57 6.57 -12.85
-3.53 -9.47 -12.28
3.11 0.45 -12.11
1.62 -13.38 13.27
-8.57 -6.55 1.49
-6.66 -12.59 0.99
-11.31 10.18 -7.16
-1.87 -6.99 11.42
-7.96 -4.68 6.85
13.0 4.05 8.4
-10.74 0.84 11.47
-6.26 -11.96 4.35
4.55 10.38 -0.1
-9.48 -5.74 8.39
5.24 12.88 2.71
-6.88 6.08 -7.69
-11.72 -10.26 -10.39
-6.96 -13.2 -4.82
1.53 5.74 1.43
-5.55 0.26 5.09
-4.16 7.85 9.32
-8.65 -12.0 -6.11
-8.39 0.75 11.87
-5.44 6.82 -5.96
-2.69 2.93 -9.57
9.28 -8.16 -9.77
12.72 -6.53 4.34
4.61 13.23 -5.53
-12.06 8.03 -7.41
1.82 -6.76 1.45
6.93 11.74 -2.6
-0.05 11.15 -3.49
-3.95 6.48 4.11
9.61 7.75 8.56
-4.43 10.14 9.82
1.24 -6.22 -3.38
6.33 -7.73 10.82
-3.45 -8.33 6.97
-12.02 -6.39 3.61
2.84 4.29 -11.39
-8.39 -4.11 11.65
-13.0 11.39 -7.83
12.59 -8.88 11.1
8.97 -3.9 -11.14
5.38 3.31 -1.19
11.02 11.53 -12.9
8.94 11.94 2.83
-3.03 -1.63 -12.12
-8.91 -4.87 4.69
-2.96 9.48 -13.04
-0.46 11.49 4.58
5.92 12.34 11.82
-6.74 2.56 -3.49
-7.88 2.71 13.23
9.91 -1.69 4.28
-6.53 -8.8 8.45
-1.38 9.24 0.33
12.87 11.42 -2.58
-3.56 -0.73 4.47
-7.35 -0.66 -7.14
6.23 10.07 -4.26
-12.9 -3.66 7.79
-5.91 4.34 -8.58
0.66 -4.64 4.68
-11.28 -9.65 5.28
4.45 12.09 10.21
2.75 -10.61 -9.38
9.29 0.15 11.71
2.23 -3.31 -11.67
6.87 -8.19 -3.79
6.82 1.55 -0.8
-9.32 -1.04 -10.53
10.26 9.69 -0.25
-8.62 -7.04 3.77
7.68 7.7 -1.69
9.82 -9.21 -0.25
5.23 -9.76 -3.72
1.01 6.16 3.64
-2.19 -12.59 -11.08
1.81 5.59 -9.79
11.19 -4.99 -6.38
-8.14 -12.57 -8.33
-9.51 -5.69 -4.79
4.94 11.47 4.78
8.84 -7.47 4.6
-0.63 -9.44 -9.84
-2.67 4.98 -6.57
12.02 -4.31 4.05
-7.44 11.64 -10.99
-12.94 -9.16 -12.3
-9.28 7.91 9.08
-10.82 -2.31 -2.68
-1.54 -11.69 8.43
-2.6 -9.72 8.85
-0.4 -3.6 -0.84
7.37 -1.8 -3.12
2.08 0.94 -5.62
9.24 10.8 -7.9
8.09 -5.35 -1.65
-1.06 7.17 6.79
4.08 -10.24 1.8
8.66 5.78 8.94
-12.46 7.54 -11.71
3.49 -8.36 -11.52
-4.7 7.71 0.36
6.61 -8.71 7.18
4.91 -10.95 -8.46
-2.23 -2.32 -1.27
13.02 10.95 13.17
-1.35 -12.96 2.1
10.28 -9.09 4.46
-6.32 10.89 -0.07
0.91 2.44 1.87
12.14 -11.12 6.27
5.46 -12.2 12.59
12.59 8.6 -10.43
-3.92 -11.09 -10.71
-3.49 -12.33 -3.99
-2.36 -6.24 -2.51
3.39 9.59 4.5
11.05 7.98 6.67
10.98 -2.89 -5.46
1.42 6.99 6.9
7.53 -11.13 12.15
10.5 6.4 5.38
5.39 -1.82 7.46
-3.89 -10.54 -8.51
-12.27 -2.54 2.08
-10.95 -12.45 -5.99
3.97 -0.24 -4.84
6.04 8.55 8.36
-1.76 1.84 -7.92
-5.21 -2.79 -5.04
-0.9 13.08 -0.01
11.13 -9.14 6.44
0.06 -0.62 3.88
1.91 -10.26 2.4
10.65 -2.18 9.29
-3.14 -5.83 1.34
-0.69 10.42 -12.65
-3.04 -4.33 4.51
-2.54 -3.89 2.38
0.59 -11.14 9.05
-11.33 -2.45 9.15
4.52 3.3 -10.54
-7.75 -6.23 12.51
-10.3 -4.34 10.26
5.23 -3.4 9.18
-2.46 1.97 2.74
-8.4 1.07 -4.15
-8.63 6.59 2.69
9.42 -8.28 -6.18
3.33 -2.35 -4.29
-5.59 -0.73 -2.26
12.24 -6.84 -5.31
-3.14 6.51 -9.98
6.94 9.07 -10.48
5.52 4.14 6.74
-10.47 -7.22 -9.34
5.42 10.72 -9.85
1.59 11.41 1.8
7.8 6.35 -13.16
6.46 -11.6 -3.09
1.98 -1.74 0.82
10.68 -3.22 -3.18
-5.26 4.67 3.92
-10.96 -10.62 11.9
-3.47 9.45 -0.42
-2.25 -9.14 -4.55
-7.01 12.76 5.11
2.93 -10.47 -11.66
-5.72 7.43 7.49
-9.09 -3.6 -7.81
4.44 -1.68 11.99
4.04 9.18 -3.89
12.01 -7.73 -12.03
9.97 5.5 -10.15
8.94 2.66 -12.5
-0.17 12.29 6.59
-13.02 8.8 -0.46
2.44 7.75 0.78
12.35 8.98 9.81
4.34 -4.12 -12.01
-2.16 5.71 5.37
-0.26 -3.4 -7.94
9.32 4.35 10.82
9.0 -12.15 7.96
2.04 -1.74 6.84
-9.76 2.44 -9.88
-3.49 -1.77 2.25
10.26 4.14 0.76
-10.69 -8.22 3.74
-13.31 9.11 11.77
4.53 -12.06 -12.1
9.5 2.2 1.98
-10.96 0.34 -9.95
11.2 2.94 5.14
12.16 -12.26 -6.96
0.86 -6.45 -12.97
10.55 9.8 -6.31
-2.33 11.45 -2.85
2.9 -4.92 11.34
0.47 -8.14 -2.28
11.62 5.89 -13.33
12.85 10.01 3.94
-4.01 -0.2 11.2
9.37 6.66 3.27
-8.68 -0.9 2.8
8.06 9.52 8.65
1.67 -9.85 -3.21
8.16 9.1 0.09
-1.41 -10.74 1.96
-12.96 12.57 0.75
-8.13 3.01 3.26
-0.87 -4.69 -6.12
-5.05 -12.02 2.42
-9.96 2.29 1.97
-9.54 -11.36 -13.33
0.51 12.92 3.2
-9.9 -10.02 8.43
-2.08 -0.97 0.66
-10.59 -12.88 3.83
-3.48 9.46 -2.63
-8.1 -1.9 -8.86
-5.02 -8.75 -7.72
-5.63 1.34 -1.71
-6.16 4.62 0.37
1.75 4.05 -2.48
-11.39 12.38 11.7
-0.03 1.6 -11.84
-1.97 6.98 8.86
6.13 5.15 2.25
7.98 8.35 2.47
-6.73 -9.97 -1.49
-3.08 3.99 6.61
13.1 -2.82 5.65
1.28 -2.36 -5.17
5.16 8.56 12.41
-0.15 7.05 10.33
4.21 -1.86 3.67
6.35 1.85 6.87
9.31 12.45 -2.51
5.01 1.34 -11.63
-7.4 -0.79 13.19
8.26 -11.6 -4.53
10.41 -12.3 -8.52
-8.49 9.05 5.6
1.29 -4.69 2.47
-5.26 6.06 -1.17
-12.57 5.76 7.79
2.21 -1.19 -10.7
-12.24 4.55 -6.75
-4.0 -3.04 13.24
-11.92 -8.82 -8.56
-4.45 2.06 -10.75
-8.08 11.84 10.19
-11.39 10.01 11.14
2.18 -5.8 5.96
7.52 -5.49 -10.44
2.34 13.1 -5.94
-0.07 -1.51 1.74
3.14 -6.23 9.43
-2.35 -12.95 -13.35
0.74 -4.72 12.34
4.76 -4.49 1.09
10.81 9.83 5.27
11.81 6.51 -5.47
-1.8 2.03 6.32
-7.34 0.33 9.66
3.33 -5.58 -2.74
2.68 3.78 1.35
11.12 -3.61 12.7
7.1 -8.58 1.77
-12.97 -13.19 8.45
8.81 8.9 -9.36
-0.97 -11.89 -6.65
7.73 -5.56 -6.71
0.37 -2.36 5.46
4.32 6.24 -7.17
0.33 -7.95 0.08
1.36 -2.18 -1.17
-5.77 -9.47 -5.55
-7.1 10.9 -2.16
-7.62 9.52 -7.43
1.0 -11.21 -12.63
-12.76 -4.95 -2.6
-10.5 -7.59 0.49
9.34 -4.7 -13.26
8.45 3.84 -10.5
-2.57 -6.24 -9.97
-7.17 6.47 -2.41
7.07 -10.28 3.51
8.74 -9.33 -4.25
6.22 6.9 -11.45
-12.18 -0.46 1.52
4.57 -9.41 8.08
5.04 -8.08 2.05
11.15 10.97 9.19
11.88 0.69 -10.81
-0.06 1.67 -0.14
1.73 12.48 -9.78
-2.27 4.73 8.61
9.15 8.92 11.76
11.68 -4.27 0.1
6.22 -6.44 12.75
9.25 -4.29 0.22
-8.49 -8.0 11.35
-6.03 11.09 -6.97
1.94 2.38 -12.33
-7.95 4.28 -2.7
-12.91 -1.45 -2.15
7.27 1.24 4.85
3.32 10.55 -2.12
-7.07 -3.62 -11.89
-4.97 8.2 5.31
2.95 -7.79 5.02
-0.91 -1.28 -7.44
-7.35 12.11 1.44
-10.9 -4.28 -1.66
13.33 -10.98 8.09
7.35 -4.85 6.28
3.72 8.21 -7.73
-4.28 -6.81 11.11
-9.19 -5.78 -2.59
3.51 2.76 -8.43
-4.81 -9.86 1.83
-3.15 -9.78 -1.31
-1.51 -9.77 4.11
13.08 7.9 7.87
3.06 -3.29 2.12
-10.46 1.84 -3.44
-8.49 -5.05 -10.95
-3.03 -1.78 9.87
13.3 12.77 11.98
0.52 -1.12 9.95
-11.24 -7.81 -12.97
-6.61 -7.12 0.96
2.52 8.54 -5.82
-6.52 -11.02 7.49
6.14 -3.0 -8.81
8.78 -7.01 2.35
-8.95 -1.71 -1.81
-12.62 6.53 -5.7
1.11 6.76 -4.98
-6.85 7.56 12.25
5.81 -2.68 -13.15
7.3 -3.99 10.17
3.51 -3.03 10.44
-6.04 1.78 6.56
10.47 -13.08 13.22
11.48 2.27 -9.16
-4.44 -2.3 8.0
-1.64 4.08 12.05
0.17 9.59 5.22
-12.59 11.01 -0.79
5.02 5.93 -4.96
-0.59 10.14 -5.46
-9.09 9.66 -2.03
-6.76 -9.36 12.15
7.37 -1.76 -5.5
8.62 2.3 -1.8
13.08 -1.01 12.2
2.39 -7.0 -9.89
-7.25 1.21 -0.23
10.35 8.63 -11.22
1.27 7.97 -1.34
11.08 -4.95 -8.69
10.82 -5.77 7.65
9.32 -5.48 5.81
-7.84 3.41 -0.54
12.31 -3.14 1.98
7.18 7.57 11.78
11.04 -3.29 -10.27
-12.84 7.94 3.2
-4.37 -12.42 -7.34
7.83 -1.13 4.9
12.06 -11.55 1.5
-11.31 -3.35 -8.08
2.87 -4.87 -6.88
1.14 -5.31 -10.91
3.6 4.55 11.99
-6.42 9.73 12.85
-10.29 11.38 -1.07
7.66 1.68 8.72
8.44 2.14 -5.68
6.78 1.45 -6.92
9.01 10.57 10.3
12.17 -13.2 3.25
12.46 -10.51 -5.58
-6.63 7.81 -4.33
9.63 9.87 -12.95
-1.03 3.62 2.69
6.17 0.15 -10.21
5.28 3.1 -7.07
-0.97 7.82 -5.05
-4.4 10.65 12.17
1.53 -8.14 3.24
-6.13 13.13 -8.07
-3.03 -5.38 -6.29
2.91 1.3 10.97
12.63 1.0 4.91
6.52 -3.93 -2.5
-4.18 -4.53 8.11
6.26 -6.74 -5.45
0.15 3.26 6.15
5.68 1.61 3.03
-12.51 -13.06 -7.77
-4.47 -8.31 -4.22
-7.88 -5.21 -8.66
6.97 -7.19 -11.96
3.5 8.26 10.75
-1.85 2.13 -4.24
7.21 5.62 5.88
6.73 -11.2 -0.85
9.16 -12.66 11.51
-9.99 8.88 -4.05
5.02 -3.33 -0.87
-3.89 11.28 -9.74
-9.93 5.37 11.72
2.72 6.11 5.15
7.9 0.94 -8.86
-5.75 -7.74 6.74
-1.68 -8.46 -2.61
-12.44 2.08 8.16
7.72 10.6 -12.13
-1.86 -4.64 7.69
1.38 5.83 8.93
-8.79 -0.19 4.79
4.01 -4.64 6.01
-6.54 2.75 -7.3
-1.33 -5.91 4.81
-6.75 0.08 1.77
-11.5 5.9 -10.23
9.82 -10.97 1.23
-9.34 7.0 4.89
11.25 -0.29 8.06
-6.55 -1.86 8.87
5.24 -11.65 -6.54
1.51 0.82 9.27
-4.19 3.7 0.74
1.28 -12.18 -9.09
6.04 5.13 -8.03
-13.18 10.2 -4.18
0.67 -1.01 12.26
2.83 -0.34 12.57
-1.01 -2.4 -11.5
2.99 -12.9 -0.51
-9.27 12.44 4.97
-11.75 -9.45 7.46
-12.7 -1.86 -12.59
-11.58 7.33 5.16
-0.12 2.2 9.43
-12.22 -0.78 10.52
1.6 -2.69 9.03
-7.81 8.6 2.43
-12.26 12.81 6.46
-8.68 -9.67 -2.61
-4.71 -5.67 -10.54
-8.08 -6.77 -12.01
-5.96 1.87 8.83
13.3 -9.92 2.46
11.67 -0.93 5.77
0.95 8.85 -13.2
2.09 2.19 5.61
3.69 4.0 5.23
4.27 6.98 -3.1
-9.62 -11.02 4.89
10.92 -1.64 11.61
-13.15 5.33 -8.83
-10.92 12.82 -11.11
-3.05 7.21 12.93
5.72 -5.26 4.66
-12.72 -12.82 4.57
0.8 -8.16 -6.7
-5.7 9.84 -3.57
2.04 2.93 12.15
5.41 -1.31 -0.2
-4.02 11.84 6.66
-4.17 11.39 0.31
9.25 3.85 -6.87
-0.1 -10.93 5.42
5.7 7.45 2.54
11.23 2.02 -12.53
-0.22 11.06 -10.33
-11.99 -10.55 -5.15
-1.96 -1.62 -3.38
-9.33 4.18 9.8
4.59 8.13 0.56
-10.77 9.64 8.86
-13.27 2.68 -5.84
7.51 -12.28 -6.49
-3.85 1.1 -5.04
-12.0 1.04 -4.9
7.92 12.42 10.66
9.99 9.24 -4.12
-6.5 9.74 -11.65
12.98 -5.93 -9.45
11.09 7.69 -7.18
-5.08 -8.67 -2.07
10.48 -12.93 6.29
-1.93 1.08 8.43
-1.32 -12.52 6.43
-1.69 8.65 2.42
1.37 -13.12 9.51
-6.83 -8.69 -9.12
5.13 -11.59 3.37
4.47 -3.9 -5.57
-9.94 6.82 0.73
-6.74 -9.33 0.69
12.57 -12.32 13.26
11.29 6.43 -1.93
1.01 4.55 -6.06
-7.79 -10.45 3.94
-3.9 8.19 -7.24
-0.8 -7.74 3.49
-10.03 -11.59 10.03
-3.72 -5.6 -0.75
-5.44 2.9 -5.19
8.09 0.64 -13.09
11.89 -4.13 8.9
8.88 -6.09 -8.84
-5.77 -5.49 6.57
-10.16 -11.27 -1.73
-11.16 12.85 -4.29
-5.0 -6.55 2.61
-11.49 8.42 1.33
0.66 -12.1 -0.73
-12.63 0.23 -11.56
-11.8 -2.62 4.49
10.71 7.73 10.52
-6.59 10.72 8.79
5.16 -11.08 9.39
-11.11 10.63 -4.93
-7.21 -2.13 -5.31
7.92 4.94 3.72
11.03 -11.29 -10.41
-8.99 6.33 -6.97
7.94 4.26 12.73
0.31 -0.47 -5.47
12.62 1.2 12.65
-4.39 13.05 12.47
9.32 6.95 -8.38
12.03 1.22 -0.41
6.69 6.63 9.58
-4.28 -3.55 -7.02
3.56 -11.7 5.18
-7.43 0.03 -11.41
-0.34 12.4 10.54
4.28 -9.71 -5.79
-4.48 7.99 -9.4
-8.57 -2.66 -13.38
-4.35 5.03 -5.03
5.9 3.47 12.11
-9.14 0.74 8.29
-11.68 5.28 -2.44
13.09 -6.88 -1.83
1.96 12.51 7.5
-4.47 2.86 2.76
8.67 10.01 3.96
-6.71 8.71 0.57
-2.49 3.87 -12.72
12.49 11.64 2.25
8.67 4.32 -0.67
1.01 9.92 -6.93
-9.57 8.73 -10.15
12.65 -12.61 -11.18
-6.87 4.05 9.37
-10.62 -8.47 11.7
-4.26 9.59 -11.0
-7.9 2.15 -11.29
-9.99 4.41 -6.2
-6.87 -8.43 4.62
-1.91 7.04 -6.99
4.79 0.43 7.77
-10.85 9.13 -12.01
12.31 2.12 10.81
-9.21 -7.81 -6.03
4.34 -7.2 -1.38
11.62 7.83 -0.02
-12.45 -7.26 -4.98
1.81 -3.0 -7.42
-0.48 4.71 4.45
9.89 -4.04 4.19
1.08 -6.1 -5.78
-3.63 2.24 -0.86
4.95 -7.78 -7.04
-5.51 -1.8 1.66
-11.09 -4.1 0.69
7.27 -4.29 12.46
9.25 2.67 -8.87
-10.04 0.03 1.53
2.87 8.94 -11.75
-5.28 4.6 11.0
-12.32 -7.56 10.38
4.7 -5.28 8.1
-8.01 12.41 -13.01
-7.65 -10.85 -9.9
-1.08 10.57 8.04
6.12 -0.26 -1.96
-12.47 -7.41 7.95
8.37 -2.3 9.03
10.1 13.18 -0.46
12.93 4.32 10.59
4.49 3.75 -4.95
2.26 7.98 -9.66
-1.13 3.5 -11.05
0.58 -2.86 -13.2
11.68 -8.54 -6.54
7.79 8.45 -3.94
-12.22 -3.51 -5.98
-6.3 -12.84 -13.24
-0.98 6.2 12.23
-7.88 -2.44 7.2
-13.19 8.43 -2.86
12.22 5.02 4.7
-5.46 -6.45 12.88
3.99 -6.65 0.76
12.39 4.01 -12.13
3.99 13.11 6.46
-3.26 3.72 10.42
4.42 10.32 -7.85
7.64 -0.32 10.09
-0.12 2.64 11.6
-3.9 -6.08 -4.24
11.11 5.56 11.32
10.9 6.25 1.64
-4.26 -1.46 -10.11
6.47 -2.06 3.21
13.2 10.7 -9.99
-3.7 -10.42 10.65
-6.23 1.51 3.23
-7.63 -0.93 -3.4
1.39 13.03 -3.86
7.36 6.43 -5.06
-11.11 5.11 -0.12
7.55 -9.05 -0.34
-6.59 5.29 7.34
-2.26 5.02 1.29
-5.31 3.9 6.05
-5.12 -4.67 -12.54
-4.65 -4.81 10.23
-3.33 -13.26 3.14
13.2 -0.38 -4.07
-10.6 -2.33 -5.0
3.71 -9.46 -2.04
8.38 -11.34 -8.2
-10.09 10.43 4.64
-1.17 7.18 -9.21
9.43 -1.53 -2.01
4.31 7.41 -12.6
-11.42 3.29 4.95
-3.85 -12.05 -1.78
7.32 1.21 1.35
0.96 -9.83 7.16
3.1 -9.69 6.42
9.22 -0.98 -8.66
-9.44 10.38 -8.52
0.88 0.16 -1.71
12.39 -7.21 6.65
8.31 -12.46 0.36
-5.67 12.7 -10.1
-1.57 -11.34 -4.42
-6.18 -7.55 -11.01
-12.52 5.26 5.69
-2.91 -3.61 11.25
-2.45 10.48 3.67
-1.92 -8.08 -11.32
10.52 11.51 6.9
10.09 -9.03 8.4
3.1 12.81 -11.74
-9.0 4.69 -13.08
-8.88 -11.5 6.96
11.32 0.75 1.68
-12.09 8.99 6.97
13.02 -11.77 -2.26
-2.41 11.42 -6.25
-10.07 4.06 -3.74
-0.91 -8.35 9.79
6.84 -8.64 5.05
-7.44 -11.48 12.35
8.26 -9.13 -8.11
5.75 -0.37 -6.36
12.28 -5.0 11.11
-0.28 3.71 -1.4
3.42 5.85 10.01
10.47 11.44 1.14
8.16 11.15 7.18
-12.07 -10.43 -2.78
4.53 3.67 2.96
2.94 0.99 -1.32
1.97 -9.87 -5.62
-4.84 -11.3 5.83
-5.73 -6.66 -1.03
-6.71 9.27 4.18
2.39 11.55 -7.67
-3.63 4.69 -8.61
0.04 -0.4 -10.61
-2.98 11.48 8.61
-1.72 -6.71 6.75
-7.69 -3.42 -0.76
8.71 5.0 -3.94
-9.92 9.9 2.32
-4.0 2.2 -12.89
-6.1 12.31 7.3
7.23 12.6 1.48
0.04 4.05 8.33
-7.58 8.82 7.79
-3.58 -9.48 5.09
12.32 3.49 -0.23
-5.48 0.28 -10.15
-3.28 -2.37 5.93
6.52 -11.98 -9.5
10.6 10.68 -2.43
7.42 -2.43 6.86
5.64 6.87 -1.16
-5.7 -4.47 -8.78
6.22 7.94 6.1
4.75 1.27 9.93
-0.52 5.49 0.06
-10.83 1.48 -1.29
-10.88 -13.23 1.62
-12.1 1.59 13.35
2.45 4.76 -7.83
-2.32 3.48 -2.41
11.29 -7.08 -3.13
5.99 -8.85 -8.57
1.98 9.34 2.55
5.75 -0.1 11.27
-0.22 -11.44 -10.68
-1.41 -2.52 6.86
-5.27 -8.87 10.47
-10.0 -7.78 -1.85
-11.34 -8.71 -6.31
3.56 12.21 1.1
8.33 12.59 -10.87
-0.46 -3.7 1.48
0.41 10.38 9.68
-5.71 11.64 -4.97
6.64 -6.37 7.76
-8.38 7.81 -0.85
-0.0 -4.55 8.98
-2.31 13.29 9.6
-3.1 -7.12 -7.72
8.68 -8.35 -12.08
5.38 -4.77 -9.89
11.08 -7.13 11.34
-10.58 4.2 -11.31
-6.17 3.54 -10.57
-7.07 -5.16 -2.2
3.31 12.79 -2.48
5.31 13.32 -3.32
-3.58 5.81 -12.13
0.22 9.04 -9.04
9.21 -10.91 3.44
1.74 1.02 3.58
12.31 11.01 -5.99
3.91 -11.27 11.28
-12.18 10.98 -11.69
3.15 -3.3 -2.16
6.65 12.65 -9.44
10.77 3.48 7.3
-7.0 -1.49 5.28
-11.06 -4.83 4.99
-8.17 10.85 12.27
-1.51 9.12 6.52
-8.46 8.19 -5.61
9.69 -5.43 -3.29
-3.99 10.35 -7.49
1.15 10.14 -1.82
1.15 8.81 11.16
-12.24 -12.4 -10.04
1.53 -11.91 4.05
-12.72 0.19 -0.63
12.98 -5.75 -11.74
8.0 -2.31 -10.12
1.98 9.18 6.38
-1.66 -7.55 1.28
-12.15 1.33 5.99
-2.86 -9.51 0.87
-1.9 0.65 4.45
-7.88 -12.59 10.36
-13.12 -10.8 4.62
5.77 11.26 -6.22
-8.9 0.75 -6.38
1.36 -8.65 -8.9
-9.81 13.31 -2.42
9.28 -5.92 -5.57
0.02 -7.78 7.85
4.14 -5.8 13.07
-2.22 13.21 -7.46
13.36 13.22 -3.61
-12.03 2.83 2.76
-0.79 7.47 -1.04
-12.27 10.66 5.58
11.84 -8.25 3.01
-2.19 1.1 0.51
-10.44 -2.46 -12.14
-6.23 11.39 3.46
-4.14 -3.6 -1.4
10.12 2.12 10.55
1.22 -11.89 -6.81
-1.36 -1.09 8.75
10.14 -7.11 -13.34
0.23 8.29 3.46
-12.22 -5.42 11.44
-0.44 -4.88 -2.63
11.7 13.08 -5.28
7.95 5.77 -7.1
7.06 -9.95 10.34
-11.87 -5.3 -4.75
-4.91 -8.48 3.56
-9.14 12.33 -9.58
-3.23 6.98 2.1
-6.41 -3.01 3.5
10.52 -12.17 9.84
0.38 -11.75 -3.01
6.05 1.38 13.06
-9.53 -10.27 -11.25
-9.7 -8.03 -11.45
-4.02 11.59 2.65
9.45 -1.36 -6.36
2.05 6.4 -2.83
5.11 -7.41 4.22
4.58 0.75 -3.01
8.03 -10.54 -12.57
9.82 -7.02 9.35
5.14 -5.19 -4.09
-12.87 4.41 1.3
9.97 -13.03 4.11
-11.11 13.31 9.73
12.0 4.32 -9.91
5.75 10.68 13.33
-8.15 -9.68 -5.1
-6.23 -2.68 -10.0
2.91 -1.18 -8.57
-12.23 3.69 -12.83
2.13 0.91 -7.89
9.19 5.17 6.94
11.68 12.05 -10.76
-8.84 -4.26 1.12
-2.19 7.5 -3.01
-8.96 7.49 11.36
11.55 7.65 -3.59
11.3 -8.92 -10.16
12.76 4.53 -2.27
-4.24 -12.64 10.36
6.28 4.83 -10.23
3.19 3.17 -0.84
7.15 -1.1 1.22
-0.86 -4.38 -10.02
1.37 -6.18 8.13
6.18 -10.9 -11.33
-2.92 0.31 13.17
12.84 -1.96 -5.8
-10.51 2.14 9.49
12.51 -6.36 0.27
7.5 12.2 -7.25
-0.65 -3.36 -4.35
-13.22 7.05 13.04
-7.06 4.97 2.55
12.88 7.55 -8.49
-1.74 -10.12 -7.96
-8.04 -10.81 1.61
12.81 -0.74 -7.76
6.98 10.19 5.45
2.88 5.73 -13.07
9.33 -12.19 -11.8
-5.71 3.42 12.92
-10.37 7.09 -8.74
-5.5 -8.46 -12.84
12.69 -8.12 -8.63
-0.7 0.82 12.9
9.15 5.91 -1.96
-3.34 -13.02 5.54
-0.99 -4.89 11.04
2.83 -9.17 11.46
4.51 7.7 4.59
11.67 -10.24 9.55
12.55 -3.36 -1.93
9.83 1.67 8.37
4.18 9.86 9.27
11.28 -1.12 -9.52
7.67 -6.25 9.58
3.82 0.22 2.81
-0.59 0.22 -3.61
-9.14 3.37 5.3
8.19 -10.02 8.33
6.18 3.02 9.97
-11.63 7.18 -3.67
7.47 12.98 8.39
2.56 0.54 7.23
9.93 6.68 -12.11
6.43 4.91 -0.12
-8.75 5.36 6.38
-3.84 1.58 9.76
12.35 -12.63 -0.27
13.3 0.98 2.79
-7.51 13.19 -2.7
12.42 -3.56 -12.1
-3.62 0.48 -7.13
-9.79 11.78 8.73
8.57 -4.86 2.3
6.73 10.99 -0.3
12.07 1.39 -7.18
-2.45 -10.67 12.68
10.22 0.75 -5.73
-3.16 -1.58 -7.9
-11.67 -5.12 -9.42
-8.33 1.57 6.25
-0.11 0.43 -8.59
-3.48 12.28 -4.54
4.14 10.89 -11.77
-6.11 -12.61 8.89
-2.84 12.81 -1.0
-10.13 5.79 8.24
5.27 4.95 8.95
11.4 -10.99 -3.44
-8.91 2.71 -7.5
-12.1 -6.09 1.27
-9.87 13.05 6.94
-0.11 5.66 -10.65
-5.25 -4.38 -3.39
-6.66 7.82 -8.96
4.12 -8.04 9.89
-5.54 -1.64 12.14
-8.82 -3.62 -5.62
-1.52 -8.42 -6.64
10.6 4.58 -5.28
"""
pairs="""
0 930
0 907
0 490
0 674
1 860
1 947
1 270
1 175
2 334
2 619
2 211
2 75
3 583
3 483
3 203
3 158
4 576
4 648
4 480
4 230
5 412
5 147
5 866
5 927
6 627
6 759
6 651
6 803
7 934
7 38
7 792
7 594
8 649
8 707
8 170
8 141
9 548
9 235
9 955
9 761
10 64
10 916
10 561
10 999
11 549
11 836
11 737
11 386
12 131
12 501
12 971
12 781
13 442
13 126
13 744
13 40
14 773
14 389
14 792
14 454
15 18
15 947
15 214
15 749
16 320
16 795
16 623
16 912
17 671
17 834
17 85
17 133
18 976
18 62
18 356
19 46
19 600
19 849
19 499
20 636
20 567
20 36
20 994
21 114
21 581
21 161
21 238
22 75
22 137
22 828
22 575
23 407
23 50
23 845
23 876
24 288
24 706
24 791
24 441
25 712
25 112
25 508
25 996
26 267
26 449
26 935
26 42
27 147
27 988
27 796
27 364
28 137
28 690
28 603
28 961
29 495
29 524
29 647
29 507
30 658
30 771
30 870
30 225
31 232
31 840
31 128
31 205
32 667
32 541
32 300
32 289
33 85
33 291
33 378
33 127
34 723
34 305
34 77
34 969
35 895
35 116
35 61
35 675
36 742
36 41
36 416
37 432
37 720
37 614
37 64
38 532
38 358
38 263
39 878
39 988
39 316
39 313
40 377
40 720
40 920
41 823
41 939
41 819
42 715
42 855
42 564
43 431
43 348
43 578
43 411
44 189
44 446
44 353
44 89
45 675
45 299
45 583
45 168
46 215
46 684
46 625
47 657
47 450
47 816
47 434
48 913
48 835
48 328
48 646
49 283
49 598
49 208
49 351
50 868
50 403
50 979
51 120
51 885
51 279
51 911
52 518
52 485
52 716
52 172
53 188
53 732
53 682
53 668
54 973
54 336
54 543
54 699
55 791
55 413
55 435
55 662
56 225
56 563
56 557
56 204
57 628
57 952
57 847
57 808
58 542
58 664
58 92
58 416
59 369
59 886
59 345
59 405
60 197
60 500
60 311
60 259
61 432
61 772
61 456
62 738
62 270
62 79
63 268
63 383
63 606
63 266
64 714
64 977
65 686
65 899
65 697
65 445
66 489
66 555
66 861
66 150
67 906
67 411
67 753
67 464
68 169
68 317
68 910
68 806
69 885
69 212
69 596
69 593
70 590
70 464
70 417
70 846
71 923
71 175
71 481
71 797
72 534
72 937
72 992
72 683
73 976
73 941
73 188
73 738
74 322
74 314
74 516
74 380
75 741
75 356
76 911
76 358
76 145
76 408
77 389
77 287
77 934
78 604
78 113
78 728
78 100
79 749
79 946
79 394
80 593
80 85
80 120
80 684
81 674
81 832
81 321
81 495
82 524
82 793
82 926
82 94
83 241
83 287
83 763
83 584
84 974
84 384
84 805
84 559
85 218
86 577
86 776
86 155
86 805
87 608
87 994
87 95
87 134
88 889
88 325
88 161
88 842
89 969
89 809
89 93
90 149
90 790
90 342
90 252
91 702
91 130
91 420
91 833
92 243
92 106
92 302
93 904
93 153
93 200
94 125
94 340
94 315
95 461
95 585
95 623
96 767
96 203
96 326
96 677
97 915
97 815
97 752
97 592
98 159
98 730
98 110
98 866
99 822
99 331
99 509
99 854
100 414
100 932
100 940
101 688
101 319
101 468
101 351
102 974
102 313
102 132
102 822
103 428
103 704
103 272
103 840
104 884
104 386
104 237
104 255
105 601
105 192
105 280
105 173
106 602
106 769
106 467
107 274
107 877
107 341
107 655
108 880
108 376
108 995
108 954
109 779
109 165
109 493
109 770
110 263
110 834
110 990
111 216
111 151
111 380
111 937
112 218
112 622
112 217
113 827
113 700
113 478
114 949
114 817
114 665
115 359
115 444
115 330
115 846
116 142
116 964
116 919
117 421
117 910
117 180
117 462
118 757
118 776
118 900
118 630
119 924
119 324
119 698
119 517
120 145
120 834
121 211
121 640
121 467
121 542
122 250
122 425
122 290
122 737
123 137
123 565
123 186
123 903
124 381
124 589
124 221
124 297
125 641
125 742
125 939
126 654
126 533
126 447
127 493
127 410
127 802
128 864
128 574
128 239
129 784
129 514
129 862
129 426
130 782
130 851
130 261
131 605
131 295
131 855
132 854
132 246
132 680
133 307
133 591
133 215
134 767
134 501
134 819
135 329
135 502
135 349
135 319
136 538
136 263
136 520
136 853
137 952
138 242
138 856
138 512
138 178
139 590
139 693
139 539
139 871
140 451
140 254
140 678
140 322
141 475
141 148
141 364
142 670
142 432
142 724
143 868
143 295
143 267
143 618
144 282
144 757
144 784
144 650
145 263
145 643
146 680
146 282
146 786
146 944
147 505
147 707
148 716
148 234
148 620
149 491
149 653
149 875
150 334
150 188
150 800
151 794
151 992
151 676
152 858
152 226
152 193
152 438
153 883
153 469
153 668
154 648
154 395
154 997
154 881
155 936
155 690
155 191
156 750
156 182
156 412
156 440
157 856
157 738
157 933
157 800
158 644
158 767
158 623
159 307
159 442
159 654
160 732
160 883
160 667
160 567
161 247
161 407
162 778
162 913
162 560
162 986
163 390
163 382
163 715
163 413
164 214
164 573
164 813
164 165
165 749
165 701
166 352
166 877
166 179
166 807
167 720
167 670
167 473
167 431
168 908
168 201
168 610
169 346
169 928
169 271
170 473
170 838
170 377
171 255
171 194
171 302
171 836
172 208
172 577
172 368
173 909
173 257
173 615
174 646
174 187
174 504
174 930
175 242
175 434
176 320
176 884
176 631
176 239
177 750
177 367
177 810
177 958
178 509
178 797
178 783
179 292
179 870
179 557
180 829
180 405
180 264
181 713
181 290
181 205
181 283
182 206
182 825
182 866
183 389
183 631
183 550
183 354
184 826
184 371
184 342
184 463
185 391
185 571
185 853
185 206
186 828
186 265
186 195
187 436
187 700
187 932
188 198
189 723
189 982
189 733
190 494
190 877
190 588
190 695
191 798
191 847
191 948
192 196
192 337
192 400
193 892
193 925
193 236
194 491
194 847
194 498
195 880
195 486
195 896
196 909
196 686
196 278
197 645
197 785
197 219
198 446
198 296
198 933
199 366
199 659
199 600
199 442
200 595
200 556
200 478
201 753
201 224
201 895
202 952
202 615
202 280
202 788
203 981
203 971
204 616
204 605
204 993
205 985
205 598
206 740
206 730
207 332
207 349
207 851
207 826
208 468
208 843
209 507
209 672
209 539
209 591
210 213
210 588
210 596
210 848
211 555
211 534
212 502
212 213
212 782
213 261
213 807
214 725
214 575
215 218
215 524
216 918
216 396
216 314
217 687
217 378
217 530
218 876
219 419
219 418
219 666
220 629
220 463
220 867
220 851
221 855
221 402
221 703
222 526
222 931
222 506
222 579
223 858
223 752
223 679
223 364
224 830
224 308
224 578
225 297
225 703
226 679
226 651
226 796
227 767
227 621
227 719
227 823
228 365
228 231
228 496
228 346
229 484
229 536
229 312
229 987
230 325
230 890
230 979
231 831
231 692
231 983
232 290
232 798
232 805
233 443
233 963
233 609
233 365
234 485
234 822
234 316
235 332
235 401
235 352
236 720
236 950
236 838
237 710
237 629
237 931
238 289
238 587
238 639
239 294
239 550
240 733
240 494
240 479
240 998
241 869
241 519
241 775
242 265
242 356
243 778
243 708
243 386
244 295
244 449
244 997
244 480
245 419
245 516
245 799
245 417
246 409
246 537
246 384
247 915
247 845
247 874
248 360
248 963
248 902
248 613
249 360
249 609
249 590
249 554
250 628
250 669
250 573
251 650
251 685
251 597
251 426
252 559
252 437
252 798
253 601
253 400
253 369
253 264
254 860
254 816
254 417
255 306
255 653
256 286
256 388
256 652
256 921
257 871
257 696
257 609
258 961
258 571
258 958
258 886
259 349
259 962
259 525
260 818
260 641
260 267
260 989
261 658
261 292
262 697
262 634
262 780
262 266
264 930
264 328
265 923
265 741
266 744
266 724
267 599
268 472
268 832
268 686
269 317
269 460
269 478
269 878
270 335
270 451
271 569
271 827
271 566
272 294
272 985
272 982
273 860
273 335
273 419
273 333
274 281
274 494
274 351
275 930
275 689
275 963
275 696
276 337
276 865
276 633
276 445
277 996
277 966
277 404
277 924
278 304
278 697
278 606
279 662
279 499
279 503
280 458
280 758
281 887
281 762
281 716
282 974
282 304
283 399
283 850
284 633
284 967
284 792
284 426
285 702
285 957
285 288
285 931
286 655
286 929
286 470
287 397
287 713
288 863
288 662
289 751
289 889
290 843
291 743
291 587
291 520
292 867
292 332
293 538
293 792
293 519
293 544
294 912
294 546
295 905
296 353
296 814
296 576
297 435
297 656
298 511
298 441
298 320
298 931
299 919
299 893
299 755
300 405
300 328
300 901
301 677
301 768
301 943
301 380
302 373
302 310
303 553
303 606
303 760
303 964
304 553
304 630
305 570
305 528
305 580
306 710
306 339
306 373
307 600
307 533
308 610
308 652
308 929
309 903
309 482
309 721
309 443
310 841
310 683
310 498
311 955
311 699
311 401
312 645
312 383
312 455
313 673
313 784
314 464
314 888
315 618
315 622
315 996
316 364
316 562
317 717
317 607
318 718
318 506
318 765
318 778
319 401
319 807
320 362
321 986
321 735
321 400
322 768
322 906
323 642
323 540
323 414
323 561
324 996
324 736
324 711
325 804
325 942
326 781
326 774
326 819
327 602
327 972
327 852
327 835
328 560
329 922
329 500
329 387
330 816
330 592
330 481
331 766
331 704
331 872
332 807
333 922
333 666
333 995
334 976
334 612
335 946
335 678
336 688
336 401
336 488
337 630
337 739
338 414
338 999
338 569
338 914
339 851
339 476
339 572
340 531
340 508
340 625
341 898
341 830
341 649
342 919
342 760
343 754
343 539
343 359
343 970
344 412
344 707
344 363
344 368
345 901
345 391
345 527
346 436
346 613
347 933
347 733
347 872
347 861
348 592
348 858
348 475
349 801
350 427
350 794
350 393
350 513
351 848
352 830
352 729
353 479
353 904
354 546
354 969
354 429
355 994
355 728
355 837
355 379
356 800
357 390
357 627
357 950
357 881
358 990
358 803
359 660
359 874
360 918
360 661
361 529
361 814
361 738
361 921
362 811
362 381
362 461
363 750
363 577
363 825
365 918
365 721
366 968
366 844
366 662
367 726
367 995
367 603
368 688
368 894
369 739
369 458
370 953
370 554
370 422
370 599
371 755
371 729
371 867
372 512
372 741
372 555
372 766
373 691
373 777
374 443
374 458
374 462
374 601
375 950
375 377
375 442
375 927
376 481
376 660
376 860
377 973
378 430
378 639
379 809
379 839
379 469
380 547
381 441
381 748
382 950
382 714
382 844
383 477
383 447
384 840
384 821
385 711
385 905
385 403
385 622
386 765
387 468
387 894
387 726
388 978
388 610
388 981
389 869
390 395
390 659
391 520
391 949
392 785
392 810
392 543
392 440
393 409
393 692
393 676
394 687
394 802
394 712
395 820
395 803
396 794
396 465
396 908
397 850
397 580
397 882
398 850
398 570
398 723
398 494
399 552
399 586
399 779
400 745
402 748
402 564
402 791
403 480
403 530
404 736
404 873
404 423
405 581
406 525
406 873
406 510
406 515
407 639
407 890
408 596
408 764
408 580
409 635
409 415
410 743
410 984
410 763
411 846
411 816
412 973
413 703
413 771
414 960
415 466
415 893
415 583
416 453
416 913
417 660
418 660
418 954
418 672
419 525
420 531
420 980
420 710
421 581
421 486
421 938
422 661
422 975
422 902
423 508
423 474
423 782
424 691
424 683
424 632
424 694
425 836
425 875
425 847
426 454
427 537
427 705
427 675
428 747
428 635
428 466
429 454
429 487
429 811
430 802
430 751
430 941
431 892
431 753
432 634
433 521
433 539
433 611
433 524
434 856
434 451
435 441
435 503
436 963
436 462
437 840
437 893
437 864
438 592
438 444
438 568
439 591
439 897
439 440
439 730
440 654
443 615
444 953
444 970
445 522
445 597
446 469
446 861
447 785
447 699
448 505
448 532
448 459
448 967
449 979
449 681
450 578
450 652
450 655
451 921
452 547
452 937
452 756
452 624
453 567
453 467
453 835
454 857
455 951
455 959
455 693
456 551
456 457
456 977
457 492
457 753
457 465
458 565
459 633
459 544
459 900
460 679
460 556
460 988
461 546
461 837
462 496
463 709
463 653
464 492
465 675
465 513
466 644
466 912
467 612
468 586
469 732
470 695
470 616
470 814
471 789
471 516
471 510
471 547
472 968
472 533
472 849
473 488
473 898
474 593
474 497
474 712
475 898
475 657
476 777
476 653
476 535
477 955
477 724
477 760
478 842
479 570
479 695
480 787
481 815
482 841
482 952
482 756
483 795
483 956
483 563
484 788
484 606
484 909
485 707
485 731
486 886
486 565
487 960
487 837
487 604
488 830
488 548
489 640
489 839
489 732
490 913
490 742
490 558
491 536
491 948
492 661
492 727
493 643
493 593
495 926
495 849
496 806
496 903
497 770
497 801
497 812
498 756
498 777
499 980
499 833
500 543
500 666
501 989
501 589
502 586
502 770
503 702
503 658
504 540
504 940
504 818
505 731
505 825
506 522
506 965
507 951
507 533
508 684
509 620
509 562
510 962
510 523
511 656
511 629
511 709
512 872
512 800
513 879
513 918
514 827
514 604
514 685
515 678
515 943
515 516
517 768
517 921
517 678
518 821
518 805
518 598
519 718
519 991
520 671
521 970
521 868
521 599
522 745
522 735
523 572
523 694
523 777
525 812
526 631
526 773
526 765
527 544
527 991
527 865
528 594
528 904
528 803
529 734
529 787
529 711
530 890
530 734
531 966
531 638
532 866
532 853
534 841
534 663
535 536
535 962
535 826
536 760
537 786
537 893
538 743
538 584
540 902
540 932
541 883
541 842
541 829
542 683
542 823
543 894
544 853
545 762
545 655
545 856
545 998
546 809
547 694
548 920
548 670
549 775
549 769
549 945
550 985
550 891
551 879
551 999
551 661
552 843
552 573
552 725
553 948
553 559
554 611
554 689
555 824
556 804
556 759
557 956
557 929
558 986
558 926
558 638
559 786
560 745
560 972
561 975
561 564
562 717
562 928
563 589
563 971
564 714
565 961
566 680
566 784
566 914
567 640
568 942
568 979
568 845
569 613
569 932
570 764
571 739
571 900
572 873
572 966
573 945
574 875
574 884
574 737
575 619
575 628
576 668
576 734
577 617
578 898
579 811
579 706
579 597
580 934
581 637
582 914
582 650
582 944
582 916
583 794
584 643
584 934
585 644
585 621
585 839
586 848
587 901
587 852
588 764
588 870
589 623
590 888
591 754
594 857
594 759
595 862
595 604
595 857
596 882
597 773
598 887
599 793
600 834
601 696
602 778
602 775
603 828
603 880
605 997
605 703
607 938
607 915
607 637
608 642
608 940
608 837
609 624
610 956
611 793
611 647
612 682
612 917
613 879
614 780
614 844
614 744
615 987
616 787
616 978
617 726
617 690
617 843
618 781
618 641
619 808
619 813
620 762
620 657
621 640
621 994
622 868
624 888
624 959
625 980
625 926
626 960
626 748
626 706
626 916
627 796
627 927
628 690
629 702
630 936
631 811
632 823
632 677
632 774
633 757
634 944
634 964
635 824
635 766
636 728
636 646
636 940
637 910
637 842
638 708
638 664
639 665
641 819
642 989
642 748
643 882
644 719
645 962
645 789
646 829
647 674
647 871
648 904
648 804
649 716
649 688
650 697
651 881
651 804
652 906
654 973
656 795
656 867
657 797
658 885
659 911
659 990
663 721
663 983
663 676
664 691
664 939
665 876
665 671
666 810
667 682
667 835
668 889
669 836
669 769
669 808
670 895
671 730
672 785
672 693
673 967
673 731
673 757
674 696
676 824
677 992
679 942
680 705
681 881
681 715
681 925
682 751
684 833
685 914
685 960
686 735
687 941
687 711
689 902
689 907
691 966
692 766
692 854
693 799
694 943
695 993
698 905
698 978
698 781
699 920
700 910
700 829
701 802
701 917
701 976
704 887
704 821
705 772
705 879
706 899
708 710
708 965
709 884
709 790
712 736
713 891
713 945
714 925
715 997
717 783
717 752
718 773
718 865
719 992
719 824
721 937
722 735
722 957
722 849
722 863
723 985
724 920
725 726
725 859
727 953
727 892
727 846
728 883
729 761
729 956
731 776
733 887
734 941
736 946
737 891
739 758
740 949
740 958
740 897
741 983
742 818
743 991
744 968
745 865
746 967
746 862
746 988
746 759
747 861
747 982
747 839
749 859
750 894
751 852
752 797
754 876
754 817
755 795
755 790
756 987
758 961
758 936
761 895
761 919
762 872
763 945
763 779
764 820
765 869
768 981
769 813
770 859
771 820
771 911
772 944
772 999
774 939
774 924
775 984
776 974
779 882
780 916
780 899
782 801
783 831
783 923
786 964
787 905
788 948
788 936
789 799
789 959
790 864
791 844
793 907
796 838
798 875
799 888
801 873
806 938
806 831
808 841
809 982
810 954
812 946
812 922
813 917
814 998
815 896
815 874
817 874
817 897
818 907
820 993
821 822
825 900
826 955
827 878
828 947
831 928
832 909
832 951
833 885
838 858
845 970
848 850
852 984
854 928
855 989
857 969
859 922
862 878
863 899
863 968
864 912
869 891
870 993
871 951
877 929
880 958
886 949
889 890
892 977
896 923
896 938
897 954
901 972
903 983
906 908
908 981
915 942
917 984
924 943
925 935
927 990
933 998
935 975
935 953
947 995
957 965
957 980
959 987
965 986
971 978
972 991
975 977
"""

