def extract_txt_text(txt_path):
    with open(txt_path, "r", encoding="utf-8") as file:
        return file.read()