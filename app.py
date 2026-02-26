"""
CodeMaster Pro — Flask Backend v2.1
Correção: libs JS servidas localmente, sem depender de CDN
"""

from flask import Flask, jsonify, request, send_from_directory, Response, redirect
from flask_cors import CORS
import json, os, random, threading
from datetime import datetime

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
CORS(app)

API_KEY    = "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"
PROGRESS_F = os.path.join(os.path.expanduser("~"), ".codemaster_pro.json")

# ── Download automático de libs ────────────────────────────
LIBS = {
    "vue.min.js":        "https://unpkg.com/vue@3.4.21/dist/vue.global.prod.js",
    "hljs.min.js":       "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js",
    "hljs-python.min.js":"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js",
    "hljs-js.min.js":    "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/javascript.min.js",
    "hljs-java.min.js":  "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/java.min.js",
    "atom-dark.min.css": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css",
    "tailwind.min.js":   "https://cdn.tailwindcss.com",
}

def download_libs():
    try:
        import urllib.request
        for fname, url in LIBS.items():
            dest = os.path.join(STATIC_DIR, fname)
            if not os.path.exists(dest):
                print(f"  [download] {fname}...")
                try:
                    urllib.request.urlretrieve(url, dest)
                    print(f"  [ok] {fname}")
                except Exception as e:
                    print(f"  [aviso] Nao foi possivel baixar {fname}: {e}")
    except Exception as e:
        print(f"  [aviso] Erro no download: {e}")

threading.Thread(target=download_libs, daemon=True).start()

# ── Rota para servir libs locais ───────────────────────────
CDN_FALLBACK = {
    "vue.min.js":        "https://unpkg.com/vue@3.4.21/dist/vue.global.prod.js",
    "hljs.min.js":       "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js",
    "hljs-python.min.js":"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js",
    "hljs-js.min.js":    "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/javascript.min.js",
    "hljs-java.min.js":  "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/java.min.js",
    "atom-dark.min.css": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css",
    "tailwind.min.js":   "https://cdn.tailwindcss.com",
}

@app.route("/lib/<filename>")
def serve_lib(filename):
    local = os.path.join(STATIC_DIR, filename)
    if os.path.exists(local):
        mime = "text/css" if filename.endswith(".css") else "application/javascript"
        with open(local, "rb") as f:
            return Response(f.read(), mimetype=mime)
    if filename in CDN_FALLBACK:
        return redirect(CDN_FALLBACK[filename])
    return "Not found", 404

# ══════════════════════════════════════════════════════════
#  DADOS — LICOES
# ══════════════════════════════════════════════════════════
LESSONS = {
  "python": [
    {"id":"py_01","title":"Ola, Python!","level":"Iniciante","emoji":"🐍","duration":"10 min","xp":50,
     "theory":"Python e uma linguagem de alto nivel criada por Guido van Rossum em 1991.\n\nPOR QUE PYTHON?\n* Sintaxe simples e legivel\n* Versatil: Web, IA, Data Science, Automacao\n* A linguagem mais popular do mundo\n* Usado por Google, Netflix, Instagram, NASA\n\nSEU PRIMEIRO PROGRAMA\nUsamos print() para exibir texto na tela.\nA funcao aceita qualquer valor como argumento.\n\nCOMENTARIOS\nLinhas que comecam com # sao ignoradas.\nServem para explicar o codigo para humanos.\n\nEXECUTANDO\nNo Pydroid 3: salve e pressione o botao play\nNo terminal: python3 nome_do_arquivo.py",
     "code":"# Meu primeiro programa Python!\n# Tudo apos # e comentario\n\nprint(\"Ola, Mundo!\")\nprint(\"Bem-vindo ao CodeMaster Pro!\")\n\n# Tipos diferentes de dados\nprint(42)           # numero inteiro\nprint(3.14)         # numero decimal\nprint(True)         # booleano\n\n# Combinando valores\nprint(\"Python\", \"e\", \"incrivel!\", sep=\" | \")\nprint(\"2 + 2 =\", 2 + 2)",
     "tip":"Python e case-sensitive: print() funciona, Print() da erro!"},

    {"id":"py_02","title":"Variaveis e Tipos","level":"Iniciante","emoji":"📦","duration":"12 min","xp":50,
     "theory":"Variaveis sao conteineres que guardam dados na memoria.\n\nCRIANDO VARIAVEIS\nnome = 'Ana'      # cria a variavel nome\nidade = 25        # cria a variavel idade\n\n4 TIPOS BASICOS\n  str   texto:    'Ola'  'Python'\n  int   inteiro:  42  -10  0\n  float decimal:  3.14  -0.5\n  bool  logico:   True  False\n\nDESCOBRINDO O TIPO\ntype('texto')  ->  <class 'str'>\ntype(42)       ->  <class 'int'>\n\nCONVERSAO\nint('42')     ->  42\nstr(42)       ->  '42'\nfloat('3.14') ->  3.14",
     "code":"# VARIAVEIS EM ACAO\n\nnome = \"Ana Silva\"\nidade = 25\naltura = 1.68\nestudante = True\n\n# Exibindo com f-string (forma moderna)\nprint(f\"Nome: {nome}\")\nprint(f\"Idade: {idade} anos\")\nprint(f\"Altura: {altura}m\")\nprint(f\"Estudante: {estudante}\")\n\n# Verificando tipos\nprint(f\"\\nTipo nome:  {type(nome)}\")\nprint(f\"Tipo idade: {type(idade)}\")\n\n# Multipla atribuicao\nx, y, z = 10, 20, 30\nprint(f\"\\nx={x}, y={y}, z={z}\")\n\n# Incrementando\ncontador = 0\ncontador += 1\nprint(f\"Contador: {contador}\")",
     "tip":"Use nomes descritivos: 'idade_usuario' e melhor que 'x'!"},

    {"id":"py_03","title":"Operadores","level":"Iniciante","emoji":"🔢","duration":"10 min","xp":50,
     "theory":"Operadores permitem calculos e comparacoes.\n\nARITMETICOS\n  +   adicao:        5 + 3  =  8\n  -   subtracao:     5 - 3  =  2\n  *   multiplicacao: 5 * 3  =  15\n  /   divisao:       7 / 2  =  3.5\n  //  divisao int:   7 // 2 =  3\n  %   modulo:        7 % 2  =  1\n  **  potencia:      2 ** 8 =  256\n\nCOMPARACAO (retornam bool)\n  ==  igual\n  !=  diferente\n  >   maior\n  <   menor\n  >=  maior ou igual\n\nLOGICOS\n  and  ambos True\n  or   um e True\n  not  inverte",
     "code":"# OPERADORES EM ACAO\n\na, b = 10, 3\n\nprint(\"=== ARITMETICA ===\")\nprint(f\"{a} + {b}  = {a + b}\")\nprint(f\"{a} - {b}  = {a - b}\")\nprint(f\"{a} * {b}  = {a * b}\")\nprint(f\"{a} / {b}  = {a / b:.4f}\")\nprint(f\"{a} // {b} = {a // b} (inteira)\")\nprint(f\"{a} % {b}  = {a % b} (resto)\")\nprint(f\"{a} ** {b} = {a ** b} (potencia)\")\n\nprint(\"\\n=== COMPARACAO ===\")\nprint(f\"{a} > {b}  -> {a > b}\")\nprint(f\"{a} == {b} -> {a == b}\")\nprint(f\"{a} != {b} -> {a != b}\")\n\nprint(\"\\n=== LOGICOS ===\")\nprint(f\"True and True  -> {True and True}\")\nprint(f\"True or False  -> {True or False}\")\nprint(f\"not True       -> {not True}\")",
     "tip":"7 / 2 = 3.5 (float), mas 7 // 2 = 3 (int). Atencao a diferenca!"},

    {"id":"py_04","title":"Condicionais","level":"Iniciante","emoji":"🔀","duration":"15 min","xp":60,
     "theory":"Condicionais permitem que o programa tome decisoes!\n\nESTRUTURA IF/ELIF/ELSE\n  if condicao_1:\n      # executa se True\n  elif condicao_2:\n      # executa se True\n  else:\n      # nenhuma foi True\n\nRegras:\n* Indentacao com 4 espacos e obrigatoria\n* elif e else sao opcionais\n\nOPERADOR TERNARIO\nresultado = 'sim' if condicao else 'nao'\n\nVALORES FALSY\nFalse, None, 0, 0.0, '', [], {}, ()",
     "code":"# CONDICIONAIS EM ACAO\n\nnota = 7.8\n\nif nota >= 9.0:\n    conceito = \"A - Excelente!\"\nelif nota >= 7.0:\n    conceito = \"B - Bom!\"\nelif nota >= 5.0:\n    conceito = \"C - Regular\"\nelse:\n    conceito = \"F - Reprovado\"\n\nprint(f\"Nota: {nota}\")\nprint(f\"Conceito: {conceito}\")\n\n# Operador ternario\naprovado = \"Aprovado\" if nota >= 5 else \"Reprovado\"\nprint(f\"Situacao: {aprovado}\")\n\n# Condicoes compostas\nidade = 20\ntem_cnh = True\nif idade >= 18 and tem_cnh:\n    print(\"\\nPode dirigir!\")\nelif idade >= 18:\n    print(\"\\nTem idade mas precisa de CNH\")\nelse:\n    print(\"\\nMenor de idade\")",
     "tip":"Sempre verifique n % 15 antes de n % 3 e n % 5 no FizzBuzz!"},

    {"id":"py_05","title":"Loops: for e while","level":"Iniciante","emoji":"🔄","duration":"18 min","xp":60,
     "theory":"Loops repetem blocos de codigo!\n\nFOR LOOP\nfor i in range(5):        # 0,1,2,3,4\nfor i in range(1, 6):     # 1,2,3,4,5\nfor i in range(0, 10, 2): # 0,2,4,6,8\n\nWHILE LOOP\nwhile condicao:\n    # SEMPRE atualize a condicao!\n\nAVISO: while True sem break = loop infinito!\n\nCONTROLE\n  break     sai do loop\n  continue  pula iteracao\n  pass      nao faz nada\n\nENUMERATE\nfor i, valor in enumerate(lista):",
     "code":"# LOOPS EM ACAO\n\n# Range basico\nprint(\"=== Quadrados ===\")\nfor i in range(1, 8):\n    print(f\"  {i} ao quadrado = {i**2}\")\n\n# Iterando lista com enumerate\nfrutas = [\"Maca\", \"Banana\", \"Uva\"]\nprint(\"\\n=== Frutas ===\")\nfor i, fruta in enumerate(frutas):\n    print(f\"  [{i}] {fruta}\")\n\n# While\nprint(\"\\n=== Contagem ===\")\nn = 5\nwhile n > 0:\n    print(f\"  {n}...\", end=\" \")\n    n -= 1\nprint(\"LANCAMENTO!\")\n\n# Break e Continue\nprint(\"\\n=== Sem multiplos de 3 ===\")\nfor num in range(1, 16):\n    if num % 3 == 0:\n        continue\n    if num > 13:\n        break\n    print(f\"  {num}\", end=\" \")",
     "tip":"Prefira for sobre while quando souber o numero de iteracoes!"},

    {"id":"py_06","title":"Funcoes","level":"Intermediário","emoji":"⚙️","duration":"20 min","xp":80,
     "theory":"Funcoes sao blocos de codigo reutilizaveis!\n\nDEFININDO\n  def nome(parametros):\n      '''Docstring'''\n      return valor\n\nTIPOS DE PARAMETROS\n  def f(a, b):       posicionais\n  def f(a, b=10):    com default\n  def f(*args):      qualquer qtd -> tupla\n  def f(**kwargs):   nomeados -> dict\n\nLAMBDA\nFuncoes anonimas de uma linha:\n  dobro = lambda x: x * 2\n\nESCOPO\n* Variaveis dentro sao LOCAIS\n* Use global para modificar externas",
     "code":"# FUNCOES EM ACAO\n\ndef calcular_imc(peso, altura):\n    '''Calcula o IMC'''\n    imc = peso / (altura ** 2)\n    if imc < 18.5:   cat = \"Abaixo do peso\"\n    elif imc < 25:   cat = \"Normal\"\n    elif imc < 30:   cat = \"Sobrepeso\"\n    else:            cat = \"Obesidade\"\n    return round(imc, 1), cat\n\nimc, cat = calcular_imc(70, 1.75)\nprint(f\"IMC: {imc} -- {cat}\")\n\n# *args\ndef somar(*numeros):\n    return sum(numeros)\n\nprint(f\"\\nSoma: {somar(1, 2, 3)}\")\nprint(f\"Soma: {somar(10, 20, 30, 40)}\")\n\n# **kwargs\ndef criar_perfil(**dados):\n    print(\"\\nPERFIL:\")\n    for campo, valor in dados.items():\n        print(f\"  {campo}: {valor}\")\n\ncriar_perfil(nome=\"Ana\", idade=25, cidade=\"SP\")\n\n# Lambda\ndobro = lambda x: x * 2\nprint(f\"\\nDobro de 7: {dobro(7)}\")",
     "tip":"Uma boa funcao: faz UMA coisa, tem nome descritivo e docstring!"},

    {"id":"py_07","title":"Listas","level":"Intermediário","emoji":"📋","duration":"22 min","xp":80,
     "theory":"Listas sao a estrutura mais usada em Python!\n\nACESSO\n  lista[0]    primeiro\n  lista[-1]   ultimo\n  lista[1:4]  fatia\n\nMETODOS\n  append(x)   adiciona ao fim\n  insert(i,x) insere na posicao\n  remove(x)   remove primeira ocorrencia\n  pop()       remove e retorna o ultimo\n  sort()      ordena no lugar\n  len(lista)  tamanho\n\nLIST COMPREHENSION\n[expressao for item in iteravel if condicao]\nquadrados = [x**2 for x in range(10)]\npares     = [x for x in range(20) if x%2==0]",
     "code":"# LISTAS EM ACAO\n\nlinguagens = [\"Python\", \"JavaScript\", \"Java\", \"Rust\"]\nprint(f\"Lista: {linguagens}\")\nprint(f\"Primeira: {linguagens[0]}\")\nprint(f\"Ultima: {linguagens[-1]}\")\nprint(f\"Fatia [1:3]: {linguagens[1:3]}\")\n\n# Manipulacao\nlinguagens.append(\"Go\")\nlinguagens.insert(0, \"C++\")\nprint(f\"\\nApos add: {linguagens}\")\nlinguagens.remove(\"C++\")\nprint(f\"Final: {linguagens}\")\n\n# Ordenacao\nnumeros = [64, 34, 25, 12, 22, 11, 90]\nprint(f\"\\nOriginal: {numeros}\")\nprint(f\"Crescente: {sorted(numeros)}\")\n\n# List Comprehension\nprint(\"\\n=== List Comprehension ===\")\nquadrados = [x**2 for x in range(1, 9)]\nprint(f\"Quadrados: {quadrados}\")\n\npares = [x for x in range(1, 21) if x % 2 == 0]\nprint(f\"Pares ate 20: {pares}\")",
     "tip":"List comprehension e ate 35% mais rapida que loop for equivalente!"},

    {"id":"py_08","title":"Dicionarios e Sets","level":"Intermediário","emoji":"🗂️","duration":"20 min","xp":80,
     "theory":"Dicionarios armazenam pares chave -> valor!\n\nCRIANDO\n  pessoa = {\n      'nome': 'Ana',\n      'idade': 25\n  }\n\nACESSANDO\n  pessoa['nome']          Ana\n  pessoa.get('nome')      seguro\n  pessoa.get('x', 'N/A')  com default\n\nMETODOS\n  .keys()    chaves\n  .values()  valores\n  .items()   pares (k,v)\n  .update()  mescla\n\nSETS\nColecao sem duplicatas:\n  a | b  uniao\n  a & b  intersecao\n  a - b  diferenca",
     "code":"# DICIONARIOS E SETS\n\ndev = {\n    \"nome\": \"Carlos\",\n    \"idade\": 28,\n    \"skills\": [\"Python\", \"Django\", \"Docker\"],\n    \"nivel\": \"Senior\"\n}\n\nprint(f\"Nome: {dev['nome']}\")\nprint(f\"Cargo: {dev.get('cargo', 'Nao informado')}\")\n\nprint(\"\\nPerfil completo:\")\nfor chave, valor in dev.items():\n    print(f\"  {chave:12} -> {valor}\")\n\n# Dict Comprehension\nprint(\"\\n=== Potencias ===\")\npotencias = {f\"2^{i}\": 2**i for i in range(1, 9)}\nfor k, v in potencias.items():\n    print(f\"  {k:5} = {v}\")\n\n# Sets\nprint(\"\\n=== Sets ===\")\na = {1, 2, 3, 4, 5}\nb = {3, 4, 5, 6, 7}\nprint(f\"Uniao:     {a | b}\")\nprint(f\"Intersec:  {a & b}\")\nprint(f\"Diferenca: {a - b}\")",
     "tip":"Use set() para remover duplicatas de uma lista rapidamente!"},
  ],
  "javascript": [
    {"id":"js_01","title":"Fundamentos do JS","level":"Iniciante","emoji":"⚡","duration":"12 min","xp":50,
     "theory":"JavaScript e a linguagem da web!\n\nVARIAVEIS\n  var x = 1;   EVITE\n  let y = 2;   mutavel\n  const Z = 3; imutavel\n\nTIPOS\n  number:    42, 3.14, NaN\n  string:    'texto', `template`\n  boolean:   true, false\n  null:      valor vazio explicitamente\n  undefined: variavel sem valor\n  object:    {}, []\n\nTEMPLATE LITERALS\nconst nome = 'Ana';\nconsole.log(`Ola, ${nome}!`);\n\nCUIDADO\ntypeof null -> 'object'  (bug historico!)\nSempre use === nao ==",
     "code":"// JAVASCRIPT FUNDAMENTOS\n\nlet nome = \"Ana Silva\";\nconst ANO = 1999;\nlet ativo = true;\n\nconst idade = 2024 - ANO;\nconsole.log(`${nome} tem ${idade} anos`);\n\n// Operadores\nconst a = 10, b = 3;\nconsole.log(`${a} + ${b} = ${a + b}`);\nconsole.log(`${a} ** ${b} = ${a ** b}`);\nconsole.log(`${a} % ${b} = ${a % b}`);\n\n// == vs ===\nconsole.log('\\n=== Comparacao ===');\nconsole.log(`5 == \"5\"  -> ${5 == \"5\"}`);\nconsole.log(`5 === \"5\" -> ${5 === \"5\"}`);\n\n// Tipos\nconst vals = [42, \"texto\", true, null, undefined];\nvals.forEach(v => console.log(`${String(v).padEnd(10)} -> ${typeof v}`));",
     "tip":"Sempre use === (triplo igual) -- nunca == em JavaScript!"},

    {"id":"js_02","title":"Arrow Functions","level":"Iniciante","emoji":"🏹","duration":"18 min","xp":60,
     "theory":"JavaScript tem 3 formas de criar funcoes!\n\nDECLARATION (hoisting)\nfunction somar(a, b) { return a + b; }\n\nEXPRESSION (sem hoisting)\nconst somar = function(a, b) { return a + b; };\n\nARROW FUNCTION\nconst somar = (a, b) => a + b;\n\nSimplificacoes:\n* 1 parametro: sem parenteses\n* 1 linha: sem {} e sem return\n\nDEFAULT\nconst greet = (nome = 'dev') => `Ola, ${nome}!`;\n\nREST\nconst soma = (...nums) => nums.reduce((a,b)=>a+b,0);",
     "code":"// FUNCOES EM ACAO\n\n// Arrow functions\nconst dobro = x => x * 2;\nconst quadrado = x => x ** 2;\nconst saudar = (nome = \"Dev\") => `Ola, ${nome}!`;\n\nconsole.log(`Dobro de 7: ${dobro(7)}`);\nconsole.log(`Quadrado de 8: ${quadrado(8)}`);\nconsole.log(saudar());\nconsole.log(saudar(\"Ana\"));\n\n// Rest parameters\nconst somar = (...nums) => {\n    const total = nums.reduce((acc, n) => acc + n, 0);\n    console.log(`Soma de [${nums}] = ${total}`);\n    return total;\n};\nsomar(1, 2, 3);\nsomar(10, 20, 30, 40, 50);\n\n// Higher-order functions\nconst nums = [1,2,3,4,5,6,7,8,9,10];\nconst resultado = nums\n    .filter(n => n % 2 === 0)\n    .map(n => n ** 2)\n    .reduce((acc, n) => acc + n, 0);\n\nconsole.log(`\\nSoma quadrados pares: ${resultado}`);",
     "tip":"Arrow functions nao tem 'this' -- use function para metodos de objeto!"},

    {"id":"js_03","title":"Arrays Modernos","level":"Intermediário","emoji":"📊","duration":"25 min","xp":80,
     "theory":"Arrays em JS tem metodos funcionais poderosos!\n\nTRANSFORMACAO\n  map(fn)      novo array transformado\n  filter(fn)   novo array filtrado\n  reduce(fn,i) reduz a um valor\n\nBUSCA\n  find(fn)     primeiro que passa\n  includes(x)  boolean\n  some(fn)     true se ALGUM passa\n  every(fn)    true se TODOS passam\n\nOUTROS\n  sort(fn)     SEMPRE passe comparador!\n  slice(i,j)   copia (nao modifica)\n\nDESTRUTURACAO\nconst [a, b, ...resto] = [1, 2, 3, 4];",
     "code":"// ARRAYS MODERNOS\n\nconst produtos = [\n    { nome: \"Notebook\",  preco: 2500, estoque: 15 },\n    { nome: \"Mouse\",     preco: 80,   estoque: 50 },\n    { nome: \"Teclado\",   preco: 150,  estoque: 30 },\n    { nome: \"Monitor\",   preco: 1200, estoque: 8  },\n];\n\n// filter\nconst caros = produtos.filter(p => p.preco > 200);\nconsole.log(\"Produtos caros:\");\ncaros.forEach(p => console.log(`  ${p.nome}: R$${p.preco}`));\n\n// map\nconst nomes = produtos.map(p => p.nome);\nconsole.log(\"\\nNomes:\", nomes);\n\n// reduce\nconst total = produtos.reduce(\n    (acc, p) => acc + (p.preco * p.estoque), 0\n);\nconsole.log(`\\nValor total: R$${total.toLocaleString()}`);\n\n// sort com comparador\nconst ordenados = [...produtos].sort((a, b) => a.preco - b.preco);\nconsole.log(\"\\nPor preco:\");\nordenados.forEach(p => console.log(`  R$${p.preco} -- ${p.nome}`));\n\nconsole.log(`\\nAlgum > R$2000? ${produtos.some(p => p.preco > 2000)}`);\nconsole.log(`Todos em estoque? ${produtos.every(p => p.estoque > 0)}`);",
     "tip":"Nunca use .sort() sem comparador para numeros -- da resultado errado!"},

    {"id":"js_04","title":"Classes ES6+","level":"Intermediário","emoji":"🏛️","duration":"28 min","xp":90,
     "theory":"JavaScript moderno tem classes reais!\n\nESTRUTURA\nclass Animal {\n    #nome;  // privado (ES2022)\n\n    constructor(nome) { this.#nome = nome; }\n    get nome() { return this.#nome; }\n    falar() { return `${this.nome}...`; }\n}\n\nHERANCA\nclass Cachorro extends Animal {\n    falar() { return `${this.nome}: Au au!`; }\n}\n\nDESTRUTURACAO\nconst { nome, idade = 25 } = pessoa;\nconst novo = { ...pessoa, cidade: 'SP' };",
     "code":"// CLASSES EM ACAO\n\nclass ContaBancaria {\n    #saldo = 0;\n    #historico = [];\n\n    constructor(titular, numero) {\n        this.titular = titular;\n        this.numero = numero;\n    }\n\n    depositar(valor) {\n        if (valor <= 0) throw new Error(\"Invalido\");\n        this.#saldo += valor;\n        this.#historico.push({ tipo: \"Deposito\", valor, saldo: this.#saldo });\n        return this;\n    }\n\n    sacar(valor) {\n        if (valor > this.#saldo) throw new Error(\"Saldo insuficiente\");\n        this.#saldo -= valor;\n        this.#historico.push({ tipo: \"Saque\", valor, saldo: this.#saldo });\n        return this;\n    }\n\n    get saldo() { return this.#saldo; }\n\n    extrato() {\n        console.log(`\\n=== Conta ${this.numero} ===`);\n        this.#historico.forEach(({ tipo, valor, saldo }) => {\n            console.log(`  ${tipo}: R$${valor.toFixed(2)} | Saldo: R$${saldo.toFixed(2)}`);\n        });\n    }\n}\n\nconst conta = new ContaBancaria(\"Ana\", \"001-234\");\nconta.depositar(1000).depositar(500).sacar(200);\nconta.extrato();\nconsole.log(`\\nSaldo: R$${conta.saldo.toFixed(2)}`);",
     "tip":"Use # para campos privados reais em classes modernas (ES2022)!"},
  ],
  "java": [
    {"id":"java_01","title":"Introducao ao Java","level":"Iniciante","emoji":"☕","duration":"15 min","xp":60,
     "theory":"Java e fortemente tipada e orientada a objetos!\n\nESTRUTURA OBRIGATORIA\npublic class NomeArquivo {\n    public static void main(String[] args) {\n        // codigo aqui\n    }\n}\nATENCAO: Nome da classe = nome do arquivo!\n\nTIPOS PRIMITIVOS\n  int     inteiro       (4 bytes)\n  double  decimal       (8 bytes)\n  float   decimal leve  3.14f\n  long    int grande    100L\n  char    caractere     'A'\n  boolean true/false\n\nString NAO e primitivo -- e uma CLASSE!\n\nSAIDA\nSystem.out.println()  com quebra\nSystem.out.printf()   formatado",
     "code":"// JAVA FUNDAMENTOS\n// Arquivo: Fundamentos.java\n\npublic class Fundamentos {\n\n    public static void main(String[] args) {\n\n        // Tipos primitivos\n        int     idade     = 25;\n        double  altura    = 1.75;\n        float   peso      = 70.5f;      // 'f' obrigatorio!\n        long    pop       = 8000000000L; // 'L' obrigatorio!\n        char    inicial   = 'A';\n        boolean ativo     = true;\n\n        // String (e uma Classe!)\n        String nome = \"Carlos Silva\";\n\n        // Printf formatado\n        System.out.println(\"=== DADOS ===\");\n        System.out.printf(\"Nome:   %s%n\", nome);\n        System.out.printf(\"Idade:  %d anos%n\", idade);\n        System.out.printf(\"Altura: %.2f m%n\", altura);\n\n        // Operacoes -- CUIDADO com int/int!\n        int a = 10, b = 3;\n        System.out.println(\"\\n=== OPERACOES ===\");\n        System.out.println(\"Divisao int:  \" + (a / b));         // 3!\n        System.out.println(\"Divisao real: \" + (a / (double)b)); // 3.33\n        System.out.println(\"Modulo:       \" + (a % b));\n        System.out.println(\"Potencia:     \" + (int)Math.pow(a, b));\n    }\n}",
     "tip":"int/int = int em Java! Use (double)a / b para resultado decimal."},

    {"id":"java_02","title":"Condicionais e Loops","level":"Iniciante","emoji":"🔄","duration":"18 min","xp":70,
     "theory":"Java tem as mesmas estruturas do C/C++!\n\nIF/ELSE\n  if (condicao) { }\n  else if (outra) { }\n  else { }\n\nSWITCH Java 14+\n  switch (valor) {\n      case 1 -> \"Um\";\n      default -> \"Outro\";\n  }\n\nFOR LOOP\n  for (int i=0; i<10; i++) { }\n\nWHILE\n  while (condicao) {  }       // testa antes\n  do { } while (condicao);    // testa depois\n\nFOR-EACH\n  for (int n : array) { }",
     "code":"// CONDICIONAIS E LOOPS\n\npublic class ControleDeFluxo {\n\n    public static void main(String[] args) {\n\n        // Switch Expression (Java 14+)\n        int mes = 7;\n        String estacao = switch (mes) {\n            case 12, 1, 2  -> \"Verao\";\n            case 3, 4, 5   -> \"Outono\";\n            case 6, 7, 8   -> \"Inverno\";\n            case 9, 10, 11 -> \"Primavera\";\n            default -> \"Invalido\";\n        };\n        System.out.println(\"Mes \" + mes + \": \" + estacao);\n\n        // For -- Tabuada\n        System.out.println(\"\\n=== TABUADA DO 7 ===\");\n        for (int i = 1; i <= 10; i++) {\n            System.out.printf(\"7 x %2d = %2d%n\", i, 7 * i);\n        }\n\n        // For-each\n        String[] langs = {\"Java\", \"Python\", \"JavaScript\"};\n        System.out.println(\"\\n=== LINGUAGENS ===\");\n        for (String lang : langs) {\n            System.out.println(\"  -> \" + lang);\n        }\n\n        // Do-while\n        System.out.println(\"\\n=== POTENCIAS DE 2 ===\");\n        int v = 1;\n        do {\n            System.out.print(v + \" \");\n            v *= 2;\n        } while (v <= 1024);\n    }\n}",
     "tip":"Use for-each quando nao precisar do indice -- mais seguro e legivel!"},

    {"id":"java_03","title":"Classes e OOP","level":"Intermediário","emoji":"🏛️","duration":"35 min","xp":100,
     "theory":"Java foi construido para OOP!\n\n4 PILARES\n1. ENCAPSULAMENTO\n   Ocultar dados. Use private + getters/setters.\n\n2. HERANCA\n   class Filho extends Pai { }\n\n3. POLIMORFISMO\n   Mesma interface, comportamentos diferentes.\n\n4. ABSTRACAO\n   Simplificar complexidade.\n\nCLASSE\npublic class Produto {\n    private String nome;\n    private double preco;\n\n    public Produto(String n, double p) {\n        this.nome = n;\n        this.preco = p;\n    }\n    public String getNome() { return nome; }\n}\n\nABSTRACT\nabstract class Forma {\n    abstract double area();\n}",
     "code":"// CLASSES E OOP\n\nabstract class Funcionario {\n    protected String nome;\n    protected double salarioBase;\n\n    public Funcionario(String nome, double salBase) {\n        this.nome = nome;\n        this.salarioBase = salBase;\n    }\n\n    public abstract double calcularSalario();\n\n    public void exibirInfo() {\n        System.out.printf(\"%-18s -> R$%.2f%n\",\n                         nome, calcularSalario());\n    }\n}\n\nclass Desenvolvedor extends Funcionario {\n    private int horasExtras;\n    private static final double H_EXTRA = 80.0;\n\n    public Desenvolvedor(String nome, double base, int horas) {\n        super(nome, base);\n        this.horasExtras = horas;\n    }\n\n    @Override\n    public double calcularSalario() {\n        return salarioBase + (horasExtras * H_EXTRA);\n    }\n}\n\nclass Gerente extends Funcionario {\n    private double bonus;\n\n    public Gerente(String nome, double base, double bonus) {\n        super(nome, base);\n        this.bonus = bonus;\n    }\n\n    @Override\n    public double calcularSalario() {\n        return salarioBase + bonus;\n    }\n}\n\npublic class SistemaRH {\n    public static void main(String[] args) {\n        Funcionario[] equipe = {\n            new Desenvolvedor(\"Ana Silva\",   8000, 20),\n            new Desenvolvedor(\"Carlos Lima\", 9500, 15),\n            new Gerente(\"Beatriz Costa\",    12000, 3000),\n        };\n\n        System.out.println(\"=== FOLHA DE PAGAMENTO ===\");\n        double total = 0;\n        for (Funcionario f : equipe) {\n            f.exibirInfo();\n            total += f.calcularSalario();\n        }\n        System.out.printf(\"\\nTotal: R$%.2f%n\", total);\n    }\n}",
     "tip":"Programe para interfaces/abstracoes, nao para implementacoes!"},
  ]
}

EXERCISES = [
  {"id":"ex_py_01","lang":"python","level":"Iniciante","emoji":"👋","xp":100,"title":"Saudacao Personalizada",
   "desc":"Crie saudar(nome) que retorne:\n'Ola, [NOME]! Bem-vindo ao CodeMaster Pro!'\nO nome deve estar em MAIUSCULAS.",
   "hint":"Use .upper() para maiusculas e f-strings para formatar.",
   "starter":"def saudar(nome):\n    nome_maiusculo = nome._____()\n    return f\"_____, {_____}! Bem-vindo ao CodeMaster Pro!\"\n\nprint(saudar(\"ana\"))\nprint(saudar(\"carlos\"))",
   "solution":"def saudar(nome):\n    nome_maiusculo = nome.upper()\n    return f\"Ola, {nome_maiusculo}! Bem-vindo ao CodeMaster Pro!\"\n\nprint(saudar(\"ana\"))\nprint(saudar(\"carlos\"))"},

  {"id":"ex_py_02","lang":"python","level":"Iniciante","emoji":"🔢","xp":100,"title":"Par ou Impar",
   "desc":"Crie verificar(n) que retorne 'par' ou 'impar'.\nDepois liste todos os pares de 1 a 20.",
   "hint":"Use % 2 para paridade. Se n % 2 == 0, e par!",
   "starter":"def verificar(numero):\n    if numero % ___ == ___:\n        return \"par\"\n    return \"impar\"\n\nfor i in range(1, 11):\n    print(f\"{i} e {verificar(i)}\")\n\npares = [n for n in range(1, 21) if ___]\nprint(\"Pares:\", pares)",
   "solution":"def verificar(numero):\n    if numero % 2 == 0:\n        return 'par'\n    return 'impar'\n\nfor i in range(1, 11):\n    print(f\"{i} e {verificar(i)}\")\n\npares = [n for n in range(1, 21) if n % 2 == 0]\nprint('Pares:', pares)"},

  {"id":"ex_py_03","lang":"python","level":"Iniciante","emoji":"✖️","xp":120,"title":"Tabuada Formatada",
   "desc":"Crie tabuada(n) imprimindo a tabuada de 1 a 10:\n7 x  1 =  7\n7 x  2 = 14",
   "hint":"Use range(1, 11) e f-strings com :2d para alinhar.",
   "starter":"def tabuada(n):\n    print(f\"\\n{'='*20}\")\n    print(f\"  TABUADA DO {n}\")\n    print(f\"{'='*20}\")\n    for i in range(___, ___):\n        resultado = ___ * ___\n        print(f\"  {n} x {i:2d} = {resultado:3d}\")\n\ntabuada(7)",
   "solution":"def tabuada(n):\n    print(f\"\\n{'='*20}\")\n    print(f\"  TABUADA DO {n}\")\n    print(f\"{'='*20}\")\n    for i in range(1, 11):\n        resultado = n * i\n        print(f\"  {n} x {i:2d} = {resultado:3d}\")\n\ntabuada(7)"},

  {"id":"ex_py_04","lang":"python","level":"Intermediário","emoji":"🎯","xp":150,"title":"FizzBuzz Classico",
   "desc":"Para numeros de 1 a 50:\n- Divisivel por 3: 'Fizz'\n- Divisivel por 5: 'Buzz'\n- Divisivel por 3 e 5: 'FizzBuzz'\n- Outro: o numero",
   "hint":"Verifique % 15 PRIMEIRO! A ordem importa.",
   "starter":"resultado = []\nfor n in range(1, 51):\n    if n % ___ == 0:\n        resultado.append('FizzBuzz')\n    elif n % ___ == 0:\n        resultado.append('Fizz')\n    elif n % ___ == 0:\n        resultado.append('Buzz')\n    else:\n        resultado.append(str(n))\n\nfor i in range(0, 50, 10):\n    print(' '.join(resultado[i:i+10]))",
   "solution":"resultado = []\nfor n in range(1, 51):\n    if n % 15 == 0:\n        resultado.append('FizzBuzz')\n    elif n % 3 == 0:\n        resultado.append('Fizz')\n    elif n % 5 == 0:\n        resultado.append('Buzz')\n    else:\n        resultado.append(str(n))\n\nfor i in range(0, 50, 10):\n    print(' '.join(resultado[i:i+10]))"},

  {"id":"ex_py_05","lang":"python","level":"Intermediário","emoji":"📊","xp":180,"title":"Analisador de Lista",
   "desc":"Crie analisar(nums) retornando dict com:\nsoma, media, maior, menor, qtd_pares, qtd_impares",
   "hint":"Use sum(), max(), min(), len() do Python.",
   "starter":"def analisar(nums):\n    return {\n        'soma':        ___,\n        'media':       round(___ / len(nums), 2),\n        'maior':       ___,\n        'menor':       ___,\n        'qtd_pares':   len([n for n in nums if ___ == 0]),\n        'qtd_impares': len([n for n in nums if ___ != 0]),\n    }\n\nnumeros = [3, 7, 2, 9, 4, 1, 8, 5, 6, 10]\nstats = analisar(numeros)\nfor k, v in stats.items():\n    print(f'{k:14}: {v}')",
   "solution":"def analisar(nums):\n    return {\n        'soma':        sum(nums),\n        'media':       round(sum(nums) / len(nums), 2),\n        'maior':       max(nums),\n        'menor':       min(nums),\n        'qtd_pares':   len([n for n in nums if n % 2 == 0]),\n        'qtd_impares': len([n for n in nums if n % 2 != 0]),\n    }\n\nnumeros = [3, 7, 2, 9, 4, 1, 8, 5, 6, 10]\nstats = analisar(numeros)\nfor k, v in stats.items():\n    print(f'{k:14}: {v}')"},

  {"id":"ex_js_01","lang":"javascript","level":"Iniciante","emoji":"🌡️","xp":120,"title":"Conversor de Temperatura",
   "desc":"Crie 3 arrow functions:\n- celsiusParaF(c): (c x 9/5) + 32\n- fahrenheitParaC(f): (f-32) x 5/9\n- celsiusParaK(c): c + 273.15",
   "hint":"Use arrow functions e .toFixed(2) para 2 casas decimais.",
   "starter":"const celsiusParaF = (c) => ___;\nconst fahrenheitParaC = (f) => ___;\nconst celsiusParaK = (c) => ___;\n\nconsole.log('100C = ' + celsiusParaF(100) + ' F');\nconsole.log('212F = ' + fahrenheitParaC(212) + ' C');\nconsole.log('0C = ' + celsiusParaK(0) + ' K');",
   "solution":"const celsiusParaF = (c) => ((c * 9/5) + 32).toFixed(2);\nconst fahrenheitParaC = (f) => ((f - 32) * 5/9).toFixed(2);\nconst celsiusParaK = (c) => (c + 273.15).toFixed(2);\n\nconsole.log('100C = ' + celsiusParaF(100) + ' F');\nconsole.log('212F = ' + fahrenheitParaC(212) + ' C');\nconsole.log('0C = ' + celsiusParaK(0) + ' K');"},

  {"id":"ex_js_02","lang":"javascript","level":"Intermediário","emoji":"🛒","xp":160,"title":"Pipeline de Produtos",
   "desc":"Use filter/map/sort/reduce para:\n1. Filtrar estoque > 0\n2. Aplicar 15% desconto nos acima de R$100\n3. Ordenar por preco crescente\n4. Calcular total",
   "hint":"Encadeie: .filter().map().sort() depois .reduce()",
   "starter":"const produtos = [\n  {nome:'Notebook',preco:2500,estoque:3},\n  {nome:'Caneta',preco:5,estoque:0},\n  {nome:'Mouse',preco:80,estoque:10},\n  {nome:'Monitor',preco:1200,estoque:2},\n];\n\nconst pipeline = produtos\n  ._____(p => p.estoque > 0)\n  ._____(p => ({...p, final: p.preco > 100 ? p.preco * 0.85 : p.preco}))\n  ._____((___, b) => a.final - b.final);\n\nconst total = pipeline.reduce((___, p) => ___ + p.final, 0);\npipeline.forEach(p => console.log(p.nome + ': R$' + p.final.toFixed(2)));\nconsole.log('Total: R$' + total.toFixed(2));",
   "solution":"const produtos = [\n  {nome:'Notebook',preco:2500,estoque:3},\n  {nome:'Caneta',preco:5,estoque:0},\n  {nome:'Mouse',preco:80,estoque:10},\n  {nome:'Monitor',preco:1200,estoque:2},\n];\n\nconst pipeline = produtos\n  .filter(p => p.estoque > 0)\n  .map(p => ({...p, final: p.preco > 100 ? p.preco * 0.85 : p.preco}))\n  .sort((a, b) => a.final - b.final);\n\nconst total = pipeline.reduce((acc, p) => acc + p.final, 0);\npipeline.forEach(p => console.log(p.nome + ': R$' + p.final.toFixed(2)));\nconsole.log('Total: R$' + total.toFixed(2));"},

  {"id":"ex_java_01","lang":"java","level":"Intermediário","emoji":"🌀","xp":180,"title":"Fibonacci",
   "desc":"Implemente:\n- fibonacci(n): recursivo\n- fibonacciLoop(n): iterativo\nImprime os 12 primeiros termos.\nF(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)",
   "hint":"Iterativo: 2 variaveis que vao trocando de valor.",
   "starter":"public class Fibonacci {\n\n    static long fibonacci(int n) {\n        if (n <= 1) return ___;\n        return ___(n-1) + ___(n-2);\n    }\n\n    static long fibonacciLoop(int n) {\n        if (n <= 1) return n;\n        long a = 0, b = 1;\n        for (int i = 2; i <= n; i++) {\n            long temp = a + b;\n            a = ___;\n            b = ___;\n        }\n        return b;\n    }\n\n    public static void main(String[] args) {\n        System.out.print(\"Recursivo: \");\n        for (int i = 0; i < 12; i++)\n            System.out.print(fibonacci(i) + \" \");\n    }\n}",
   "solution":"public class Fibonacci {\n    static long fibonacci(int n) {\n        if (n <= 1) return n;\n        return fibonacci(n-1) + fibonacci(n-2);\n    }\n    static long fibonacciLoop(int n) {\n        if (n <= 1) return n;\n        long a = 0, b = 1;\n        for (int i = 2; i <= n; i++) {\n            long temp = a + b; a = b; b = temp;\n        }\n        return b;\n    }\n    public static void main(String[] args) {\n        System.out.print(\"Recursivo: \");\n        for (int i=0;i<12;i++) System.out.print(fibonacci(i)+\" \");\n        System.out.print(\"\\nIterativo: \");\n        for (int i=0;i<12;i++) System.out.print(fibonacciLoop(i)+\" \");\n    }\n}"},
]

QUIZZES = [
  {"id":"q01","lang":"python","level":"Iniciante","q":"O que imprime: print(10 // 3)?","opts":["3.33","3","4","1"],"ans":1,"exp":"// e divisao inteira. 10 // 3 = 3 (trunca o decimal)."},
  {"id":"q02","lang":"python","level":"Iniciante","q":"Qual funcao verifica o tipo de uma variavel?","opts":["typeof()","typeOf()","type()","getType()"],"ans":2,"exp":"type(variavel) retorna o tipo. Ex: type(42) retorna <class 'int'>."},
  {"id":"q03","lang":"python","level":"Iniciante","q":"O que faz o operador ** em Python?","opts":["Multiplicacao","Divisao","Potencia","Bitwise AND"],"ans":2,"exp":"** e potencia. 2**8 = 256, 3**3 = 27."},
  {"id":"q04","lang":"python","level":"Intermediário","q":"O que imprime: print([x**2 for x in range(4)])?","opts":["[0,1,4,9]","[1,4,9,16]","[0,1,2,3]","[1,2,3,4]"],"ans":0,"exp":"range(4) gera [0,1,2,3]. Elevando ao quadrado: [0,1,4,9]."},
  {"id":"q05","lang":"python","level":"Intermediário","q":"Qual metodo de dict retorna None se a chave nao existir?","opts":["d['chave']","d.find()","d.get()","d.fetch()"],"ans":2,"exp":"d.get('chave') retorna None. d['chave'] lanca KeyError!"},
  {"id":"q06","lang":"python","level":"Avançado","q":"O que sao *args em Python?","opts":["Apenas 1 arg","Args nomeados","Qualquer qtd de args em tupla","Arg obrigatorio"],"ans":2,"exp":"*args captura qualquer numero de argumentos posicionais como tupla."},
  {"id":"q07","lang":"javascript","level":"Iniciante","q":"Diferenca entre let e const?","opts":["let e mais rapido","const nao pode ser reatribuido","let tem escopo global","Nao ha diferenca"],"ans":1,"exp":"const cria referencia imutavel. let pode ser reatribuido."},
  {"id":"q08","lang":"javascript","level":"Iniciante","q":"O que retorna typeof null?","opts":["'null'","'undefined'","'object'","'boolean'"],"ans":2,"exp":"Bug historico do JS! typeof null retorna 'object'. Use === null para checar."},
  {"id":"q09","lang":"javascript","level":"Intermediário","q":"O que faz Array.filter()?","opts":["Transforma cada elemento","Filtra e retorna novo array","Ordena o array","Encontra 1 elemento"],"ans":1,"exp":"filter(fn) retorna novo array com elementos onde fn retorna true."},
  {"id":"q10","lang":"javascript","level":"Intermediário","q":"Arrow function correta:","opts":["function => x*2","x -> x*2","x => x*2","(x) >> x*2"],"ans":2,"exp":"Arrow function: x => x * 2. Com 2 params: (x, y) => x + y."},
  {"id":"q11","lang":"java","level":"Iniciante","q":"int x = 7 / 2 em Java resulta em?","opts":["3.5","3","4","Erro"],"ans":1,"exp":"Java: int/int = int (trunca). 7/2 = 3. Use (double)7/2 para 3.5."},
  {"id":"q12","lang":"java","level":"Iniciante","q":"Qual modificador torna membro privado a classe?","opts":["public","protected","package","private"],"ans":3,"exp":"private: acesso apenas dentro da propria classe."},
  {"id":"q13","lang":"java","level":"Intermediário","q":"O que e @Override em Java?","opts":["Cria nova classe","Indica sobrescrita de metodo","Torna estatico","Declara excecao"],"ans":1,"exp":"@Override indica sobrescrita de metodo da superclasse. Compilador verifica!"},
  {"id":"q14","lang":"python","level":"Avançado","q":"Qual estrutura Python NAO permite duplicatas?","opts":["list","tuple","dict","set"],"ans":3,"exp":"set nao aceita duplicatas. {1,2,2,3} = {1,2,3}."},
  {"id":"q15","lang":"javascript","level":"Avançado","q":"O que e uma Closure?","opts":["Tipo de loop","Funcao que lembra escopo lexico","Forma de importar","Metodo de array"],"ans":1,"exp":"Closure e funcao que lembra o ambiente onde foi criada."},
]

def load_progress():
    try:
        if os.path.exists(PROGRESS_F):
            with open(PROGRESS_F) as f: return json.load(f)
    except: pass
    return {"lessons":[],"exercises":[],"xp":0,"level":1,"quizzes_taken":0,"quiz_correct":0}

def save_progress(data):
    try:
        with open(PROGRESS_F, "w") as f: json.dump(data, f, indent=2)
    except: pass

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/api/languages")
def get_languages():
    return jsonify([
        {"id":"python",     "name":"Python",     "emoji":"🐍","color":"#3b82f6","lessons":len(LESSONS["python"]),     "desc":"Simples, poderoso e versatil"},
        {"id":"javascript", "name":"JavaScript", "emoji":"⚡","color":"#fbbf24","lessons":len(LESSONS["javascript"]), "desc":"A linguagem da web moderna"},
        {"id":"java",       "name":"Java",       "emoji":"☕","color":"#ef4444","lessons":len(LESSONS["java"]),       "desc":"Robusto e orientado a objetos"},
    ])

@app.route("/api/lessons/<lang>")
def get_lessons(lang):
    if lang not in LESSONS: return jsonify({"error":"Nao encontrado"}), 404
    return jsonify(LESSONS[lang])

@app.route("/api/exercises")
def get_exercises():
    lang  = request.args.get("lang")
    exs   = EXERCISES
    if lang: exs = [e for e in exs if e["lang"] == lang]
    return jsonify(exs)

@app.route("/api/quiz/random")
def get_quiz():
    lang  = request.args.get("lang")
    count = int(request.args.get("count", 8))
    pool  = [q for q in QUIZZES if q["lang"] == lang] if lang else QUIZZES
    selected = random.sample(pool, min(count, len(pool)))
    clean = [{k:v for k,v in q.items() if k != "ans"} for q in selected]
    return jsonify({"questions":clean, "ids":[q["id"] for q in selected]})

@app.route("/api/quiz/check", methods=["POST"])
def check_quiz():
    data = request.json
    answers = data.get("answers", {})
    correct = 0
    results = []
    for qid, user_ans in answers.items():
        q = next((x for x in QUIZZES if x["id"] == qid), None)
        if q:
            ok = (user_ans == q["ans"])
            if ok: correct += 1
            results.append({"id":qid,"correct":ok,"right_answer":q["ans"],"explanation":q["exp"]})
    p = load_progress()
    p["quizzes_taken"] = p.get("quizzes_taken",0) + 1
    p["quiz_correct"]  = p.get("quiz_correct",0)  + correct
    p["xp"]    = p.get("xp",0) + correct * 20
    p["level"] = p["xp"] // 500 + 1
    save_progress(p)
    return jsonify({"correct":correct,"total":len(answers),"results":results})

@app.route("/api/progress", methods=["GET","POST"])
def progress():
    if request.method == "GET": return jsonify(load_progress())
    data = request.json
    p    = load_progress()
    if data.get("action") == "complete_lesson":
        lid = data["lesson_id"]
        if lid not in p.get("lessons",[]):
            p.setdefault("lessons",[]).append(lid)
            p["xp"] = p.get("xp",0) + 50
            p["level"] = p["xp"] // 500 + 1
    elif data.get("action") == "complete_exercise":
        eid = data["exercise_id"]
        if eid not in p.get("exercises",[]):
            p.setdefault("exercises",[]).append(eid)
            p["xp"] = p.get("xp",0) + 100
            p["level"] = p["xp"] // 500 + 1
    save_progress(p)
    return jsonify(p)

@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    try:
        import anthropic
        if not API_KEY:
            return jsonify({"response":"Configure a API_KEY no server.py para usar a IA!\n\nEnquanto isso, explore as licoes e exercicios!", "offline":True})
        client = anthropic.Anthropic(api_key=API_KEY)
        msgs   = request.json.get("messages",[])
        resp   = client.messages.create(
            model="claude-opus-4-6", max_tokens=1024,
            system="Voce e o CodeMaster AI, tutor de Python, JavaScript e Java. Responda em portugues brasileiro, seja didatico e use emojis ocasionalmente.",
            messages=msgs[-12:]
        )
        return jsonify({"response":resp.content[0].text,"offline":False})
    except ImportError:
        return jsonify({"response":"Instale o pacote anthropic:\npip install anthropic","offline":True})
    except Exception as e:
        return jsonify({"response":f"Erro: {str(e)}","offline":True})

if __name__ == "__main__":
    print("\n╔══════════════════════════════════════╗")
    print("║   CodeMaster Pro — Servidor Ativo    ║")
    print("║   http://localhost:5000              ║")
    print("╚══════════════════════════════════════╝")
    print("Abrindo o Chrome: localhost:5000\n")
