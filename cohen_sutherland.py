"""Recorte de retas - Cohen-Sutherland"""

DENTRO, ESQUERDA, DIREITA, BASE, TOPO = 0, 1, 2, 4, 8


def codigo_regiao(x, y, xmin, ymin, xmax, ymax):
    codigo = DENTRO
    if x < xmin:
        codigo |= ESQUERDA
    elif x > xmax:
        codigo |= DIREITA
    if y < ymin:
        codigo |= TOPO
    elif y > ymax:
        codigo |= BASE
    return codigo


def cohen_sutherland(x0, y0, x1, y1, xmin, ymin, xmax, ymax):
    c0 = codigo_regiao(x0, y0, xmin, ymin, xmax, ymax)
    c1 = codigo_regiao(x1, y1, xmin, ymin, xmax, ymax)

    while (c0 | c1) and not (
        c0 & c1
    ):  # continua enquanto não for trivialmente aceita e nem for trivialmente rejeitada
        c = c0 if c0 else c1  # ponto que está fora
        if c & TOPO:
            x = x0 + (x1 - x0) * (ymin - y0) / (y1 - y0)
            y = ymin
        elif c & BASE:
            x = x0 + (x1 - x0) * (ymax - y0) / (y1 - y0)
            y = ymax
        elif c & DIREITA:
            y = y0 + (y1 - y0) * (xmax - x0) / (x1 - x0)
            x = xmax
        else:  # ESQUERDA
            y = y0 + (y1 - y0) * (xmin - x0) / (x1 - x0)
            x = xmin

        if c == c0:
            x0, y0 = x, y
            c0 = codigo_regiao(x0, y0, xmin, ymin, xmax, ymax)
        else:
            x1, y1 = x, y
            c1 = codigo_regiao(x1, y1, xmin, ymin, xmax, ymax)

    if c0 & c1:  # trivialmente rejeitada: totalmente fora da janela
        return None  # não retorna nada
    return (
        x0,
        y0,
        x1,
        y1,
    )  # aceita (original ou já recortada): retorna os valores iniciais e finais de x e y
