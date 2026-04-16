from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ronamy_secret_key_2024')

DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'ronamy2024')

WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '5511999999999')

HORARIOS = [
    '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
    '11:00', '11:30', '12:00', '12:30', '13:00', '13:30',
    '14:00', '14:30', '15:00', '15:30', '16:00', '16:30',
    '17:00', '17:30', '18:00'
]


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS profissionais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        ativo INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL,
        duracao INTEGER NOT NULL,
        ativo INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nome TEXT NOT NULL,
        cliente_telefone TEXT NOT NULL,
        profissional_id INTEGER NOT NULL,
        servico_id INTEGER NOT NULL,
        data TEXT NOT NULL,
        horario TEXT NOT NULL,
        status TEXT DEFAULT 'confirmado',
        observacoes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (profissional_id) REFERENCES profissionais(id),
        FOREIGN KEY (servico_id) REFERENCES servicos(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS horarios_bloqueados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profissional_id INTEGER NOT NULL,
        data TEXT NOT NULL,
        horario TEXT NOT NULL,
        motivo TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (profissional_id) REFERENCES profissionais(id)
    )''')

    profissionais_iniciais = ['Larissa Magna', 'Selvina', 'Ronamy']
    for nome in profissionais_iniciais:
        c.execute('SELECT id FROM profissionais WHERE nome = ?', (nome,))
        if not c.fetchone():
            c.execute('INSERT INTO profissionais (nome) VALUES (?)', (nome,))

    servicos_iniciais = [
        ('Corte feminino', 50.00, 30),
        ('Escova', 40.00, 30),
        ('Hidratação', 60.00, 40),
        ('Progressiva', 150.00, 120),
        ('Alisamento', 120.00, 90),
        ('Corte + Escova', 80.00, 60),
    ]
    for nome, preco, duracao in servicos_iniciais:
        c.execute('SELECT id FROM servicos WHERE nome = ?', (nome,))
        if not c.fetchone():
            c.execute('INSERT INTO servicos (nome, preco, duracao) VALUES (?, ?, ?)', (nome, preco, duracao))

    conn.commit()
    conn.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_horarios_ocupados(profissional_id, data, servico_duracao=0, excluir_agendamento_id=None):
    conn = get_db()
    c = conn.cursor()

    c.execute('''SELECT a.horario, s.duracao FROM agendamentos a
                 JOIN servicos s ON a.servico_id = s.id
                 WHERE a.profissional_id = ? AND a.data = ? AND a.status != 'cancelado'
                 AND (? IS NULL OR a.id != ?)''',
              (profissional_id, data, excluir_agendamento_id, excluir_agendamento_id))
    agendamentos = c.fetchall()

    c.execute('SELECT horario FROM horarios_bloqueados WHERE profissional_id = ? AND data = ?',
              (profissional_id, data))
    bloqueados = [row['horario'] for row in c.fetchall()]
    conn.close()

    ocupados = set(bloqueados)

    for ag in agendamentos:
        h, m = map(int, ag['horario'].split(':'))
        inicio = h * 60 + m
        fim = inicio + ag['duracao']
        for horario in HORARIOS:
            hh, mm = map(int, horario.split(':'))
            t = hh * 60 + mm
            if inicio <= t < fim:
                ocupados.add(horario)

    return ocupados


def get_horarios_disponiveis(profissional_id, data, servico_duracao, excluir_agendamento_id=None):
    ocupados = get_horarios_ocupados(profissional_id, data, servico_duracao, excluir_agendamento_id)
    disponiveis = []
    for horario in HORARIOS:
        h, m = map(int, horario.split(':'))
        inicio = h * 60 + m
        fim = inicio + servico_duracao
        slots_necessarios = set()
        for hor in HORARIOS:
            hh, mm = map(int, hor.split(':'))
            t = hh * 60 + mm
            if inicio <= t < fim:
                slots_necessarios.add(hor)
        if not slots_necessarios.intersection(ocupados):
            disponiveis.append(horario)
    return disponiveis


@app.route('/')
def index():
    conn = get_db()
    profissionais = conn.execute('SELECT * FROM profissionais WHERE ativo = 1').fetchall()
    servicos = conn.execute('SELECT * FROM servicos WHERE ativo = 1').fetchall()
    conn.close()
    return render_template('index.html', profissionais=profissionais, servicos=servicos)


@app.route('/horarios_disponiveis')
def horarios_disponiveis():
    profissional_id = request.args.get('profissional_id')
    data = request.args.get('data')
    servico_id = request.args.get('servico_id')

    if not all([profissional_id, data, servico_id]):
        return jsonify({'horarios': []})

    conn = get_db()
    servico = conn.execute('SELECT duracao FROM servicos WHERE id = ?', (servico_id,)).fetchone()
    conn.close()

    if not servico:
        return jsonify({'horarios': []})

    disponiveis = get_horarios_disponiveis(profissional_id, data, servico['duracao'])
    return jsonify({'horarios': disponiveis})


@app.route('/agendar', methods=['POST'])
def agendar():
    nome = request.form.get('nome', '').strip()
    telefone = request.form.get('telefone', '').strip()
    profissional_id = request.form.get('profissional_id')
    servico_id = request.form.get('servico_id')
    data = request.form.get('data')
    horario = request.form.get('horario')

    if not all([nome, telefone, profissional_id, servico_id, data, horario]):
        flash('Por favor, preencha todos os campos obrigatórios.', 'error')
        return redirect(url_for('index'))

    try:
        data_obj = datetime.strptime(data, '%Y-%m-%d')
        if data_obj.date() < datetime.now().date():
            flash('Não é possível agendar para datas passadas.', 'error')
            return redirect(url_for('index'))
    except ValueError:
        flash('Data inválida.', 'error')
        return redirect(url_for('index'))

    conn = get_db()
    servico = conn.execute('SELECT * FROM servicos WHERE id = ?', (servico_id,)).fetchone()
    profissional = conn.execute('SELECT * FROM profissionais WHERE id = ?', (profissional_id,)).fetchone()

    if not servico or not profissional:
        conn.close()
        flash('Serviço ou profissional inválido.', 'error')
        return redirect(url_for('index'))

    ocupados = get_horarios_ocupados(profissional_id, data)
    if horario in ocupados:
        conn.close()
        flash('Horário não disponível. Por favor, escolha outro horário.', 'error')
        return redirect(url_for('index'))

    conn.execute('''INSERT INTO agendamentos (cliente_nome, cliente_telefone, profissional_id, servico_id, data, horario)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (nome, telefone, profissional_id, servico_id, data, horario))
    conn.commit()

    data_formatada = data_obj.strftime('%d/%m/%Y')
    mensagem_whatsapp = f"Olá! Acabei de agendar no salão Ronamy! 💛%0A%0AServiço: {servico['nome']}%0AProfissional: {profissional['nome']}%0AData: {data_formatada}%0AHorário: {horario}%0A%0AAguardo a confirmação! 😊"
    whatsapp_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={mensagem_whatsapp}"

    conn.close()
    return render_template('success.html',
                           nome=nome,
                           servico=servico['nome'],
                           profissional=profissional['nome'],
                           data=data_formatada,
                           horario=horario,
                           preco=servico['preco'],
                           whatsapp_link=whatsapp_link)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('dashboard'))
        flash('Usuário ou senha inválidos.', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))


@app.route('/admin')
@login_required
def dashboard():
    conn = get_db()
    hoje = datetime.now().strftime('%Y-%m-%d')

    agendamentos_hoje = conn.execute('''
        SELECT a.*, p.nome as profissional_nome, s.nome as servico_nome, s.preco
        FROM agendamentos a
        JOIN profissionais p ON a.profissional_id = p.id
        JOIN servicos s ON a.servico_id = s.id
        WHERE a.data = ? AND a.status != 'cancelado'
        ORDER BY a.horario
    ''', (hoje,)).fetchall()

    total_mes_row = conn.execute('''
        SELECT COUNT(*) as total, COALESCE(SUM(s.preco), 0) as faturamento
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        WHERE strftime('%Y-%m', a.data) = strftime('%Y-%m', 'now')
        AND a.status != 'cancelado'
    ''').fetchone()

    total_hoje = len(agendamentos_hoje)
    total_mes = total_mes_row['total']
    faturamento_mes = total_mes_row['faturamento']

    ultimos_30_dias = []
    for i in range(29, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        row = conn.execute('''
            SELECT COUNT(*) as total FROM agendamentos
            WHERE data = ? AND status != 'cancelado'
        ''', (d,)).fetchone()
        ultimos_30_dias.append({'data': d, 'total': row['total']})

    servicos_mais = conn.execute('''
        SELECT s.nome, COUNT(*) as total FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        WHERE a.status != 'cancelado'
        GROUP BY s.id ORDER BY total DESC LIMIT 5
    ''').fetchall()

    profissionais = conn.execute('SELECT * FROM profissionais WHERE ativo = 1').fetchall()
    servicos = conn.execute('SELECT * FROM servicos WHERE ativo = 1').fetchall()

    conn.close()
    return render_template('dashboard.html',
                           agendamentos_hoje=agendamentos_hoje,
                           total_hoje=total_hoje,
                           total_mes=total_mes,
                           faturamento_mes=faturamento_mes,
                           ultimos_30_dias=ultimos_30_dias,
                           servicos_mais=servicos_mais,
                           profissionais=profissionais,
                           servicos=servicos,
                           hoje=datetime.now().strftime('%d/%m/%Y'))


@app.route('/admin/agendamentos')
@login_required
def admin_agendamentos():
    conn = get_db()
    data_filtro = request.args.get('data', '')
    profissional_filtro = request.args.get('profissional_id', '')
    status_filtro = request.args.get('status', '')

    query = '''SELECT a.*, p.nome as profissional_nome, s.nome as servico_nome, s.preco
               FROM agendamentos a
               JOIN profissionais p ON a.profissional_id = p.id
               JOIN servicos s ON a.servico_id = s.id
               WHERE 1=1'''
    params = []

    if data_filtro:
        query += ' AND a.data = ?'
        params.append(data_filtro)
    if profissional_filtro:
        query += ' AND a.profissional_id = ?'
        params.append(profissional_filtro)
    if status_filtro:
        query += ' AND a.status = ?'
        params.append(status_filtro)

    query += ' ORDER BY a.data DESC, a.horario'
    agendamentos = conn.execute(query, params).fetchall()
    profissionais = conn.execute('SELECT * FROM profissionais WHERE ativo = 1').fetchall()
    conn.close()
    return render_template('admin_agendamentos.html',
                           agendamentos=agendamentos,
                           profissionais=profissionais,
                           data_filtro=data_filtro,
                           profissional_filtro=profissional_filtro,
                           status_filtro=status_filtro)


@app.route('/admin/agendamento/novo', methods=['GET', 'POST'])
@login_required
def novo_agendamento_admin():
    conn = get_db()
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        telefone = request.form.get('telefone', '').strip()
        profissional_id = request.form.get('profissional_id')
        servico_id = request.form.get('servico_id')
        data = request.form.get('data')
        horario = request.form.get('horario')
        observacoes = request.form.get('observacoes', '').strip()

        if not all([nome, telefone, profissional_id, servico_id, data, horario]):
            flash('Preencha todos os campos obrigatórios.', 'error')
        else:
            conn.execute('''INSERT INTO agendamentos (cliente_nome, cliente_telefone, profissional_id, servico_id, data, horario, observacoes)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (nome, telefone, profissional_id, servico_id, data, horario, observacoes))
            conn.commit()
            flash('Agendamento criado com sucesso!', 'success')
            conn.close()
            return redirect(url_for('admin_agendamentos'))

    profissionais = conn.execute('SELECT * FROM profissionais WHERE ativo = 1').fetchall()
    servicos = conn.execute('SELECT * FROM servicos WHERE ativo = 1').fetchall()
    conn.close()
    return render_template('novo_agendamento.html', profissionais=profissionais, servicos=servicos, horarios=HORARIOS)


@app.route('/admin/agendamento/<int:id>/cancelar', methods=['POST'])
@login_required
def cancelar_agendamento(id):
    conn = get_db()
    conn.execute("UPDATE agendamentos SET status = 'cancelado' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Agendamento cancelado.', 'success')
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/admin/agendamento/<int:id>/confirmar', methods=['POST'])
@login_required
def confirmar_agendamento(id):
    conn = get_db()
    conn.execute("UPDATE agendamentos SET status = 'confirmado' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Agendamento confirmado.', 'success')
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/admin/servicos')
@login_required
def manage_services():
    conn = get_db()
    servicos = conn.execute('SELECT * FROM servicos ORDER BY nome').fetchall()
    conn.close()
    return render_template('manage_services.html', servicos=servicos)


@app.route('/admin/servicos/novo', methods=['POST'])
@login_required
def novo_servico():
    nome = request.form.get('nome', '').strip()
    preco = request.form.get('preco')
    duracao = request.form.get('duracao')

    if not all([nome, preco, duracao]):
        flash('Preencha todos os campos.', 'error')
        return redirect(url_for('manage_services'))

    try:
        preco = float(preco)
        duracao = int(duracao)
    except ValueError:
        flash('Preço ou duração inválidos.', 'error')
        return redirect(url_for('manage_services'))

    conn = get_db()
    conn.execute('INSERT INTO servicos (nome, preco, duracao) VALUES (?, ?, ?)', (nome, preco, duracao))
    conn.commit()
    conn.close()
    flash('Serviço adicionado com sucesso!', 'success')
    return redirect(url_for('manage_services'))


@app.route('/admin/servicos/<int:id>/editar', methods=['POST'])
@login_required
def editar_servico(id):
    nome = request.form.get('nome', '').strip()
    preco = request.form.get('preco')
    duracao = request.form.get('duracao')
    ativo = 1 if request.form.get('ativo') else 0

    try:
        preco = float(preco)
        duracao = int(duracao)
    except ValueError:
        flash('Preço ou duração inválidos.', 'error')
        return redirect(url_for('manage_services'))

    conn = get_db()
    conn.execute('UPDATE servicos SET nome = ?, preco = ?, duracao = ?, ativo = ? WHERE id = ?',
                 (nome, preco, duracao, ativo, id))
    conn.commit()
    conn.close()
    flash('Serviço atualizado!', 'success')
    return redirect(url_for('manage_services'))


@app.route('/admin/servicos/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_servico(id):
    conn = get_db()
    conn.execute('DELETE FROM servicos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Serviço excluído.', 'success')
    return redirect(url_for('manage_services'))


@app.route('/admin/profissionais')
@login_required
def manage_professionals():
    conn = get_db()
    profissionais = conn.execute('SELECT * FROM profissionais ORDER BY nome').fetchall()
    conn.close()
    return render_template('manage_professionals.html', profissionais=profissionais)


@app.route('/admin/profissionais/novo', methods=['POST'])
@login_required
def novo_profissional():
    nome = request.form.get('nome', '').strip()
    if not nome:
        flash('Informe o nome do profissional.', 'error')
        return redirect(url_for('manage_professionals'))
    conn = get_db()
    conn.execute('INSERT INTO profissionais (nome) VALUES (?)', (nome,))
    conn.commit()
    conn.close()
    flash('Profissional adicionado com sucesso!', 'success')
    return redirect(url_for('manage_professionals'))


@app.route('/admin/profissionais/<int:id>/editar', methods=['POST'])
@login_required
def editar_profissional(id):
    nome = request.form.get('nome', '').strip()
    ativo = 1 if request.form.get('ativo') else 0
    if not nome:
        flash('Informe o nome.', 'error')
        return redirect(url_for('manage_professionals'))
    conn = get_db()
    conn.execute('UPDATE profissionais SET nome = ?, ativo = ? WHERE id = ?', (nome, ativo, id))
    conn.commit()
    conn.close()
    flash('Profissional atualizado!', 'success')
    return redirect(url_for('manage_professionals'))


@app.route('/admin/profissionais/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_profissional(id):
    conn = get_db()
    conn.execute('DELETE FROM profissionais WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Profissional excluído.', 'success')
    return redirect(url_for('manage_professionals'))


@app.route('/admin/bloqueios')
@login_required
def manage_bloqueios():
    conn = get_db()
    profissionais = conn.execute('SELECT * FROM profissionais WHERE ativo = 1').fetchall()
    bloqueios = conn.execute('''
        SELECT hb.*, p.nome as profissional_nome FROM horarios_bloqueados hb
        JOIN profissionais p ON hb.profissional_id = p.id
        WHERE hb.data >= date('now')
        ORDER BY hb.data, hb.horario
    ''').fetchall()
    conn.close()
    return render_template('manage_bloqueios.html', profissionais=profissionais, bloqueios=bloqueios, horarios=HORARIOS)


@app.route('/admin/bloqueios/novo', methods=['POST'])
@login_required
def novo_bloqueio():
    profissional_id = request.form.get('profissional_id')
    data = request.form.get('data')
    horario = request.form.get('horario')
    motivo = request.form.get('motivo', '').strip()

    if not all([profissional_id, data, horario]):
        flash('Preencha todos os campos.', 'error')
        return redirect(url_for('manage_bloqueios'))

    conn = get_db()
    existing = conn.execute('SELECT id FROM horarios_bloqueados WHERE profissional_id = ? AND data = ? AND horario = ?',
                            (profissional_id, data, horario)).fetchone()
    if existing:
        flash('Este horário já está bloqueado.', 'error')
    else:
        conn.execute('INSERT INTO horarios_bloqueados (profissional_id, data, horario, motivo) VALUES (?, ?, ?, ?)',
                     (profissional_id, data, horario, motivo))
        conn.commit()
        flash('Horário bloqueado com sucesso!', 'success')
    conn.close()
    return redirect(url_for('manage_bloqueios'))


@app.route('/admin/bloqueios/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_bloqueio(id):
    conn = get_db()
    conn.execute('DELETE FROM horarios_bloqueados WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Bloqueio removido.', 'success')
    return redirect(url_for('manage_bloqueios'))


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

with app.app_context():
    init_db()
