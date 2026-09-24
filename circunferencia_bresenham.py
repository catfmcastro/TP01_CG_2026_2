"""Rasterização de circunferência - Bresenham """
import math

# arredondamento pra cima
def _arred(v):
    return int(math.floor(v + 0.5))

def circunferencia_bresenham(xc, yc, raio):
    xc, yc, r = _arred(xc), _arred(yc), max(0, _arred(raio)) # somente valores inteiros

    pontos = set()
    x, y = 0, r
    p = 3 - 2 * r  # parâmetro de decisão inicial

    while x <= y: # somente 2o octante
        for px, py in ((x, y), (y, x), (-x, y), (-y, x),
                       (x, -y), (y, -x), (-x, -y), (-y, -x)):
            pontos.add((xc + px, yc + py))
        if p < 0:
            p += 4 * x + 6
        else:
            p += 4 * (x - y) + 10
            y -= 1
        x += 1
    return sorted(pontos) # retorna pixels que formam a circunferencia + raio
