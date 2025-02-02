import os

from openai import OpenAI
from typing import Generator


class LLMEngine:
    def __init__(self, api_key="sk-no-key-required"):
        self.client = OpenAI(base_url=os.getenv(
            'LLM_BASE_URL', "http://localhost:8080/v1"), api_key=api_key)

    def _stream_and_process(self, messages: list) -> Generator:
        response_stream = self.client.chat.completions.create(
            model="LLaMA_CPP", messages=messages, stream=True
        )

        for chunk in response_stream:
            if chunk.choices[0].delta.content:
                t = chunk.choices[0].delta.content
                # print(t, end="", flush=True)
                yield t

    def text2sql(self, prompt: str) -> str:
        messages = [
            {"role": "user", "content": self._get_text2sql_sys_msg(prompt)}]
        return "".join(self._stream_and_process(messages)).replace("<|eot_id|>", "").replace("```sql", "").replace("```", "")

    def _get_text2sql_sys_msg(self, prompt: str) -> str:
        return f"""
            Task
            Generate a SQL query to answer the following question:
            {prompt}

            Here is the Database Schema
            CREATE TABLE csv_entries (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                week_day VARCHAR(10) NOT NULL,
                hour TIME NOT NULL,
                ticket_number VARCHAR(50) NOT NULL,
                waiter INTEGER NOT NULL,
                product_name VARCHAR(200) NOT NULL,
                quantity FLOAT NOT NULL,
                unitary_price FLOAT NOT NULL,
                total FLOAT NOT NULL
            )

            YOU MUST JUST ANSWER WITH ONLY THE SQL QUERY AND NOTHING ELSE
            EVERY TABLE WILL BE IN THE public SCHEMA. for example public.csv_entries
            HAVE IN MIND THAT THIS QUERY WILL BE RUN ON A POSTGRESQL DATABASE.
            """

    def ask(self, question: str, sql: str, result: str) -> str:
        messages = [
            {"role": "system", "content": self._get_sys_msg(question, sql, result)}]
        return "".join(self._stream_and_process(messages)).replace("<|eot_id|>", "")

    def _get_sys_msg(self, question: str, sql: str, result: str) -> str:
        return f"""
            you are a helpful assistant which only task consists of receiving the result of a sql query and adapting it to be more human friendly.
            the original plain text question made by the user is this:
            {question}
            the response from the text2sql llm engine was this:
            {sql}
            the result from running the query is this:
            {result}
            Ensure your responses are:
            - Clear and easy to understand: Use simple and direct language.
            - Helpful and informative: Provide relevant and actionable information.
            - Safe and ethical: Avoid providing harmful, biased, or discriminatory information.
            - Consistent with company policies: Adhere to all relevant company guidelines and regulations.

            DO NOT INCLUDE ANY BOILERPLATE CODE LIKE FOR EXAMPLE: "Here's the result of the query, presented in a more human-friendly format:"
            JUST GIVE ME THE FINAL HUMANIZED RESPONSE
            DO NOT HALUCINATE OR INVENT ANY RESPONSE THAT IS NOT BASED ON THE GIVEN CONTEXT
            IF THE QUERY HAD AN ERROR COMUNICATE IT
        """
