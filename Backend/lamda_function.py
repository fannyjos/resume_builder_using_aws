import json
import boto3
import io
import datetime
import types, sys

# 🩹 Bypass PIL import error
fake_pil = types.ModuleType("PIL")
fake_pil.Image = types.ModuleType("PIL.Image")
sys.modules["PIL"] = fake_pil
sys.modules["PIL.Image"] = fake_pil.Image

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

s3 = boto3.client('s3')
BUCKET_NAME = 'resume-upload-task3.1'  # ← Replace with your actual S3 bucket name

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        name = body.get('name', 'N/A')
        email = body.get('email', 'N/A')
        phone = body.get('phone', 'N/A')
        skills = body.get('skills', 'N/A')

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=LETTER)
        width, height = LETTER

        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(50, height - 50, "Resume")

        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, height - 100, f"Name: {name}")
        pdf.drawString(50, height - 130, f"Email: {email}")
        pdf.drawString(50, height - 160, f"Phone: {phone}")
        pdf.drawString(50, height - 190, f"Skills: {skills}")

        pdf.showPage()
        pdf.save()
        buffer.seek(0)

        filename = f"resume_{name.replace(' ', '_')}_{datetime.datetime.utcnow().timestamp()}.pdf"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=buffer,
            ContentType='application/pdf'
        )

        pdf_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "Resume generated successfully!",
                "pdf_url": pdf_url
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": str(e)
            })
        }
