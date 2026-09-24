"""Rasterização de retas - DDA"""

import math

# arredondamento pra cima
def _arred(v):
    return int(math.floor(v + 0.5))

def dda(x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0 # variações de x e y
    
    passos = _arred(max(abs(dx), abs(dy))) # passos = maior de dx ou dy
    if passos == 0:
        return [(_arred(x0), _arred(y0))]

    x_inc = dx / passos # 1o caso
    y_inc = dy / passos # 2o caso
    x, y = x0, y0
    pontos = []
    
    for _ in range(passos + 1):
        pontos.append((_arred(x), _arred(y))) # arredonda somente ao plotar
        x += x_inc
        y += y_inc
    
    return pontos # retorna a lista de pixels que forma a reta
