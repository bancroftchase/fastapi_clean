from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
from twilio.rest import Client

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Initialize services
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)
openai_client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

@app.get("/")
async def health_check():
    return {"status": "CONFIRMED_WORKING"}

@app.post("/twilio-sms")
async def handle_sms(request: Request):
    form_data = await request.form()
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a medical assistant."},
                {"role": "user", "content": form_data.get("Body", "").strip()}
            ],
            temperature=0.3
        )
        twilio_client.messages.create(
            body=response.choices[0].message.content,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=form_data.get("From")
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
