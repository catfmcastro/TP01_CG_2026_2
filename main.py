""" TP01 - Computação Gráfica """

import math
import tkinter as tk
from tkinter import ttk, colorchooser

import transformacoes as tf
from estruturas import Cena, MatrizPixels, Ponto, Reta, Circulo, Poligono, arred
from cohen_sutherland import cohen_sutherland
from liang_barsky import liang_barsky

LARGURA, ALTURA, ESCALA = 100, 70, 8 # matriz 100x70, cada pixel = 8x8 na tela
COR_FUNDO = "#ffffff"

DICAS = {
    "selecionar": "Selecionar: arraste um retângulo envolvendo os objetos desejados.",
    "ponto": "Ponto: clique para criar um ponto.",
    "dda": "Reta DDA: clique no ponto inicial e depois no ponto final.",
    "bresenham": "Reta Bresenham: clique no ponto inicial e depois no ponto final.",
    "circulo": "Circunferência Bresenham: clique no centro e depois em um ponto do contorno.",
    "poligono": "Polígono: clique nos vértices; botão direito (ou 'Fechar polígono') fecha o polígono.",
    "pivo": "Pivô: clique para definir o ponto de referência de rotação/escala/reflexão.",
    "janela": "Janela de recorte: arraste um retângulo.",
    "boundary": "Boundary Fill: clique no interior de uma região fechada (borda = cor de contorno atual).",
    "flood": "Flood Fill: clique no interior de uma região (substitui a cor do pixel clicado).",
}


class App:
    def __init__(self, root):
        self.root = root
        root.title("TP01 - Computação Gráfica")

        self.cena = Cena()
        self.matriz = MatrizPixels(LARGURA, ALTURA, COR_FUNDO)
        self.img = tk.PhotoImage(width=LARGURA, height=ALTURA)
        self.img_zoom = None
        self.historico = []

        self.modo = "selecionar"
        self.temp = []          # cliques pendentes (vértices em construção)
        self.arrasto = None     # início de um arrasto (seleção / janela)
        self.pivo = None        # None = centro da seleção
        self.cor_contorno = "#000000"
        self.cor_preench = "#ff0000"

        self.var_grade = tk.BooleanVar(value=True)
        self.var_somar = tk.BooleanVar(value=False)
        self.var_dx = tk.DoubleVar(value=10)
        self.var_dy = tk.DoubleVar(value=10)
        self.var_ang = tk.DoubleVar(value=45)
        self.var_sx = tk.DoubleVar(value=1.5)
        self.var_sy = tk.DoubleVar(value=1.5)
        self.var_status = tk.StringVar()
        self.var_coord = tk.StringVar(value="x=-  y=-")

        self._montar_interface()
        self.set_modo("selecionar")

    # GUI ------------------------------------------------------------------
    def _botao(self, pai, texto, comando, **pack):
        b = ttk.Button(pai, text=texto, command=comando)
        b.pack(fill="x", pady=1, **pack)
        return b

    def _slider(self, pai, rotulo, var, de, ate, res):
        tk.Scale(pai, from_=de, to=ate, resolution=res, orient="horizontal",
                 variable=var, label=rotulo, length=200).pack(fill="x")

    def _montar_interface(self):
        esq = ttk.Frame(self.root, padding=6)
        esq.grid(row=0, column=0, sticky="n")
        dire = ttk.Frame(self.root, padding=6)
        dire.grid(row=0, column=2, sticky="n")

        # ---- área de desenho
        self.canvas = tk.Canvas(self.root, width=LARGURA * ESCALA, height=ALTURA * ESCALA,
                                bg="white", highlightthickness=1, cursor="crosshair")
        self.canvas.grid(row=0, column=1, padx=4, pady=6)
        self.canvas.bind("<Button-1>", self.ao_pressionar)
        self.canvas.bind("<B1-Motion>", self.ao_arrastar)
        self.canvas.bind("<ButtonRelease-1>", self.ao_soltar)
        self.canvas.bind("<Motion>", self.ao_mover)
        self.canvas.bind("<Button-2>", self.ao_botao_direito)
        self.canvas.bind("<Button-3>", self.ao_botao_direito)

        # painel esquerdo
        f = ttk.LabelFrame(esq, text="Desenho / Rasterização", padding=4)
        f.pack(fill="x", pady=3)
        for texto, modo in (("Ponto", "ponto"), ("Reta - DDA", "dda"),
                            ("Reta - Bresenham", "bresenham"),
                            ("Circunferência - Bresenham", "circulo"),
                            ("Polígono", "poligono")):
            self._botao(f, texto, lambda m=modo: self.set_modo(m))
        self._botao(f, "Fechar polígono", self.fechar_poligono)

        f = ttk.LabelFrame(esq, text="Seleção", padding=4)
        f.pack(fill="x", pady=3)
        self._botao(f, "Selecionar (região retangular)", lambda: self.set_modo("selecionar"))
        ttk.Checkbutton(f, text="Somar à seleção", variable=self.var_somar).pack(anchor="w")
        self._botao(f, "Limpar seleção", self.limpar_selecao)
        self._botao(f, "Excluir selecionados", self.excluir_selecionados)

        f = ttk.LabelFrame(esq, text="Geral", padding=4)
        f.pack(fill="x", pady=3)
        self._botao(f, "Desfazer", self.desfazer)
        self._botao(f, "Limpar tudo", self.limpar_tudo)
        ttk.Checkbutton(f, text="Mostrar grade", variable=self.var_grade,
                        command=self.redesenhar).pack(anchor="w")

        # painel direito - transformações
        f = ttk.LabelFrame(dire, text="Transformações 2D (nos selecionados)", padding=4)
        f.pack(fill="x")
        self._slider(f, "Deslocamento X (px)", self.var_dx, -50, 50, 1)
        self._slider(f, "Deslocamento Y (px, + = para baixo)", self.var_dy, -50, 50, 1)
        self._botao(f, "Translação", lambda: self.transformar("translacao"))
        self._slider(f, "Ângulo (graus, anti-horário)", self.var_ang, -180, 180, 1)
        self._botao(f, "Rotação", lambda: self.transformar("rotacao"))
        self._slider(f, "Fator de escala X", self.var_sx, 0.1, 5, 0.1)
        self._slider(f, "Fator de escala Y", self.var_sy, 0.1, 5, 0.1)
        self._botao(f, "Escala", lambda: self.transformar("escala"))
        self._botao(f, "Reflexão X", lambda: self.transformar("X"))
        self._botao(f, "Reflexão Y", lambda: self.transformar("Y"))
        self._botao(f, "Reflexão XY", lambda: self.transformar("XY"))
        ttk.Separator(f).pack(fill="x", pady=4)
        self._botao(f, "Definir pivô (clique)", lambda: self.set_modo("pivo"))
        self._botao(f, "Pivô = centro da seleção", self.pivo_centro)

        # barra inferior - recorte e preenchimento
        barra = ttk.Frame(self.root, padding=(6, 0))
        barra.grid(row=1, column=0, columnspan=3, sticky="w")

        f = ttk.LabelFrame(barra, text="Recorte (retas)", padding=4)
        f.pack(side="left", padx=4)
        for texto, cmd in (("Definir janela", lambda: self.set_modo("janela")),
                           ("Cohen-Sutherland", lambda: self.recortar("cohen")),
                           ("Liang-Barsky", lambda: self.recortar("liang")),
                           ("Limpar janela", self.limpar_janela)):
            ttk.Button(f, text=texto, command=cmd).pack(side="left", padx=2)

        f = ttk.LabelFrame(barra, text="Preenchimento", padding=4)
        f.pack(side="left", padx=4)
        ttk.Button(f, text="Boundary Fill", command=lambda: self.set_modo("boundary")).pack(side="left", padx=2)
        ttk.Button(f, text="Flood Fill", command=lambda: self.set_modo("flood")).pack(side="left", padx=2)
        ttk.Button(f, text="Limpar preench.", command=self.limpar_preenchimentos).pack(side="left", padx=2)
        ttk.Button(f, text="Cor do contorno", command=lambda: self.escolher_cor("contorno")).pack(side="left", padx=2)
        self.lbl_contorno = tk.Label(f, width=2, bg=self.cor_contorno, relief="sunken")
        self.lbl_contorno.pack(side="left")
        ttk.Button(f, text="Cor do preench.", command=lambda: self.escolher_cor("preench")).pack(side="left", padx=2)
        self.lbl_preench = tk.Label(f, width=2, bg=self.cor_preench, relief="sunken")
        self.lbl_preench.pack(side="left")

        # status
        st = ttk.Frame(self.root, padding=(6, 2))
        st.grid(row=2, column=0, columnspan=3, sticky="we")
        ttk.Label(st, textvariable=self.var_status).pack(side="left")
        ttk.Label(st, textvariable=self.var_coord).pack(side="right")

    # utilidades ------------------------------------------------------------------
    def msg(self, texto):
        self.var_status.set(texto)

    def set_modo(self, modo):
        self.modo = modo
        self.temp = []
        self.arrasto = None
        self.canvas.delete("previa")
        self.msg(DICAS[modo])
        self.redesenhar()

    def empilhar(self):
        self.historico.append(self.cena.snapshot())
        del self.historico[:-50]

    def desfazer(self):
        if self.historico:
            self.cena.restaurar(self.historico.pop())
            self.temp = []
            self.msg("Ação desfeita.")
            self.redesenhar()
        else:
            self.msg("Nada para desfazer.")

    def escolher_cor(self, qual):
        atual = self.cor_contorno if qual == "contorno" else self.cor_preench
        cor = colorchooser.askcolor(color=atual)[1]
        if not cor:
            return
        cor = cor.lower()
        if qual == "contorno":
            self.cor_contorno = cor
            self.lbl_contorno.config(bg=cor)
        else:
            self.cor_preench = cor
            self.lbl_preench.config(bg=cor)

    def _pos(self, ev):
        x = min(max(ev.x // ESCALA, 0), LARGURA - 1)
        y = min(max(ev.y // ESCALA, 0), ALTURA - 1)
        return x, y

    @staticmethod
    def _cel(x, y):
        """Coordenadas de canvas do quadrado do pixel (x, y)."""
        return x * ESCALA, y * ESCALA, (x + 1) * ESCALA, (y + 1) * ESCALA

    @staticmethod
    def _rect_canvas(x0, y0, x1, y1):
        xa, xb = sorted((x0, x1))
        ya, yb = sorted((y0, y1))
        return xa * ESCALA, ya * ESCALA, (xb + 1) * ESCALA, (yb + 1) * ESCALA

    @staticmethod
    def _centro_canvas(x, y):
        return x * ESCALA + ESCALA / 2, y * ESCALA + ESCALA / 2

    # eventos ------------------------------------------------------------------
    def ao_pressionar(self, ev):
        x, y = self._pos(ev)
        if self.modo in ("selecionar", "janela"):
            self.arrasto = (x, y)
            return
        self.clique(x, y)

    def ao_arrastar(self, ev):
        x, y = self._pos(ev)
        self.var_coord.set(f"x={x}  y={y}")
        if self.arrasto:
            self.canvas.delete("previa")
            cor = "#1e90ff" if self.modo == "selecionar" else "#d62728"
            self.canvas.create_rectangle(*self._rect_canvas(*self.arrasto, x, y),
                                         outline=cor, dash=(4, 3), width=2, tags="previa")

    def ao_soltar(self, ev):
        if not self.arrasto:
            return
        x, y = self._pos(ev)
        x0, y0 = self.arrasto
        self.arrasto = None
        self.canvas.delete("previa")
        if self.modo == "selecionar":
            self.cena.selecionar_retangulo(x0, y0, x, y, self.var_somar.get())
            self.msg(f"{len(self.cena.selecionados())} objeto(s) selecionado(s).")
        else:  # janela de recorte
            self.empilhar()
            xa, xb = sorted((x0, x))
            ya, yb = sorted((y0, y))
            self.cena.janela = (xa, ya, xb, yb)
            self.msg("Janela definida. Use Cohen-Sutherland ou Liang-Barsky para recortar.")
        self.redesenhar()

    def ao_botao_direito(self, ev):
        if self.modo == "poligono":
            self.fechar_poligono()

    def ao_mover(self, ev):
        x, y = self._pos(ev)
        self.var_coord.set(f"x={x}  y={y}")
        self.canvas.delete("previa")
        if self.modo in ("dda", "bresenham") and len(self.temp) == 1:
            ax, ay = self._centro_canvas(*self.temp[0])
            bx, by = self._centro_canvas(x, y)
            self.canvas.create_line(ax, ay, bx, by, fill="#888", dash=(3, 3), tags="previa")
        elif self.modo == "circulo" and len(self.temp) == 1:
            cx, cy = self.temp[0]
            r = math.hypot(x - cx, y - cy) * ESCALA
            ax, ay = self._centro_canvas(cx, cy)
            self.canvas.create_oval(ax - r, ay - r, ax + r, ay + r,
                                    outline="#888", dash=(3, 3), tags="previa")
        elif self.modo == "poligono" and self.temp:
            pts = [c for p in self.temp for c in self._centro_canvas(*p)]
            pts += list(self._centro_canvas(x, y))
            if len(pts) >= 4:
                self.canvas.create_line(*pts, fill="#888", dash=(3, 3), tags="previa")

    # eventos ------------------------------------------------------------------
    def clique(self, x, y):
        m = self.modo
        if m == "ponto":
            self.empilhar()
            self.cena.adicionar(Ponto(x, y, self.cor_contorno))
        elif m in ("dda", "bresenham"):
            self.temp.append((x, y))
            if len(self.temp) == 2:
                (x0, y0), (x1, y1) = self.temp
                self.empilhar()
                self.cena.adicionar(Reta(Ponto(x0, y0), Ponto(x1, y1), m, self.cor_contorno))
                self.temp = []
        elif m == "circulo":
            self.temp.append((x, y))
            if len(self.temp) == 2:
                (cx, cy), (bx, by) = self.temp
                self.empilhar()
                self.cena.adicionar(Circulo(Ponto(cx, cy), round(math.hypot(bx - cx, by - cy)),
                                            self.cor_contorno))
                self.temp = []
        elif m == "poligono":
            self.temp.append((x, y))
        elif m == "pivo":
            self.pivo = (x, y)
            self.msg(f"Pivô definido em ({x}, {y}).")
        elif m in ("boundary", "flood"):
            self.empilhar()
            self.cena.preenchimentos.append((m, x, y, self.cor_preench, self.cor_contorno))
        self.redesenhar()

    def fechar_poligono(self):
        if len(self.temp) < 3:
            self.msg("Um polígono precisa de pelo menos 3 vértices.")
            return
        self.empilhar()
        self.cena.adicionar(Poligono([Ponto(x, y) for x, y in self.temp], self.cor_contorno))
        self.temp = []
        self.canvas.delete("previa")
        self.redesenhar()

    # seleção / geral ------------------------------------------------------------------
    def limpar_selecao(self):
        self.cena.limpar_selecao()
        self.redesenhar()

    def excluir_selecionados(self):
        if not self.cena.selecionados():
            self.msg("Nenhum objeto selecionado.")
            return
        self.empilhar()
        self.cena.objetos = [o for o in self.cena.objetos if not o.selecionado]
        self.redesenhar()

    def limpar_tudo(self):
        self.empilhar()
        self.cena = Cena()
        self.temp = []
        self.pivo = None
        self.redesenhar()

    def limpar_janela(self):
        if self.cena.janela:
            self.empilhar()
            self.cena.janela = None
            self.redesenhar()

    def limpar_preenchimentos(self):
        if self.cena.preenchimentos:
            self.empilhar()
            self.cena.preenchimentos = []
            self.redesenhar()

    def pivo_centro(self):
        self.pivo = None
        self.msg("Pivô = centro da caixa envolvente da seleção.")
        self.redesenhar()

    # transformações ------------------------------------------------------------------
    def _pivo(self, sel):
        if self.pivo:
            return self.pivo
        pts = [v for o in sel for v in o.vertices()]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2

    def transformar(self, nome):
        sel = self.cena.selecionados()
        if not sel:
            self.msg("Selecione objetos antes (modo Selecionar: arraste um retângulo).")
            return
        cx, cy = self._pivo(sel)
        if nome == "translacao":
            m = tf.translacao(self.var_dx.get(), self.var_dy.get())
        elif nome == "rotacao":
            m = tf.rotacao(self.var_ang.get(), cx, cy)
        elif nome == "escala":
            m = tf.escala(self.var_sx.get(), self.var_sy.get(), cx, cy)
        else:
            m = tf.reflexao(nome, cx, cy)
        self.empilhar()
        for o in sel:
            o.transformar(m)
        self.redesenhar()

    # recorte ------------------------------------------------------------------
    def recortar(self, algoritmo):
        if not self.cena.janela:
            self.msg("Defina antes a janela de recorte (botão 'Definir janela').")
            return
        xmin, ymin, xmax, ymax = self.cena.janela
        func = cohen_sutherland if algoritmo == "cohen" else liang_barsky
        retas = [o for o in self.cena.objetos if isinstance(o, Reta)]
        alvo = [r for r in retas if r.selecionado] or retas
        if not alvo:
            self.msg("Não há retas para recortar.")
            return
        self.empilhar()
        removidas = 0
        for r in alvo:
            res = func(r.p1.x, r.p1.y, r.p2.x, r.p2.y, xmin, ymin, xmax, ymax)
            if res is None:
                self.cena.objetos.remove(r)
                removidas += 1
            else:
                r.p1.x, r.p1.y, r.p2.x, r.p2.y = res
        self.msg(f"Recorte concluído: {len(alvo) - removidas} reta(s) mantida(s), "
                 f"{removidas} removida(s) (fora da janela).")
        self.redesenhar()

    # renderização ------------------------------------------------------------------
    def redesenhar(self):
        self.cena.renderizar(self.matriz)
        self.img.put(self.matriz.como_dados())
        self.img_zoom = self.img.zoom(ESCALA)
        c = self.canvas
        c.delete("all")
        c.create_image(0, 0, image=self.img_zoom, anchor="nw")

        if self.var_grade.get():
            for i in range(1, LARGURA):
                c.create_line(i * ESCALA, 0, i * ESCALA, ALTURA * ESCALA, fill="#e3e3e3")
            for j in range(1, ALTURA):
                c.create_line(0, j * ESCALA, LARGURA * ESCALA, j * ESCALA, fill="#e3e3e3")

        if self.cena.janela:
            c.create_rectangle(*self._rect_canvas(*self.cena.janela),
                               outline="#d62728", dash=(4, 3), width=2)

        for o in self.cena.selecionados():
            for x, y in o.pontos_controle():
                px, py = arred(x), arred(y)
                x0, y0, x1, y1 = self._cel(px, py)
                c.create_rectangle(x0 - 2, y0 - 2, x1 + 2, y1 + 2, outline="#1e90ff", width=2)

        if self.pivo:
            px, py = self._centro_canvas(*self.pivo)
            c.create_line(px - 8, py, px + 8, py, fill="#c000c0", width=2)
            c.create_line(px, py - 8, px, py + 8, fill="#c000c0", width=2)

        for x, y in self.temp:  # vértices já clicados
            c.create_rectangle(*self._cel(x, y), outline="#888", width=2)


if __name__ == "__main__":
    raiz = tk.Tk()
    App(raiz)
    raiz.mainloop()
