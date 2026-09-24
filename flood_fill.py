""" Preenchimento - Flood Fill """

def flood_fill(pixels, x, y, cor_nova):
    altura, largura = len(pixels), len(pixels[0])

    if not (0 <= x < largura and 0 <= y < altura):
        return

    cor_alvo = pixels[y][x] # cor que será substituida
    if cor_alvo == cor_nova:
        return

    pilha = [(x, y)]
    while pilha: # termina quando não há mais pixels a visitar
        px, py = pilha.pop()
        if 0 <= px < largura and 0 <= py < altura and pixels[py][px] == cor_alvo:
            pixels[py][px] = cor_nova
            pilha.extend(
                ((px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1))
            )  # empilha os 4 vizinhos do pixel pintado
