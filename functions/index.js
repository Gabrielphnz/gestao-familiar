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

  const valorNum = parseFloat(String(valor).replace(",", "."));
  if (isNaN(valorNum) || valorNum <= 0) {
    res.status(400).json({ error: "Valor inválido" });
    return;
  }

  const tipoNorm = tipo === "Receita" ? "Receita" : "Despesa";
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
