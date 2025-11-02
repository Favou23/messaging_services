### Building and running your application

When you're ready, start your application by running:
`docker compose up --build`.

Your application will be available at http://localhost:8000.

### Deploying your application to the cloud

First, build your image, e.g.: `docker build -t myapp .`.
If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t myapp .`.

Then, push it to your registry, e.g. `docker push myregistry.com/myapp`.


Complete Postman Testing Guide

Method: POST
URL: http://auth.localhost/api/register/

Headers:
Content-Type: application/json

Body (raw JSON):
```sh
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "TestPass123!",
  "first_name": "Alice",
  "last_name": "Wonder"
}
```

Expected Response: 201 Created
```sh
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com"
}
```

#### Request 2: Register Bob
```sh
Method: POST
URL: http://auth.localhost/api/register/
```

Body:
```sh
{
  "username": "bob",
  "email": "bob@example.com",
  "password": "TestPass123!",
  "first_name": "Bob",
  "last_name": "Builder"
}
```

Expected Response: 201 Created
```sh
{
  "id": 2,
  "username": "bob",
  "email": "bob@example.com"
}
```

---

### **Phase 2: Login & Get Tokens**

#### Request 3: Login as Alice
```sh
Method: POST
URL: http://auth.localhost/api/login/

Headers:
Content-Type: application/json
```

Body:
```sh
{
  "username": "alice",
  "password": "TestPass123!"
}

Expected Response: 200 OK
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

📝 COPY THE ACCESS TOKEN!
```

In Postman Tests Tab (Auto-save tokens):

var jsonData = pm.response.json();
pm.environment.set("alice_token", jsonData.access);
pm.environment.set("alice_refresh", jsonData.refresh);
console.log("Alice tokens saved!");
```

#### Request 4: Login as Bob
```
Same as above, but with Bob's credentials

In Tests Tab:
var jsonData = pm.response.json();
pm.environment.set("bob_token", jsonData.access);
pm.environment.set("bob_refresh", jsonData.refresh);
```

---

### **Phase 3: Create Chat Room**

#### Request 5: Create Room
```
Method: POST
URL: http://chat.localhost/api/chat/rooms/

Headers:
Content-Type: application/json
Authorization: Bearer {{alice_token}}

Body:
{
  "participant_a": "alice",
  "participant_b": "bob"
}

Expected Response: 201 Created
{
  "id": 1,
  "participant_a": "alice",
  "participant_b": "bob",
  "created_at": "2025-11-02T20:18:12.365841Z"
}

In Tests Tab:
var jsonData = pm.response.json();
pm.environment.set("room_id", jsonData.id);
```

---

### **Phase 4: Send Messages (REST API)**

#### Request 6: Send Message via REST
```
Method: POST
URL: http://chat.localhost/api/chat/rooms/{{room_id}}/messages/

Headers:
Content-Type: application/json
Authorization: Bearer {{alice_token}}

Body:
{
  "sender_id": "alice",
  "content": "Hi Bob! How are you?"
}

Expected Response: 201 Created
{
  "id": 1,
  "room": 1,
  "sender_id": "alice",
  "content": "Hi Bob! How are you?",
  "timestamp": "2025-11-02T20:30:00Z",
  "is_read": false
}
```

#### Request 7: Get All Messages
```
Method: GET
URL: http://chat.localhost/api/chat/rooms/{{room_id}}/messages/

Headers:
Authorization: Bearer {{alice_token}}

Expected Response: 200 OK
[
  {
    "id": 1,
    "room": 1,
    "sender_id": "alice",
    "content": "Hi Bob! How are you?",
    "timestamp": "2025-11-02T20:30:00Z",
    "is_read": false
  }
]
```

---

### **Phase 5: Test WebSocket (Postman)**

**Note:** Postman's WebSocket support is limited. For real-time testing, use:
- The HTML file I provided
- Or wscat: `wscat -c ws://chat.localhost/ws/chat/1/`

But if you have **Postman v10+** with WebSocket support:
```
1. Create New → WebSocket Request
2. URL: ws://chat.localhost/ws/chat/1/
3. Click "Connect"
4. In Message box, send:
   {"message": "Hello from Postman!", "username": "alice", "sender_id": "alice"}
5. Watch for incoming messages
```

---

### **Phase 6: Token Refresh**

#### Request 8: Refresh Token
```
Method: POST
URL: http://auth.localhost/api/token/refresh/

Headers:
Content-Type: application/json

Body:
{
  "refresh": "{{alice_refresh}}"
}

Expected Response: 200 OK
{
  "access": "NEW_ACCESS_TOKEN_HERE"
}

In Tests Tab:
var jsonData = pm.response.json();
pm.environment.set("alice_token", jsonData.access);
```

---

### **Phase 7: Get User Profile**

#### Request 9: Get Profile
```
Method: GET
URL: http://auth.localhost/api/users/profile/

Headers:
Authorization: Bearer {{alice_token}}

Expected Response: 200 OK
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com"
}
```

---

### **Phase 8: Logout**

#### Request 10: Logout
```
Method: POST
URL: http://auth.localhost/api/logout/

Headers:
Authorization: Bearer {{alice_token}}
Content-Type: application/json

Body:
{
  "refresh": "{{alice_refresh}}"
}

Expected Response: 200 OK
```

---

## **Postman Collection Structure**

Create folders:
```
📁 Auth API
  └─ Register Alice
  └─ Register Bob
  └─ Login Alice
  └─ Login Bob
  └─ Get Profile
  └─ Refresh Token
  └─ Logout

📁 Chat API
  └─ Create Room
  └─ Get Room Messages
  └─ Send Message