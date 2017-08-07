# ScreenPy
Parse and annotate screenplays with markup language

| File     | info |
|--- | ---|
|screenpile | Main algorithms for compiling screenplay structure|
|screenpy | Parses shot headings with recursive descent |
|screenpy_vars | Defines valid shot heading element patterns |
|screenpy_tests | Extra tests in addition to screenpy |
|moviescript_crawler | crawls through imsdb_raw_nov_2015 folder |
|parsing_stats | outputs table (below) |


Dependencies:
---


PyParsing  (http://pyparsing.wikispaces.com/) (for parsing shot heading grammar)


sense2vec (spaCy) (https://github.com/explosion/sense2vec) (for temporal expression classification)


Screenplay Structure
---

See the attached paper for more details (![Paper](https://github.com/drwiner/ScreenPy/blob/master/INT17_screenplays.pdf))


![Segmentation](https://www.github.com/drwiner/screenpy/blob/master/scene_segs.png)


IMSDb screenplay parsing
---


ScreenPy parses raw screenplays. The following table are the stats for a corpus of screenplays extracted from IMSDb (www.imsdb.com). Some screenplays are tagged as multiple genres.

Screenplay genre: number of films, avg number of master headings (msegs), avg number of segments (segs), avg subset of segments which have shot heading (headings), avg subset of segments which are speaker (speakers), avg number of headings which have a shot type (has shot), avg number of headings which have subject (has subj), and avg number of headings which have a time of day (has tod).

|	GENRE	|	FILMS	|	msegs	|	segs	|	headings	|	speakers	|	has shot	|	has subj	|	has tod	|
|	---------	|	---------	|	---------	|	---------	|	---------	|	---------	|	---------	|	---------	|	---------	|
|	Action	|	272	|	145.32	|	1240.44	|	621.07	|	538.46	|	26.28	|	207.86	|	89.86	|
|	Adventure	|	143	|	135.96	|	1201.85	|	574.01	|	546.62	|	19.32	|	181.02	|	80.64	|
|	Animation	|	24	|	83.42	|	1190.79	|	466.08	|	674.71	|	18.96	|	116.88	|	47.92	|
|	Biography	|	3	|	144.33	|	1352.67	|	543.00	|	756.00	|	8.33	|	57.67	|	123.00	|
|	Comedy	|	310	|	114.37	|	1370.38	|	581.92	|	720.32	|	20.25	|	174.33	|	78.83	|
|	Crime	|	193	|	135.07	|	1352.31	|	656.12	|	620.73	|	18.33	|	185.67	|	93.49	|
|	Drama	|	541	|	123.10	|	1328.10	|	591.28	|	666.60	|	20.36	|	161.21	|	85.77	|
|	Family	|	22	|	110.45	|	1385.86	|	740.59	|	561.36	|	36.95	|	208.23	|	59.64	|
|	Fantasy	|	90	|	120.06	|	1213.94	|	627.40	|	526.83	|	29.60	|	227.74	|	73.33	|
|	Film-Noir	|	4	|	49.50	|	1535.00	|	721.75	|	786.50	|	139.25	|	201.50	|	13.00	|
|	History	|	3	|	107.33	|	1302.00	|	594.00	|	600.67	|	1.67	|	175.33	|	95.00	|
|	Horror	|	134	|	124.38	|	1149.94	|	631.57	|	450.96	|	32.89	|	238.72	|	79.32	|
|	Music	|	5	|	110.40	|	1179.20	|	503.40	|	660.80	|	7.00	|	53.60	|	96.40	|
|	Musical	|	14	|	96.21	|	1388.93	|	712.64	|	606.29	|	27.00	|	208.43	|	71.57	|
|	Mystery	|	97	|	137.91	|	1294.98	|	608.71	|	621.03	|	14.27	|	168.92	|	90.93	|
|	Romance	|	177	|	116.37	|	1367.10	|	596.67	|	710.13	|	25.08	|	176.86	|	84.27	|
|	Sci-Fi	|	140	|	142.34	|	1161.19	|	606.56	|	471.83	|	23.66	|	202.91	|	79.14	|
|	Short	|	3	|	39.00	|	269.33	|	138.33	|	118.00	|	8.33	|	32.67	|	25.67	|
|	Sport	|	2	|	229.00	|	1380.00	|	881.00	|	499.00	|	3.00	|	647.00	|	71.00	|
|	Thriller	|	352	|	135.31	|	1265.74	|	626.78	|	574.90	|	25.98	|	216.25	|	86.01	|
|	War	|	25	|	105.76	|	1272.40	|	616.08	|	577.88	|	26.36	|	263.68	|	85.88	|
|	Western	|	10	|	145.70	|	1367.10	|	706.00	|	602.10	|	76.10	|	223.50	|	103.30	|
| *** | *** | *** | *** | *** | *** | *** | *** | *** |
|	sum	|	2564	|	2651.29	|	27569.26	|	13344.96	|	12891.72	|	608.97	|	4329.98	|	1713.95	|
|	avg	|	116.55	|	120.51	|	1253.15	|	606.59	|	585.99	|	27.68	|	196.82	|	77.91	|


### Verb sense disambiguation


genre	|	num	|	avg SD frames / screenplay	|	avg frames / mseg	|	avg frames / seg	|	avg msegs / screenplay	|	avg segs / screenplay	|	avg headings/screenplay	|	avg speaking-turns/ screenplay	|	avg has-shot		|	avg has-shot	|	has-subj	|
|	---------	|	---------	|	---------	|	---------	|	---------	|	---------	|	---------	|	---------	|	---------	| ---------	|	---------	|	---------	|
Western	|	10	|	1442.10	|	9.90	|	1.05	|	145.7	|	1367.1	|	706	|	602.1	|	76.1		|	223.5	|	103.3	|
Film-Noir	|	4	|	1353.00	|	27.33	|	0.88	|	49.5	|	1535	|	721.75	|	786.5	|	139.25		|	201.5	|	13	|
Sport	|	2	|	1170.00	|	5.11	|	0.85	|	229	|	1380	|	881	|	499	|	3		|	647	|	71	|
Horror	|	134	|	1117.10	|	8.98	|	0.97	|	124.380597	|	1149.940299	|	631.5671642	|	450.9552239	|	32.8880597		|	238.7238806	|	79.32089552	|
Mystery	|	97	|	1092.80	|	7.92	|	0.84	|	137.9072165	|	1294.979381	|	608.7113402	|	621.0309278	|	14.26804124		|	168.9175258	|	90.92783505	|
Thriller	|	352	|	1078.94	|	7.97	|	0.85	|	135.3068182	|	1265.744318	|	626.7755682	|	574.9005682	|	25.98011364		|	216.2528409	|	86.00568182	|
Crime	|	193	|	1074.30	|	7.95	|	0.79	|	135.0673575	|	1352.310881	|	656.1243523	|	620.7253886	|	18.33160622		|	185.6683938	|	93.48704663	|
Sci-Fi	|	140	|	1062.73	|	7.47	|	0.92	|	142.3357143	|	1161.192857	|	606.5571429	|	471.8285714	|	23.65714286		|	202.9142857	|	79.13571429	|
War	|	25	|	1061.08	|	10.03	|	0.83	|	105.76	|	1272.4	|	616.08	|	577.88	|	26.36		|	263.68	|	85.88	|
Fantasy	|	90	|	1056.44	|	8.80	|	0.87	|	120.0555556	|	1213.944444	|	627.4	|	526.8333333	|	29.6		|	227.7444444	|	73.33333333	|
Action	|	272	|	1053.60	|	7.25	|	0.85	|	145.3235294	|	1240.441176	|	621.0735294	|	538.4632353	|	26.28308824		|	207.8566176	|	89.86397059	|
Family	|	22	|	1052.23	|	9.53	|	0.76	|	110.4545455	|	1385.863636	|	740.5909091	|	561.3636364	|	36.95454545		|	208.2272727	|	59.63636364	|
Music	|	5	|	1033.60	|	9.36	|	0.88	|	110.4	|	1179.2	|	503.4	|	660.8	|	7		|	53.6	|	96.4	|
Adventure	|	143	|	1008.74	|	7.42	|	0.84	|	135.958042	|	1201.846154	|	574.006993	|	546.6223776	|	19.32167832		|	181.020979	|	80.64335664	|
Musical	|	14	|	996.86	|	10.36	|	0.72	|	96.21428571	|	1388.928571	|	712.6428571	|	606.2857143	|	27		|	208.4285714	|	71.57142857	|
Drama	|	541	|	996.49	|	8.09	|	0.75	|	123.103512	|	1328.096118	|	591.2809612	|	666.6044362	|	20.35674677		|	161.2144177	|	85.77264325	|
Romance	|	177	|	969.79	|	8.33	|	0.71	|	116.3672316	|	1367.101695	|	596.6666667	|	710.1299435	|	25.08474576		|	176.8587571	|	84.26553672	|
Biography	|	3	|	965.33	|	6.69	|	0.71	|	144.3333333	|	1352.666667	|	543	|	756	|	8.333333333		|	57.66666667	|	123	|
Comedy	|	310	|	899.93	|	7.87	|	0.66	|	114.3741935	|	1370.380645	|	581.9193548	|	720.3225806	|	20.24516129		|	174.3290323	|	78.82580645	|
History	|	3	|	860.00	|	8.01	|	0.66	|	107.3333333	|	1302	|	594	|	600.6666667	|	1.666666667		|	175.3333333	|	95	|
Animation	|	24	|	768.71	|	9.22	|	0.65	|	83.41666667	|	1190.791667	|	466.0833333	|	674.7083333	|	18.95833333		|	116.875	|	47.91666667	|
Short	|	3	|	189.67	|	4.86	|	0.70	|	39	|	269.3333333	|	138.3333333	|	118	|	8.333333333		|	32.66666667	|	25.66666667	|



Development
---
Working on verb sense disambiguation to classify clauses in stage direction with FrameNet frames using off-the-shelf frame-semantic parser [Semafor] (https://github.com/Noahs-ARK/semafor).