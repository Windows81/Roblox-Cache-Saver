import os


def perform(rd: str, wd: str):
    if not os.path.isdir(rd) or not os.path.isdir(wd):
        raise ValueError("At least one of the arguments is not a directory.")

    files = os.listdir(rd)
    files.sort(key=lambda x: os.stat(os.path.join(rd, x)).st_size, reverse=True)
    for f in files:
        rf = os.path.join(rd, f)
        wf = os.path.join(wd, f)
        if os.stat(rf).st_size < 92:
            break
        if os.path.isfile(wf):
            continue
        with open(rf, "rb") as r:
            if not b"RBXH" in r.readline():
                continue
            l, off = b":\r\n", r.tell()
            while b":" in l and l.endswith(b"\r\n"):
                off = r.tell()
                l = r.readline()
            r.seek(off)
            with open(wf, "wb") as w:
                for b in r:
                    w.write(b)


if __name__ == "__main__":
    perform(
        os.path.join(os.getenv("LOCALAPPDATA"), "Temp", "Roblox", "http"),
        os.path.join(os.getenv("USERPROFILE"), "Documents", "ROBLOX"),
    )
