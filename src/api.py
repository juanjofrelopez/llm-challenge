import logging
import os

import pandas as pd
from datetime import datetime, time
from fastapi import FastAPI, UploadFile, HTTPException
from .db import Database
from .models import CsvEntry, PromptRequest
from .utils import clean_dataframe
from .llm import LLMEngine

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

db = Database(os.getenv("DATABASE_URL") or
              "host=localhost port=5432  dbname=postgres user=postgres password=postgres")

llm = LLMEngine()


@app.post("/upload-csv")
async def upload_csv(file: UploadFile):
    try:
        df = pd.read_csv(file.file)
        df = clean_dataframe(df)

        print(df.head())

        entries = [CsvEntry(
            date=datetime.strptime(row['date'], "%m/%d/%Y").date(),
            week_day=row['week_day'],
            hour=row['hour'],
            ticket_number=row['ticket_number'],
            waiter=row['waiter'],
            product_name=row['product_name'],
            quantity=row['quantity'],
            unitary_price=row['unitary_price'],
            total=row['total']
        ) for _, row in df.iterrows()]

        db.insert_entries(entries)
        return {"message": "Data uploaded successfully", "rows_processed": len(entries)}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/text2sql")
async def text2sql(request: PromptRequest):
    try:
        sql = llm.text2sql(request.prompt)
        return {"sql": sql}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/nlp-query")
async def npl_query(request: PromptRequest):
    try:
        question = request.prompt
        sql = llm.text2sql(question)
        result = db.execute_and_stringify(sql)
        humanized_result = llm.ask(question, sql, result)
        return {"question": question, "sql": sql, "result": result, "humanized_result": humanized_result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
