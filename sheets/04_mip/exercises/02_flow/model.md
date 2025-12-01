Erstelle fuer jeden Tunnel von $u$ nach $v$ Entscheidungsvariable ${x_{uv}}$ und ${x_{vu}}$ $\in \mathbb{B}$ 
die angibt ob ein Tunnel in die bestimme Richtung genutzt wird
Ausserdem erstelle Flowvariablen $f_{uv}$ und $f_{vu}$ $\in \mathbb{R}^+$ die den Flow in eine Richtung angeben.

Constraints:

$x_{uv} + x_{vu} \leq 1 \quad \forall e=u, v \in E$

$f_{uv} \leq x_{uv} * u_e \land f_{vu} \leq x_{vu} * u_e \quad \forall e=u, v \in E$

$\sum_{e=u,v \in E}f_{uv} - \sum_{e=w,u \in E}f_{wu} \leq o_u \quad \forall u \in M$

$\sum_{e=u,v \in E} x_{uv}*c_e \leq b$

Objective:

$ max \sum_{e=u,a \in E}f_{ua} \quad$ wobei $a$ die elevator Location ist.
