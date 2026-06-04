from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChecklistItem(BaseModel):
    item_id: str
    realizado: bool
    observacao: str = ""
    responsavel: str = ""
    data_execucao: str = ""

def conectar():
    return sqlite3.connect("checklist.db")

@app.on_event("startup")
def criar_tabela():
    conn = conectar()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS checklist (
            item_id TEXT PRIMARY KEY,
            realizado BOOLEAN,
            observacao TEXT,
            responsavel TEXT,
            data_execucao TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.get("/checklist")
def listar():
    conn = conectar()
    rows = conn.execute("SELECT * FROM checklist").fetchall()
    conn.close()

    return [
        {
            "item_id": r[0],
            "realizado": bool(r[1]),
            "observacao": r[2],
            "responsavel": r[3],
            "data_execucao": r[4],
        }
        for r in rows
    ]

@app.post("/checklist")
def salvar(item: ChecklistItem):
    conn = conectar()
    conn.execute("""
        INSERT INTO checklist 
        (item_id, realizado, observacao, responsavel, data_execucao)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(item_id) DO UPDATE SET
            realizado = excluded.realizado,
            observacao = excluded.observacao,
            responsavel = excluded.responsavel,
            data_execucao = excluded.data_execucao
    """, (
        item.item_id,
        item.realizado,
        item.observacao,
        item.responsavel,
        item.data_execucao
    ))
    conn.commit()
    conn.close()

    return {"status": "salvo"}
