from pathlib import Path


def load_documents(data_dir: str = "data"):
    documents = []
    folder = Path(data_dir)

    for file_path in folder.glob("*"):
        if file_path.suffix in [".txt", ".md"]:
            text = file_path.read_text(encoding="utf-8")
            documents.append({
                "source": file_path.name,
                "text": text
            })

    return documents