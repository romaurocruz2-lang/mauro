const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.send("Sistema de Agendamento Online 🚀");
});

let profissionais = [
  { id: 1, nome: "Juliana Corte & Estilo" },
  { id: 2, nome: "Amanda Beauty Hair" },
  { id: 3, nome: "Camila Tesoura de Ouro" }
];

let agendamentos = [];

app.get("/profissionais", (req, res) => {
  res.json(profissionais);
});

app.get("/agendamentos", (req, res) => {
  res.json(agendamentos);
});

app.post("/agendamentos", (req, res) => {
  const novo = req.body;
  agendamentos.push(novo);
  res.json({ message: "Agendamento criado com sucesso!" });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log("Servidor rodando na porta " + PORT);
});
