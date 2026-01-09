from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from detector import is_phishing, ml_detect, translate_to_english
from datetime import datetime
import os
import uvicorn

app = FastAPI(title="AI Phishing Detector API")

class EmailInput(BaseModel):
    content: str

@app.post("/detect")
def detect_email(input: EmailInput):
    try:
        translated = translate_to_english(input.content)
        rule_result, score, confidence, reasons = is_phishing(translated)
        ml_result, ml_conf = ml_detect(translated)

        # ✅ Enterprise logging logic
        os.makedirs("logs", exist_ok=True)
        log_entry = (
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"- IP: 127.0.0.1 "
            f"- Length: {len(input.content)} "
            f"- ML: {'PHISHING' if ml_result else 'SAFE'} ({ml_conf}%) "
            f"- Rule: {'PHISHING' if rule_result else 'SAFE'} ({confidence}%)\n"
        )
        with open("logs/api_requests.log", "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)

        return {
            "rule_based": {
                "phishing": rule_result,
                "score": score,
                "confidence": confidence,
                "reasons": reasons
            },
            "ml_based": {
                "phishing": bool(ml_result),
                "confidence": ml_conf
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
