#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   Gestão Familiar — Monitor de Notificações (Android)    ║
║   Requer: Termux + Termux:API + Python                   ║
╚══════════════════════════════════════════════════════════╝

Instalação:
  1. Instale o Termux e Termux:API na Play Store / F-Droid
  2. Execute: bash setup.sh
  3. Configure UID_FIREBASE e WEBHOOK_TOKEN abaixo
"""

import subprocess, json, re, time, os

# ════════════════════════════════════════════════════
#   CONFIGURE AQUI — copie do app em Ajustes
# ════════════════════════════════════════════════════
UID_FIREBASE   = "SEU_UID_AQUI"
WEBHOOK_TOKEN  = "SEU_TOKEN_AQUI"
WEBHOOK_URL    = "https://webhook-petxgwxf5a-uc.a.run.app"
# ════════════════════════════════════════════════════

INTERVALO_SEG = 6   # verifica notificações a cada N segundos
VALOR_MINIMO  = 0.50  # ignora valores abaixo disso

# Padrões de detecção em português (bancos brasileiros)
PADROES = {
    "Despesa": [
        r"(?:compra|d[eé]bito|pix enviado|pagamento|cobrado|debitado)[^\d]*R?\$?\s*(\d[\d.]*[,]\d{2})",
        r"R?\$\s*(\d[\d.]*[,]\d{2})[^\d]*(?:debitado|cobrado|pago|enviado)",
        r"(?:compra aprovada)[^\d]*(\d[\d.]*[,]\d{2})",
    ],
    "Receita": [
        r"(?:cr[eé]dito|pix recebido|dep[oó]sito|recebeu|creditado)[^\d]*R?\$?\s*(\d[\d.]*[,]\d{2})",
        r"R?\$\s*(\d[\d.]*[,]\d{2})[^\d]*(?:creditado|recebido)",
        r"(?:pix de .+ para voc)[^\d]*(\d[\d.]*[,]\d{2})",
    ],
}

BANCOS = {
    "nubank": "Nubank", "nu ": "Nubank",
    "bradesco": "Bradesco",
    "ita[uú]": "Itaú",
    "caixa": "Caixa Econômica",
    "banco do brasil": "Banco do Brasil", "bb ": "Banco do Brasil",
    "santander": "Santander",
    "inter": "Banco Inter",
    "c6": "C6 Bank",
    "picpay": "PicPay",
    "mercado pago": "Mercado Pago",
    "pagseguro": "PagSeguro",
    "next": "Next",
    "original": "Banco Original",
}

def extrair_valor(texto):
    for tipo, padroes in PADROES.items():
        for p in padroes:
            m = re.search(p, texto, re.I | re.S)
            if m:
                raw = m.group(1).replace(".", "").replace(",", ".")
                try:
                    val = float(raw)
                    if val >= VALOR_MINIMO:
                        return tipo, val
                except ValueError:
                    pass
    return None, None

def detectar_banco(pkg, titulo):
    texto = (pkg + " " + titulo).lower()
    for k, v in BANCOS.items():
        if re.search(k, texto):
            return v
    return "Automático"

def enviar(tipo, valor, descricao, banco):
    import urllib.request
    payload = json.dumps({
        "uid":      UID_FIREBASE,
        "token":    WEBHOOK_TOKEN,
        "tipo":     tipo,
        "valor":    valor,
        "descricao": descricao[:100],
        "banco":    banco,
        "fonte":    "android-termux",
    }).encode()

    req = urllib.request.Request(
        WEBHOOK_URL, data=payload, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            r = json.loads(resp.read())
            sinal = "✅" if r.get("success") else "⚠️"
            print(f"{sinal} {tipo}: R${valor:.2f} | {descricao[:45]} | {banco}")
    except Exception as e:
        print(f"❌ Falha ao enviar: {e}")

def monitorar():
    print("\n🤖  Gestão Familiar — Monitor ativo")
    print(f"    UID   : {UID_FIREBASE[:10]}...")
    print(f"    Token : {'*' * 8}{WEBHOOK_TOKEN[-4:]}")
    print("    Aguardando notificações bancárias...\n")

    vistos = set()

    while True:
        try:
            r = subprocess.run(
                ["termux-notification-list"],
                capture_output=True, text=True, timeout=8,
            )
            notifs = json.loads(r.stdout or "[]")

            for n in notifs:
                nid = f"{n.get('id','')}_{n.get('when',0)}"
                if nid in vistos:
                    continue
                vistos.add(nid)

                titulo = str(n.get("title", "") or "")
                corpo  = str(n.get("content", "") or n.get("body", "") or "")
                pkg    = str(n.get("packageName", "") or "")
                texto  = f"{titulo} {corpo}"

                tipo, valor = extrair_valor(texto)
                if tipo and valor:
                    banco = detectar_banco(pkg, titulo)
                    desc  = f"{titulo}: {corpo}".strip(": ")
                    enviar(tipo, valor, desc, banco)

            # Limpa IDs antigos para não crescer indefinidamente
            if len(vistos) > 500:
                vistos = set(list(vistos)[-200:])

        except FileNotFoundError:
            print("⚠️  termux-notification-list não encontrado. Instale o Termux:API.")
            time.sleep(30)
        except Exception as e:
            pass

        time.sleep(INTERVALO_SEG)


if __name__ == "__main__":
    if UID_FIREBASE == "SEU_UID_AQUI" or WEBHOOK_TOKEN == "SEU_TOKEN_AQUI":
        print("\n⚠️  Configure UID_FIREBASE e WEBHOOK_TOKEN neste arquivo antes de iniciar!")
        print("    Copie em: Gestão Familiar → Ajustes → Token de Integração\n")
        exit(1)
    monitorar()
