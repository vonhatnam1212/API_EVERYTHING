# Getting Started
## DOWNLOADS MP3
```
cd spotify
docker build -t downloads_spotify .
docker run -v <desired path>:/app/data -p 5000:8080 downloads_spotify #path: Đường dẫn lưu trữ trong máy
```
