const mongoose = require("mongoose");

mongoose.connect("mongodb+srv://romaurocruz2_db_user:IvAlA43mIQQa1sAc@cluster0.0mvwde9.mongodb.net/agendamentos")
.then(() => console.log("MongoDB conectado"))
.catch(err => console.log(err));const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static("public"));

// banco simples (memória)
let agendamentos = [];

// criar agendamento
app.post("/agendar", (req, res) => {
  const { nome, profissional, servico, data, horario } = req.body;

  const novo = {
    id: Date.now(),
    nome,
    profissional,
    servico,
    data,
    horario
  };

  agendamentos.push(novo);

  res.json({ ok: true, message: "Agendamento criado com sucesso" });
});

// listar agendamentos
app.get("/agendamentos", (req, res) => {
  res.json(agendamentos);
});

// painel admin
app.get("/admin", (req, res) => {
  res.json({
    total: agendamentos.length,
    agendamentos
  });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log("Servidor rodando na porta " + PORT);
});
