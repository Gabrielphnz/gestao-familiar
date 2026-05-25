#!/data/data/com.termux/files/usr/bin/bash
# =============================================================
#  Gestão Familiar — Monitor Android (Termux)
#  Execute no Termux: curl -fsSL <URL_RAW> | bash
# =============================================================
set -e

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   Gestão Familiar – Monitor Android  ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Dependências
echo "📦 Instalando dependências..."
pkg update -y -q
pkg install -y python termux-api 2>/dev/null
pip install requests 2>/dev/null

# Baixa o monitor
DEST="$HOME/gestao-monitor.py"
cp "$(dirname "$0")/monitor.py" "$DEST" 2>/dev/null || \
  curl -fsSL "https://raw.githubusercontent.com/Gabrielphnz/gestao-familiar/main/companion/android/monitor.py" -o "$DEST"

chmod +x "$DEST"

# Auto-inicialização com Termux:Boot
mkdir -p "$HOME/.termux/boot"
cat > "$HOME/.termux/boot/gestao.sh" << 'BOOT'
#!/data/data/com.termux/files/usr/bin/bash
sleep 8
python $HOME/gestao-monitor.py >> $HOME/gestao-monitor.log 2>&1 &
BOOT
chmod +x "$HOME/.termux/boot/gestao.sh"

echo ""
echo "✅  Instalação concluída!"
echo ""
echo "👉  PRÓXIMOS PASSOS:"
echo "    1. Abra o app Gestão Familiar"
echo "    2. Vá em Ajustes → Token de Integração → Copiar UID"
echo "    3. Edite o monitor:  nano ~/gestao-monitor.py"
echo "    4. Cole seu UID e Token nas variáveis no topo do arquivo"
echo "    5. Execute:  python ~/gestao-monitor.py"
echo ""
echo "    Para rodar em segundo plano:"
echo "    nohup python ~/gestao-monitor.py &"
echo ""
