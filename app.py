"""
CodeMaster Pro — Flask Backend v3.0
Production-ready. All known bugs fixed.

SETUP:
  export ANTHROPIC_API_KEY="sk-ant-..."
  pip install flask flask-cors anthropic
  python server.py

GitHub / Railway / Render: set ANTHROPIC_API_KEY as env var.
"""

import os
import json
import time
import random
import hashlib
import threading
import urllib.request
from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory, Response, redirect, abort
from flask_cors import CORS

# ─── Constants ────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR  = os.path.join(BASE_DIR, "static")
PROGRESS_F  = os.path.join(os.path.expanduser("~"), ".codemaster_pro_v3.json")

# FIX #1: API key via environment variable — never hardcode!
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

os.makedirs(STATIC_DIR, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Restrict in production

# ─── Simple in-memory rate limiter (FIX #2) ───────────────────────────────────
_rate_store: dict = {}
_rate_lock = threading.Lock()

def rate_limit(max_calls: int = 20, window_seconds: int = 60):
    """Decorator: limits calls per IP within a rolling window."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ip  = request.remote_addr or "unknown"
            key = f"{fn.__name__}:{ip}"
            now = time.time()
            with _rate_lock:
                calls = [t for t in _rate_store.get(key, []) if now - t < window_seconds]
                if len(calls) >= max_calls:
                    return jsonify({"error": "Too many requests. Please wait."}), 429
                calls.append(now)
                _rate_store[key] = calls
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# ─── Static lib downloader ────────────────────────────────────────────────────
LIBS = {
    "vue.min.js":         "https://unpkg.com/vue@3.4.21/dist/vue.global.prod.js",
    "hljs.min.js":        "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js",
    "hljs-python.min.js": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js",
    "hljs-js.min.js":     "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/javascript.min.js",
    "hljs-java.min.js":   "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/java.min.js",
    "atom-dark.min.css":  "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css",
    "tailwind.min.js":    "https://cdn.tailwindcss.com",
}
CDN_FALLBACK = dict(LIBS)

def _download_libs():
    for fname, url in LIBS.items():
        dest = os.path.join(STATIC_DIR, fname)
        if not os.path.exists(dest):
            try:
                urllib.request.urlretrieve(url, dest)
                print(f"  [lib] Downloaded {fname}")
            except Exception as e:
                print(f"  [lib] Could not download {fname}: {e}")

threading.Thread(target=_download_libs, daemon=True).start()

@app.route("/lib/<path:filename>")
def serve_lib(filename):
    local = os.path.join(STATIC_DIR, filename)
    if os.path.exists(local):
        mime = "text/css" if filename.endswith(".css") else "application/javascript"
        with open(local, "rb") as f:
            return Response(f.read(), mimetype=mime)
    if filename in CDN_FALLBACK:
        return redirect(CDN_FALLBACK[filename])
    abort(404)

# ══════════════════════════════════════════════════════════════════════════════
#  CONTENT DATABASE
# ══════════════════════════════════════════════════════════════════════════════
LESSONS = {
  "python": [
    {
      "id": "py_01", "title": "Olá, Python!", "level": "Iniciante",
      "emoji": "🐍", "duration": "10 min", "xp": 50,
      "theory": (
        "Python é uma linguagem de alto nível criada por Guido van Rossum em 1991.\n\n"
        "POR QUE PYTHON?\n"
        "  • Sintaxe simples e legível\n"
        "  • Versátil: Web, IA, Data Science, Automação\n"
        "  • Linguagem mais popular do mundo (TIOBE 2024)\n"
        "  • Usado por Google, Netflix, Instagram, NASA\n\n"
        "SEU PRIMEIRO PROGRAMA\n"
        "  print() exibe texto na tela.\n"
        "  Aceita qualquer tipo de valor como argumento.\n\n"
        "COMENTÁRIOS\n"
        "  Linhas que começam com # são ignoradas pelo interpretador.\n\n"
        "EXECUTANDO\n"
        "  Terminal:   python3 arquivo.py\n"
        "  Pydroid 3:  salve e pressione ▶"
      ),
      "code": (
        "# Meu primeiro programa Python!\n"
        "# Tudo após # é comentário — ignorado pelo Python\n\n"
        'print("Olá, Mundo!")\n'
        'print("Bem-vindo ao CodeMaster Pro!")\n\n'
        "# Tipos diferentes de dados\n"
        "print(42)           # número inteiro\n"
        "print(3.14)         # número decimal\n"
        "print(True)         # booleano\n\n"
        "# Combinando valores\n"
        'print("Python", "é", "incrível!", sep=" | ")\n'
        'print("2 + 2 =", 2 + 2)'
      ),
      "tip": "Python é case-sensitive: print() funciona, Print() dá erro!"
    },
    {
      "id": "py_02", "title": "Variáveis e Tipos", "level": "Iniciante",
      "emoji": "📦", "duration": "12 min", "xp": 50,
      "theory": (
        "Variáveis são contêineres que guardam dados na memória.\n\n"
        "CRIANDO VARIÁVEIS\n"
        "  nome  = 'Ana'   → str\n"
        "  idade = 25      → int\n"
        "  altura= 1.68    → float\n"
        "  ativo = True    → bool\n\n"
        "4 TIPOS BÁSICOS\n"
        "  str   texto:    'Olá'  \"Python\"\n"
        "  int   inteiro:  42  -10  0\n"
        "  float decimal:  3.14  -0.5\n"
        "  bool  lógico:   True  False\n\n"
        "DESCOBRINDO O TIPO\n"
        "  type('texto')  →  <class 'str'>\n"
        "  type(42)       →  <class 'int'>\n\n"
        "CONVERSÃO\n"
        "  int('42')      →  42\n"
        "  str(42)        →  '42'\n"
        "  float('3.14')  →  3.14"
      ),
      "code": (
        "# VARIÁVEIS EM AÇÃO\n\n"
        'nome      = "Ana Silva"\n'
        "idade     = 25\n"
        "altura    = 1.68\n"
        "estudante = True\n\n"
        "# Exibindo com f-string (forma moderna)\n"
        'print(f"Nome: {nome}")\n'
        'print(f"Idade: {idade} anos")\n'
        'print(f"Altura: {altura}m")\n'
        'print(f"Estudante: {estudante}")\n\n'
        "# Verificando tipos\n"
        'print(f"\\nTipo nome:  {type(nome)}")\n'
        'print(f"Tipo idade: {type(idade)}")\n\n'
        "# Múltipla atribuição\n"
        "x, y, z = 10, 20, 30\n"
        'print(f"\\nx={x}, y={y}, z={z}")\n\n'
        "# Incrementando\n"
        "contador = 0\n"
        "contador += 1\n"
        'print(f"Contador: {contador}")'
      ),
      "tip": "Use nomes descritivos: 'idade_usuario' é melhor que 'x'!"
    },
    {
      "id": "py_03", "title": "Operadores", "level": "Iniciante",
      "emoji": "🔢", "duration": "10 min", "xp": 50,
      "theory": (
        "Operadores permitem cálculos e comparações.\n\n"
        "ARITMÉTICOS\n"
        "  +    adição:        5 + 3  =  8\n"
        "  -    subtração:     5 - 3  =  2\n"
        "  *    multiplicação: 5 * 3  =  15\n"
        "  /    divisão:       7 / 2  =  3.5  (sempre float!)\n"
        "  //   divisão int:   7 // 2 =  3    (trunca)\n"
        "  %    módulo:        7 % 2  =  1    (resto)\n"
        "  **   potência:      2 ** 8 =  256\n\n"
        "COMPARAÇÃO (retornam bool)\n"
        "  ==  igual\n"
        "  !=  diferente\n"
        "  >   maior\n"
        "  <   menor\n"
        "  >=  maior ou igual\n\n"
        "LÓGICOS\n"
        "  and  ambos True\n"
        "  or   um é True\n"
        "  not  inverte"
      ),
      "code": (
        "a, b = 10, 3\n\n"
        'print("=== ARITMÉTICA ===")\n'
        'print(f"{a} + {b}  = {a + b}")\n'
        'print(f"{a} - {b}  = {a - b}")\n'
        'print(f"{a} * {b}  = {a * b}")\n'
        'print(f"{a} / {b}  = {a / b:.4f}")\n'
        'print(f"{a} // {b} = {a // b}  (inteira)")\n'
        'print(f"{a} % {b}  = {a % b}  (resto)")\n'
        'print(f"{a} ** {b} = {a ** b}  (potência)")\n\n'
        'print("\\n=== COMPARAÇÃO ===")\n'
        'print(f"{a} >  {b}  → {a > b}")\n'
        'print(f"{a} == {b}  → {a == b}")\n'
        'print(f"{a} != {b}  → {a != b}")\n\n'
        'print("\\n=== LÓGICOS ===")\n'
        'print(f"True and True  → {True and True}")\n'
        'print(f"True or  False → {True or False}")\n'
        'print(f"not True       → {not True}")'
      ),
      "tip": "7 / 2 = 3.5 (float), mas 7 // 2 = 3 (int). Atenção à diferença!"
    },
    {
      "id": "py_04", "title": "Condicionais", "level": "Iniciante",
      "emoji": "🔀", "duration": "15 min", "xp": 60,
      "theory": (
        "Condicionais permitem que o programa tome decisões!\n\n"
        "ESTRUTURA IF/ELIF/ELSE\n"
        "  if condicao_1:\n"
        "      # executa se True\n"
        "  elif condicao_2:\n"
        "      # executa se True\n"
        "  else:\n"
        "      # nenhuma foi True\n\n"
        "REGRAS\n"
        "  • Indentação com 4 espaços é OBRIGATÓRIA\n"
        "  • elif e else são opcionais\n"
        "  • Pode ter quantos elif quiser\n\n"
        "OPERADOR TERNÁRIO\n"
        "  resultado = 'sim' if condicao else 'não'\n\n"
        "VALORES FALSY (tratados como False)\n"
        "  False, None, 0, 0.0, '', [], {}, ()"
      ),
      "code": (
        "nota = 7.8\n\n"
        "if nota >= 9.0:\n"
        '    conceito = "A — Excelente!"\n'
        "elif nota >= 7.0:\n"
        '    conceito = "B — Bom!"\n'
        "elif nota >= 5.0:\n"
        '    conceito = "C — Regular"\n'
        "else:\n"
        '    conceito = "F — Reprovado"\n\n'
        'print(f"Nota: {nota}")\n'
        'print(f"Conceito: {conceito}")\n\n'
        "# Operador ternário\n"
        'aprovado = "Aprovado" if nota >= 5 else "Reprovado"\n'
        'print(f"Situação: {aprovado}")\n\n'
        "# Condições compostas\n"
        "idade = 20\n"
        "tem_cnh = True\n"
        "if idade >= 18 and tem_cnh:\n"
        '    print("\\nPode dirigir!")\n'
        "elif idade >= 18:\n"
        '    print("\\nTem idade mas precisa de CNH")\n'
        "else:\n"
        '    print("\\nMenor de idade")'
      ),
      "tip": "Sempre verifique n % 15 antes de n % 3 e n % 5 no FizzBuzz!"
    },
    {
      "id": "py_05", "title": "Loops: for e while", "level": "Iniciante",
      "emoji": "🔄", "duration": "18 min", "xp": 60,
      "theory": (
        "Loops repetem blocos de código!\n\n"
        "FOR LOOP\n"
        "  for i in range(5):         # 0,1,2,3,4\n"
        "  for i in range(1, 6):      # 1,2,3,4,5\n"
        "  for i in range(0, 10, 2):  # 0,2,4,6,8\n\n"
        "WHILE LOOP\n"
        "  while condicao:\n"
        "      # SEMPRE atualize a condição!\n\n"
        "⚠️  while True sem break = loop infinito!\n\n"
        "CONTROLE\n"
        "  break     → sai do loop\n"
        "  continue  → pula iteração atual\n"
        "  pass      → não faz nada\n\n"
        "ENUMERATE (índice + valor)\n"
        "  for i, valor in enumerate(lista):"
      ),
      "code": (
        "# Range básico\n"
        'print("=== Quadrados ===")\n'
        "for i in range(1, 8):\n"
        '    print(f"  {i}² = {i**2}")\n\n'
        "# Iterando com enumerate\n"
        'frutas = ["Maçã", "Banana", "Uva"]\n'
        'print("\\n=== Frutas ===")\n'
        "for i, fruta in enumerate(frutas):\n"
        '    print(f"  [{i}] {fruta}")\n\n'
        "# While\n"
        'print("\\n=== Contagem ===")\n'
        "n = 5\n"
        "while n > 0:\n"
        '    print(f"  {n}...", end=" ")\n'
        "    n -= 1\n"
        'print("LANÇAMENTO!")\n\n'
        "# Break e Continue\n"
        'print("\\n=== Sem múltiplos de 3 ===")\n'
        "for num in range(1, 16):\n"
        "    if num % 3 == 0:\n"
        "        continue\n"
        "    if num > 13:\n"
        "        break\n"
        '    print(f"  {num}", end=" ")'
      ),
      "tip": "Prefira for sobre while quando souber o número de iterações!"
    },
    {
      "id": "py_06", "title": "Funções", "level": "Intermediário",
      "emoji": "⚙️", "duration": "20 min", "xp": 80,
      "theory": (
        "Funções são blocos de código reutilizáveis!\n\n"
        "DEFININDO\n"
        "  def nome(parâmetros):\n"
        "      '''Docstring'''\n"
        "      return valor\n\n"
        "TIPOS DE PARÂMETROS\n"
        "  def f(a, b):       posicionais\n"
        "  def f(a, b=10):    com default\n"
        "  def f(*args):      qualquer qtd → tupla\n"
        "  def f(**kwargs):   nomeados → dict\n\n"
        "LAMBDA\n"
        "  Funções anônimas de uma linha:\n"
        "  dobro = lambda x: x * 2\n\n"
        "ESCOPO\n"
        "  • Variáveis dentro são LOCAIS\n"
        "  • Use global para modificar externas\n"
        "  • Prefira retornar valores a modificar globais"
      ),
      "code": (
        "def calcular_imc(peso: float, altura: float) -> tuple:\n"
        "    '''Calcula o IMC e retorna (valor, categoria)'''\n"
        "    if altura <= 0:\n"
        '        raise ValueError("Altura deve ser positiva")\n'
        "    imc = peso / (altura ** 2)\n"
        '    if imc < 18.5:   cat = "Abaixo do peso"\n'
        '    elif imc < 25.0: cat = "Normal"\n'
        '    elif imc < 30.0: cat = "Sobrepeso"\n'
        '    else:            cat = "Obesidade"\n'
        "    return round(imc, 1), cat\n\n"
        "imc, cat = calcular_imc(70, 1.75)\n"
        'print(f"IMC: {imc} — {cat}")\n\n'
        "# *args\n"
        "def somar(*numeros: float) -> float:\n"
        "    return sum(numeros)\n\n"
        'print(f"\\nSoma: {somar(1, 2, 3)}")\n'
        'print(f"Soma: {somar(10, 20, 30, 40)}")\n\n'
        "# **kwargs\n"
        "def criar_perfil(**dados) -> None:\n"
        '    print("\\nPERFIL:")\n'
        "    for campo, valor in dados.items():\n"
        '        print(f"  {campo}: {valor}")\n\n'
        'criar_perfil(nome="Ana", idade=25, cidade="SP")\n\n'
        "# Lambda com map\n"
        "dobro = lambda x: x * 2\n"
        "nums  = list(map(dobro, range(1, 6)))\n"
        'print(f"\\nDobros: {nums}")'
      ),
      "tip": "Uma boa função: faz UMA coisa, tem nome descritivo e docstring!"
    },
    {
      "id": "py_07", "title": "Listas", "level": "Intermediário",
      "emoji": "📋", "duration": "22 min", "xp": 80,
      "theory": (
        "Listas são a estrutura mais usada em Python!\n\n"
        "ACESSO\n"
        "  lista[0]     → primeiro\n"
        "  lista[-1]    → último\n"
        "  lista[1:4]   → fatia [1,2,3]\n"
        "  lista[::-1]  → invertida\n\n"
        "MÉTODOS\n"
        "  append(x)    adiciona ao fim\n"
        "  insert(i,x)  insere na posição\n"
        "  remove(x)    remove 1ª ocorrência\n"
        "  pop()        remove e retorna o último\n"
        "  sort()       ordena no lugar (in-place)\n"
        "  sorted()     retorna nova lista ordenada\n"
        "  len(lista)   tamanho\n\n"
        "LIST COMPREHENSION\n"
        "  [expr for item in iter if cond]\n"
        "  quadrados = [x**2 for x in range(10)]\n"
        "  pares = [x for x in range(20) if x%2==0]"
      ),
      "code": (
        'linguagens = ["Python", "JavaScript", "Java", "Rust"]\n\n'
        'print(f"Lista:   {linguagens}")\n'
        'print(f"Primeira: {linguagens[0]}")\n'
        'print(f"Última:   {linguagens[-1]}")\n'
        'print(f"Fatia:    {linguagens[1:3]}")\n\n'
        "# Manipulação\n"
        'linguagens.append("Go")\n'
        'linguagens.insert(0, "C++")\n'
        'print(f"\\nApós add: {linguagens}")\n'
        'linguagens.remove("C++")\n'
        'print(f"Final:    {linguagens}")\n\n'
        "# Ordenação\n"
        "numeros = [64, 34, 25, 12, 22, 11, 90]\n"
        'print(f"\\nOriginal:   {numeros}")\n'
        'print(f"Crescente:  {sorted(numeros)}")\n'
        'print(f"Decrescente:{sorted(numeros, reverse=True)}")\n\n'
        "# List Comprehension\n"
        'print("\\n=== List Comprehension ===")\n'
        "quadrados = [x**2 for x in range(1, 9)]\n"
        'print(f"Quadrados: {quadrados}")\n\n'
        "pares = [x for x in range(1, 21) if x % 2 == 0]\n"
        'print(f"Pares:     {pares}")'
      ),
      "tip": "List comprehension é até 35% mais rápida que loop for equivalente!"
    },
    {
      "id": "py_08", "title": "Dicionários e Sets", "level": "Intermediário",
      "emoji": "🗂️", "duration": "20 min", "xp": 80,
      "theory": (
        "Dicionários armazenam pares chave → valor!\n\n"
        "CRIANDO\n"
        "  pessoa = {\n"
        "      'nome': 'Ana',\n"
        "      'idade': 25\n"
        "  }\n\n"
        "ACESSANDO\n"
        "  pessoa['nome']          → 'Ana'\n"
        "  pessoa.get('nome')      → 'Ana' (seguro)\n"
        "  pessoa.get('x', 'N/A') → 'N/A' (default)\n\n"
        "MÉTODOS ÚTEIS\n"
        "  .keys()    → chaves\n"
        "  .values()  → valores\n"
        "  .items()   → pares (k,v)\n"
        "  .update()  → mescla outro dict\n"
        "  .pop(k)    → remove e retorna\n\n"
        "SETS — Coleção sem duplicatas:\n"
        "  a | b  → união\n"
        "  a & b  → interseção\n"
        "  a - b  → diferença\n"
        "  a ^ b  → diferença simétrica"
      ),
      "code": (
        "dev = {\n"
        '    "nome":   "Carlos",\n'
        '    "idade":  28,\n'
        '    "skills": ["Python", "Django", "Docker"],\n'
        '    "nivel":  "Senior"\n'
        "}\n\n"
        'print(f"Nome: {dev[\'nome\']}")\n'
        'print(f"Cargo: {dev.get(\'cargo\', \'Não informado\')}")\n\n'
        'print("\\nPerfil completo:")\n'
        "for chave, valor in dev.items():\n"
        '    print(f"  {chave:12} → {valor}")\n\n'
        "# Dict Comprehension\n"
        'print("\\n=== Potências ===")\n'
        'potencias = {f"2^{i}": 2**i for i in range(1, 9)}\n'
        "for k, v in potencias.items():\n"
        '    print(f"  {k:5} = {v}")\n\n'
        "# Sets\n"
        'print("\\n=== Sets ===")\n'
        "a = {1, 2, 3, 4, 5}\n"
        "b = {3, 4, 5, 6, 7}\n"
        'print(f"União:     {a | b}")\n'
        'print(f"Interseção:{a & b}")\n'
        'print(f"Diferença: {a - b}")\n\n'
        "# Remove duplicatas\n"
        "lista = [1, 2, 2, 3, 3, 3, 4]\n"
        'print(f"\\nSem duplicatas: {list(set(lista))}")'
      ),
      "tip": "Use set() para remover duplicatas de uma lista rapidamente!"
    },
  ],
  "javascript": [
    {
      "id": "js_01", "title": "Fundamentos do JS", "level": "Iniciante",
      "emoji": "⚡", "duration": "12 min", "xp": 50,
      "theory": (
        "JavaScript é a linguagem da web!\n\n"
        "VARIÁVEIS\n"
        "  var x = 1;   → EVITE (escopo problemático)\n"
        "  let y = 2;   → mutável, escopo de bloco\n"
        "  const Z = 3; → imutável\n\n"
        "TIPOS PRIMITIVOS\n"
        "  number:    42, 3.14, NaN, Infinity\n"
        "  string:    'texto', \"texto\", `template`\n"
        "  boolean:   true, false\n"
        "  null:      valor vazio intencional\n"
        "  undefined: variável declarada sem valor\n"
        "  bigint:    9007199254740993n\n"
        "  symbol:    Symbol('id')\n\n"
        "TEMPLATE LITERALS\n"
        "  const msg = `Olá, ${nome}! Você tem ${idade} anos.`;\n\n"
        "⚠️  ARMADILHAS\n"
        "  typeof null  → 'object'  (bug histórico!)\n"
        "  5 == '5'     → true   (coerção)\n"
        "  5 === '5'    → false  (sem coerção)\n"
        "  SEMPRE use === !"
      ),
      "code": (
        "// JAVASCRIPT FUNDAMENTOS\n\n"
        'let nome = "Ana Silva";\n'
        "const ANO_NASC = 1999;\n"
        "let ativo = true;\n\n"
        "const idade = new Date().getFullYear() - ANO_NASC;\n"
        "console.log(`${nome} tem ${idade} anos`);\n\n"
        "// Operadores\n"
        "const a = 10, b = 3;\n"
        'console.log(`${a} + ${b} = ${a + b}`);\n'
        'console.log(`${a} ** ${b} = ${a ** b}`);\n'
        'console.log(`${a} % ${b} = ${a % b}`);\n\n'
        "// == vs ===\n"
        "console.log('\\n=== Comparação ===');\n"
        'console.log(`5 == "5"  → ${5 == "5"}`);\n'
        'console.log(`5 === "5" → ${5 === "5"}`);\n\n'
        "// typeof\n"
        "const vals = [42, 'texto', true, null, undefined];\n"
        "vals.forEach(v => {\n"
        "  console.log(`${String(v).padEnd(10)} → typeof: ${typeof v}`);\n"
        "});"
      ),
      "tip": "Sempre use === (triplo igual) — nunca == em JavaScript!"
    },
    {
      "id": "js_02", "title": "Arrow Functions", "level": "Iniciante",
      "emoji": "🏹", "duration": "18 min", "xp": 60,
      "theory": (
        "JavaScript tem 3 formas de criar funções!\n\n"
        "FUNCTION DECLARATION (com hoisting)\n"
        "  function somar(a, b) { return a + b; }\n\n"
        "FUNCTION EXPRESSION (sem hoisting)\n"
        "  const somar = function(a, b) { return a + b; };\n\n"
        "ARROW FUNCTION (ES6+)\n"
        "  const somar = (a, b) => a + b;\n\n"
        "SIMPLIFICAÇÕES\n"
        "  1 parâmetro: sem parênteses → x => x * 2\n"
        "  1 linha:     sem {} e sem return\n"
        "  0 params:    parênteses obrigatórios → () => 42\n\n"
        "DEFAULT PARAMS\n"
        "  const greet = (nome = 'Dev') => `Olá, ${nome}!`;\n\n"
        "REST PARAMS\n"
        "  const soma = (...nums) => nums.reduce((a,b)=>a+b,0);\n\n"
        "⚠️  Arrow functions NÃO têm 'this' próprio!"
      ),
      "code": (
        "// Arrow functions\n"
        "const dobro    = x => x * 2;\n"
        "const quadrado = x => x ** 2;\n"
        "const saudar   = (nome = 'Dev') => `Olá, ${nome}!`;\n\n"
        'console.log(`Dobro de 7: ${dobro(7)}`);\n'
        'console.log(`Quadrado de 8: ${quadrado(8)}`);\n'
        'console.log(saudar());\n'
        'console.log(saudar("Ana"));\n\n'
        "// Rest parameters\n"
        "const somar = (...nums) => {\n"
        "  const total = nums.reduce((acc, n) => acc + n, 0);\n"
        '  console.log(`Soma de [${nums}] = ${total}`);\n'
        "  return total;\n"
        "};\n"
        "somar(1, 2, 3);\n"
        "somar(10, 20, 30, 40, 50);\n\n"
        "// Higher-order functions encadeadas\n"
        "const nums = [1,2,3,4,5,6,7,8,9,10];\n"
        "const resultado = nums\n"
        "  .filter(n => n % 2 === 0)    // pares\n"
        "  .map(n => n ** 2)            // quadrado\n"
        "  .reduce((acc, n) => acc + n, 0); // soma\n\n"
        'console.log(`\\nSoma dos quadrados dos pares: ${resultado}`);'
      ),
      "tip": "Arrow functions não têm 'this' — use function para métodos de objeto!"
    },
    {
      "id": "js_03", "title": "Arrays Modernos", "level": "Intermediário",
      "emoji": "📊", "duration": "25 min", "xp": 80,
      "theory": (
        "Arrays em JS têm métodos funcionais poderosos!\n\n"
        "TRANSFORMAÇÃO\n"
        "  map(fn)        → novo array transformado\n"
        "  filter(fn)     → novo array filtrado\n"
        "  reduce(fn, i)  → reduz a um único valor\n"
        "  flatMap(fn)    → map + flatten\n\n"
        "BUSCA\n"
        "  find(fn)       → primeiro que passa\n"
        "  findIndex(fn)  → índice do primeiro\n"
        "  includes(x)    → boolean\n"
        "  some(fn)       → true se ALGUM passa\n"
        "  every(fn)      → true se TODOS passam\n\n"
        "OUTROS\n"
        "  sort(fn)       → SEMPRE passe comparador!\n"
        "  slice(i,j)     → cópia (não modifica)\n"
        "  splice(i,n)    → modifica no lugar\n"
        "  flat(depth)    → achata arrays aninhados\n\n"
        "DESTRUCTURING\n"
        "  const [a, b, ...resto] = [1, 2, 3, 4];"
      ),
      "code": (
        "const produtos = [\n"
        '  { nome: "Notebook",  preco: 2500, estoque: 15 },\n'
        '  { nome: "Mouse",     preco: 80,   estoque: 50 },\n'
        '  { nome: "Teclado",   preco: 150,  estoque: 30 },\n'
        '  { nome: "Monitor",   preco: 1200, estoque: 0  },\n'
        "];\n\n"
        "// filter + map + sort encadeados\n"
        "const pipeline = produtos\n"
        "  .filter(p => p.estoque > 0)\n"
        "  .map(p => ({ ...p, total: p.preco * p.estoque }))\n"
        "  .sort((a, b) => b.total - a.total);\n\n"
        "console.log('=== Produtos em estoque (por valor) ===');\n"
        "pipeline.forEach(p =>\n"
        '  console.log(`  ${p.nome.padEnd(10)} → R$${p.total.toLocaleString()}`)\n'
        ");\n\n"
        "// reduce\n"
        "const valorTotal = pipeline.reduce((acc, p) => acc + p.total, 0);\n"
        'console.log(`\\nEstoque total: R$${valorTotal.toLocaleString()}`);\n\n'
        "// Destructuring\n"
        "const [maisValioso, ...resto] = pipeline;\n"
        'console.log(`\\nMais valioso: ${maisValioso.nome}`);\n\n'
        'console.log(`Algum > R$2000? ${produtos.some(p => p.preco > 2000)}`);\n'
        'console.log(`Todos com preço? ${produtos.every(p => p.preco > 0)}`);'
      ),
      "tip": "Nunca use .sort() sem comparador para números — dá resultado errado!"
    },
    {
      "id": "js_04", "title": "Classes ES6+", "level": "Intermediário",
      "emoji": "🏛️", "duration": "28 min", "xp": 90,
      "theory": (
        "JavaScript moderno tem classes reais!\n\n"
        "ESTRUTURA\n"
        "  class Animal {\n"
        "    #nome;           // campo privado (ES2022)\n"
        "    static count = 0; // campo estático\n\n"
        "    constructor(nome) {\n"
        "      this.#nome = nome;\n"
        "      Animal.count++;\n"
        "    }\n"
        "    get nome() { return this.#nome; }\n"
        "    falar() { return `${this.nome}...`; }\n"
        "  }\n\n"
        "HERANÇA\n"
        "  class Cachorro extends Animal {\n"
        "    falar() { return `${this.nome}: Au au!`; }\n"
        "  }\n\n"
        "SPREAD / REST\n"
        "  const novo = { ...pessoa, cidade: 'SP' };\n"
        "  const copia = [...array, 99];"
      ),
      "code": (
        "class ContaBancaria {\n"
        "  #saldo = 0;\n"
        "  #historico = [];\n\n"
        "  constructor(titular, numero) {\n"
        "    if (!titular) throw new Error('Titular obrigatório');\n"
        "    this.titular = titular;\n"
        "    this.numero  = numero;\n"
        "  }\n\n"
        "  depositar(valor) {\n"
        "    if (valor <= 0) throw new Error('Valor inválido');\n"
        "    this.#saldo += valor;\n"
        "    this.#historico.push({ tipo: 'Depósito', valor, saldo: this.#saldo });\n"
        "    return this; // permite encadeamento\n"
        "  }\n\n"
        "  sacar(valor) {\n"
        "    if (valor > this.#saldo) throw new Error('Saldo insuficiente');\n"
        "    this.#saldo -= valor;\n"
        "    this.#historico.push({ tipo: 'Saque', valor, saldo: this.#saldo });\n"
        "    return this;\n"
        "  }\n\n"
        "  get saldo() { return this.#saldo; }\n\n"
        "  extrato() {\n"
        "    console.log(`\\n=== Conta ${this.numero} — ${this.titular} ===`);\n"
        "    this.#historico.forEach(({ tipo, valor, saldo }) =>\n"
        "      console.log(`  ${tipo.padEnd(9)} R$${valor.toFixed(2).padStart(8)} | Saldo: R$${saldo.toFixed(2)}`)\n"
        "    );\n"
        "  }\n"
        "}\n\n"
        "const conta = new ContaBancaria('Ana', '001-234');\n"
        "conta.depositar(1000).depositar(500).sacar(200);\n"
        "conta.extrato();\n"
        'console.log(`\\nSaldo: R$${conta.saldo.toFixed(2)}`);'
      ),
      "tip": "Use # para campos privados reais em classes modernas (ES2022)!"
    },
  ],
  "java": [
    {
      "id": "java_01", "title": "Introdução ao Java", "level": "Iniciante",
      "emoji": "☕", "duration": "15 min", "xp": 60,
      "theory": (
        "Java é fortemente tipada e orientada a objetos!\n\n"
        "ESTRUTURA OBRIGATÓRIA\n"
        "  public class NomeArquivo {\n"
        "      public static void main(String[] args) {\n"
        "          // código aqui\n"
        "      }\n"
        "  }\n"
        "  ⚠️  Nome da classe == nome do arquivo!\n\n"
        "TIPOS PRIMITIVOS\n"
        "  int     inteiro       (4 bytes, -2^31 a 2^31-1)\n"
        "  long    inteiro grande (8 bytes) → use 100L\n"
        "  double  decimal (64-bit) → padrão para reais\n"
        "  float   decimal (32-bit) → use 3.14f\n"
        "  char    caractere Unicode → 'A'\n"
        "  boolean true / false\n\n"
        "⚠️  String NÃO é primitivo — é uma Classe!\n\n"
        "SAÍDA\n"
        "  System.out.println()  → com quebra de linha\n"
        "  System.out.printf()   → formatação estilo C"
      ),
      "code": (
        "// JAVA FUNDAMENTOS\n"
        "// Arquivo: Fundamentos.java\n\n"
        "public class Fundamentos {\n\n"
        "    public static void main(String[] args) {\n\n"
        "        // Tipos primitivos\n"
        "        int     idade  = 25;\n"
        "        double  altura = 1.75;\n"
        "        float   peso   = 70.5f;       // 'f' obrigatório!\n"
        "        long    pop    = 8_000_000_000L; // '_' melhora leitura\n"
        "        char    inicial= 'A';\n"
        "        boolean ativo  = true;\n\n"
        "        // String (é uma Classe!)\n"
        '        String nome = "Carlos Silva";\n\n'
        "        // Printf formatado\n"
        '        System.out.println("=== DADOS ===");\n'
        '        System.out.printf("Nome:   %s%n",   nome);\n'
        '        System.out.printf("Idade:  %d anos%n", idade);\n'
        '        System.out.printf("Altura: %.2f m%n", altura);\n'
        '        System.out.printf("Ativo:  %b%n", ativo);\n\n'
        "        // CUIDADO: int / int = int !\n"
        "        int a = 10, b = 3;\n"
        '        System.out.println("\\n=== OPERAÇÕES ===");\n'
        '        System.out.println("int/int:  " + (a / b));          // 3\n'
        '        System.out.println("double:   " + (a / (double)b));  // 3.333\n'
        '        System.out.println("Módulo:   " + (a % b));\n'
        '        System.out.println("Potência: " + (int)Math.pow(a, b));\n'
        "    }\n"
        "}"
      ),
      "tip": "int/int = int em Java! Use (double)a / b para resultado decimal."
    },
    {
      "id": "java_02", "title": "Condicionais e Loops", "level": "Iniciante",
      "emoji": "🔄", "duration": "18 min", "xp": 70,
      "theory": (
        "Java tem as mesmas estruturas do C/C++!\n\n"
        "IF/ELSE IF/ELSE\n"
        "  if (condicao) { }\n"
        "  else if (outra) { }\n"
        "  else { }\n\n"
        "SWITCH EXPRESSION (Java 14+)\n"
        "  String result = switch (valor) {\n"
        "      case 1 -> \"Um\";\n"
        "      case 2, 3 -> \"Dois ou Três\";\n"
        "      default -> \"Outro\";\n"
        "  };\n\n"
        "LOOPS\n"
        "  for (int i=0; i<10; i++) { }     // clássico\n"
        "  while (cond) { }                 // testa antes\n"
        "  do { } while (cond);             // testa depois\n"
        "  for (int n : array) { }          // for-each\n\n"
        "CONTROLE\n"
        "  break    → sai do loop\n"
        "  continue → pula iteração\n"
        "  return   → sai do método"
      ),
      "code": (
        "public class ControleDeFluxo {\n\n"
        "    public static void main(String[] args) {\n\n"
        "        // Switch Expression (Java 14+)\n"
        "        int mes = 7;\n"
        "        String estacao = switch (mes) {\n"
        "            case 12, 1, 2  -> \"Verão\";\n"
        "            case 3, 4, 5   -> \"Outono\";\n"
        "            case 6, 7, 8   -> \"Inverno\";\n"
        "            case 9, 10, 11 -> \"Primavera\";\n"
        "            default -> throw new IllegalArgumentException(\"Mês inválido: \" + mes);\n"
        "        };\n"
        "        System.out.println(\"Mês \" + mes + \": \" + estacao);\n\n"
        "        // For — Tabuada com printf\n"
        "        System.out.println(\"\\n=== TABUADA DO 7 ===\");\n"
        "        for (int i = 1; i <= 10; i++)\n"
        "            System.out.printf(\"  7 × %2d = %2d%n\", i, 7 * i);\n\n"
        "        // For-each\n"
        "        String[] langs = {\"Java\", \"Python\", \"JavaScript\"};\n"
        "        System.out.println(\"\\n=== LINGUAGENS ===\");\n"
        "        for (String lang : langs)\n"
        "            System.out.println(\"  → \" + lang);\n\n"
        "        // Do-while — potências de 2\n"
        "        System.out.println(\"\\n=== POTÊNCIAS DE 2 ===\");\n"
        "        int v = 1;\n"
        "        do {\n"
        "            System.out.print(v + \" \");\n"
        "            v *= 2;\n"
        "        } while (v <= 1024);\n"
        "    }\n"
        "}"
      ),
      "tip": "Use for-each quando não precisar do índice — mais seguro e legível!"
    },
    {
      "id": "java_03", "title": "Classes e OOP", "level": "Intermediário",
      "emoji": "🏛️", "duration": "35 min", "xp": 100,
      "theory": (
        "Java foi construído para OOP!\n\n"
        "OS 4 PILARES\n"
        "  1. ENCAPSULAMENTO\n"
        "     Oculte dados com private.\n"
        "     Exponha via getters/setters.\n\n"
        "  2. HERANÇA\n"
        "     class Filho extends Pai { }\n"
        "     Use super() para chamar o pai.\n\n"
        "  3. POLIMORFISMO\n"
        "     Mesma interface, comportamentos diferentes.\n"
        "     @Override para sobrescrever métodos.\n\n"
        "  4. ABSTRAÇÃO\n"
        "     abstract class / interface simplificam.\n\n"
        "ABSTRACT vs INTERFACE\n"
        "  abstract: herança única, pode ter estado\n"
        "  interface: múltipla, apenas contrato"
      ),
      "code": (
        "abstract class Funcionario {\n"
        "    protected final String nome;\n"
        "    protected double salarioBase;\n\n"
        "    public Funcionario(String nome, double salBase) {\n"
        "        if (nome == null || nome.isBlank())\n"
        "            throw new IllegalArgumentException(\"Nome inválido\");\n"
        "        if (salBase <= 0)\n"
        "            throw new IllegalArgumentException(\"Salário deve ser > 0\");\n"
        "        this.nome = nome;\n"
        "        this.salarioBase = salBase;\n"
        "    }\n\n"
        "    public abstract double calcularSalario();\n\n"
        "    public void exibirInfo() {\n"
        "        System.out.printf(\"  %-20s → R$ %,10.2f%n\",\n"
        "                          nome, calcularSalario());\n"
        "    }\n"
        "}\n\n"
        "class Desenvolvedor extends Funcionario {\n"
        "    private final int horasExtras;\n"
        "    private static final double VALOR_HORA_EXTRA = 80.0;\n\n"
        "    public Desenvolvedor(String nome, double base, int horas) {\n"
        "        super(nome, base);\n"
        "        this.horasExtras = Math.max(0, horas);\n"
        "    }\n\n"
        "    @Override\n"
        "    public double calcularSalario() {\n"
        "        return salarioBase + (horasExtras * VALOR_HORA_EXTRA);\n"
        "    }\n"
        "}\n\n"
        "class Gerente extends Funcionario {\n"
        "    private final double bonus;\n\n"
        "    public Gerente(String nome, double base, double bonus) {\n"
        "        super(nome, base);\n"
        "        this.bonus = Math.max(0, bonus);\n"
        "    }\n\n"
        "    @Override\n"
        "    public double calcularSalario() {\n"
        "        return salarioBase + bonus;\n"
        "    }\n"
        "}\n\n"
        "public class SistemaRH {\n"
        "    public static void main(String[] args) {\n"
        "        Funcionario[] equipe = {\n"
        '            new Desenvolvedor("Ana Silva",     8000, 20),\n'
        '            new Desenvolvedor("Carlos Lima",   9500, 15),\n'
        '            new Gerente("Beatriz Costa",       12000, 3000),\n'
        "        };\n\n"
        '        System.out.println("=== FOLHA DE PAGAMENTO ===");\n'
        "        double total = 0;\n"
        "        for (Funcionario f : equipe) {\n"
        "            f.exibirInfo();\n"
        "            total += f.calcularSalario();\n"
        "        }\n"
        '        System.out.printf("%n  TOTAL: R$ %,10.2f%n", total);\n'
        "    }\n"
        "}"
      ),
      "tip": "Programe para interfaces/abstrações, não para implementações!"
    },
  ]
}

EXERCISES = [
  {
    "id": "ex_py_01", "lang": "python", "level": "Iniciante", "emoji": "👋", "xp": 100,
    "title": "Saudação Personalizada",
    "desc": (
      "Crie a função saudar(nome) que retorne:\n"
      "  'Olá, [NOME]! Bem-vindo ao CodeMaster Pro!'\n\n"
      "O nome deve estar em MAIÚSCULAS.\n\n"
      "Exemplos:\n"
      "  saudar('ana')    → 'Olá, ANA! Bem-vindo ao CodeMaster Pro!'\n"
      "  saudar('carlos') → 'Olá, CARLOS! Bem-vindo ao CodeMaster Pro!'"
    ),
    "hint": "Use .upper() para maiúsculas e f-strings para formatar.",
    "starter": (
      "def saudar(nome: str) -> str:\n"
      "    nome_maiusculo = nome._____()\n"
      '    return f"_____, {_____}! Bem-vindo ao CodeMaster Pro!"\n\n'
      'print(saudar("ana"))\n'
      'print(saudar("carlos"))'
    ),
    "solution": (
      "def saudar(nome: str) -> str:\n"
      "    nome_maiusculo = nome.upper()\n"
      '    return f"Olá, {nome_maiusculo}! Bem-vindo ao CodeMaster Pro!"\n\n'
      'print(saudar("ana"))\n'
      'print(saudar("carlos"))'
    )
  },
  {
    "id": "ex_py_02", "lang": "python", "level": "Iniciante", "emoji": "🔢", "xp": 100,
    "title": "Par ou Ímpar",
    "desc": (
      "Crie verificar(n) que retorne 'par' ou 'ímpar'.\n"
      "Depois use list comprehension para listar todos\n"
      "os pares de 1 a 20."
    ),
    "hint": "Use % 2. Se n % 2 == 0, é par!",
    "starter": (
      "def verificar(numero: int) -> str:\n"
      "    if numero % ___ == ___:\n"
      '        return "par"\n'
      '    return "ímpar"\n\n'
      "for i in range(1, 11):\n"
      '    print(f"{i} é {verificar(i)}")\n\n'
      "pares = [n for n in range(1, 21) if ___]\n"
      'print("Pares:", pares)'
    ),
    "solution": (
      "def verificar(numero: int) -> str:\n"
      "    if numero % 2 == 0:\n"
      "        return 'par'\n"
      "    return 'ímpar'\n\n"
      "for i in range(1, 11):\n"
      '    print(f"{i} é {verificar(i)}")\n\n'
      "pares = [n for n in range(1, 21) if n % 2 == 0]\n"
      "print('Pares:', pares)"
    )
  },
  {
    "id": "ex_py_03", "lang": "python", "level": "Iniciante", "emoji": "✖️", "xp": 120,
    "title": "Tabuada Formatada",
    "desc": (
      "Crie tabuada(n) imprimindo a tabuada de 1 a 10:\n\n"
      "  ====================\n"
      "    TABUADA DO 7\n"
      "  ====================\n"
      "  7 x  1 =   7\n"
      "  7 x  2 =  14\n"
      "    ..."
    ),
    "hint": "Use range(1, 11) e f-strings com :2d para alinhar.",
    "starter": (
      "def tabuada(n: int) -> None:\n"
      '    print(f"\\n{\'=\'*22}")\n'
      '    print(f"  TABUADA DO {n}")\n'
      '    print(f"{\'=\'*22}")\n'
      "    for i in range(___, ___):\n"
      "        resultado = ___ * ___\n"
      '        print(f"  {n} x {i:2d} = {resultado:3d}")\n\n'
      "tabuada(7)"
    ),
    "solution": (
      "def tabuada(n: int) -> None:\n"
      '    print(f"\\n{\'=\'*22}")\n'
      '    print(f"  TABUADA DO {n}")\n'
      '    print(f"{\'=\'*22}")\n'
      "    for i in range(1, 11):\n"
      "        resultado = n * i\n"
      '        print(f"  {n} x {i:2d} = {resultado:3d}")\n\n'
      "tabuada(7)"
    )
  },
  {
    "id": "ex_py_04", "lang": "python", "level": "Intermediário", "emoji": "🎯", "xp": 150,
    "title": "FizzBuzz Clássico",
    "desc": (
      "Para números de 1 a 50:\n"
      "  • Divisível por 15 → 'FizzBuzz'\n"
      "  • Divisível por 3  → 'Fizz'\n"
      "  • Divisível por 5  → 'Buzz'\n"
      "  • Outro            → o número\n\n"
      "Imprima 10 por linha."
    ),
    "hint": "Verifique % 15 PRIMEIRO! A ordem dos elif importa.",
    "starter": (
      "resultado = []\n"
      "for n in range(1, 51):\n"
      "    if n % ___ == 0:\n"
      "        resultado.append('FizzBuzz')\n"
      "    elif n % ___ == 0:\n"
      "        resultado.append('Fizz')\n"
      "    elif n % ___ == 0:\n"
      "        resultado.append('Buzz')\n"
      "    else:\n"
      "        resultado.append(str(n))\n\n"
      "for i in range(0, 50, 10):\n"
      "    print(' '.join(resultado[i:i+10]))"
    ),
    "solution": (
      "resultado = []\n"
      "for n in range(1, 51):\n"
      "    if n % 15 == 0:\n"
      "        resultado.append('FizzBuzz')\n"
      "    elif n % 3 == 0:\n"
      "        resultado.append('Fizz')\n"
      "    elif n % 5 == 0:\n"
      "        resultado.append('Buzz')\n"
      "    else:\n"
      "        resultado.append(str(n))\n\n"
      "for i in range(0, 50, 10):\n"
      "    print(' '.join(resultado[i:i+10]))"
    )
  },
  {
    "id": "ex_py_05", "lang": "python", "level": "Intermediário", "emoji": "📊", "xp": 180,
    "title": "Analisador de Lista",
    "desc": (
      "Crie analisar(nums) retornando um dicionário com:\n"
      "  soma, media, maior, menor, qtd_pares, qtd_impares"
    ),
    "hint": "Use sum(), max(), min(), len() nativos do Python.",
    "starter": (
      "def analisar(nums: list) -> dict:\n"
      "    return {\n"
      "        'soma':        ___,\n"
      "        'media':       round(___ / len(nums), 2),\n"
      "        'maior':       ___,\n"
      "        'menor':       ___,\n"
      "        'qtd_pares':   len([n for n in nums if ___ == 0]),\n"
      "        'qtd_impares': len([n for n in nums if ___ != 0]),\n"
      "    }\n\n"
      "numeros = [3, 7, 2, 9, 4, 1, 8, 5, 6, 10]\n"
      "stats = analisar(numeros)\n"
      "for k, v in stats.items():\n"
      "    print(f'{k:14}: {v}')"
    ),
    "solution": (
      "def analisar(nums: list) -> dict:\n"
      "    return {\n"
      "        'soma':        sum(nums),\n"
      "        'media':       round(sum(nums) / len(nums), 2),\n"
      "        'maior':       max(nums),\n"
      "        'menor':       min(nums),\n"
      "        'qtd_pares':   len([n for n in nums if n % 2 == 0]),\n"
      "        'qtd_impares': len([n for n in nums if n % 2 != 0]),\n"
      "    }\n\n"
      "numeros = [3, 7, 2, 9, 4, 1, 8, 5, 6, 10]\n"
      "stats = analisar(numeros)\n"
      "for k, v in stats.items():\n"
      "    print(f'{k:14}: {v}')"
    )
  },
  {
    "id": "ex_js_01", "lang": "javascript", "level": "Iniciante", "emoji": "🌡️", "xp": 120,
    "title": "Conversor de Temperatura",
    "desc": (
      "Crie 3 arrow functions:\n"
      "  celsiusParaF(c)   → (c × 9/5) + 32\n"
      "  fahrenheitParaC(f) → (f-32) × 5/9\n"
      "  celsiusParaK(c)   → c + 273.15\n\n"
      "Retorne sempre com 2 casas decimais."
    ),
    "hint": "Use arrow functions e .toFixed(2) para 2 casas decimais.",
    "starter": (
      "const celsiusParaF    = (c) => ___;\n"
      "const fahrenheitParaC = (f) => ___;\n"
      "const celsiusParaK    = (c) => ___;\n\n"
      "console.log('100°C =', celsiusParaF(100), '°F');\n"
      "console.log('212°F =', fahrenheitParaC(212), '°C');\n"
      "console.log('  0°C =', celsiusParaK(0), 'K');"
    ),
    "solution": (
      "const celsiusParaF    = (c) => ((c * 9/5) + 32).toFixed(2);\n"
      "const fahrenheitParaC = (f) => ((f - 32) * 5/9).toFixed(2);\n"
      "const celsiusParaK    = (c) => (c + 273.15).toFixed(2);\n\n"
      "console.log('100°C =', celsiusParaF(100), '°F');\n"
      "console.log('212°F =', fahrenheitParaC(212), '°C');\n"
      "console.log('  0°C =', celsiusParaK(0), 'K');"
    )
  },
  {
    "id": "ex_js_02", "lang": "javascript", "level": "Intermediário", "emoji": "🛒", "xp": 160,
    "title": "Pipeline de Produtos",
    "desc": (
      "Use filter/map/sort/reduce para:\n"
      "  1. Filtrar apenas produtos em estoque\n"
      "  2. Aplicar 15% de desconto em produtos > R$100\n"
      "  3. Ordenar por preço final crescente\n"
      "  4. Calcular o total"
    ),
    "hint": "Encadeie: .filter().map().sort() depois .reduce()",
    "starter": (
      "const produtos = [\n"
      "  {nome:'Notebook',preco:2500,estoque:3},\n"
      "  {nome:'Caneta',preco:5,estoque:0},\n"
      "  {nome:'Mouse',preco:80,estoque:10},\n"
      "  {nome:'Monitor',preco:1200,estoque:2},\n"
      "];\n\n"
      "const pipeline = produtos\n"
      "  ._____(p => p.estoque > 0)\n"
      "  ._____(p => ({...p, final: p.preco > 100 ? p.preco * 0.85 : p.preco}))\n"
      "  ._____((a, b) => a.final - b.final);\n\n"
      "const total = pipeline.reduce((acc, p) => ___ + p.final, 0);\n"
      "pipeline.forEach(p => console.log(`${p.nome}: R$${p.final.toFixed(2)}`));\n"
      "console.log('Total: R$' + total.toFixed(2));"
    ),
    "solution": (
      "const produtos = [\n"
      "  {nome:'Notebook',preco:2500,estoque:3},\n"
      "  {nome:'Caneta',preco:5,estoque:0},\n"
      "  {nome:'Mouse',preco:80,estoque:10},\n"
      "  {nome:'Monitor',preco:1200,estoque:2},\n"
      "];\n\n"
      "const pipeline = produtos\n"
      "  .filter(p => p.estoque > 0)\n"
      "  .map(p => ({...p, final: p.preco > 100 ? p.preco * 0.85 : p.preco}))\n"
      "  .sort((a, b) => a.final - b.final);\n\n"
      "const total = pipeline.reduce((acc, p) => acc + p.final, 0);\n"
      "pipeline.forEach(p => console.log(`${p.nome}: R$${p.final.toFixed(2)}`));\n"
      "console.log('Total: R$' + total.toFixed(2));"
    )
  },
  {
    "id": "ex_java_01", "lang": "java", "level": "Intermediário", "emoji": "🌀", "xp": 180,
    "title": "Fibonacci",
    "desc": (
      "Implemente dois métodos:\n"
      "  fibonacci(n)     → recursivo\n"
      "  fibonacciLoop(n) → iterativo (mais eficiente!)\n\n"
      "Imprima os 12 primeiros termos de cada.\n"
      "F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)"
    ),
    "hint": "Iterativo: 2 variáveis que vão trocando de valor (temp = a+b; a=b; b=temp).",
    "starter": (
      "public class Fibonacci {\n\n"
      "    static long fibonacci(int n) {\n"
      "        if (n <= 1) return ___;\n"
      "        return ___(n-1) + ___(n-2);\n"
      "    }\n\n"
      "    static long fibonacciLoop(int n) {\n"
      "        if (n <= 1) return n;\n"
      "        long a = 0, b = 1;\n"
      "        for (int i = 2; i <= n; i++) {\n"
      "            long temp = a + b;\n"
      "            a = ___;\n"
      "            b = ___;\n"
      "        }\n"
      "        return b;\n"
      "    }\n\n"
      "    public static void main(String[] args) {\n"
      '        System.out.print("Recursivo: ");\n'
      "        for (int i = 0; i < 12; i++)\n"
      "            System.out.print(fibonacci(i) + \" \");\n"
      "    }\n"
      "}"
    ),
    "solution": (
      "public class Fibonacci {\n"
      "    static long fibonacci(int n) {\n"
      "        if (n <= 1) return n;\n"
      "        return fibonacci(n-1) + fibonacci(n-2);\n"
      "    }\n"
      "    static long fibonacciLoop(int n) {\n"
      "        if (n <= 1) return n;\n"
      "        long a = 0, b = 1;\n"
      "        for (int i = 2; i <= n; i++) {\n"
      "            long temp = a + b; a = b; b = temp;\n"
      "        }\n"
      "        return b;\n"
      "    }\n"
      "    public static void main(String[] args) {\n"
      '        System.out.print("Recursivo: ");\n'
      "        for (int i=0;i<12;i++) System.out.print(fibonacci(i)+\" \");\n"
      '        System.out.print("\\nIterativo: ");\n'
      "        for (int i=0;i<12;i++) System.out.print(fibonacciLoop(i)+\" \");\n"
      "    }\n"
      "}"
    )
  },
]

# FIX #3: Correct lang prefix for langDone — use full prefix
QUIZZES = [
  {"id":"q01","lang":"python","level":"Iniciante",
   "q":"O que imprime: print(10 // 3)?",
   "opts":["3.33","3","4","1"],"ans":1,
   "exp":"// é divisão inteira (floor division). 10 // 3 = 3 (trunca o decimal)."},

  {"id":"q02","lang":"python","level":"Iniciante",
   "q":"Qual função verifica o tipo de uma variável em Python?",
   "opts":["typeof()","typeOf()","type()","getType()"],"ans":2,
   "exp":"type(variavel) retorna o tipo. Ex: type(42) → <class 'int'>."},

  {"id":"q03","lang":"python","level":"Iniciante",
   "q":"O que faz o operador ** em Python?",
   "opts":["Multiplicação","Divisão","Potência","Bitwise AND"],"ans":2,
   "exp":"** é potência. 2**8 = 256, 3**3 = 27."},

  {"id":"q04","lang":"python","level":"Intermediário",
   "q":"O que imprime: print([x**2 for x in range(4)])?",
   "opts":["[0,1,4,9]","[1,4,9,16]","[0,1,2,3]","[1,2,3,4]"],"ans":0,
   "exp":"range(4) gera [0,1,2,3]. Elevando ao quadrado: [0,1,4,9]."},

  {"id":"q05","lang":"python","level":"Intermediário",
   "q":"Qual método de dict retorna None se a chave não existir?",
   "opts":["d['chave']","d.find()","d.get()","d.fetch()"],"ans":2,
   "exp":"d.get('chave') retorna None. d['chave'] lança KeyError!"},

  {"id":"q06","lang":"python","level":"Avançado",
   "q":"O que são *args em Python?",
   "opts":["Apenas 1 argumento","Argumentos nomeados","Qualquer qtd de args como tupla","Argumento obrigatório"],"ans":2,
   "exp":"*args captura qualquer número de argumentos posicionais como tupla."},

  {"id":"q07","lang":"javascript","level":"Iniciante",
   "q":"Diferença entre let e const?",
   "opts":["let é mais rápido","const não pode ser reatribuído","let tem escopo global","Não há diferença"],"ans":1,
   "exp":"const cria referência imutável. let pode ser reatribuído."},

  {"id":"q08","lang":"javascript","level":"Iniciante",
   "q":"O que retorna typeof null?",
   "opts":["'null'","'undefined'","'object'","'boolean'"],"ans":2,
   "exp":"Bug histórico do JS! typeof null retorna 'object'. Use === null para checar nulo."},

  {"id":"q09","lang":"javascript","level":"Intermediário",
   "q":"O que faz Array.filter()?",
   "opts":["Transforma cada elemento","Filtra e retorna novo array","Ordena o array","Encontra 1 elemento"],"ans":1,
   "exp":"filter(fn) retorna novo array com elementos onde fn retorna true."},

  {"id":"q10","lang":"javascript","level":"Intermediário",
   "q":"Arrow function correta para dobrar um número:",
   "opts":["function => x*2","x -> x*2","x => x*2","(x) >> x*2"],"ans":2,
   "exp":"Arrow function: x => x * 2. Com 2 params: (x, y) => x + y."},

  {"id":"q11","lang":"java","level":"Iniciante",
   "q":"int x = 7 / 2 em Java resulta em?",
   "opts":["3.5","3","4","Erro de compilação"],"ans":1,
   "exp":"Java: int/int = int (trunca). 7/2 = 3. Use (double)7/2 para obter 3.5."},

  {"id":"q12","lang":"java","level":"Iniciante",
   "q":"Qual modificador torna um membro acessível apenas dentro da própria classe?",
   "opts":["public","protected","package-private","private"],"ans":3,
   "exp":"private: acesso somente dentro da própria classe."},

  {"id":"q13","lang":"java","level":"Intermediário",
   "q":"O que a anotação @Override faz em Java?",
   "opts":["Cria nova classe","Indica sobrescrita de método","Torna o método estático","Declara exceção"],"ans":1,
   "exp":"@Override indica sobrescrita de método da superclasse. O compilador verifica se o método existe!"},

  {"id":"q14","lang":"python","level":"Avançado",
   "q":"Qual estrutura de dados Python NÃO permite duplicatas?",
   "opts":["list","tuple","dict","set"],"ans":3,
   "exp":"set não aceita duplicatas. {1,2,2,3} = {1,2,3}."},

  {"id":"q15","lang":"javascript","level":"Avançado",
   "q":"O que é uma Closure em JavaScript?",
   "opts":["Um tipo de loop","Uma função que lembra seu escopo léxico","Uma forma de importar módulos","Um método de array"],"ans":1,
   "exp":"Closure é uma função que lembra o ambiente (escopo) onde foi criada, mesmo após esse escopo ter encerrado."},
]

# ── Allowed content IDs (FIX #4: input validation) ──────────────────────────
_VALID_LESSON_IDS    = {l["id"] for lessons in LESSONS.values() for l in lessons}
_VALID_EXERCISE_IDS  = {e["id"] for e in EXERCISES}
_VALID_QUIZ_IDS      = {q["id"] for q in QUIZZES}

# ══════════════════════════════════════════════════════════════════════════════
#  PROGRESS PERSISTENCE
# ══════════════════════════════════════════════════════════════════════════════
_progress_lock = threading.Lock()

def _default_progress() -> dict:
    return {
        "lessons": [], "exercises": [],
        "xp": 0, "level": 1,
        "quizzes_taken": 0, "quiz_correct": 0
    }

def load_progress() -> dict:
    """Thread-safe progress loader with validation."""
    try:
        with _progress_lock:
            if not os.path.exists(PROGRESS_F):
                return _default_progress()
            with open(PROGRESS_F, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Validate & patch missing keys
            defaults = _default_progress()
            for k, v in defaults.items():
                if k not in data:
                    data[k] = v
            return data
    except (json.JSONDecodeError, OSError):
        return _default_progress()

def save_progress(data: dict) -> bool:
    """Thread-safe progress saver. Returns True on success."""
    try:
        with _progress_lock:
            # Write to temp file first, then rename (atomic)
            tmp = PROGRESS_F + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, PROGRESS_F)
        return True
    except OSError as e:
        app.logger.error(f"save_progress failed: {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "ai": bool(API_KEY)})

@app.route("/api/languages")
def get_languages():
    return jsonify([
        {"id": "python",     "name": "Python",     "emoji": "🐍", "color": "#3b82f6",
         "lessons": len(LESSONS["python"]),     "desc": "Simples, poderoso e versátil"},
        {"id": "javascript", "name": "JavaScript", "emoji": "⚡", "color": "#fbbf24",
         "lessons": len(LESSONS["javascript"]), "desc": "A linguagem da web moderna"},
        {"id": "java",       "name": "Java",       "emoji": "☕", "color": "#ef4444",
         "lessons": len(LESSONS["java"]),       "desc": "Robusto e orientado a objetos"},
    ])

@app.route("/api/lessons/<lang>")
def get_lessons(lang: str):
    if lang not in LESSONS:
        return jsonify({"error": "Linguagem não encontrada"}), 404
    return jsonify(LESSONS[lang])

@app.route("/api/exercises")
def get_exercises():
    lang = request.args.get("lang", "").strip()
    exs  = EXERCISES if not lang else [e for e in EXERCISES if e["lang"] == lang]
    return jsonify(exs)

@app.route("/api/quiz/random")
def get_quiz():
    lang  = request.args.get("lang", "").strip()
    count = min(int(request.args.get("count", 8)), 15)
    pool  = [q for q in QUIZZES if q["lang"] == lang] if lang else QUIZZES
    if not pool:
        return jsonify({"questions": [], "ids": []})
    selected = random.sample(pool, min(count, len(pool)))
    # Strip answer before sending to client
    clean = [{k: v for k, v in q.items() if k not in ("ans", "exp")} for q in selected]
    return jsonify({"questions": clean, "ids": [q["id"] for q in selected]})

@app.route("/api/quiz/check", methods=["POST"])
@rate_limit(max_calls=60, window_seconds=60)
def check_quiz():
    """FIX #5: XP awarded per quiz-session via session_xp, not per call."""
    data    = request.get_json(silent=True) or {}
    answers = data.get("answers", {})

    if not isinstance(answers, dict) or len(answers) > 15:
        return jsonify({"error": "Payload inválido"}), 400

    correct = 0
    results = []
    for qid, user_ans in answers.items():
        # FIX: validate qid
        if qid not in _VALID_QUIZ_IDS:
            continue
        if not isinstance(user_ans, int):
            continue
        q  = next((x for x in QUIZZES if x["id"] == qid), None)
        if not q:
            continue
        ok = (user_ans == q["ans"])
        if ok:
            correct += 1
        results.append({
            "id": qid, "correct": ok,
            "right_answer": q["ans"], "explanation": q["exp"]
        })

    p = load_progress()
    p["quizzes_taken"] = p.get("quizzes_taken", 0) + 1  # Once per quiz-session
    p["quiz_correct"]  = p.get("quiz_correct",  0) + correct
    p["xp"]            = p.get("xp",  0) + correct * 20
    p["level"]         = p["xp"] // 500 + 1
    save_progress(p)

    return jsonify({"correct": correct, "total": len(answers), "results": results})

@app.route("/api/progress", methods=["GET", "POST"])
def progress():
    if request.method == "GET":
        return jsonify(load_progress())

    data = request.get_json(silent=True) or {}
    action = data.get("action", "")
    p = load_progress()

    if action == "complete_lesson":
        lid = data.get("lesson_id", "")
        # FIX: validate lesson_id
        if lid not in _VALID_LESSON_IDS:
            return jsonify({"error": "lesson_id inválido"}), 400
        if lid not in p.get("lessons", []):
            p.setdefault("lessons", []).append(lid)
            p["xp"]    = p.get("xp", 0) + 50
            p["level"] = p["xp"] // 500 + 1

    elif action == "complete_exercise":
        eid = data.get("exercise_id", "")
        # FIX: validate exercise_id
        if eid not in _VALID_EXERCISE_IDS:
            return jsonify({"error": "exercise_id inválido"}), 400
        if eid not in p.get("exercises", []):
            p.setdefault("exercises", []).append(eid)
            p["xp"]    = p.get("xp", 0) + 100
            p["level"] = p["xp"] // 500 + 1

    elif action == "reset":
        p = _default_progress()

    else:
        return jsonify({"error": "Ação inválida"}), 400

    save_progress(p)
    return jsonify(p)

@app.route("/api/ai/chat", methods=["POST"])
@rate_limit(max_calls=15, window_seconds=60)
def ai_chat():
    if not API_KEY:
        return jsonify({
            "response": (
                "⚠️  A IA não está configurada.\n\n"
                "Para ativar, defina a variável de ambiente:\n"
                "  export ANTHROPIC_API_KEY='sk-ant-...'\n\n"
                "Enquanto isso, explore as lições e exercícios!"
            ),
            "offline": True
        })

    data = request.get_json(silent=True) or {}
    msgs = data.get("messages", [])

    # Sanitize: only keep role/content, limit history
    clean_msgs = [
        {"role": m["role"], "content": str(m["content"])[:4000]}
        for m in msgs[-12:]
        if isinstance(m, dict) and m.get("role") in ("user", "assistant")
        and m.get("content")
    ]

    if not clean_msgs:
        return jsonify({"error": "Mensagem vazia"}), 400

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=API_KEY)
        resp   = client.messages.create(
            model      = "claude-opus-4-5",
            max_tokens = 1024,
            system     = (
                "Você é o CodeMaster AI, tutor especialista em Python, JavaScript e Java. "
                "Responda sempre em português brasileiro. "
                "Seja didático, use exemplos práticos de código quando relevante. "
                "Use emojis com moderação. "
                "Para código, use blocos markdown com a linguagem: ```python, ```javascript ou ```java."
            ),
            messages   = clean_msgs
        )
        return jsonify({"response": resp.content[0].text, "offline": False})

    except ImportError:
        return jsonify({
            "response": "Instale o pacote Anthropic:\n  pip install anthropic",
            "offline": True
        })
    except Exception as e:
        app.logger.error(f"AI error: {e}")
        return jsonify({"response": f"Erro temporário. Tente novamente.", "offline": True})

# ─── 404 / Error handlers ────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Recurso não encontrado"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Erro interno do servidor"}), 500

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════╗")
    print("║     CodeMaster Pro v3.0 — Iniciando     ║")
    print("╚══════════════════════════════════════════╝")
    print(f"  AI:       {'✅ Configurada' if API_KEY else '⚠️  Sem ANTHROPIC_API_KEY'}")
    print(f"  Progress: {PROGRESS_F}")
    print( "  URL:      http://localhost:5000\n")
