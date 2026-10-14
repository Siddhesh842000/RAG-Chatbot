"""
Phase 7 test: the complete API (PDF -> chunks -> embeddings -> FAISS -> Groq).

This uses the real embedding model and the real Groq API, so your key must be in .env.

Run from the backend folder:
    python test_api.py
"""
from pathlib import Path

import pymupdf
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services import llm_service

BACKEND_DIR = Path(__file__).parent
SAMPLE = BACKEND_DIR / "sample.pdf"

SESSION = {"X-Session-ID": "test-session-one"}
OTHER_SESSION = {"X-Session-ID": "test-session-two"}


def check(name: str, passed: bool, detail: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name} {detail}")
    return passed


def make_pdf(pages: int, with_text: bool = True) -> bytes:
    doc = pymupdf.open()
    for i in range(pages):
        page = doc.new_page()
        if with_text:
            page.insert_textbox(pymupdf.Rect(72, 72, 523, 770), f"This is page {i + 1}.", fontsize=12)
    data = doc.tobytes()
    doc.close()
    return data


def main() -> None:
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_key_here":
        print("GROQ_API_KEY is not set in backend\\.env. Please add it and run again.")
        return

    results = []

    # "with" runs the app startup, which also loads the embedding model
    with TestClient(app) as client:

        def upload(name: str, data: bytes, headers=SESSION):
            return client.post("/api/upload", files={"file": (name, data, "application/pdf")}, headers=headers)

        def ask(question: str, headers=SESSION):
            return client.post("/api/chat", json={"question": question}, headers=headers)

        # ---- Basic endpoints ----
        r = client.get("/")
        results.append(check("GET / works", r.status_code == 200 and "running" in r.json()["message"]))
        r = client.get("/health")
        results.append(check("GET /health works", r.status_code == 200 and r.json()["status"] == "ok"))

        # ---- Upload errors ----
        print("\nUpload errors:")
        r = upload("notes.txt", b"hello")
        results.append(check("Wrong file type -> 400", r.status_code == 400, f"-> {r.json()['detail']}"))

        r = upload("empty.pdf", b"")
        results.append(check("Empty file -> 400", r.status_code == 400, f"-> {r.json()['detail']}"))

        r = upload("fake.pdf", b"this is not a pdf")
        results.append(check("Invalid PDF -> 400", r.status_code == 400, f"-> {r.json()['detail']}"))

        r = upload("broken.pdf", b"%PDF-1.4\nthis is not a real pdf")
        results.append(check("Corrupted PDF -> 400", r.status_code == 400, f"-> {r.json()['detail']}"))

        r = upload("blank.pdf", make_pdf(1, with_text=False))
        results.append(check("PDF with no text -> 422", r.status_code == 422, f"-> {r.json()['detail']}"))

        r = upload("huge.pdf", b"%PDF-" + b"0" * (settings.MAX_FILE_SIZE_MB * 1024 * 1024 + 10))
        results.append(check("File too large -> 413", r.status_code == 413, f"-> {r.json()['detail']}"))

        r = upload("long.pdf", make_pdf(settings.MAX_PAGES + 1))
        results.append(check("Too many pages -> 413", r.status_code == 413, f"-> {r.json()['detail']}"))

        r = upload("a.pdf", b"x", headers={"X-Session-ID": "bad id!"})
        results.append(check("Invalid session id -> 400", r.status_code == 400))

        # ---- Chat before any upload ----
        print("\nChat errors:")
        r = ask("What is FAISS?")
        results.append(check("Missing vector store -> 404", r.status_code == 404, f"-> {r.json()['detail']}"))

        # ---- Upload the sample PDF ----
        print("\nUpload sample.pdf:")
        if not SAMPLE.exists():
            print("sample.pdf not found. Run python test_pdf.py first to create it.")
            return
        r = upload("sample.pdf", SAMPLE.read_bytes())
        print(f"   {r.json()}")
        body = r.json()
        results.append(
            check("Upload works", r.status_code == 200 and body["pages"] == 3 and body["chunks"] == 3)
        )

        r = ask("   ")
        results.append(check("Empty question -> 400", r.status_code == 400, f"-> {r.json()['detail']}"))

        # ---- Questions that ARE in the document ----
        print("\nQuestions that are in the document:")
        for question, expected_page in [
            ("What is FAISS used for?", 2),
            ("Why does each chunk keep its page number?", 3),
            ("How does retrieval augmented generation work?", 1),
        ]:
            r = ask(question)
            data = r.json()
            pages = [s["page"] for s in data.get("sources", [])]
            print(f"   Q: {question}\n   A: {data.get('answer')}\n   Source pages: {pages}")
            results.append(
                check(
                    f"Answer found, only page {expected_page} is shown as source",
                    r.status_code == 200 and data["found"] and pages == [expected_page],
                )
            )

        # ---- Questions that are NOT in the document ----
        print("\nQuestions that are NOT in the document:")
        for question in ["What is the capital of France?", "How much does a laptop cost?"]:
            r = ask(question)
            data = r.json()
            print(f"   Q: {question}\n   A: {data.get('answer')}")
            results.append(
                check(
                    "Not found, no sources, no invented answer",
                    r.status_code == 200 and data["found"] is False and data["sources"] == [],
                )
            )

        # ---- Sessions ----
        print("\nSessions and clearing:")
        r = ask("What is FAISS used for?", headers=OTHER_SESSION)
        results.append(check("Another visitor has no document -> 404", r.status_code == 404))

        r = client.post("/api/clear", headers=SESSION)
        results.append(check("Clear works", r.status_code == 200 and r.json()["cleared"] is True))
        r = ask("What is FAISS used for?")
        results.append(check("Chat after clear -> 404", r.status_code == 404))
        r = client.post("/api/clear", headers=SESSION)
        results.append(check("Clearing again says nothing to clear", r.json()["cleared"] is False))

        # ---- LLM error ----
        print("\nLLM error:")
        upload("sample.pdf", SAMPLE.read_bytes())
        real_key = settings.GROQ_API_KEY
        settings.GROQ_API_KEY = "gsk_this_key_is_not_real"
        llm_service.reset_client()
        r = ask("What is FAISS used for?")
        results.append(check("Bad Groq key -> 500 with message", r.status_code == 500, f"-> {r.json()['detail']}"))
        settings.GROQ_API_KEY = real_key
        llm_service.reset_client()

        r = ask("What is FAISS used for?")
        results.append(check("Works again after the key is restored", r.status_code == 200 and r.json()["found"]))
        client.post("/api/clear", headers=SESSION)

    print()
    print(f"{sum(results)} of {len(results)} checks passed")


if __name__ == "__main__":
    main()
