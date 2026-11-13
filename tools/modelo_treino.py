# Gera o modelo de plano de treino do STEK (formulário PDF preenchível) para o módulo Força.
# O app lê os campos pelo nome (stek_f_*), então o layout pode mudar sem quebrar a importação.
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

OUT = sys.argv[1] if len(sys.argv) > 1 else "modelo-plano-de-treino.pdf"
W, H = A4
M = 36
ACC = HexColor("#6d28d9"); INK = HexColor("#1e1433"); MUT = HexColor("#5b5370")
LINE = HexColor("#c9b8f5"); FILL = HexColor("#f7f4ff"); HEAD = HexColor("#ede7ff")
TREINOS, ROWS, ROW = 6, 10, 17
CW = W - 2 * M
COLS = [("Exercício", 196, "ex", "Nome do exercício, ex.: Supino reto com halteres"),
        ("Séries", 44, "series", "Séries de trabalho, ex.: 3 ou 3-4"),
        ("Repetições", 64, "reps", "Um número (10), uma faixa (8 a 12) ou tempo (30s)"),
        ("Descanso", 54, "desc", "Opcional, ex.: 60s ou 1min30"),
        ("Observação", CW - 196 - 44 - 64 - 54, "obs", "Opcional: aquecimento, técnica, carga por halter…")]

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("STEK - modelo de plano de treino"); c.setAuthor("STEK"); c.setSubject("Preencha e importe no módulo Força")
form = c.acroForm
PAGES = 3

def tf(name, x, y, w, h, tip, fs=10, multi=False):
    form.textfield(name=name, tooltip=tip, x=x, y=y, width=w, height=h, value="", fontName="Helvetica", fontSize=fs,
                   borderStyle="solid", borderWidth=0.6, borderColor=LINE, fillColor=FILL, textColor=INK, forceBorder=True,
                   fieldFlags="multiline" if multi else "")

def label(x, y, t, size=10, bold=True, color=INK):
    c.setFillColor(color); c.setFont("Helvetica-Bold" if bold else "Helvetica", size); c.drawString(x, y, t)

def footer(p):
    c.setFillColor(MUT); c.setFont("Helvetica", 7.5)
    c.drawString(M, 22, "STEK · modelo de plano de treino")
    c.drawRightString(W - M, 22, "Página %d de %d" % (p, PAGES))

def block(top, t):
    fh = 19; base = (fh - 10) / 2 + 2
    label(M, top - 12, "TREINO %d" % t, 9, True, ACC)
    y = top - 18 - fh
    label(M, y + base, "Nome:"); tf("stek_f_t%d_nome" % t, M + 40, y, 300, fh, "Nome do treino, ex.: Treino A – Peito e tríceps")
    label(M + 352, y + base, "Dias:"); tf("stek_f_t%d_dias" % t, M + 384, y, CW - 384, fh, "Dias da semana, ex.: seg e qui. Vazio = treino opcional")
    y -= fh + 6
    label(M, y + base, "Foco:"); tf("stek_f_t%d_foco" % t, M + 40, y, CW - 40, fh, "Opcional: objetivo do treino, ex.: peito e tríceps")
    y -= 4
    c.setFillColor(HEAD); c.rect(M, y - 15, CW, 15, stroke=0, fill=1)
    x = M
    for name, w, k, tip in COLS:
        label(x + 4, y - 11, name, 8.5, True, ACC); x += w
    y -= 15
    for r in range(1, ROWS + 1):
        y -= ROW; x = M
        for name, w, k, tip in COLS:
            tf("stek_f_t%d_e%d_%s" % (t, r, k), x, y + 1.5, w, ROW - 3, tip, fs=8.5); x += w
    return y - 14

# ---------- página 1 ----------
c.setFillColor(ACC); c.rect(0, H - 6, W, 6, stroke=0, fill=1)
label(M, H - 46, "STEK · FORÇA", 11, True, ACC)
label(M, H - 70, "Plano de treino", 22, True, INK)
c.setFont("Helvetica", 9.5); c.setFillColor(MUT)
c.drawString(M, H - 88, "Preencha direto neste PDF (no celular ou no computador), salve e importe no app, no módulo Força.")
y = H - 120; fh = 20; base = (fh - 10) / 2 + 2
label(M, y + base, "Plano:"); tf("stek_f_plano", M + 44, y, CW - 44, fh, "Nome do plano, ex.: Hipertrofia – Ana")
y -= 26
label(M, y + base, "Observações:"); tf("stek_f_obs", M + 80, y - 14, CW - 80, fh + 14, "Opcional: aquecimento, progressão, cuidados", fs=9, multi=True)
y -= 30
label(M, y, "Como preencher", 11, True, ACC)
tips = ["Um bloco por treino (até 6). Dias: os dias da semana daquele treino (ex.: seg e qui). Sem dia, o treino fica como opcional.",
        "Repetições: um número (10), uma faixa (8 a 12) ou tempo (30s). Descanso e Observação são opcionais.",
        "No app você anota carga, séries e repetições de cada exercício, e ele avisa quando é hora de subir a carga.",
        "Treinos e linhas vazias são ignorados."]
for t in tips:
    words, line, first = t.split(" "), "", True
    for w_ in words + [None]:
        if w_ is not None and stringWidth(("· " if first else "   ") + line + " " + w_, "Helvetica", 8.8) < CW:
            line = (line + " " + w_).strip(); continue
        y -= 12.5; c.setFont("Helvetica", 8.8); c.setFillColor(INK); c.drawString(M, y, ("· " if first else "   ") + line); first = False; line = w_ or ""
        if w_ is None: break
y -= 10
t = 1
y = block(y, t); t += 1
y = block(y, t); t += 1
footer(1)
for p in range(2, PAGES + 1):
    c.showPage()
    c.setFillColor(ACC); c.rect(0, H - 6, W, 6, stroke=0, fill=1)
    label(M, H - 32, "Plano de treino · continuação", 11, True, INK)
    y = H - 42
    while t <= TREINOS and y - (18 + 19 + 25 + 4 + 15 + ROWS * ROW + 14) > 34:
        y = block(y, t); t += 1
    footer(p)
c.save()
print("treinos:", t - 1)
