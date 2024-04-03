# Getting Started
```
cd spotify
docker build -t downloads_spotify .
docker run -v <desired path>:/app/data -p 5000:8080 downloads_spotify #path: Đường dẫn lưu trữ trong máy
```
# SPOTIFY
url_download(string): url để download spotify (ví dụ https://open.spotify.com/playlist/4i3lC1FqKJz9En6mfn04KZ)


curl --location --request POST 'http://127.0.0.1:5000/downloads_spotify' \
--header 'Content-Type: application/json' \
--data-raw '{
    "url_downloads": "https://open.spotify.com/playlist/4i3lC1FqKJz9En6mfn04KZ"
}'

# YOUTUBE
url_download(string): url để download spotify (ví dụ https://youtube.com/watch?v=GIa5d8cZOIY)


curl --location --request POST 'http://127.0.0.1:5000/downloads_youtube' \
--header 'Content-Type: application/json' \
--data-raw '{
    "url_downloads": "https://youtube.com/watch?v=GIa5d8cZOIY"
}'
