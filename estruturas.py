""" Estruturas de dados """
import copy
import math

from reta_dda import dda
from reta_bresenham import bresenham
from circunferencia_bresenham import circunferencia_bresenham
from flood_fill import flood_fill
from boundary_fill import boundary_fill
from transformacoes import aplicar_ponto, fator_area


def arred(v):
    return int(math.floor(v + 0.5))

# área de desenho
class MatrizPixels:
    def __init__(self, largura, altura, fundo="#ffffff"):
        self.largura, self.altura, self.fundo = largura, altura, fundo
        self.pixels = [[fundo] * largura for _ in range(altura)]

    def limpar(self):
        for linha in self.pixels:
            linha[:] = [self.fundo] * self.largura

    def pintar(self, x, y, cor):
        if 0 <= x < self.largura and 0 <= y < self.altura:
            self.pixels[y][x] = cor

    def como_dados(self):
        """String no formato aceito por tk.PhotoImage.put()."""
        return " ".join("{" + " ".join(linha) + "}" for linha in self.pixels)


class Objeto:
    tipo = "Objeto"
    selecionado = False

    def pontos_controle(self):
        return self.vertices()


class Ponto(Objeto):
    tipo = "Ponto"

    def __init__(self, x, y, cor="#000000"):
        self.x, self.y, self.cor = x, y, cor

    def vertices(self):
        return [(self.x, self.y)]

    def transformar(self, m):
        self.x, self.y = aplicar_ponto(m, self.x, self.y)

    def desenhar(self, matriz):
        matriz.pintar(arred(self.x), arred(self.y), self.cor)


class Reta(Objeto):
    tipo = "Reta"

    def __init__(self, p1, p2, algoritmo="bresenham", cor="#000000"):
        self.p1, self.p2, self.algoritmo, self.cor = p1, p2, algoritmo, cor

    def vertices(self):
        return [(self.p1.x, self.p1.y), (self.p2.x, self.p2.y)]

    def transformar(self, m):
        self.p1.transformar(m)
        self.p2.transformar(m)

    def desenhar(self, matriz):
        alg = dda if self.algoritmo == "dda" else bresenham
        for x, y in alg(self.p1.x, self.p1.y, self.p2.x, self.p2.y):
            matriz.pintar(x, y, self.cor)


class Circulo(Objeto):
    tipo = "Circunferência"

    def __init__(self, centro, raio, cor="#000000"):
        self.centro, self.raio, self.cor = centro, raio, cor

    def vertices(self):  # caixa envolvente, usada na seleção por região
        c, r = self.centro, self.raio
        return [(c.x - r, c.y - r), (c.x + r, c.y + r)]

    def pontos_controle(self):
        return [(self.centro.x, self.centro.y)]

    def transformar(self, m):
        self.centro.transformar(m)
        self.raio *= math.sqrt(fator_area(m))  # continua sendo um círculo

    def desenhar(self, matriz):
        for x, y in circunferencia_bresenham(self.centro.x, self.centro.y, self.raio):
            matriz.pintar(x, y, self.cor)


class Poligono(Objeto):
    tipo = "Polígono"

    def __init__(self, vertices, cor="#000000"):
        self.pontos = vertices  # lista de Ponto
        self.cor = cor

    def vertices(self):
        return [(p.x, p.y) for p in self.pontos]

    def transformar(self, m):
        for p in self.pontos:
            p.transformar(m)

    def desenhar(self, matriz):
        n = len(self.pontos)
        for i in range(n):
            a, b = self.pontos[i], self.pontos[(i + 1) % n]
            for x, y in bresenham(a.x, a.y, b.x, b.y):
                matriz.pintar(x, y, self.cor)


class Cena:
    def __init__(self):
        self.objetos = []
        self.preenchimentos = []
        self.janela = None

    def adicionar(self, objeto):
        self.objetos.append(objeto)

    def selecionados(self):
        return [o for o in self.objetos if o.selecionado]

    def selecionar_retangulo(self, x0, y0, x1, y1, somar=False):
        xmin, xmax = sorted((x0, x1))
        ymin, ymax = sorted((y0, y1))
        for o in self.objetos:
            dentro = all(xmin - .5 <= x <= xmax + .5 and ymin - .5 <= y <= ymax + .5
                         for x, y in o.vertices())
            o.selecionado = dentro or (somar and o.selecionado)

    def limpar_selecao(self):
        for o in self.objetos:
            o.selecionado = False

    def snapshot(self):
        return copy.deepcopy((self.objetos, self.preenchimentos, self.janela))

    def restaurar(self, estado):
        self.objetos, self.preenchimentos, self.janela = estado

    def renderizar(self, matriz):
        matriz.limpar()
        for o in self.objetos:
            o.desenhar(matriz)
        for algoritmo, x, y, cor, borda in self.preenchimentos:
            if algoritmo == "flood":
                flood_fill(matriz.pixels, x, y, cor)
            else:
                boundary_fill(matriz.pixels, x, y, cor, borda)
