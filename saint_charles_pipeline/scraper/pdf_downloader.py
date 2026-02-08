import os

def download_pdf(session, url, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    filename = url.split("=")[-1] + ".pdf"
    path = os.path.join(save_dir, filename)

    r = session.get(url)
    with open(path, "wb") as f:
        f.write(r.content)

    return path

