import os
import mimetypes
from fastapi import Request, Response, HTTPException

def range_requests_response(
    request: Request, file_path: str, content_type: str = None
):
    """
    Returns a Response that supports HTTP Range Requests.
    Reads chunk into memory to bypass Uvicorn StreamingResponse Range crash bug.
    """
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    file_size = os.path.getsize(file_path)
    
    if not content_type:
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or "application/octet-stream"

    range_header = request.headers.get("range")

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Type": content_type,
    }

    if not range_header:
        # Client isn't asking for a range, send the whole file (up to a limit, or just open it)
        # We'll just return the first 5MB or so if they really want it, but usually browsers ask for Range.
        # Actually, if no range, just use FileResponse (which works fine without Range).
        from fastapi.responses import FileResponse
        return FileResponse(file_path, media_type=content_type)

    # Parse Range header: 'bytes=0-100' -> '0-100'
    try:
        range_str = range_header.replace("bytes=", "").split("-")
        start = int(range_str[0]) if range_str[0] else 0
        end = int(range_str[1]) if len(range_str) > 1 and range_str[1] else file_size - 1
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Range Header")

    if start >= file_size:
        raise HTTPException(status_code=416, detail="Requested Range Not Satisfiable")

    # Limit chunk size to 2MB to prevent memory overload
    end = min(end, start + 2 * 1024 * 1024 - 1)
    chunk_size = end - start + 1
    
    headers["Content-Length"] = str(chunk_size)
    headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"

    with open(file_path, "rb") as f:
        f.seek(start)
        data = f.read(chunk_size)

    return Response(
        content=data,
        status_code=206,
        headers=headers,
        media_type=content_type,
    )
