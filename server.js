const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static("public"));

mongoose.connect("mongodb+srv://romaurocruz2_db_user:IvAlA43mIQQa1sAc@cluster0.0mvwde9.mongodb.net/agendamentos")
.then(() => console.log("MongoDB conectado"))
.catch(err => console.log(err));

// LOGIN
const ADMIN_USER = "admin";
const ADMIN_PASS = "123456";

app.post("/login", (req, res) => {
  const { user, pass } = req.body;

  if (user === ADMIN_USER && pass === ADMIN_PASS) {
    res.json({ ok: true });
  } else {
    res.json({ ok: false });
  }
});

// AGENDAMENTOS
let agendamentos = [];

app.post("/agendar", (req, res) => {
  const { nome, profissional, servico, data, horario } = req.body;

  agendamentos.push({
    id: Date.now(),
    nome,
    profissional,
    servico,
    data,
    horario
  });

  res.json({ ok: true });
});

app.get("/agendamentos", (req, res) => {
  res.json(agendamentos);
});

// ADMIN
app.get("/admin", (req, res) => {
  res.json({
    total: agendamentos.length,
    agendamentos
  });
});

// START
const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log("Servidor rodando na porta " + PORT);
});
