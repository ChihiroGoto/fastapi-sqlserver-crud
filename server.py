from fastapi import FastAPI, HTTPException
import pyodbc
from pydantic import BaseModel
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)


DB_CONFIG = {
    "driver": "{ODBC Driver 18 for SQL Server}",
    "server": "localhost,1444",
    "database": "Users_kadai",
    "uid": "sa",
    "pwd": "123456789"
}

def get_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=localhost,1444;"
        "DATABASE=Users_kadai;"
        "UID=sa;"
        "PWD=123456789;"
        "TrustServerCertificate=yes;"
    )
    return conn

class User(BaseModel):
    name: str
    gender: str
    age: int
    address: str
    
class SearchRequest(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    minAge: Optional[int] = None
    maxAge: Optional[int] = None
    
    
@app.post("/api/users")
def create_user(user: User):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Users (Name, Gender, Age, Address) VALUES (?, ?, ?, ?)",
                (user.name, user.gender, user.age, user.address)
            )
            conn.commit()
            return{"message" : "登録完了"}
        except Exception as e:
            raise HTTPException(status_code = 500, detail = str(e))
        
        
@app.post("/api/users/search")
def search_users(req: SearchRequest):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
            SELECT
               Id As id, Name AS name,Gender AS gender, Age AS age, Address AS address
            FROM Users 
            WHERE 1 = 1
            """
            params = []
            if req.name:
                query += " AND Name LIKE ?"
                params.append(f"%{req.name}%")
            if req.gender:
                query += " AND Gender = ?"
                params.append(req.gender)
            if req.minAge is not None:
                query += " AND Age >= ?"
                params.append(req.minAge)
            if req.maxAge is not None:
                query += " AND Age <= ?"
                params.append(req.maxAge)
                
            print("実行SQL:", query)
            print("パラメータ:", params)
                
            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = [
                {"id":row.id, "name":row.name, "gender":row.gender,"age":row.age, "address":row.address}
                for row in rows
            ]
            return results
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code = 500, detail = str(e))
    
@app.get("/api/users/{user_id}")
def get_user(user_id: int):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Id AS id, Name AS name, Gender AS gender, Age AS age, Address AS address FROM Users WHERE Id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code = 404, detail = "ユーザーが見つかりません")
            return {"id": row.id, "name": row.name, "gender": row.gender, "age": row.age, "address": row.address}
        except Exception as e:
            raise HTTPException(status_code = 500, detail = str(e))
        
    
@app.put("/api/users/{user_id}")
def update_user(user_id: int, user: User):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Users SET Name = ?, Gender = ?, Age = ?, Address = ? WHERE Id = ?",
                (user.name, user.gender, user.age, user.address, user_id)
            )
            conn.commit()
            return{"message": "更新完了"}
        except Exception as e:
            raise HTTPException(status_code = 500, detail = str(e))
        
    
@app.get("/")
def root():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")  
        return {"message": "Python APIサーバーが動作中です (DB接続OK)"}
    except Exception as e:
        return {"message": "DB接続エラー", "error": str(e)}
