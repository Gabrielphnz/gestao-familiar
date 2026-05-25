const { onRequest } = require("firebase-functions/v2/https");
const { initializeApp }  = require("firebase-admin/app");
const { getFirestore, FieldValue } = require("firebase-admin/firestore");

initializeApp();
const db = getFirestore();

/**
 * POST /webhook
 * Body: { uid, token, tipo, valor, descricao, categoria?, banco?, fonte? }
 */
exports.webhook = onRequest({ cors: true, region: "us-central1", invoker: "public" }, async (req, res) => {
  res.set("Access-Control-Allow-Origin", "*");
  res.set("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") { res.status(204).send(""); return; }
  if (req.method !== "POST")    { res.status(405).json({ error: "Método não permitido" }); return; }

  const { uid, token, tipo, valor, descricao, categoria, banco, fonte } = req.body || {};

  if (!uid || !token || valor === undefined) {
    res.status(400).json({ error: "uid, token e valor são obrigatórios" });
    return;
  }

  // Valida token contra Firestore
  const configSnap = await db.doc(`usuarios/${uid}/configuracoes/geral`).get();
  if (!configSnap.exists) {
    res.status(404).json({ error: "Usuário não encontrado" });
    return;
  }
  const config = configSnap.data();
  if (!config.webhookToken || config.webhookToken !== token) {
    res.status(401).json({ error: "Token inválido ou expirado" });
    return;
  }

  // Tenta usar valor enviado; se inválido, extrai da descrição
  let valorNum = parseFloat(String(valor).replace(",", "."));
  let tipoNorm = tipo === "Receita" ? "Receita" : "Despesa";

  if (isNaN(valorNum) || valorNum <= 0) {
    const txt = String(descricao || "").toLowerCase();
    // Procura padrão R$ X,YZ ou R$ X.YYY,YZ
    const m = txt.match(/r?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})/i) || txt.match(/(\d+,\d{2})/) || txt.match(/(\d+\.\d{2})/);
    if (m) {
      const raw = m[1].replace(/\./g, "").replace(",", ".");
      valorNum = parseFloat(raw);
    }
    // Auto-detecta tipo se não informado
    if (!tipo) {
      const recPalavras = ["recebeu", "recebido", "creditad", "crédito", "credito", "depósito", "deposito", "pix recebido", "estorno"];
      const desPalavras = ["enviado", "pagamento", "compra", "débito", "debito", "cobrado", "pix enviado", "pagou", "debitado"];
      if (recPalavras.some(p => txt.includes(p))) tipoNorm = "Receita";
      else if (desPalavras.some(p => txt.includes(p))) tipoNorm = "Despesa";
    }
  }

  if (isNaN(valorNum) || valorNum <= 0) {
    res.status(400).json({ error: "Valor inválido e não foi possível extrair da descrição" });
    return;
  }
  const timestamp = Date.now();

  const lancamento = {
    tipo:      tipoNorm,
    valor:     valorNum,
    categoria: categoria || (tipoNorm === "Receita" ? "💰 Automático" : "💸 Automático"),
    banco:     banco     || "Automático",
    texto:     String(descricao || "Lançamento automático").slice(0, 100),
    timestamp,
    fonte:     fonte || "webhook",
    createdAt: FieldValue.serverTimestamp(),
  };

  await db.doc(`usuarios/${uid}/lancamentos/${timestamp}`).set(lancamento);

  res.status(200).json({
    success: true,
    id: String(timestamp),
    mensagem: `${tipoNorm} de R$${valorNum.toFixed(2)} registrada com sucesso`,
  });
});
