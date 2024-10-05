from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'mysecretkey'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DATABASE'] = 'produtos_db'

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DATABASE']
        )
        if conn.is_connected():
            return conn
    except Error as e:
        flash(f'Erro ao conectar ao banco de dados: {e}', 'error')
    return None

@app.route('/')
def index():
    if 'loggedin' in session:
        conn = get_db_connection()
        if not conn:
            return redirect(url_for('login'))
        cursor = conn.cursor(dictionary=True) 
        cursor.execute('SELECT * FROM categorias')
        categorias = cursor.fetchall()
        cursor.execute('SELECT * FROM produtos')
        produtos = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('index.html', categorias=categorias, produtos=produtos)
    else:
        return redirect(url_for('login'))

@app.route("/compra")
def compra():
    return render_template("compra.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        if not conn:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return render_template('login.html')
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['loggedin'] = True
            session['username'] = user['username']
            
            # Verifica se é o administrador
            if user['username'] == 'admin':
                return redirect(url_for('backoffice'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
    return render_template('login.html')



@app.route('/usuarios')
def usuarios():
    if 'loggedin' in session:
        conn = get_db_connection()
        if not conn:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return redirect(url_for('login'))
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users')
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('usuarios.html', usuarios=usuarios)
    else:
        return redirect(url_for('login'))
@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'loggedin' in session:
        conn = get_db_connection()
        if not conn:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return redirect(url_for('login'))
        
        cursor = conn.cursor(dictionary=True)
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            morada = request.form.get('morada')
            endereco = request.form.get('endereco')
            password = request.form.get('password')
            
            cursor.execute(
                'UPDATE users SET username = %s, email = %s, morada = %s, endereco = %s, password = %s WHERE id = %s',
                (username, email, morada, endereco, password, id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('usuarios'))

        cursor.execute('SELECT * FROM users WHERE id = %s', (id,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        if usuario:
            return render_template('editar_usuario.html', usuario=usuario)
        else:
            flash('Usuário não encontrado', 'error')
            return redirect(url_for('usuarios'))
    else:
        return redirect(url_for('login'))
@app.route('/remover_usuario/<int:id>')
def remover_usuario(id):
    if 'loggedin' in session:
        conn = get_db_connection()
        if not conn:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return redirect(url_for('login'))
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = %s', (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('usuarios'))
    else:
        return redirect(url_for('login'))

@app.route('/criar_perfil', methods=['GET', 'POST'])
def criar_perfil():
    if 'loggedin' in session:
        user_id = session['user_id']     
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            nome = request.form.get('nome')
            email = request.form.get('email')
            morada = request.form.get('morada')
            endereco = request.form.get('endereco')
            foto_perfil = request.form.get('foto_perfil')
            cartao_numero = request.form.get('cartao_numero')
            cartao_validade = request.form.get('cartao_validade')
            cartao_cvv = request.form.get('cartao_cvv')

            cursor.execute(
                'UPDATE users SET nome = %s, email = %s, morada = %s, endereco = %s, foto_perfil = %s, cartao_numero = %s, cartao_validade = %s, cartao_cvv = %s WHERE id = %s',
                (nome, email, morada, endereco, foto_perfil, cartao_numero, cartao_validade, cartao_cvv, user_id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('criar_perfil'))

        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('criar_perfil.html', usuario=usuario)
    else:
        return redirect(url_for('login'))
@app.route('/perfil')
def perfil():
    if 'loggedin' in session:
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('perfil.html', usuario=usuario)
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        morada = request.form['morada']
        endereco = request.form['endereco']
        password = request.form['password']

        conn = get_db_connection() 
        if not conn:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return render_template('register.html')

        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email))
        user = cursor.fetchone()
        if user:
            cursor.close()
            conn.close()
            flash('Usuário ou email já existe.', 'error')
            return render_template('register.html')
        
        cursor.execute(
            'INSERT INTO users (username, email, morada, endereco, password) VALUES (%s, %s, %s, %s, %s)',
            (username, email, morada, endereco, password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/categoria/<int:categoria_id>')
def categoria(categoria_id):
    if 'loggedin' in session:
        conn = get_db_connection()
        if not conn:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return redirect(url_for('login'))
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM categorias WHERE id = %s', (categoria_id,))
        categoria = cursor.fetchone()
        cursor.execute('SELECT * FROM produtos WHERE categoria_id = %s', (categoria_id,))
        produtos = cursor.fetchall()
        cursor.close()
        conn.close()
        if categoria:
            return render_template('categoria.html', categoria=categoria, produtos=produtos)
        else:
            flash('Categoria não encontrada', 'error')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/subcategoria/<int:subcategoria_id>')
def subcategoria(subcategoria_id):
    if 'loggedin' in session:
        conn = get_db_connection()
        if not conn:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return redirect(url_for('login'))
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM subcategorias WHERE id = %s', (subcategoria_id,))
        subcategoria = cursor.fetchone()
        cursor.execute('SELECT * FROM produtos WHERE subcategoria_id = %s', (subcategoria_id,))
        produtos = cursor.fetchall()
        cursor.close()
        conn.close()
        if subcategoria:
            return render_template('subcategoria.html', subcategoria=subcategoria, produtos=produtos)
        else:
            flash('Subcategoria não encontrada', 'error')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/backoffice', methods=['GET', 'POST'])
def backoffice():
    if 'loggedin' in session:
        conn = get_db_connection()
        if not conn:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return redirect(url_for('login'))
        cursor = conn.cursor(dictionary=True)
        if request.method == 'POST':
            nome = request.form.get('nome')
            descricao = request.form.get('descricao')
            preco = request.form.get('preco')
            categoria_id = request.form.get('categoria_id')
            subcategoria_id = request.form.get('subcategoria_id')  # Adiciona a subcategoria
            imagem_url = request.form.get('imagem_url')

            cursor.execute(
                'INSERT INTO produtos (nome, descricao, preco, categoria_id, subcategoria_id, imagem_url) VALUES (%s, %s, %s, %s, %s, %s)',
                (nome, descricao, preco, categoria_id, subcategoria_id, imagem_url)
            )
            conn.commit()

        cursor.execute('SELECT * FROM categorias')
        categorias = cursor.fetchall()
        cursor.execute('SELECT * FROM subcategorias')
        subcategorias = cursor.fetchall()  # Adiciona a recuperação das subcategorias
        cursor.execute('SELECT * FROM produtos')
        produtos = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('backoffice.html', categorias=categorias, subcategorias=subcategorias, produtos=produtos)
    else:
        return redirect(url_for('login'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'loggedin' in session:
        conn = get_db_connection()
        if not conn:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return redirect(url_for('login'))
        cursor = conn.cursor(dictionary=True)
        if request.method == 'POST':
            nome = request.form.get('nome')
            descricao = request.form.get('descricao')
            preco = request.form.get('preco')
            categoria_id = request.form.get('categoria_id')
            imagem_url = request.form.get('imagem_url')

            cursor.execute(
                'UPDATE produtos SET nome = %s, descricao = %s, preco = %s, categoria_id = %s, imagem_url = %s WHERE id = %s',
                (nome, descricao, preco, categoria_id, imagem_url, id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('backoffice'))

        cursor.execute('SELECT * FROM produtos WHERE id = %s', (id,))
        produto = cursor.fetchone()
        cursor.execute('SELECT * FROM categorias')
        categorias = cursor.fetchall()
        cursor.close()
        conn.close()
        if produto:
            return render_template('editar.html', produto=produto, categorias=categorias)
        else:
            flash('Produto não encontrado', 'error')
            return redirect(url_for('backoffice'))
    else:
        return redirect(url_for('login'))

@app.route('/remover/<int:id>')
def remover(id):
    if 'loggedin' in session:
        conn = get_db_connection()
        if not conn:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return redirect(url_for('login'))
        
        cursor = conn.cursor()
        
        # Primeiro, remove o produto de todos os carrinhos
        cursor.execute('DELETE FROM carrinho WHERE produto_id = %s', (id,))
        
        # Depois, remove o produto
        cursor.execute('DELETE FROM produtos WHERE id = %s', (id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Produto removido com sucesso.', 'success')
        return redirect(url_for('backoffice'))
    else:
        return redirect(url_for('login'))


@app.route('/produto/<int:id>')
def produto(id):
    if 'loggedin' in session:
        conn = get_db_connection()
        if not conn:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return redirect(url_for('login'))
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM produtos WHERE id = %s', (id,))
        produto = cursor.fetchone()
        cursor.close()
        conn.close()
        if produto:
            return render_template('product.html', produto=produto)
        else:
            flash('Produto não encontrado', 'error')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/adicionar_ao_carrinho/<int:produto_id>', methods=['POST'])
def adicionar_ao_carrinho(produto_id):
    user_id = session.get('user_id')  # Obtendo o ID do usuário da sessão

    if user_id is None:
        return redirect(url_for('login'))

    quantidade = request.form.get('quantidade', 1, type=int)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO carrinho (user_id, produto_id, quantidade) VALUES (%s, %s, %s)',
                   (user_id, produto_id, quantidade))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('carrinho'))  # Redirecionar para a página do carrinho após adicionar




@app.route('/carrinho')
def carrinho():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT produtos.nome, produtos.imagem_url, produtos.preco, carrinho.quantidade
        FROM carrinho
        JOIN produtos ON carrinho.produto_id = produtos.id
        WHERE carrinho.user_id = %s
    ''', (user_id,))
    itens_carrinho = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('carrinho.html', itens_carrinho=itens_carrinho)


@app.route('/editar_carrinho/<int:id>', methods=['POST'])
def editar_carrinho(id):
    if 'loggedin' in session:
        quantidade = int(request.form.get('quantidade', 1))

        if 'carrinho' in session and id in session['carrinho']:
            if quantidade > 0:
                session['carrinho'][id]['quantidade'] = quantidade
            else:
                session['carrinho'].pop(id)

        return redirect(url_for('carrinho'))
    else:
        return redirect(url_for('login'))

@app.route('/remover_do_carrinho/<int:id>')
def remover_do_carrinho(id):
    if 'loggedin' in session:
        if 'carrinho' in session and id in session['carrinho']:
            session['carrinho'].pop(id)
        return redirect(url_for('carrinho'))
    else:
        return redirect(url_for('login'))
@app.before_request
def track_page_views():
    if 'loggedin' in session:
        page_name = request.endpoint
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO page_views (page_name, view_count) 
            VALUES (%s, 1) 
            ON DUPLICATE KEY UPDATE view_count = view_count + 1
        ''', (page_name,))
        conn.commit()
        cursor.close()
        conn.close()

@app.route('/track_click/<string:button_name>', methods=['POST'])
def track_click(button_name):
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clicks (button_name, click_count) 
            VALUES (%s, 1) 
            ON DUPLICATE KEY UPDATE click_count = click_count + 1
        ''', (button_name,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(request.referrer)
    else:
        return redirect(url_for('login'))
@app.route('/estatisticas')
def estatisticas():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Número de visualizações de página
        cursor.execute('SELECT page_name, view_count FROM page_views')
        page_views = cursor.fetchall()

        # Número de cliques
        cursor.execute('SELECT button_name, click_count FROM clicks')
        clicks = cursor.fetchall()

        # Produtos mais vendidos
        cursor.execute('''
            SELECT produtos.nome, SUM(sales.quantity) as total_quantity
            FROM sales
            JOIN produtos ON sales.produto_id = produtos.id
            GROUP BY produtos.id
            ORDER BY total_quantity DESC
        ''')
        produtos_mais_vendidos = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('estatisticas.html', 
                               page_views=page_views, 
                               clicks=clicks, 
                               produtos_mais_vendidos=produtos_mais_vendidos)
    else:
        return redirect(url_for('login'))

    
if __name__ == '__main__':
    app.run(debug=True)