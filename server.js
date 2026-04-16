const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

// 🔥 SERVIR ARQUIVOS DO FRONT
app.use(express.static("public"));

/* ---------------- LOGIN SIMPLES ---------------- */
app.post("/login", (req, res) => {
  const { user, pass } = req.body;

  if (user === "admin" && pass === "123456") {
    return res.json({ ok: true });
  }

  return res.json({ ok: false });
});

/* ---------------- BANCO EM MEMÓRIA ---------------- */
let agendamentos = [];

/* ---------------- CRIAR AGENDAMENTO ---------------- */
app.post("/agendar", (req, res) => {
  const novo = {
    id: Date.now(),
    nome: req.body.nome,
    profissional: req.body.profissional,
    servico: req.body.servico,
    data: req.body.data,
    hora: req.body.hora
  };

  agendamentos.push(novo);

  res.json({ ok: true, message: "Agendamento criado" });
});

/* ---------------- LISTAR ---------------- */
app.get("/agendamentos", (req, res) => {
  res.json(agendamentos);
});

/* ---------------- START ---------------- */
const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log("Servidor rodando na porta " + PORT);
});
