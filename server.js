const express = require("express");
const cors = require("cors");
const sqlite3 = require("sqlite3").verbose();
const bcrypt = require("bcrypt");

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static("public"));

const DB = 'database.db';

// ---------------- DATABASE ----------------
function init_db() {
  const db = new sqlite3.Database(DB);

  db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS professionals (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS services (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT,
      price TEXT,
      duration TEXT
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS appointments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nome TEXT,
      whatsapp TEXT,
      profissional TEXT,
      servico TEXT,
      data TEXT,
      hora TEXT,
      status TEXT DEFAULT 'Agendado'
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS blocked (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      profissional TEXT,
      data TEXT,
      hora TEXT
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS admin (
      email TEXT, 
      password TEXT
    )`);

    db.get("SELECT COUNT(*) AS count FROM admin", (err, row) => {
      if (row.count === 0) {
        const password = bcrypt.hashSync("admin123", 10);
        db.run("INSERT INTO admin (email, password) VALUES (?, ?)", ["admin@ronamy.com", password]);
      }
    });

    db.get("SELECT COUNT(*) AS count FROM professionals", (err, row) => {
      if (row.count === 0) {
        const professionals = ["Larissa Magna", "Selvina", "Ronamy"];
        professionals.forEach((name) => {
          db.run("INSERT INTO professionals (name) VALUES (?)", [name]);
        });
      }
    });

    db.get("SELECT COUNT(*) AS count FROM services", (err, row) => {
      if (row.count === 0) {
        const services = [
          ["Corte feminino", "50", "30 min"],
          ["Escova", "40", "30 min"]
        ];
        services.forEach(([name, price, duration]) => {
          db.run("INSERT INTO services (name, price, duration) VALUES (?, ?, ?)", [name, price, duration]);
        });
      }
    });
  });

  db.close();
}

init_db();

// ---------------- LOGIN ----------------
const ADMIN_USER = "admin@ronamy.com";
const ADMIN_PASS = "admin123";

app.post("/login", (req, res) => {
  const { user, pass } = req.body;

  if (user === ADMIN_USER && pass === ADMIN_PASS) {
    res.json({ ok: true });
  } else {
    res.json({ ok: false });
  }
});

// ---------------- AGENDAMENTOS ----------------
app.post("/agendar", (req, res) => {
  const { nome, whatsapp, profissional, servico, data, hora } = req.body;

  const db = new sqlite3.Database(DB);

  db.get("SELECT * FROM appointments WHERE profissional = ? AND data = ? AND hora = ?", [profissional, data, hora], (err, row) => {
    if (row) {
      return res.json({ ok: false, message: "Horário já agendado!" });
    }

    db.run("INSERT INTO appointments (nome, whatsapp, profissional, servico, data, hora) VALUES (?, ?, ?, ?, ?, ?)",
      [nome, whatsapp, profissional, servico, data, hora], (err) => {
        if (err) {
          return res.json({ ok: false, message: "Erro ao agendar." });
        }
        res.json({ ok: true, message: "Agendamento feito com sucesso!" });
      });
  });

  db.close();
});

app.get("/agendamentos", (req, res) => {
  const db = new sqlite3.Database(DB);

  db.all("SELECT * FROM appointments", (err, rows) => {
    if (err) {
      return res.json({ ok: false, message: "Erro ao carregar agendamentos." });
    }
    res.json(rows);
  });

  db.close();
});

// ---------------- ADMIN ----------------
app.get("/admin", (req, res) => {
  res.sendFile(__dirname + "/public/admin.html");
});

// ---------------- INICIAR SERVIDOR ----------------
const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});
