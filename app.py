from flask import (
    Flask, render_template, request, redirect, url_for,
    jsonify, send_from_directory, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import conectar_database
import os
import time
from functools import wraps
from datetime import datetime, date

app = Flask(__name__)

# ✅ Sessão (pra guardar user_id após login)
app.secret_key = "gestarbem_secret_key_troque_depois"

# ✅ Uploads
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# =========================
# Helpers
# =========================
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def api_login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"message": "Não autenticado"}), 401
        return fn(*args, **kwargs)
    return wrapper


def get_logged_user():
    """Busca dados básicos do usuário logado."""
    if "user_id" not in session:
        return None
    conn = conectar_database()
    if not conn:
        return None
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nome, email, telefone, semana_gestacional, foto, humor, tipo_sanguineo, idade, problemas_saude, alergias, medicamentos, contato_emergencia, info_importantes FROM users WHERE id=%s", (session["user_id"],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


# ✅ Curiosidade baseada na semana (sem random)
def curiosidade_por_semana(semana: int) -> str:
    if not semana or int(semana) <= 0:
        return "Quando você preencher sua semana gestacional, eu te mostro curiosidades certinhas por fase 💗"

    semana = int(semana)

    curiosidades = {
        "1-4": "O corpo começa a produzir o hormônio hCG, responsável por muitos sintomas iniciais. Mesmo sem barriga aparente, o corpo já passa por grandes mudanças internas.",
        5: "O coração do bebê começa a se formar. Náuseas e cansaço costumam aparecer nessa fase.",
        6: "O coração do bebê pode começar a bater. É comum sentir sensibilidade nos seios.",
        7: "O bebê já tem braços e pernas em formação. O olfato da gestante pode ficar mais sensível.",
        8: "O bebê tem aproximadamente o tamanho de um morango. Alterações de humor são normais devido aos hormônios.",
        9: "O bebê começa a se movimentar, mesmo que ainda não seja perceptível. O corpo da mãe aumenta o volume de sangue.",
        10: "Os órgãos principais do bebê já estão formados. Pode surgir mais vontade de urinar.",
        11: "O bebê já consegue abrir e fechar as mãos. Algumas gestantes sentem melhora do enjoo.",
        12: "O bebê mede cerca de 6 cm. Final do primeiro trimestre — o risco de aborto diminui bastante.",
        "13-16": "O bebê começa a sugar o dedo e a barriga pode começar a aparecer. A energia da mãe costuma aumentar.",
        17: "O bebê tem o tamanho aproximado de uma pera pequena. Algumas gestantes começam a sentir os primeiros movimentos.",
        18: "O bebê já reage a sons externos. Pode surgir dor nas costas.",
        19: "A pele do bebê é protegida por uma camada chamada vérnix. É comum sentir coceira na barriga.",
        20: "Metade da gestação! O bebê mede cerca de 25 cm e os movimentos já ficam mais evidentes.",
        "21-24": "O bebê começa a criar uma rotina de sono. A gestante pode sentir azia com mais frequência.",
        25: "O bebê reage à voz da mãe. Inchaços leves podem aparecer.",
        26: "Os olhos do bebê começam a se abrir. Pode surgir falta de ar leve.",
        27: "Início do terceiro trimestre. O bebê já reconhece vozes familiares.",
        "28-32": "O bebê ganha mais gordura corporal e os chutes ficam mais fortes. A gestante pode sentir mais cansaço.",
        30: "O bebê mede cerca de 40 cm. O útero passa a pressionar mais os órgãos internos.",
        32: "O bebê começa a se posicionar para o parto. Dormir pode ficar mais difícil.",
        "33-36": "O bebê cresce rapidamente. Pode surgir mais vontade de urinar e contrações de treinamento (Braxton Hicks) são comuns.",
        36: "O bebê está quase pronto para nascer. É normal sentir mais pressão pélvica.",
        "37-40": "O bebê é considerado a termo. O corpo da mãe se prepara para o parto. Cada dia conta para o desenvolvimento final."
    }

    if 1 <= semana <= 4:
        return curiosidades["1-4"]
    if 13 <= semana <= 16:
        return curiosidades["13-16"]
    if 21 <= semana <= 24:
        return curiosidades["21-24"]
    if 28 <= semana <= 32:
        return curiosidades["28-32"]
    if 33 <= semana <= 36:
        return curiosidades["33-36"]
    if 37 <= semana <= 40:
        return curiosidades["37-40"]

    if semana in curiosidades:
        return curiosidades[semana]

    return "Cada gestação é única — e você está indo muito bem 💗"


def buscar_proximo_compromisso(user_id: int):
    """
    Busca o compromisso futuro mais próximo na tabela appointments.
    Usa data >= hoje e, se tiver hora, ordena também pela hora.
    """
    conn = conectar_database()
    if not conn:
        return None

    cur = conn.cursor(dictionary=True)

    hoje = date.today().strftime("%Y-%m-%d")

    cur.execute("""
        SELECT titulo, data, hora, tipo, observacao
        FROM appointments
        WHERE user_id=%s AND data >= %s
        ORDER BY data ASC, (hora IS NULL) ASC, hora ASC
        LIMIT 1
    """, (user_id, hoje))

    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def formatar_compromisso_ptbr(row):
    if not row:
        return "Sem compromissos marcados por enquanto 💗"

    titulo = (row.get("titulo") or "Compromisso").strip()
    data_db = row.get("data")  # pode ser str 'YYYY-MM-DD' ou date
    hora = row.get("hora")     # 'HH:MM' ou None

    try:
        if hasattr(data_db, "strftime"):
            data_fmt = data_db.strftime("%d/%m")
        else:
            dt = datetime.strptime(str(data_db), "%Y-%m-%d")
            data_fmt = dt.strftime("%d/%m")
    except Exception:
        data_fmt = str(data_db)

    if hora:
        return f"{titulo} • {data_fmt} às {hora}"
    return f"{titulo} • {data_fmt}"


# =========================
# Pages
# =========================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home")
@login_required
def home():
    user = get_logged_user()
    if not user:
        return redirect(url_for("login"))

    # ✅ Próximo compromisso real (appointments)
    prox_row = buscar_proximo_compromisso(user["id"])
    proximo_compromisso = formatar_compromisso_ptbr(prox_row)

    # ✅ Curiosidade fixa por semana gestacional (sem random)
    semana = user.get("semana_gestacional") or 0
    curiosidade_semana = curiosidade_por_semana(semana)

    return render_template(
        "home.html",
        user=user,
        proximo_compromisso=proximo_compromisso,
        curiosidade_semana=curiosidade_semana
    )


@app.route("/agenda")
@login_required
def agenda():
    user = get_logged_user()
    return render_template("agenda.html", user=user)


@app.route("/emergencia")
@login_required
def emergencia():
    user = get_logged_user()
    if not user:
        return redirect(url_for("login"))
    return render_template("emergencia.html", user=user)


@app.route("/documentos")
@login_required
def documentos():
    user = get_logged_user()
    return render_template("documentalizar.html", user=user)


@app.route("/listas")
@login_required
def listas():
    user = get_logged_user()
    return render_template("lista.html", user=user)


@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    user = get_logged_user()
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            nome = (request.form.get("nome") or "").strip()
            telefone = (request.form.get("telefone") or "").strip() or None
            semana = request.form.get("semana_gestacional") or None
            nova_senha = request.form.get("nova_senha") or ""
            confirmar_senha = request.form.get("confirmar_senha") or ""

            if not nome:
                flash("Nome é obrigatório", "error")
                return render_template("perfil.html", user=user)

            # Validar senha
            if nova_senha or confirmar_senha:
                if nova_senha != confirmar_senha:
                    flash("As senhas não coincidem", "error")
                    return render_template("perfil.html", user=user)
                if len(nova_senha) < 6:
                    flash("A senha deve ter no mínimo 6 caracteres", "error")
                    return render_template("perfil.html", user=user)

            # Upload de foto
            foto_path = user.get("foto")
            if 'foto' in request.files:
                file = request.files['foto']
                if file and file.filename != '':
                    original_name = file.filename
                    safe_name = secure_filename(original_name)
                    stamp = int(time.time() * 1000)
                    filename = f"perfil_u{user['id']}_{stamp}_{safe_name}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    foto_path = f"/uploads/{filename}"

            # Atualizar banco
            conn = conectar_database()
            if not conn:
                flash("Erro ao conectar no banco de dados", "error")
                return render_template("perfil.html", user=user)

            cur = conn.cursor()

            if nova_senha:
                senha_hash = generate_password_hash(nova_senha)
                cur.execute("""
                    UPDATE users
                    SET nome=%s, telefone=%s, semana_gestacional=%s, foto=%s, senha=%s
                    WHERE id=%s
                """, (nome, telefone, semana, foto_path, senha_hash, user["id"]))
            else:
                cur.execute("""
                    UPDATE users
                    SET nome=%s, telefone=%s, semana_gestacional=%s, foto=%s
                    WHERE id=%s
                """, (nome, telefone, semana, foto_path, user["id"]))

            conn.commit()
            cur.close()
            conn.close()

            flash("Perfil atualizado com sucesso!", "success")
            return redirect(url_for("perfil"))

        except Exception as e:
            flash(f"Erro ao atualizar perfil: {str(e)}", "error")
            return render_template("perfil.html", user=user)

    return render_template("perfil.html", user=user)


@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


@app.route("/login")
def login():
    return render_template("login.html")


# =========================
# Auth APIs
# =========================
@app.route("/api/cadastro", methods=["POST"])
def api_cadastro():
    try:
        data = request.get_json()
        nome = (data.get("nome") or "").strip()
        email = (data.get("email") or "").strip().lower()
        telefone = (data.get("telefone") or "").strip() or None
        semana = data.get("semana_gestacional")
        senha_raw = data.get("senha") or ""

        if not nome or not email or not senha_raw:
            return jsonify({"message": "Preencha nome, email e senha"}), 400

        senha_hash = generate_password_hash(senha_raw)

        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"message": "Email já cadastrado"}), 400

        cursor.execute("""
            INSERT INTO users (nome, email, senha, telefone, semana_gestacional)
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, email, senha_hash, telefone, semana))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Cadastro realizado com sucesso!"}), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


@app.route("/api/login", methods=["POST"])
def api_login():
    try:
        data = request.get_json()
        email = (data.get("email") or "").strip().lower()
        senha = data.get("senha") or ""

        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user or not check_password_hash(user["senha"], senha):
            return jsonify({"message": "Email ou senha incorretos"}), 401

        # ✅ cria sessão
        session["user_id"] = user["id"]

        return jsonify({
            "message": "Login realizado com sucesso!",
            "user": {
                "id": user["id"],
                "nome": user["nome"],
                "email": user["email"],
                "semana_gestacional": user.get("semana_gestacional")
            }
        }), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logout OK"}), 200


@app.route("/api/me", methods=["GET"])
@api_login_required
def api_me():
    user = get_logged_user()
    return jsonify({"user": user}), 200


# =========================
# Upload + Documents (DB)
# =========================
@app.route("/api/upload", methods=["POST"])
@api_login_required
def api_upload():
    try:
        if 'file' not in request.files:
            return jsonify({"message": "Nenhum arquivo enviado"}), 400

        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({"message": "Arquivo vazio"}), 400

        tipo = (request.form.get('tipo') or "Outros").strip() or "Outros"
        user_id = session["user_id"]

        original_name = file.filename
        safe_name = secure_filename(original_name)

        # ✅ evita sobrescrever: prefixa com user+timestamp
        stamp = int(time.time() * 1000)
        filename = f"u{user_id}_{stamp}_{safe_name}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.save(filepath)

        arquivo_url = f"/uploads/{filename}"
        mime_type = file.mimetype or None

        try:
            tamanho_bytes = os.path.getsize(filepath)
        except Exception:
            tamanho_bytes = None

        # ✅ salva no banco
        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO documents (user_id, tipo, nome_original, arquivo_url, mime_type, tamanho_bytes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, tipo, original_name, arquivo_url, mime_type, tamanho_bytes))

        conn.commit()
        doc_id = cur.lastrowid
        cur.close()
        conn.close()

        return jsonify({
            "message": "Upload realizado com sucesso",
            "id": doc_id,
            "filename": filename,
            "tipo": tipo,
            "url": arquivo_url
        }), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


@app.route("/api/documents", methods=["GET"])
@api_login_required
def api_documents_list():
    try:
        user_id = session["user_id"]
        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id, tipo, nome_original, arquivo_url, mime_type, tamanho_bytes, criado_em
            FROM documents
            WHERE user_id=%s
            ORDER BY criado_em DESC
        """, (user_id,))
        docs = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify({"documents": docs}), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


@app.route("/api/documents/<int:doc_id>", methods=["DELETE"])
@api_login_required
def api_documents_delete(doc_id):
    try:
        user_id = session["user_id"]

        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cur = conn.cursor(dictionary=True)

        # pega url pra remover arquivo (opcional)
        cur.execute("SELECT arquivo_url FROM documents WHERE id=%s AND user_id=%s", (doc_id, user_id))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return jsonify({"message": "Documento não encontrado"}), 404

        arquivo_url = row["arquivo_url"]  # /uploads/arquivo.ext
        cur.execute("DELETE FROM documents WHERE id=%s AND user_id=%s", (doc_id, user_id))
        conn.commit()

        cur.close()
        conn.close()

        # remove arquivo do disco (se existir)
        try:
            if arquivo_url and arquivo_url.startswith("/uploads/"):
                filename = arquivo_url.replace("/uploads/", "")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
        except Exception:
            pass

        return jsonify({"message": "Documento removido"}), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# =========================
# Lists + Items (DB)
# =========================
@app.route("/api/lists", methods=["GET"])
@api_login_required
def api_lists_get():
    try:
        user_id = session["user_id"]
        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id, titulo, criado_em, atualizado_em
            FROM lists
            WHERE user_id=%s
            ORDER BY atualizado_em DESC
        """, (user_id,))
        lists = cur.fetchall()

        # pega itens de cada lista
        for l in lists:
            cur.execute("""
                SELECT id, texto, concluido, ordem, criado_em
                FROM list_items
                WHERE list_id=%s
                ORDER BY ordem ASC, id ASC
            """, (l["id"],))
            l["items"] = cur.fetchall()

        cur.close()
        conn.close()
        return jsonify({"lists": lists}), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


@app.route("/api/lists", methods=["POST"])
@api_login_required
def api_lists_create():
    try:
        user_id = session["user_id"]
        data = request.get_json() or {}

        titulo = (data.get("titulo") or "").strip()
        items = data.get("items") or []

        if not titulo:
            return jsonify({"message": "Título é obrigatório"}), 400

        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cur = conn.cursor()
        cur.execute("INSERT INTO lists (user_id, titulo) VALUES (%s, %s)", (user_id, titulo))
        list_id = cur.lastrowid

        # items opcionais
        ordem = 0
        for it in items:
            texto = (it.get("texto") or it.get("text") or "").strip()
            if not texto:
                continue
            concluido = 1 if (it.get("concluido") or it.get("done")) else 0
            cur.execute("""
                INSERT INTO list_items (list_id, texto, concluido, ordem)
                VALUES (%s, %s, %s, %s)
            """, (list_id, texto, concluido, ordem))
            ordem += 1

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Lista criada", "id": list_id}), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


@app.route("/api/lists/<int:list_id>", methods=["PUT"])
@api_login_required
def api_lists_update(list_id):
    try:
        user_id = session["user_id"]
        data = request.get_json() or {}
        titulo = (data.get("titulo") or "").strip()

        if not titulo:
            return jsonify({"message": "Título é obrigatório"}), 400

        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cur = conn.cursor()
        cur.execute("""
            UPDATE lists
            SET titulo=%s
            WHERE id=%s AND user_id=%s
        """, (titulo, list_id, user_id))

        if cur.rowcount == 0:
            cur.close()
            conn.close()
            return jsonify({"message": "Lista não encontrada"}), 404

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Lista atualizada"}), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


@app.route("/api/lists/<int:list_id>", methods=["DELETE"])
@api_login_required
def api_lists_delete(list_id):
    try:
        user_id = session["user_id"]
        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cur = conn.cursor()
        cur.execute("DELETE FROM lists WHERE id=%s AND user_id=%s", (list_id, user_id))

        if cur.rowcount == 0:
            cur.close()
            conn.close()
            return jsonify({"message": "Lista não encontrada"}), 404

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Lista excluída"}), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


@app.route("/api/lists/<int:list_id>/items", methods=["POST"])
@api_login_required
def api_list_item_add(list_id):
    try:
        user_id = session["user_id"]
        data = request.get_json() or {}
        texto = (data.get("texto") or data.get("text") or "").strip()
        if not texto:
            return jsonify({"message": "Texto do item é obrigatório"}), 400

        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cur = conn.cursor(dictionary=True)

        # valida se a lista é do usuário
        cur.execute("SELECT id FROM lists WHERE id=%s AND user_id=%s", (list_id, user_id))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"message": "Lista não encontrada"}), 404

        # ordem (última + 1)
        cur.execute("SELECT COALESCE(MAX(ordem), -1) AS mx FROM list_items WHERE list_id=%s", (list_id,))
        mx = cur.fetchone()["mx"]
        ordem = (mx + 1) if mx is not None else 0

        cur2 = conn.cursor()
        cur2.execute("""
            INSERT INTO list_items (list_id, texto, concluido, ordem)
            VALUES (%s, %s, 0, %s)
        """, (list_id, texto, ordem))
        item_id = cur2.lastrowid
        conn.commit()

        cur2.close()
        cur.close()
        conn.close()

        return jsonify({"message": "Item adicionado", "id": item_id}), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


@app.route("/api/list_items/<int:item_id>", methods=["PUT"])
@api_login_required
def api_list_item_update(item_id):
    try:
        user_id = session["user_id"]
        data = request.get_json() or {}
        concluido = 1 if data.get("concluido") or data.get("done") else 0

        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cur = conn.cursor()
        # garante que pertence ao user (via join)
        cur.execute("""
            UPDATE list_items li
            JOIN lists l ON l.id = li.list_id
            SET li.concluido=%s
            WHERE li.id=%s AND l.user_id=%s
        """, (concluido, item_id, user_id))

        if cur.rowcount == 0:
            cur.close()
            conn.close()
            return jsonify({"message": "Item não encontrado"}), 404

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Item atualizado"}), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


@app.route("/api/list_items/<int:item_id>", methods=["DELETE"])
@api_login_required
def api_list_item_delete(item_id):
    try:
        user_id = session["user_id"]
        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cur = conn.cursor()
        cur.execute("""
            DELETE li FROM list_items li
            JOIN lists l ON l.id = li.list_id
            WHERE li.id=%s AND l.user_id=%s
        """, (item_id, user_id))

        if cur.rowcount == 0:
            cur.close()
            conn.close()
            return jsonify({"message": "Item não encontrado"}), 404

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Item removido"}), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


# =========================
# Appointments (DB)
# =========================
@app.route("/api/appointments", methods=["GET"])
@api_login_required
def api_appointments_get():
    """
    Query params opcionais:
      - start=YYYY-MM-DD
      - end=YYYY-MM-DD
    """
    try:
        user_id = session["user_id"]
        start = request.args.get("start")
        end = request.args.get("end")

        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cur = conn.cursor(dictionary=True)

        if start and end:
            cur.execute("""
                SELECT id, titulo, tipo, data, hora, observacao, criado_em, atualizado_em
                FROM appointments
                WHERE user_id=%s AND data BETWEEN %s AND %s
                ORDER BY data ASC, hora ASC
            """, (user_id, start, end))
        else:
            cur.execute("""
                SELECT id, titulo, tipo, data, hora, observacao, criado_em, atualizado_em
                FROM appointments
                WHERE user_id=%s
                ORDER BY data DESC, hora DESC
                LIMIT 200
            """, (user_id,))

        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"appointments": rows}), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


@app.route("/api/appointments", methods=["POST"])
@api_login_required
def api_appointments_create():
    try:
        user_id = session["user_id"]
        data = request.get_json() or {}

        titulo = (data.get("titulo") or "").strip()
        tipo = (data.get("tipo") or "").strip()
        data_d = (data.get("data") or "").strip()
        hora = data.get("hora")
        obs = data.get("observacao")

        if not titulo or not tipo or not data_d:
            return jsonify({"message": "Título, tipo e data são obrigatórios"}), 400

        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO appointments (user_id, titulo, tipo, data, hora, observacao)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, titulo, tipo, data_d, hora, obs))

        conn.commit()
        appt_id = cur.lastrowid
        cur.close()
        conn.close()

        return jsonify({"message": "Compromisso criado", "id": appt_id}), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


@app.route("/api/appointments/<int:appt_id>", methods=["PUT"])
@api_login_required
def api_appointments_update(appt_id):
    try:
        user_id = session["user_id"]
        data = request.get_json() or {}

        titulo = (data.get("titulo") or "").strip()
        tipo = (data.get("tipo") or "").strip()
        data_d = (data.get("data") or "").strip()
        hora = data.get("hora")
        obs = data.get("observacao")

        if not titulo or not tipo or not data_d:
            return jsonify({"message": "Título, tipo e data são obrigatórios"}), 400

        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cur = conn.cursor()
        cur.execute("""
            UPDATE appointments
            SET titulo=%s, tipo=%s, data=%s, hora=%s, observacao=%s
            WHERE id=%s AND user_id=%s
        """, (titulo, tipo, data_d, hora, obs, appt_id, user_id))

        if cur.rowcount == 0:
            cur.close()
            conn.close()
            return jsonify({"message": "Compromisso não encontrado"}), 404

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Compromisso atualizado"}), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


@app.route("/api/appointments/<int:appt_id>", methods=["DELETE"])
@api_login_required
def api_appointments_delete(appt_id):
    try:
        user_id = session["user_id"]

        conn = conectar_database()
        if not conn:
            return jsonify({"message": "Erro ao conectar no banco de dados"}), 500

        cur = conn.cursor()
        cur.execute("DELETE FROM appointments WHERE id=%s AND user_id=%s", (appt_id, user_id))

        if cur.rowcount == 0:
            cur.close()
            conn.close()
            return jsonify({"message": "Compromisso não encontrado"}), 404

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Compromisso excluído"}), 200

    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)