from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
import asyncpg
import os
import time

app = FastAPI()

class Professor(BaseModel):
    id: Optional[int] = None
    nome: str
    email: str
    sala_de_atendimento: str

class ProfessorAtualizar(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    sala_de_atendimento: Optional[str] = None

async def get_database():
    DATABASE_URL = os.getenv("PGURL", "postgres://postgres:postgres@db:5432/professores")
    return await asyncpg.connect(DATABASE_URL)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    print(f"{request.method} {request.url.path} - {duration:.4f}s")
    return response

@app.post("/api/v1/professores/", status_code=201)
async def criar_professor(professor: Professor):
    conn = await get_database()
    try:
        existe = await conn.fetchval("SELECT 1 FROM professores WHERE email=$1", professor.email)
        if existe:
            raise HTTPException(status_code=400, detail="Email já cadastrado.")
        await conn.execute(
            "INSERT INTO professores (nome, email, sala_de_atendimento) VALUES ($1, $2, $3)",
            professor.nome, professor.email, professor.sala_de_atendimento
        )
        return {"message": "Professor cadastrado com sucesso!"}
    finally:
        await conn.close()

@app.get("/api/v1/professores/", response_model=List[Professor])
async def listar_professores():
    conn = await get_database()
    try:
        rows = await conn.fetch("SELECT * FROM professores ORDER BY id")
        return [dict(row) for row in rows]
    finally:
        await conn.close()

@app.get("/api/v1/professores/{professor_id}")
async def obter_professor(professor_id: int):
    conn = await get_database()
    try:
        prof = await conn.fetchrow("SELECT * FROM professores WHERE id=$1", professor_id)
        if not prof:
            raise HTTPException(status_code=404, detail="Professor não encontrado.")
        return dict(prof)
    finally:
        await conn.close()

@app.patch("/api/v1/professores/{professor_id}")
async def atualizar_professor(professor_id: int, dados: ProfessorAtualizar):
    conn = await get_database()
    try:
        prof = await conn.fetchrow("SELECT * FROM professores WHERE id=$1", professor_id)
        if not prof:
            raise HTTPException(status_code=404, detail="Professor não encontrado.")

        if dados.email:
            existe = await conn.fetchval(
                "SELECT 1 FROM professores WHERE email=$1 AND id<>$2", dados.email, professor_id)
            if existe:
                raise HTTPException(status_code=400, detail="Email já cadastrado.")

        await conn.execute("""
            UPDATE professores
            SET nome = COALESCE($1, nome),
                email = COALESCE($2, email),
                sala_de_atendimento = COALESCE($3, sala_de_atendimento)
            WHERE id = $4
        """, dados.nome, dados.email, dados.sala_de_atendimento, professor_id)
        return {"message": "Professor atualizado com sucesso!"}
    finally:
        await conn.close()

@app.delete("/api/v1/professores/{professor_id}")
async def remover_professor(professor_id: int):
    conn = await get_database()
    try:
        result = await conn.execute("DELETE FROM professores WHERE id=$1", professor_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Professor não encontrado.")
        return {"message": "Professor removido com sucesso!"}
    finally:
        await conn.close()

@app.delete("/api/v1/professores/")
async def resetar_professores():
    conn = await get_database()
    try:
        init_sql = os.getenv("INIT_SQL", "db/init.sql")
        with open(init_sql, 'r') as f:
            sql = f.read()
        await conn.execute(sql)
        return {"message": "Banco de dados restaurado com sucesso!"}
    finally:
        await conn.close()