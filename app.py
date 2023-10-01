import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS


def conectar_db():
    conexao = psycopg2.connect(
        host="db-luan-rds.c4oty1gayfxe.us-east-1.rds.amazonaws.com",
        database="db_rds",
        user="professor",
        password="professor",
        port="5432",
        options="-c search_path=dbo,parte4",
    )
    return conexao

def inserir_dado(sql, values):
    conexao = conectar_db()
    cursor = conexao.cursor()
    try:
        cursor.execute(sql, values)
        conexao.commit()
        print("Registro inserido com Sucesso!")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conexao.rollback()
    finally:
        cursor.close()
        conexao.close()

def consultar_dado(sql, values):
    conexao = conectar_db()
    cursor = conexao.cursor()
    try:
        cursor.execute(sql, values)
        registro = cursor.fetchone()
        if registro is not None:
            colunas = [desc[0] for desc in cursor.description]
            registro_dict = dict(zip(colunas, registro))
            return registro_dict
        else:
            return None
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
    finally:
        cursor.close()
        conexao.close()

def deletar_dado(sql, values):
    conexao = conectar_db()
    cursor = conexao.cursor()
    try:
        cursor.execute(sql, values)
        conexao.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()

def atualizar_dado(sql, values):
    conexao = conectar_db()
    cursor = conexao.cursor()
    try:
        cursor.execute(sql, values)
        conexao.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/post/<tabela>", methods=["POST"])
def post(tabela):
    print("luan")
    data = request.json

    if not data:
        return jsonify({"message": "Dados não fornecidos"}), 400

    colunas = ", ".join(data.keys())
    valores = ", ".join(["%s"] * len(data))
    sql = f"INSERT INTO {tabela} ({colunas}) VALUES ({valores})"
    valores = list(data.values())
    inserir_dado(sql, valores)

    return jsonify({"message": "Registro inserido com sucesso"}), 201

@app.route("/get/<tabela>/<id>", methods=["GET"])
def get(tabela, id):
    if tabela == "aula_particular":
        sql = f"SELECT * FROM {tabela} WHERE cod_aula = %s"
    else:
        sql = f"SELECT * FROM {tabela} WHERE matricula = %s"

    registro = consultar_dado(sql, (id,))

    if registro is not None:
        return jsonify(registro)
    else:
        return jsonify({"message": "Registro não encontrado"}), 404

@app.route("/delete/<tabela>/<id>", methods=["DELETE"])
def delete(tabela, id):
    if tabela == "aula_particular":
        sql = f"DELETE FROM {tabela} WHERE cod_aula = %s"
    else:
        sql = f"DELETE FROM {tabela} WHERE matricula = %s"

    try:
        deletar_dado(sql, (id,))
        return jsonify({"message": "Registro excluído com sucesso"}), 200
    except Exception as error:
        print("Error: %s" % error)
        return jsonify({"message": "Erro ao excluir registro"}), 500

@app.route("/put/<tabela>/<id>", methods=["PUT"])
def put(tabela, id):
    data = request.json

    if not data:
        return jsonify({"message": "Dados não fornecidos"}), 400

    if tabela == "professor":
        sql = f"UPDATE {tabela} SET nome = %s, idade = %s, area = %s WHERE matricula = %s"
        valores = (data["nome"], data["idade"], data["area"], id)
    elif tabela == "aluno":
        sql = f"UPDATE {tabela} SET nome = %s, idade = %s, cpf = %s WHERE matricula = %s"
        valores = (data["nome"], data["idade"], data["cpf"], id)
    elif tabela == "aula_particular":
        sql = f"UPDATE {tabela} SET curso = %s, aluno = %s, professor = %s WHERE cod_aula = %s"
        valores = (data["curso"], data["aluno"], data["professor"], id)
    else:
        return jsonify({"message": "Tabela inválida"}), 400

    try:
        atualizar_dado(sql, valores)  # Use a função de atualização genérica
        return jsonify({"message": "Registro atualizado com sucesso"}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        return jsonify({"message": "Erro ao atualizar registro"}), 500

if __name__ == "__main__":
    app.run(debug=True)


# Utilitarios para a apresentação:

# pip install psycopg2-binary
# pip install Flask
# pip install Flask-CORS

# python app.py