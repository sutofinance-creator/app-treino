# Gera o modelo de plano de estudos do STEK (formulário PDF preenchível).
# O app lê os campos pelo nome (stek_*), então o layout pode mudar sem quebrar a importação.
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas

OUT = sys.argv[1] if len(sys.argv) > 1 else "modelo-plano-de-estudos.pdf"
W, H = A4
M = 36
ACC = HexColor("#6d28d9"); INK = HexColor("#1e1433"); MUT = HexColor("#5b5370")
LINE = HexColor("#c9b8f5"); FILL = HexColor("#f7f4ff"); HEAD = HexColor("#ede7ff")
PAGES = 3
COLS = [("Data", 74, "data", "Dia (13/11) ou intervalo (28/11 a 03/12)"),
        ("Qtd", 40, "qtd", "Quantos exercícios, aulas, páginas… nesse dia"),
        ("O que fazer", 236, "fazer", "Quais itens: Lista 1: 3, 4, 5(a)"),
        ("Teoria", W - 2 * M - 74 - 40 - 236, "teoria", "Assunto do dia, Revisão ou Folga")]
ROW = 19

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("STEK - modelo de plano de estudos"); c.setAuthor("STEK"); c.setSubject("Preencha e importe em Inteligência > Matérias")
form = c.acroForm
n = 0

def tf(name, x, y, w, h, tip, fs=10, value="", multi=False):
    form.textfield(name=name, tooltip=tip, x=x, y=y, width=w, height=h, value=value, fontName="Helvetica", fontSize=fs,
                   borderStyle="solid", borderWidth=0.6, borderColor=LINE, fillColor=FILL, textColor=INK, forceBorder=True,
                   fieldFlags="multiline" if multi else "")

def label(x, y, t, size=10, bold=True, color=INK):
    c.setFillColor(color); c.setFont("Helvetica-Bold" if bold else "Helvetica", size); c.drawString(x, y, t)

def footer(p):
    c.setFillColor(MUT); c.setFont("Helvetica", 7.5)
    c.drawString(M, 22, "STEK · modelo de plano de estudos")
    c.drawRightString(W - M, 22, "Página %d de %d" % (p, PAGES))

def table(top, p):
    global n
    x = M; c.setFillColor(HEAD); c.rect(M, top - 16, W - 2 * M, 16, stroke=0, fill=1)
    for t, w, k, tip in COLS:
        label(x + 4, top - 11.5, t, 9, True, ACC); x += w
    y = top - 16 - ROW
    while y > 36:
        n += 1; x = M
        for t, w, k, tip in COLS:
            tf("stek_d%d_%s" % (n, k), x, y + 1.5, w, ROW - 3, tip, fs=9); x += w
        y -= ROW
    footer(p)

# ---------- página 1: dados da matéria, instruções e as primeiras linhas ----------
c.setFillColor(ACC); c.rect(0, H - 6, W, 6, stroke=0, fill=1)
label(M, H - 46, "STEK", 11, True, ACC)
label(M, H - 70, "Plano de estudos", 22, True, INK)
c.setFont("Helvetica", 9.5); c.setFillColor(MUT)
c.drawString(M, H - 88, "Preencha direto neste PDF (no celular ou no computador), salve e importe no app em Inteligência > Matérias.")

y = H - 122; fh = 20; base = (fh - 10) / 2 + 2
label(M, y + base, "Matéria:"); tf("stek_materia", M + 56, y, W - 2 * M - 56, fh, "Nome da matéria, ex.: Cálculo 2")
y -= 28
label(M, y + base, "Contar por:"); tf("stek_unidade", M + 70, y, 90, fh, "exercícios, aulas, páginas, módulos, lições ou capítulos", value="exercícios")
label(M + 176, y + base, "Já feitos antes do plano:"); tf("stek_feitos", M + 316, y, 50, fh, "Quantos você já tinha feito antes do primeiro dia do plano")
label(M + 382, y + base, "Total:"); tf("stek_total", M + 420, y, W - 2 * M - 420, fh, "Opcional: total da matéria. Vazio = já feitos + soma das linhas")
y -= 28
label(M, y + base, "Provas:"); tf("stek_provas", M + 50, y, W - 2 * M - 50, fh, "Datas das provas separadas por vírgula, ex.: 04/12, 11/12")
y -= 22
label(M, y, "Observações", 10)
c.setFont("Helvetica", 8.5); c.setFillColor(MUT); c.drawString(M + 72, y, "dicas que você quer ver no app (o que fazer se atrasar, reservas…)")
y -= 46; tf("stek_obs", M, y, W - 2 * M, 40, "Observações da matéria", fs=9, multi=True)

y -= 22; label(M, y, "Como preencher", 11, True, ACC)
tips = ["Uma linha por dia de estudo, com a data no formato dia/mês (ex.: 13/11).",
        "Qtd: quanto você vai fazer no dia, na unidade de “Contar por”. Deixe vazio em dia só de teoria ou revisão.",
        "O que fazer: os itens do dia (ex.: Lista 1: 3, 4, 5(a)). Teoria: o assunto do dia, ou escreva Revisão ou Folga.",
        "Mesma tarefa em vários dias: escreva o intervalo na Data (ex.: 28/11 a 03/12). A quantidade é dividida igualmente entre os dias.",
        "Se acabarem as linhas, continue nas páginas 2 e 3. Linhas vazias são ignoradas."]
from reportlab.pdfbase.pdfmetrics import stringWidth
c.setFillColor(INK)
for t in tips:
    words, line, first = t.split(" "), "", True
    for w_ in words + [None]:
        if w_ is not None and stringWidth(("· " if first else "  ") + line + " " + w_, "Helvetica", 8.8) < W - 2 * M:
            line = (line + " " + w_).strip(); continue
        y -= 12.5; c.setFont("Helvetica", 8.8); c.drawString(M, y, ("· " if first else "   ") + line); first = False; line = w_ or ""
        if w_ is None: break
table(y - 14, 1)

for p in range(2, PAGES + 1):
    c.showPage()
    c.setFillColor(ACC); c.rect(0, H - 6, W, 6, stroke=0, fill=1)
    label(M, H - 34, "Plano de estudos · continuação", 11, True, INK)
    table(H - 46, p)

c.save()
print("linhas:", n)
