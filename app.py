<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ronamy — Serviços</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}" />
</head>
<body>
<div class="admin-layout">
  {% include 'sidebar.html' %}
  <div class="admin-main">
    <div class="admin-topbar">
      <div class="page-title">Gerenciar Serviços</div>
    </div>
    <div class="admin-content">

      {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}{% for cat, msg in messages %}
          <div class="flash {{ cat }}" style="margin-bottom:16px;">{{ msg }}</div>
        {% endfor %}{% endif %}
      {% endwith %}

      <!-- ADD FORM -->
      <form method="POST" action="/admin/servicos">
        <input type="hidden" name="action" value="add" />
        <div class="form-card">
          <h3>Adicionar novo serviço</h3>
          <div style="display:grid;grid-template-columns:2fr 1fr 1fr auto;gap:12px;align-items:flex-end;">
            <div class="form-group">
              <label>Nome do serviço</label>
              <input type="text" name="nome" placeholder="Ex: Selagem" required />
            </div>
            <div class="form-group">
              <label>Preço (R$)</label>
              <input type="number" name="preco" placeholder="0.00" step="0.01" min="0" required />
            </div>
            <div class="form-group">
              <label>Duração (min)</label>
              <input type="number" name="duracao_min" placeholder="30" min="5" step="5" required />
            </div>
            <div>
              <button type="submit" class="btn btn-gold">Adicionar</button>
            </div>
          </div>
        </div>
      </form>

      <!-- LIST -->
      <div class="table-card">
        <div class="table-header">
          <h3>Serviços cadastrados ({{ services | length }})</h3>
        </div>
        {% if services %}
        <table class="data-table">
          <thead>
            <tr><th>Serviço</th><th>Preço</th><th>Duração</th><th>Editar</th><th>Remover</th></tr>
          </thead>
          <tbody>
            {% for s in services %}
            <tr>
              <td><strong>{{ s.nome }}</strong></td>
              <td style="color:var(--gold);font-weight:600;">R$ {{ "%.2f"|format(s.preco) }}</td>
              <td>
                {% if s.duracao_min < 60 %}{{ s.duracao_min }}min
                {% elif s.duracao_min == 60 %}1h
                {% else %}{{ s.duracao_min // 60 }}h{% if s.duracao_min % 60 %}{{ s.duracao_min % 60 }}min{% endif %}
                {% endif %}
              </td>
              <td>
                <form method="POST" action="/admin/servicos" style="display:inline-flex;gap:6px;align-items:center;">
                  <input type="hidden" name="action" value="edit" />
                  <input type="hidden" name="id" value="{{ s.id }}" />
                  <input type="text" name="nome" value="{{ s.nome }}"
                    style="width:140px;background:var(--dark3);border:1px solid rgba(255,255,255,0.1);color:var(--white);padding:5px 8px;border-radius:6px;font-size:12px;outline:none;" />
                  <input type="number" name="preco" value="{{ s.preco }}" step="0.01"
                    style="width:70px;background:var(--dark3);border:1px solid rgba(255,255,255,0.1);color:var(--white);padding:5px 8px;border-radius:6px;font-size:12px;outline:none;" />
                  <input type="number" name="duracao_min" value="{{ s.duracao_min }}"
                    style="width:60px;background:var(--dark3);border:1px solid rgba(255,255,255,0.1);color:var(--white);padding:5px 8px;border-radius:6px;font-size:12px;outline:none;" />
                  <button type="submit" class="btn btn-outline btn-sm">Salvar</button>
                </form>
              </td>
              <td>
                <form method="POST" action="/admin/servicos"
                      onsubmit="return confirm('Remover o serviço {{ s.nome }}?')">
                  <input type="hidden" name="action" value="delete" />
                  <input type="hidden" name="id" value="{{ s.id }}" />
                  <button type="submit" class="btn btn-danger">Remover</button>
                </form>
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
        {% else %}
          <div class="empty-state">Nenhum serviço cadastrado.</div>
        {% endif %}
      </div>

    </div>
  </div>
</div>
</body>
</html>
