#!/usr/bin/env python3
"""
Gestão Familiar — Monitor Android
Uso:
  python monitor.py           → modo normal
  python monitor.py --debug   → mostra TODAS as notificações (mesmo sem valor)
  python monitor.py --test    → envia transação de teste sem precisar de notificação
  python monitor.py --config  → reconfigurar UID e Token
"""

import subprocess, json, re, time, os, sys
import urllib.request

WEBHOOK_URL = "https://webhook-petxgwxf5a-uc.a.run.app"
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".gestao_config")
INTERVALO   = 5
VALOR_MIN   = 0.50

# ── Config ────────────────────────────────────────────────────────
def carregar_config(forcar=False):
    cfg = {}
    if not forcar and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}

    uid   = cfg.get("uid","").strip()
    token = cfg.get("token","").strip()

    if not uid or not token or forcar:
        print("\n╔══════════════════════════════════════╗")
        print("║   Gestão Familiar — Configuração     ║")
        print("╚══════════════════════════════════════╝")
        print("\nAbra o app → Ajustes → copie os valores:\n")
        uid   = input("  UID Firebase : ").strip()
        token = input("  Token        : ").strip()
        if not uid or not token:
            print("❌ UID e Token são obrigatórios."); exit(1)
        with open(CONFIG_FILE, "w") as f:
            json.dump({"uid": uid, "token": token}, f)
        print(f"\n✅ Salvo em {CONFIG_FILE}\n")

    return uid, token

# ── Webhook ───────────────────────────────────────────────────────
def enviar(uid, token, tipo, valor, descricao, banco="Automático"):
    payload = json.dumps({
        "uid": uid, "token": token,
        "tipo": tipo, "valor": valor,
        "descricao": descricao[:100],
        "banco": banco,
        "categoria": "💰 Automático" if tipo == "Receita" else "💸 Automático",
        "fonte": "android-termux"
    }).encode()
    req = urllib.request.Request(
        WEBHOOK_URL, data=payload, method="POST",
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            resp = json.loads(r.read())
            ok = resp.get("success")
            print(f"  {'✅' if ok else '⚠️ '} {tipo} R${valor:.2f} | {descricao[:45]} | {banco}")
            return ok
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ❌ HTTP {e.code}: {body}")
        return False
    except Exception as e:
        print(f"  ❌ Erro de rede: {e}")
        return False

def testar_webhook(uid, token):
    print("\n🔌 Testando conexão com webhook...")
    ok = enviar(uid, token, "Despesa", 0.01, "Teste de conexão Termux", "Teste")
    if ok:
        print("   Webhook OK! Verifique o app — deve ter aparecido R$0,01.\n")
    else:
        print("   Falha. Verifique UID e Token em Ajustes.\n")
    return ok

# ── Padrões ───────────────────────────────────────────────────────
# Cobre: Pix recebido/enviado, compra débito, transferência, TED/DOC
PADROES_REC = [
    r"(?:recebeu|recebido|creditado|cr[eé]dito)[^\d]{0,30}R?\$?\s*(\d[\d.]*[,]\d{2})",
    r"R?\$\s*(\d[\d.]*[,]\d{2})[^\d]{0,20}(?:recebido|creditado|cr[eé]dito)",
    r"pix[^\d]{0,30}(\d[\d.]*[,]\d{2})[^\d]{0,20}(?:recebido|para voc|crédito)",
    r"dep[oó]sito[^\d]{0,20}R?\$?\s*(\d[\d.]*[,]\d{2})",
    r"entrada[^\d]{0,20}R?\$?\s*(\d[\d.]*[,]\d{2})",
    r"ted recebida[^\d]{0,20}R?\$?\s*(\d[\d.]*[,]\d{2})",
]
PADROES_DES = [
    r"(?:compra|d[eé]bito|pix enviado|pix de|pagamento|cobrado|debitado|saiu)[^\d]{0,30}R?\$?\s*(\d[\d.]*[,]\d{2})",
    r"R?\$\s*(\d[\d.]*[,]\d{2})[^\d]{0,20}(?:debitado|cobrado|pago|enviado|saiu)",
    r"voc[eê] (?:enviou|pagou|fez)[^\d]{0,30}(\d[\d.]*[,]\d{2})",
    r"transfer[eê]ncia[^\d]{0,20}R?\$?\s*(\d[\d.]*[,]\d{2})[^\d]{0,20}(?:enviada|realizada|efetuada)",
]
BANCOS_PKG = {
    "nubank": "Nubank", "bradesco": "Bradesco", "itau": "Itaú",
    "caixa": "Caixa", "bancobrasil": "Banco do Brasil", "bb": "Banco do Brasil",
    "santander": "Santander", "inter": "Banco Inter", "c6bank": "C6 Bank",
    "picpay": "PicPay", "mercadopago": "Mercado Pago", "pagseguro": "PagSeguro",
    "next": "Next", "original": "Banco Original", "neon": "Neon",
}

def extrair(texto):
    t = texto.lower()
    for p in PADROES_REC:
        m = re.search(p, t, re.I)
        if m:
            try:
                v = float(m.group(1).replace(".", "").replace(",", "."))
                if v >= VALOR_MIN: return "Receita", v
            except: pass
    for p in PADROES_DES:
        m = re.search(p, t, re.I)
        if m:
            try:
                v = float(m.group(1).replace(".", "").replace(",", "."))
                if v >= VALOR_MIN: return "Despesa", v
            except: pass
    return None, None

def banco_do_pkg(pkg, titulo):
    s = (pkg + " " + titulo).lower().replace(".", "").replace("_", "")
    for k, v in BANCOS_PKG.items():
        if k in s: return v
    return "Automático"

# ── Monitor ───────────────────────────────────────────────────────
def monitorar(uid, token, debug=False):
    print(f"\n🤖 Monitor ativo — UID: {uid[:8]}...")
    print(f"   Debug: {'SIM (mostra tudo)' if debug else 'NÃO'}")
    print("   Aguardando notificações bancárias... (Ctrl+C para parar)\n")

    # Verifica permissão logo no início
    try:
        r = subprocess.run(["termux-notification-list"], capture_output=True, text=True, timeout=8)
        raw = (r.stdout or "").strip()
        if not raw:
            print("\n   ❌ PERMISSÃO DE NOTIFICAÇÃO NÃO CONCEDIDA.")
            print("   ──────────────────────────────────────────────")
            print("   Faça isso AGORA no Android:")
            print("   1. Abra: Configurações → Apps")
            print("   2. Toque nos 3 pontos → Acesso especial")
            print("   3. Acesso a notificações")
            print("   4. Encontre 'Termux:API' e ATIVE")
            print("   5. Volte aqui e rode novamente\n")
            print("   ⚠️  Se não aparecer 'Termux:API' na lista,")
            print("   instale o app 'Termux:API' no F-Droid.\n")
            exit(1)
        notifs = json.loads(raw)
        print(f"   📋 {len(notifs)} notificação(ões) visível(eis) agora.")
        if len(notifs) == 0:
            print("   (Nenhuma no momento — monitor vai aguardar novas)\n")
    except FileNotFoundError:
        print("\n   ❌ termux-notification-list não encontrado!")
        print("   Execute: pkg install termux-api\n")
        exit(1)
    except Exception as e:
        print(f"   ⚠️  Erro ao listar notificações: {e}\n")

    vistos = set()

    while True:
        try:
            r = subprocess.run(["termux-notification-list"], capture_output=True, text=True, timeout=8)
            raw = (r.stdout or "").strip()
            if not raw:
                if debug: print("[AVISO] termux-notification-list retornou vazio. Verifique permissão de notificações.")
                time.sleep(INTERVALO); continue
            notifs = json.loads(raw)

            for n in notifs:
                nid = f"{n.get('id','')}_{n.get('when',0)}"
                if nid in vistos: continue
                vistos.add(nid)

                titulo = str(n.get("title","") or "")
                corpo  = str(n.get("content","") or n.get("body","") or "")
                pkg    = str(n.get("packageName","") or "")
                texto  = f"{titulo} {corpo}"

                tipo, valor = extrair(texto)

                if debug:
                    print(f"[NOTIF] {pkg[:25]:25} | {texto[:70]}")
                    if tipo:
                        print(f"         → {tipo} R${valor:.2f}")

                if tipo and valor:
                    banco = banco_do_pkg(pkg, titulo)
                    desc  = f"{titulo}: {corpo}".strip(": ").strip()
                    if not debug:
                        print(f"📲 Nova: {tipo} R${valor:.2f} — {desc[:45]}")
                    enviar(uid, token, tipo, valor, desc, banco)

            if len(vistos) > 600:
                vistos = set(list(vistos)[-200:])

        except Exception as e:
            if debug: print(f"[ERR] {e}")

        time.sleep(INTERVALO)

# ── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]

    if "--config" in args:
        carregar_config(forcar=True)
        exit(0)

    uid, token = carregar_config()

    if "--test" in args:
        testar_webhook(uid, token)
        exit(0)

    debug = "--debug" in args
    monitorar(uid, token, debug=debug)
