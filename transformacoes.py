""" Transformações 2D com coordenadas homogêneas """

import math

# multiplicação matriz 3x3
def multiplicar(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

# matriz de translação que desloca os pontos em dx e dy
def translacao(dx, dy):
    return [[1, 0, dx],
            [0, 1, dy],
            [0, 0, 1]]

# faz a transformação ocorrer em torno de um ponto (cx, cy)
def _em_torno_de(m, cx, cy):
    return multiplicar(translacao(cx, cy), multiplicar(m, translacao(-cx, -cy)))

# matriz de rotação
def rotacao(graus, cx=0, cy=0):
    r = math.radians(graus)
    c, s = math.cos(r), math.sin(r)
    return _em_torno_de([[c, s, 0],
                         [-s, c, 0],
                         [0, 0, 1]], cx, cy)

# matriz de escala
def escala(sx, sy, cx=0, cy=0):
    return _em_torno_de([[sx, 0, 0],
                         [0, sy, 0],
                         [0, 0, 1]], cx, cy)

# matriz de reflexão
def reflexao(eixo, cx=0, cy=0):
    sx = -1 if eixo in ("Y", "XY") else 1
    sy = -1 if eixo in ("X", "XY") else 1
    return escala(sx, sy, cx, cy)

def aplicar_ponto(m, x, y):
    return (m[0][0] * x + m[0][1] * y + m[0][2],
            m[1][0] * x + m[1][1] * y + m[1][2])

def fator_area(m):
    """|det| da parte linear: quanto a transformação escala áreas."""
    return abs(m[0][0] * m[1][1] - m[0][1] * m[1][0])
