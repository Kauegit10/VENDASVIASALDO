import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            saldo REAL DEFAULT 0,
            compras TEXT DEFAULT ''
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT,
            usuario TEXT,
            senha TEXT,
            preco REAL
        )
    """)
    conn.commit()

def criar_usuario(user_id, username):
    cursor.execute("INSERT OR IGNORE INTO usuarios (id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()

def get_saldo(username):
    cursor.execute("SELECT saldo FROM usuarios WHERE username = ?", (username,))
    row = cursor.fetchone()
    return row[0] if row else None

def atualizar_saldo(username, valor):
    cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE username = ?", (valor, username))
    conn.commit()

def get_usuario(username):
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
    return cursor.fetchone()

def listar_categorias():
    cursor.execute("SELECT DISTINCT categoria FROM contas")
    return [row[0] for row in cursor.fetchall()]

def listar_contas_por_categoria(categoria):
    cursor.execute("SELECT id, usuario, preco FROM contas WHERE categoria = ?", (categoria,))
    return cursor.fetchall()

def comprar_conta(username, conta_id):
    saldo = get_saldo(username)
    cursor.execute("SELECT preco, usuario, senha FROM contas WHERE id = ?", (conta_id,))
    row = cursor.fetchone()
    if not row:
        return "Conta não encontrada.", None
    preco, usuario, senha = row
    if saldo < preco:
        return "Saldo insuficiente.", None
    atualizar_saldo(username, -preco)
    cursor.execute("DELETE FROM contas WHERE id = ?", (conta_id,))
    conn.commit()
    return "Compra realizada com sucesso!", f"Usuário: {usuario}\nSenha: {senha}"

def adicionar_conta(categoria, usuario, senha, preco):
    cursor.execute("INSERT INTO contas (categoria, usuario, senha, preco) VALUES (?, ?, ?, ?)",
                   (categoria, usuario, senha, preco))
    conn.commit()
