from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from openai import OpenAI
import base64
from tempfile import NamedTemporaryFile
import os
import mimetypes

GMS_BASE_URL = os.getenv('GMS_BASE_URL', 'https://gms.ssafy.io/gmsapi/api.openai.com/v1')
GMS_KEY = os.getenv('GMS_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY') or settings.OPENAI_API_KEY

# Prefer SSAFY gateway if available; otherwise call OpenAI directly
chat_client = OpenAI(api_key=GMS_KEY, base_url=GMS_BASE_URL) if GMS_KEY else OpenAI(api_key=OPENAI_KEY)
audio_client = OpenAI(api_key=GMS_KEY, base_url=GMS_BASE_URL) if GMS_KEY else OpenAI(api_key=OPENAI_KEY)


def handle_ai_error(exc, fallback_message):
    """
    Map common AI errors (e.g., quota) to clearer client responses.
    """
    status = getattr(exc, "status_code", None)
    detail_text = str(exc)
    if not status and hasattr(exc, "response") and hasattr(exc.response, "status_code"):
        status = exc.response.status_code

    if status == 429 or "insufficient_quota" in detail_text.lower() or "quota" in detail_text.lower():
        return Response({"error": "AI quota exceeded. Please try again later.", "detail": detail_text}, status=429)

    return Response({"error": fallback_message, "detail": detail_text}, status=503)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def analyze_image(request):
    image = request.FILES.get('image')
    if not image:
        return Response({"error": "image is required."}, status=400)

    image_bytes = image.read()
    image_base64 = base64.b64encode(image_bytes).decode()
    content_type = image.content_type or 'image/png'
    data_url = f"data:{content_type};base64,{image_base64}"

    try:
        response = chat_client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "사진 속 여행지를 한국어로 간단히 설명해줘."},
                        {"type": "input_image", "image_url": data_url}
                    ]
                }
            ]
        )
        return Response({"result": response.output_text})
    except Exception as e:
        return handle_ai_error(e, "Image analysis failed.")


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def chat_ai(request):
    question = request.data.get('question')
    travel_name = request.data.get('travel_name', 'this place')

    if not question:
        return Response({"error": "question is required."}, status=400)

    try:
        completion = chat_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "너는 여행 안내원이야. 한국어로 간결하게 답변해라."
                },
                {
                    "role": "user",
                    "content": f"여행지: {travel_name}\n질문: {question}"
                }
            ],
            temperature=0.7,
            max_tokens=400
        )
        answer = completion.choices[0].message.content if completion.choices else ""
        return Response({"answer": answer})
    except Exception as e:
        return handle_ai_error(e, "AI response failed.")


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def transcribe_audio(request):
    audio = request.FILES.get('audio')
    if not audio:
        return Response({"error": "audio is required."}, status=400)

    # Basic validation: allow common audio; be lenient for browser-recorded webm/opus
    content_type = audio.content_type or mimetypes.guess_type(audio.name)[0]
    if content_type and not content_type.startswith('audio/'):
        return Response({"error": "Unsupported audio format."}, status=400)

    # Use file extension to help OpenAI detect format
    guessed_ext = mimetypes.guess_extension(content_type or '') or ''
    original_ext = '.' + audio.name.split('.')[-1] if '.' in audio.name else ''
    suffix = original_ext or guessed_ext or '.webm'

    tmp_path = None
    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            for chunk in audio.chunks():
                tmp.write(chunk)
            tmp.flush()

        with open(tmp_path, "rb") as f:
            transcript = audio_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="ko"
            )
        return Response({"text": transcript.text})
    except Exception as e:
        return handle_ai_error(e, "Audio transcription failed.")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def generate_spot_description(request):
    """
    여행지 이름과 주소를 받아 AI로 4줄 정도의 설명을 생성합니다.
    """
    spot_name = request.data.get('spot_name')
    address = request.data.get('address', '')

    if not spot_name:
        return Response({"error": "spot_name is required."}, status=400)

    try:
        completion = chat_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "너는 여행지 정보를 제공하는 전문가야. 주어진 여행지에 대해 간결하고 매력적인 설명을 한국어로 4줄 이내로 작성해줘. 여행지의 특징, 볼거리, 분위기를 포함해서 설명해줘."
                },
                {
                    "role": "user",
                    "content": f"여행지: {spot_name}\n주소: {address}\n\n이 여행지에 대해 4줄 정도로 설명해줘."
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        description = completion.choices[0].message.content if completion.choices else ""
        return Response({"description": description})
    except Exception as e:
        return handle_ai_error(e, "Description generation failed.")
