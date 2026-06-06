import asyncio
import io
import re
import subprocess
from collections import Counter
from typing import Optional

from PIL import Image, ImageOps

from ...application.ports.captcha_solver_port import CaptchaSolverPort
from ...domain.exceptions.suv_errors import CaptchaError

# El captcha del SUV es una operación "A op B = ?" en una imagen pequeña
# (~121x40) con líneas de ruido grises encima del texto negro.

# El texto es negro puro (~0); el ruido es gris (~100). Un umbral bajo
# elimina el ruido por completo y deja solo la operación.
_TEXT_THRESHOLD = 60

# Tesseract lee mejor con texto de altura moderada y margen blanco.
# Ampliar 4x lo deja demasiado grande; 2x y 3x funcionan bien.
_SCALES = (2, 3)
_BORDER = 20

# Solo dígitos y operadores. PSM 7/6 tratan la imagen como una línea.
_WHITELIST = "0123456789+-x*/=?"
_PSM_MODES = (7, 6)


class TesseractAdapter(CaptchaSolverPort):
    async def solve(self, image_bytes: bytes) -> str:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self._process, image_bytes)
        if result is None:
            raise CaptchaError("Could not solve captcha from image")
        return result

    def _process(self, image_bytes: bytes) -> Optional[str]:
        raw = Image.open(io.BytesIO(image_bytes))

        # Votación entre escalas y modos PSM para descartar lecturas sueltas
        votes: Counter = Counter()
        for scale in _SCALES:
            png = self._preprocess(raw, scale)
            for psm in _PSM_MODES:
                expression = self._parse(self._run_tesseract(png, psm))
                if expression:
                    votes[expression] += 1

        if not votes:
            return None

        winning_expression = votes.most_common(1)[0][0]
        return self._evaluate(winning_expression)

    def _preprocess(self, raw: Image.Image, scale: int) -> bytes:
        image = raw.convert("L").point(lambda p: 0 if p < _TEXT_THRESHOLD else 255)
        image = image.resize(
            (image.width * scale, image.height * scale), Image.LANCZOS
        )
        image = image.point(lambda p: 0 if p < 128 else 255)
        image = ImageOps.expand(image, border=_BORDER, fill=255)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def _run_tesseract(self, png: bytes, psm: int) -> str:
        # Leptonica en este sistema no abre el archivo temporal de pytesseract,
        # así que pasamos la imagen por stdin a tesseract directamente.
        proc = subprocess.run(
            [
                "tesseract",
                "-",
                "stdout",
                "--psm",
                str(psm),
                "-c",
                f"tessedit_char_whitelist={_WHITELIST}",
            ],
            input=png,
            capture_output=True,
        )
        return proc.stdout.decode("utf-8", errors="ignore")

    def _parse(self, text: str) -> Optional[str]:
        """Devuelve la operación normalizada 'AopB' o None."""
        normalized = text.replace("x", "*").replace("X", "*")
        # La operación está antes del '=' o '?'; el resto es ruido
        left = re.split(r"[=?]", normalized)[0]
        # Los operandos del SUV son de un solo dígito
        match = re.search(r"(\d)\s*([+\-*/])\s*(\d)", left)
        if not match:
            return None
        return f"{match.group(1)}{match.group(2)}{match.group(3)}"

    def _evaluate(self, expression: str) -> Optional[str]:
        a = int(expression[0])
        op = expression[1]
        b = int(expression[2])

        if op == "+":
            return str(a + b)
        if op == "-":
            return str(a - b)
        if op == "*":
            return str(a * b)
        if op == "/" and b != 0:
            return str(a // b)
        return None
