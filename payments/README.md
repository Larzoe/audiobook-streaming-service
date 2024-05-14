Create a payment
```
curl -X POST "http://localhost:5002/payments" -H "Content-Type: application/json" -d '{"user_id": 1, "amount": 9.99}'
```

Handle a callback (update payment status)
```
curl -X POST "http://localhost:5002/payments/1001/callback" -H "Content-Type: application/json" -d '{"status": "paid"}'
```

Get payment details
```
curl -X GET "http://localhost:5002/payments/1001"
```
