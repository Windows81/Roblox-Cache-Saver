import datetime
import os
import shutil

"""
// https://github.com/Jxys3rrV/roblox-2016-source-code/blob/4de2dc3a380e1babe4343c49a4341ceac749eddb/App/util/Shared/HttpCacheEntry.cpp#L306
Header cacheHeader = {
	gMagic(),                                                               // magic
	RBX_CACHE_FILE_VERSION,                                                 // version
	std::min(strlen(cdnUrl), static_cast<size_t>(RBX_CACHE_URL_MAX_LENGTH)),// urlBytes
	{'\0'},                                                                 // url
	responseCode,                                                           // responseCode
	headers.size(),                                                         // responseHeadersSize
	calculateHash(headers),                                                 // responseHeadersHash
	body.size(),                                                            // responseBodySize
	calculateHash(body),                                                    // responseBodyHash
	0                                                                       // reserved
};
"""


def do_file(rf: str, wf: str) -> None:
    with open(rf, "rb") as r:
        if r.read(4) != b"RBXH":  # Checks `magic`.
            shutil.copy(rf, wf)
            return

        # Skips `version`.
        r.seek(4, os.SEEK_CUR)

        # The `+ 1` is because the URL is null-terminated.
        url_len = int.from_bytes(r.read(4), byteorder='little')
        r.seek(url_len + 1, os.SEEK_CUR)

        status_code = int.from_bytes(r.read(4), byteorder='little')
        if not 200 <= status_code <= 299:
            return
        header_size = int.from_bytes(r.read(4), byteorder='little')

        # Skips `responseHeadersHash`, `responseBodySize`, `responseBodyHash`, and (what used to be) `reserved`.
        r.seek(header_size + 16, os.SEEK_CUR)

        with open(wf, "wb") as w:
            while 1:
                buf = r.read(16*1024*1024)
                if not buf:
                    break
                w.write(buf)
        print(rf)


def perform(rds: list[str], wd: str):
    if not os.path.exists(wd):
        os.makedirs(wd)

    if any(not os.path.isdir(d) for d in rds) or not os.path.isdir(wd):
        raise ValueError("At least one of the arguments is not a directory.")

    for rd in rds:
        files = os.listdir(rd)
        files.sort(key=lambda x: os.stat(
            os.path.join(rd, x)).st_mtime, reverse=True)
        for f in files:
            rf = os.path.join(rd, f)
            created_time = datetime.datetime.fromtimestamp(
                os.path.getctime(rf)
            )
            wf_name = (
                created_time.strftime(r'%Y%m%d%H%M%S') +
                ' ' +
                f
            )
            wf = os.path.join(wd, wf_name)
            if os.stat(rf).st_size < 92:
                continue
            if os.path.isfile(wf):
                continue
            do_file(rf, wf)


if __name__ == "__main__":
    perform(
        [
            os.path.join(
                os.getenv("LOCALAPPDATA", ""), "Temp", "Roblox", "sounds",
            ),
            os.path.join(
                os.getenv("LOCALAPPDATA", ""), "Temp", "Roblox", "http",
            ),
        ],
        os.path.join(os.path.dirname(__file__), "cache"),
    )
