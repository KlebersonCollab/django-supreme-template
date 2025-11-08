# SSO Authentication for Mobile Apps

This document explains how mobile apps can authenticate users using SSO providers (Google, GitHub, Microsoft) and receive Django JWT tokens for API access.

## Overview

The flow allows mobile apps to:
1. Authenticate users with SSO providers (Google, GitHub, Microsoft)
2. Send the SSO token to the Django backend
3. Backend verifies the token and creates/authenticates the user
4. Backend returns Django JWT tokens for subsequent API calls

## Endpoint

**POST** `/api/sso/authenticate/`

### Request

```json
{
  "provider": "google",
  "access_token": "ya29.a0AfH6SMC..."
}
```

**Parameters:**
- `provider` (string, required): One of `google`, `github`, or `microsoft`
- `access_token` (string, required): OAuth access token from the provider

### Response

**Success (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "is_new_user": false
  }
}
```

**Error (400 Bad Request):**
```json
{
  "error": "provider and access_token are required"
}
```

**Error (401 Unauthorized):**
```json
{
  "error": "Invalid or expired token"
}
```

## Mobile App Integration Examples

### Flutter (Dart)

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<Map<String, dynamic>> authenticateWithSSO(
  String provider,
  String accessToken,
) async {
  final response = await http.post(
    Uri.parse('https://your-api.com/api/sso/authenticate/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'provider': provider,
      'access_token': accessToken,
    }),
  );

  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Authentication failed: ${response.body}');
  }
}

// Usage
try {
  final result = await authenticateWithSSO('google', googleAccessToken);
  final jwtToken = result['access'];
  final user = result['user'];
  print('User authenticated: ${user['email']}');
  print('Is new user: ${user['is_new_user']}');
} catch (e) {
  print('Error: $e');
}
```

### React Native (JavaScript)

```javascript
const authenticateWithSSO = async (provider, accessToken) => {
  try {
    const response = await fetch('https://your-api.com/api/sso/authenticate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        provider: provider,
        access_token: accessToken,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Authentication failed');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('SSO Authentication Error:', error);
    throw error;
  }
};

// Usage
authenticateWithSSO('google', googleAccessToken)
  .then((result) => {
    const jwtToken = result.access;
    const user = result.user;
    console.log('User authenticated:', user.email);
    console.log('Is new user:', user.is_new_user);
  })
  .catch((error) => {
    console.error('Error:', error);
  });
```

### Swift (iOS)

```swift
import Foundation

func authenticateWithSSO(provider: String, accessToken: String) async throws -> [String: Any] {
    let url = URL(string: "https://your-api.com/api/sso/authenticate/")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let body: [String: Any] = [
        "provider": provider,
        "access_token": accessToken
    ]
    request.httpBody = try JSONSerialization.data(withJSONObject: body)
    
    let (data, response) = try await URLSession.shared.data(for: request)
    
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NSError(domain: "AuthenticationError", code: 401)
    }
    
    let result = try JSONSerialization.jsonObject(with: data) as? [String: Any]
    return result ?? [:]
}

// Usage
Task {
    do {
        let result = try await authenticateWithSSO(
            provider: "google",
            accessToken: googleAccessToken
        )
        let jwtToken = result["access"] as? String
        let user = result["user"] as? [String: Any]
        print("User authenticated: \(user?["email"] ?? "")")
    } catch {
        print("Error: \(error)")
    }
}
```

## Using JWT Tokens

After receiving JWT tokens, use them in subsequent API requests:

```http
GET /api/user/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Token Refresh

When the access token expires, refresh it:

**POST** `/api/token/refresh/`

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response:
```json
{
  "access": "new_access_token"
}
```

## User Flow

1. **New User:**
   - Mobile app authenticates with Google/GitHub/Microsoft
   - Sends token to `/api/sso/authenticate/`
   - Backend creates new user account
   - Returns JWT tokens with `is_new_user: true`

2. **Existing User:**
   - Mobile app authenticates with Google/GitHub/Microsoft
   - Sends token to `/api/sso/authenticate/`
   - Backend finds existing user (by email or social account)
   - Returns JWT tokens with `is_new_user: false`

## Security Notes

- Always use HTTPS in production
- Store JWT tokens securely (Keychain on iOS, Keystore on Android)
- Implement token refresh before expiration
- Validate tokens on the backend for each request
- Never expose refresh tokens to client-side JavaScript

## Error Handling

Common errors and solutions:

- **400 Bad Request**: Missing or invalid parameters
- **401 Unauthorized**: Invalid or expired SSO token
- **500 Internal Server Error**: Backend issue, check logs

