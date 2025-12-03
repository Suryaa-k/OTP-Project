from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import random
import string

# -------- DB setup --------
SQLALCHEMY_DATABASE_URL = "sqlite:///./otp.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class OTPEntry(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String, index=True)
    email = Column(String, index=True)
    mobile_otp = Column(String)
    email_otp = Column(String)
    expires_at = Column(DateTime)


Base.metadata.create_all(bind=engine)

# -------- FastAPI app --------
app = FastAPI(title="Dual OTP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # for dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Schemas --------
class SendOTPRequest(BaseModel):
    mobile: str
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    mobile: str
    email: EmailStr
    mobileOtp: str
    emailOtp: str


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


# -------- Endpoints --------
@app.post("/send-otp")
def send_otp(payload: SendOTPRequest):
    db = SessionLocal()
    try:
        mobile_otp = generate_otp()
        email_otp = generate_otp()

        # store in DB with 5‑minute expiry
        expires = datetime.utcnow() + timedelta(minutes=5)

        # delete any old entries for this user
        db.query(OTPEntry).filter(
            OTPEntry.mobile == payload.mobile,
            OTPEntry.email == payload.email
        ).delete()

        entry = OTPEntry(
            mobile=payload.mobile,
            email=payload.email,
            mobile_otp=mobile_otp,
            email_otp=email_otp,
            expires_at=expires,
        )
        db.add(entry)
        db.commit()

        # SIMULATED SENDING
        print(f"[DEBUG] Send SMS OTP {mobile_otp} to mobile {payload.mobile}")
        print(f"[DEBUG] Send EMAIL OTP {email_otp} to email {payload.email}")

        return {"success": True, "message": "OTPs generated and sent (console log)."}
    finally:
        db.close()


@app.post("/verify-otp")
def verify_otp(payload: VerifyOTPRequest):
    db = SessionLocal()
    try:
        entry = (
            db.query(OTPEntry)
            .filter(
                OTPEntry.mobile == payload.mobile,
                OTPEntry.email == payload.email,
            )
            .first()
        )

        if not entry:
            return {"verified": False, "message": "No OTP request found."}

        if datetime.utcnow() > entry.expires_at:
            return {"verified": False, "message": "OTP expired. Please request again."}

        if entry.mobile_otp != payload.mobileOtp or entry.email_otp != payload.emailOtp:
            return {"verified": False, "message": "Invalid OTP(s)."}

        # success – optionally delete used record
        db.delete(entry)
        db.commit()

        return {"verified": True, "message": "OTP verification successful."}
    finally:
        db.close()
