<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ronamy — Profissionais</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}" />
</head>
<body>
<div class="admin-layout">
  {% include 'sidebar.html' %}
  <div class="admin-main">
    <div class="admin-topbar">
      <div class="page-title">Gerenciar Profissionais</div>
    </div>
    <div class="admin-content">

      {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}{% for cat, msg in messages %}
          <div class="flash {{ cat }}" style="margin-bottom:16px;">{{ msg }}</div>
        {% endfor %}{% endif %}
      {% endwith %}

      <form method="POST" action="/admin/profissionais">
        <input type="hidden" name="action" value="add" />
        <div class="form-card">
          <h3>Adicionar profissional</h3>
          <div style="display:flex;gap:12px;align-items:flex-end;">
            <div class="form-group" style="flex:1;">
              <label>Nome completo</label>
              <input type="text" name="nome" placeholder="Ex: Fernanda Lima" required />
            </div>
            <div>
              <button type="submit" class="btn btn-gold">Adicionar</button>
            </div>
          </div>
        </div>
      </form>

      <div class="table-card">
        <div class="table-header">
          <h3>Profissionais ativas ({{ professionals | length }})</h3>
        </div>
        {% if professionals %}
        <table class="data-table">
          <thead>
            <tr><th>#</th><th>Nome</th><th>Status</th><th>Ação</th></tr>
          </thead>
          <tbody>
            {% for p in professionals %}
            <tr>
              <td style="color:var(--gray);">{{ p.id }}</td>
              <td>
                <div style="display:flex;align-items:center;gap:10px;">
                  <div style="width:36px;height:36px;border-radius:50%;background:var(--gold-dark);color:var(--black);font-weight:700;font-size:14px;display:flex;align-items:center;justify-content:center;">
                    {{ p.nome[0] }}
                  </div>
                  <strong>{{ p.nome }}</strong>
                </div>
              </td>
              <td><span class="badge badge-green">Ativa</span></td>
              <td>
                <form method="POST" action="/admin/profissionais"
                      onsubmit="return confirm('Remover {{ p.nome }}? Os agendamentos existentes serão mantidos.')">
                  <input type="hidden" name="action" value="delete" />
                  <input type="hidden" name="id" value="{{ p.id }}" />
                  <button type="submit" class="btn btn-danger">Remover</button>
                </form>
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
        {% else %}
          <div class="empty-state">Nenhuma profissional cadastrada.</div>
        {% endif %}
      </div>

    </div>
  </div>
</div>
</body>
</html>
