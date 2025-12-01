Wenn wir ${l}$ gleiche Kanten von der Linearen Relaxation und der optimalen Loesung haben, muss ueber diese nicht gebrancht werden. 
Von also urspruenglich ${2^n}$ mal branchen bleibt nur ${2^{n-l}}$ branchen ueber. Wir sparen also ${2^n} - {2^{n-l}}$ branches.

overlap:
1. k=1 172, k=2 181
2. k=1 175, k=2 179
3. k=1 174, k=2 163
4. k=1 172, k=2 184
5. k=1 180, k=2 177
6. k=1 185, k=2 177
7. k=1 168, k=2 177
8. k=1 177, k=2 176
9. k=1 178, k=2 179
10. k=1 174, k=2 181
11. k=1 173, k=2 170
12. k=1 169, k=2 176
13. k=1 179, k=2 178
14. k=1 175, k=2 184
15. k=1 173, k=2 182
16. k=1 180, k=2 178
17. k=1 169, k=2 184
18. k=1 178, k=2 178
19. k=1 173, k=2 174
20. k=1 172, k=2 173

Average: k=1 174.8, k=2 177.5

Man sieht ausserdem das fuer k=2 2 die Differenz vom Objective und der Relaxtion bei ca 200-400 liegt, waehrend sie fuer k=2 bei 400-600 liegt.
Man sieht dass die Relaxation fur k=2 mehr gleiche Kanten hat als die Relaxation fuer k=1.
