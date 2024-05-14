Add a new audiobook
```
curl -X POST "http://localhost:5003/audiobooks" -H "Content-Type: application/json" -d '{"title": "New Book", "author": "Author Name", "genre": "Genre", "price": 9.99}'
```

Update an audiobook
```
curl -X PUT "http://localhost:5003/audiobooks/1001" -H "Content-Type: application/json" -d '{"title": "Updated Book"}'
```

Delete an audiobook
```
curl -X DELETE "http://localhost:5003/audiobooks/1001"
```
