### Register a user
```
curl -X POST "http://localhost:5000/register" -H "Content-Type: application/json" -d '{"username": "testuser", "password": "testpassword"}'
```

### Login
```
curl -X POST "http://localhost:5000/login" -H "Content-Type: application/json" -d '{"username": "testuser", "password": "testpassword"}'
```
