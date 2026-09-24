""" Preenchimento - Boundary Fill """

def boundary_fill(pixels, x, y, cor_nova, cor_borda):
    
    altura, largura = len(pixels), len(pixels[0])
    pilha = [(x, y)] # evita uso de recursão
    
    while pilha:
        px, py = pilha.pop()
        if not (0 <= px < largura and 0 <= py < altura):
            continue
        cor = pixels[py][px]
        
        # pinta se não for borda e ainda não tiver a cor nova
        if cor != cor_borda and cor != cor_nova:
            pixels[py][px] = cor_nova
            pilha.extend(((px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1))) # empilha os 4 vizinhos do pixel pintado
