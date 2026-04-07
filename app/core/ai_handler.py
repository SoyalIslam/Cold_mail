from openai import OpenAI
from app.core.database import get_user_by_id
import streamlit as st

def generate_ai_template(prompt: str) -> str:
    # In the multi-user version, we get the user_id from session state
    if "user_id" not in st.session_state:
        return "Error: User not logged in."
        
    user = get_user_by_id(st.session_state["user_id"])
    if not user or not user['openai_api_key']:
        return "Error: Please set your OpenAI API Key in Settings."
    
    try:
        client = OpenAI(api_key=user['openai_api_key'])
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional career coach and expert at writing cold emails for students seeking recruitment."},
                {"role": "user", "content": f"Generate a cold email template based on this: {prompt}. Use placeholders like {{Name}}, {{Company}}, {{Role}}, and {{SENDER_NAME}}."}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"
