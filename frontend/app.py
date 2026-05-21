
from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "secret"

API_URL = "http://backend:8000/api/v1/professores"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        data = {
            "nome": request.form["nome"],
            "email": request.form["email"],
            "sala_de_atendimento": request.form["sala_de_atendimento"]
        }
        response = requests.post(API_URL + "/", json=data)
        if response.status_code == 201:
            flash("Professor cadastrado com sucesso!", "success")
            return redirect(url_for("professores"))
        else:
            flash(response.json().get("detail", "Erro ao cadastrar professor."), "danger")
    return render_template("cadastro.html")

@app.route("/professores")
def professores():
    response = requests.get(API_URL + "/")
    professores = response.json() if response.ok else []
    return render_template("professores.html", professores=professores)

@app.route("/editar/<int:professor_id>", methods=["GET", "POST"])
def editar(professor_id):
    if request.method == "POST":
        data = {
            "nome": request.form["nome"],
            "email": request.form["email"],
            "sala_de_atendimento": request.form["sala_de_atendimento"]
        }
        response = requests.patch(f"{API_URL}/{professor_id}", json=data)
        if response.ok:
            flash("Professor atualizado com sucesso!", "success")
        else:
            flash("Erro ao atualizar professor.", "danger")
        return redirect(url_for("professores"))
    else:
        prof = requests.get(f"{API_URL}/{professor_id}").json()
        return render_template("editar.html", professor=prof)

@app.route("/excluir/<int:professor_id>")
def excluir(professor_id):
    response = requests.delete(f"{API_URL}/{professor_id}")
    if response.ok:
        flash("Professor removido com sucesso!", "success")
    else:
        flash("Erro ao remover professor.", "danger")
    return redirect(url_for("professores"))

@app.route("/reset")
def reset():
    response = requests.delete(API_URL + "/")
    if response.ok:
        flash("Banco de dados resetado com sucesso!", "info")
    else:
        flash("Erro ao resetar banco.", "danger")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, port=3000, host="0.0.0.0")