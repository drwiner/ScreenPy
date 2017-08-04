# ScreenPy
Parse and annotate screenplays with markup language

| File     | info |
|--- | ---|
|Screenpile | Main algorithms for compiling screenplay structure|
|Screenpy | Parses shot headings with recursive descent |
|moviescript_crawler | crawls through imsdb_raw_nov_2015 folder |
|parsing_stats | outputs table (below) |


Dependencies:
---


PyParsing  (http://pyparsing.wikispaces.com/) (for parsing shot heading grammar)


sense2vec (spaCy) (https://github.com/explosion/sense2vec) (for temporal expression classification)


Screenplay Structure
---

See the attached paper for more details (![Paper](https://raw.githubusercontent.com/drwiner/screenpy/INT17_screenplays.pdf))


![Segmentation](https://www.github.com/drwiner/screenpy/scene_segs.png)


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