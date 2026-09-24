""" Recorte de retas - Liang-Barsky """


def liang_barsky(x0, y0, x1, y1, xmin, ymin, xmax, ymax):
    dx, dy = x1 - x0, y1 - y0
    p = (-dx, dx, -dy, dy)
    q = (x0 - xmin, xmax - x0, y0 - ymin, ymax - y0)

    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0: # paralela à borda e fora da janela
                return None # não retorna nada, pois reta está totalmente fora 
        else:
            u = qi / pi
            if pi < 0: # entrando na janela
                u1 = max(u1, u)
            else: # saindo da janela
                u2 = min(u2, u)
            if u1 > u2:
                return None # não retorna nada, pois reta está totalmente fora

    return x0 + u1 * dx, y0 + u1 * dy, x0 + u2 * dx, y0 + u2 * dy # retorna novos inicios e fins das retas recortadas
