""" Rasterização de retas - Bresenham """

import math

# arredondamento pra cima
def _arred(v):
    return int(math.floor(v + 0.5))

def bresenham(x0, y0, x1, y1):
    x0, y0, x1, y1 = _arred(x0), _arred(y0), _arred(x1), _arred(y1) # somente valores inteiros

    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    erro = dx + dy  # variável de decisão

    pontos = []
    while (x0, y0) != (x1, y1): # continua até alcançar o ponto final
        pontos.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * erro
        if e2 >= dy: # avança em x
            erro += dy
            x0 += sx
        if e2 <= dx: # avança em y
            erro += dx
            y0 += sy

    return pontos # retorna a lista de pixels que formam a reta
