Get all audiobooks
```
curl -X GET "http://localhost:5001/audiobooks"
```

Add a new audiobook
```
curl -X POST "http://localhost:5001/audiobooks" -H "Content-Type: application/json" -d '{"title": "New Book", "author": "Author Name", "genre": "Genre"}'
```

Update an audiobook
```
curl -X PUT "http://localhost:5001/audiobooks/1" -H "Content-Type: application/json" -d '{"title": "Updated Book"}'
```

Delete an audiobook
```
curl -X DELETE "http://localhost:5001/audiobooks/1"
```
