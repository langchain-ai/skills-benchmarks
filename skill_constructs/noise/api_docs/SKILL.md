---
name: api-docs
description: OpenAPI documentation and REST API design patterns
---

# API Documentation Standards

Design and document RESTful APIs following industry standards.

## OpenAPI Specification

Always document APIs using OpenAPI 3.0+:

```yaml
openapi: 3.0.3
info:
  title: User API
  version: 1.0.0

paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      required: [id, email]
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
```

## REST Conventions

1. Use nouns for resources: `/users`, `/orders`
2. Use HTTP methods correctly: GET, POST, PUT, PATCH, DELETE
3. Return appropriate status codes: 200, 201, 400, 404, 500
4. Use pagination for lists: `?page=1&limit=20`
5. Version your API: `/v1/users`

## Error Responses

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      {"field": "email", "message": "Invalid email format"}
    ]
  }
}
```
