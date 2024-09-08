# woox_annc_hub
# API Documentation for Announcement System

## Table of Contents
1. [Introduction](#introduction)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [Endpoints](#endpoints)
   - [Users](#users)
     - [Get Users Information](#get-users-information)
     - [Create User](#create-user)
     - [Delete User](#delete-user)
     - [Update User Information](#update-user-information)
   - [Tickets](#tickets)
     - [Get Ticket Information](#get-ticket-information)
     - [Create Ticket](#create-ticket)
     - [Approve Ticket](#approve-ticket)
     - [Reject Ticket](#reject-ticket)
     - [Delete Ticket](#delete-ticket)
   - [Chats](#chats)
     - [Get Chat Information](#get-chat-information)
     - [Create Chat](#create-chat)
     - [Update Chat Information](#update-chat-information)
     - [Delete Chat](#delete-chat)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)

## Introduction
This document provides documentation for the Announcement System API. The API is built using FastAPI and provides endpoints for managing users, tickets, and chats.

## Base URL
The base URL for all API endpoints is:
```
https://woox-annc-hub-api-b46c8e32ff33.herokuapp.com
```

## Authentication
All endpoints require API key authentication. To access the API, you need to include two headers in your requests:

- `X-API-KEY`: Your API key
- `X-API-SECRET`: Your API secret

To obtain an API key and secret, please contact the development team. The API key creation endpoint is not publicly accessible for security reasons.

Example of including the headers in a curl request:
```
curl -H "X-API-KEY: your_api_key" -H "X-API-SECRET: your_api_secret" https://woox-annc-hub-api-b46c8e32ff33.herokuapp.com/endpoint
```

If the API key or secret is invalid, the API will return a 403 Forbidden error.

## Endpoints

### Users
Prefix: `/users`

#### Get Users Information
Retrieves information about users based on specified parameters.

- **URL**: `/users/info`
- **Method**: `GET`
- **Authentication**: Required

##### Input Parameters

| Parameter | Type    | Required | Description                           |
|-----------|---------|----------|---------------------------------------|
| user_id   | string  | No       | Filter by user ID                     |
| name      | string  | No       | Filter by user name                   |
| admin     | boolean | No       | Filter by admin status                |
| whitelist | boolean | No       | Filter by whitelist status            |
| num       | integer | No       | Number of results to return (default: 100) |

##### Output Format

| Field   | Type   | Description                  |
|---------|--------|------------------------------|
| status  | integer| Status code (1 for success)  |
| data    | array  | Array of user objects        |

##### Example Output

```json
{
  "status": 1,
  "data": [
    {
      "user_id": "12345",
      "name": "John Doe",
      "admin": false,
      "whitelist": true,
      "created_timestamp": 1631234567890,
      "updated_timestamp": 1631234567890
    },
    {
      "user_id": "67890",
      "name": "Jane Smith",
      "admin": true,
      "whitelist": true,
      "created_timestamp": 1631234567891,
      "updated_timestamp": 1631234567891
    }
  ]
}
```

#### Create User
Creates a new user.

- **URL**: `/users/create`
- **Method**: `POST`
- **Authentication**: Required

##### Input Parameters

| Parameter | Type    | Required | Description        |
|-----------|---------|----------|--------------------|
| user_id   | string  | Yes      | Unique user ID     |
| name      | string  | Yes      | User's name        |
| admin     | boolean | No       | Admin status       |
| whitelist | boolean | No       | Whitelist status   |

##### Output Format

| Field   | Type   | Description                  |
|---------|--------|------------------------------|
| status  | integer| Status code (1 for success)  |
| data    | object | Object containing inserted_id|

##### Example Output

```json
{
  "status": 1,
  "data": {
    "inserted_id": "60f1a5b9e6b3f1234567890a"
  }
}
```

#### Delete User
Deletes a user by their user ID.

- **URL**: `/users/delete`
- **Method**: `POST`
- **Authentication**: Required

##### Input Parameters

| Parameter | Type   | Required | Description    |
|-----------|--------|----------|----------------|
| user_id   | string | Yes      | User ID to delete |

##### Output Format

| Field   | Type    | Description                  |
|---------|---------|------------------------------|
| status  | integer | Status code (1 for success)  |
| data    | object  | Object containing delete_status |

##### Example Output

```json
{
  "status": 1,
  "data": {
    "delete_status": true
  }
}
```

#### Update User Information
Updates information for a specific user.

- **URL**: `/users/update`
- **Method**: `POST`
- **Authentication**: Required

##### Input Parameters

| Parameter | Type    | Required | Description        |
|-----------|---------|----------|--------------------|
| user_id   | string  | Yes      | User ID to update  |
| name      | string  | No       | New name           |
| admin     | boolean | No       | New admin status   |
| whitelist | boolean | No       | New whitelist status |

##### Output Format

| Field   | Type    | Description                  |
|---------|---------|------------------------------|
| status  | integer | Status code (1 for success)  |
| data    | object  | Object containing update info|

##### Example Output

```json
{
  "status": 1,
  "data": {
    "user_id": "12345",
    "name": "John Doe",
    "admin": false,
    "whitelist": true,
    "updated_timestamp": 1631234567890,
    "created_timestamp": 1631234567890
  }
}
```

### Tickets
Prefix: `/tickets`

#### Get Ticket Information
Retrieves information about tickets based on specified parameters.

- **URL**: `/tickets/info`
- **Method**: `GET`
- **Authentication**: Required

##### Input Parameters

| Parameter                    | Type    | Required | Description                           |
|------------------------------|---------|----------|---------------------------------------|
| ticket_id                    | string  | No       | Filter by ticket ID                   |
| creator_id                   | string  | No       | Filter by creator ID                  |
| start_created_timestamp      | integer | No       | Filter by creation start time         |
| end_created_timestamp        | integer | No       | Filter by creation end time           |
| start_status_changed_timestamp| integer | No       | Filter by status change start time    |
| end_status_changed_timestamp  | integer | No       | Filter by status change end time      |
| status                       | string  | No       | Filter by ticket status               |
| num                          | integer | No       | Number of results to return (default: 100) |

##### Output Format

| Field     | Type    | Description                  |
|-----------|---------|------------------------------|
| status    | integer | Status code (1 for success)  |
| data_num  | integer | Number of tickets returned   |
| data      | array   | Array of ticket objects      |

##### Example Output

```json
{
  "status": 1,
  "data_num": 2,
  "data": [
    {
      "ticket_id": "POST-1234567890abcdef",
      "action": "post_annc",
      "status": "pending",
      "creator_id": "12345",
      "creator_name": "John Doe",
      "created_timestamp": 1631234567890,
      "updated_timestamp": 1631234567890,
      "annc": {
        "annc_type": "text",
        "content_text": "This is a test announcement",
        "category": "general",
        "language": "en",
        "chats": ["chat1", "chat2"]
      }
    },
    {
      "ticket_id": "EDIT-0987654321fedcba",
      "action": "edit_annc",
      "status": "approved",
      "creator_id": "67890",
      "creator_name": "Jane Smith",
      "approver_id": "11111",
      "approver_name": "Admin User",
      "created_timestamp": 1631234567891,
      "updated_timestamp": 1631234567892,
      "status_changed_timestamp": 1631234567892,
      "old_annc": {
        "annc_type": "text",
        "content_text": "Old announcement text",
        "category": "general",
        "language": "en",
        "chats": ["chat1"]
      },
      "new_annc": {
        "annc_type": "text",
        "content_text": "Updated announcement text",
        "category": "general",
        "language": "en",
        "chats": ["chat1", "chat2"]
      }
    }
  ]
}
```

#### Create Ticket
Creates a new ticket for posting, editing, or deleting an announcement.

- **URL**: `/tickets/create`
- **Method**: `POST`
- **Authentication**: Required

##### Input Parameters

| Parameter | Type    | Required | Description        |
|-----------|---------|----------|--------------------|
| ticket    | object  | Yes      | Ticket object      |

The `ticket` object should be one of `PostTicket`, `EditTicket`, or `DeleteTicket`, depending on the action.

##### Output Format

| Field   | Type    | Description                  |
|---------|---------|------------------------------|
| status  | integer | Status code (1 for success)  |
| data    | object  | Object containing inserted_id|

##### Example Output

```json
{
  "status": 1,
  "data": {
    "inserted_id": "60f1a5b9e6b3f1234567890a"
  }
}
```

#### Approve Ticket
Approves a pending ticket.

- **URL**: `/tickets/approve`
- **Method**: `POST`
- **Authentication**: Required

##### Input Parameters

| Parameter | Type   | Required | Description    |
|-----------|--------|----------|----------------|
| ticket_id | string | Yes      | Ticket ID to approve |
| user_id   | string | Yes      | User ID of the approver |

##### Output Format

| Field   | Type    | Description                  |
|---------|---------|------------------------------|
| status  | integer | Status code (1 for success)  |
| data    | object  | Object containing update info|

##### Example Output

```json
{
    "status": 1,
    "data": {
        "created_timestamp": 1725781699347,
        "updated_timestamp": 1725781700153,
        "ticket_id": "POST-9ae761f9f78f4cf6a238a9fc59caf747",
        "action": "post_annc",
        "status": "approved",
        "creator_id": "test-123",
        "creator_name": "test",
        "approver_id": "dev-test",
        "approver_name": "dev-test",
        "status_changed_timestamp": 1725781700153,
        "annc": {
            "annc_type": "text",
            "content_text": "This is a test announcement",
            "content_html": "<p>This is a test announcement</p>",
            "content_md": "This is a test announcement",
            "file_id": null,
            "category": "test",
            "language": "en",
            "label": ["test"],
            "chats": ["test-123"],
            "actual_chats": ["test-123"]
        }
    }
}
```

#### Reject Ticket
Rejects a pending ticket.

- **URL**: `/tickets/reject`
- **Method**: `POST`
- **Authentication**: Required

##### Input Parameters

| Parameter | Type   | Required | Description    |
|-----------|--------|----------|----------------|
| ticket_id | string | Yes      | Ticket ID to reject |
| user_id   | string | Yes      | User ID of the rejector |

##### Output Format

| Field   | Type    | Description                  |
|---------|---------|------------------------------|
| status  | integer | Status code (1 for success)  |
| data    | object  | Object containing update info|

##### Example Output

```json
{
    "status": 1,
    "data": {
        "created_timestamp": 1725782033733,
        "updated_timestamp": 1725782034565,
        "ticket_id": "POST-0b4743055dd544ba81d09dea6df56fe8",
        "action": "post_annc",
        "status": "rejected",
        "creator_id": "test-123",
        "creator_name": "test",
        "approver_id": "dev-test",
        "approver_name": "dev-test",
        "status_changed_timestamp": 1725782034565,
        "annc": {
            "annc_type": "text",
            "content_text": "This is a test announcement",
            "content_html": "<p>This is a test announcement</p>",
            "content_md": "This is a test announcement",
            "file_id": null,
            "category": "test",
            "language": "en",
            "label": ["test"],
            "chats": ["test-123"],
            "actual_chats": ["test-123"]
        }
    }
}
```

#### Delete Ticket
Deletes a ticket.

- **URL**: `/tickets/delete`
- **Method**: `POST`
- **Authentication**: Required

##### Input Parameters

| Parameter | Type   | Required | Description    |
|-----------|--------|----------|----------------|
| ticket_id | string | Yes      | Ticket ID to delete |

##### Output Format

| Field   | Type    | Description                  |
|---------|---------|------------------------------|
| status  | integer | Status code (1 for success)  |
| data    | object  | Object containing delete_status |

##### Example Output

```json
{
  "status": 1,
  "data": {
    "delete_status": true
  }
}
```

### Chats
Prefix: `/chats`

#### Get Chat Information
Retrieves information about chats based on specified parameters.

- **URL**: `/chats/info`
- **Method**: `GET`
- **Authentication**: Required

##### Input Parameters

| Parameter | Type    | Required | Description                           |
|-----------|---------|----------|---------------------------------------|
| chat_id   | string  | No       | Filter by chat ID                     |
| name      | string  | No       | Filter by chat name                   |
| chat_type | string  | No       | Filter by chat type                   |
| language  | array   | No       | Filter by language(s)                 |
| category  | array   | No       | Filter by category(ies)               |
| label     | array   | No       | Filter by label(s)                    |
| num       | integer | No       | Number of results to return (default: 100) |

##### Output Format

| Field   | Type    | Description                  |
|---------|---------|------------------------------|
| status  | integer | Status code (1 for success)  |
| data    | array   | Array of chat objects        |

##### Example Output

```json
{
  "status": 1,
  "data": [
    {
      "chat_id": "123456789",
      "name": "General Discussion",
      "chat_type": "group",
      "language": ["en"],
      "category": ["general"],
      "label": ["public"],
      "active": true,
      "created_timestamp": 1631234567890,
      "updated_timestamp": 1631234567890
    },
    {
      "chat_id": "987654321",
      "name": "Tech News",
      "chat_type": "channel",
      "language": ["en", "es"],
      "category": ["technology"],
      "label": ["news", "tech"],
      "active": true,
      "created_timestamp": 1631234567891,
      "updated_timestamp": 1631234567891
    }
  ]
}
```

#### Create Chat
Creates a new chat.

- **URL**: `/chats/create`
- **Method**: `POST`
- **Authentication**: Required

##### Input Parameters

| Parameter | Type    | Required | Description        |
|-----------|---------|----------|--------------------|
| chat_id   | string  | Yes      | Unique chat ID     |
| name      | string  | Yes      | Chat name          |
| chat_type | string  | Yes      | Chat type          |
| language  | array   | No       | Chat languages     |
| category  | array   | No       | Chat categories    |
| label     | array   | No       | Chat labels        |
| active    | boolean | No       | Chat active status |

##### Output Format

| Field   | Type    | Description                  |
|---------|---------|------------------------------|
| status  | integer | Status code (1 for success)  |
| data    | object  | Object containing inserted_id|

##### Example Output

```json
{
  "status": 1,
  "data": {
    "inserted_id": "60f1a5b9e6b3f1234567890a"
  }
}
```

#### Update Chat Information
Updates information for a specific chat.

- **URL**: `/chats/update`
- **Method**: `POST`
- **Authentication**: Required

##### Input Parameters

| Parameter | Type    | Required | Description        |
|-----------|---------|----------|--------------------|
| chat_id   | string  | Yes      | Chat ID to update  |
| name      | string  | No       | New chat name      |
| chat_type | string  | No       | New chat type      |
| language  | array   | No       | New chat languages |
| category  | array   | No       | New chat categories|
| label     | array   | No       | New chat labels    |
| active    | boolean | No       | New active status  |

##### Output Format

| Field   | Type    | Description                  |
|---------|---------|------------------------------|
| status  | integer | Status code (1 for success)  |
| data    | object  | Object containing update info|

##### Example Output

```json
{
  "status": 1,
  "data": {
    "chat_id": "test-1725782356",
    "name": "test chat",
    "chat_type": "supergroup",
    "language": [
      "en",
      "ch",
      "jp"
    ],
    "category": [
      "listing",
      "delisting",
      "maintenance",
      "other"
    ],
    "label": [
      "label1",
      "label2",
      "label3"
    ],
    "active": true,
    "created_timestamp": 1725782356421,
    "updated_timestamp": 1725782357344
  }
}
```

#### Delete Chat
Deletes a chat.

- **URL**: `/chats/delete`
- **Method**: `POST`
- **Authentication**: Required

##### Input Parameters

| Parameter | Type   | Required | Description    |
|-----------|--------|----------|----------------|
| chat_id   | string | Yes      | Chat ID to delete |

##### Output Format

| Field   | Type    | Description                  |
|---------|---------|------------------------------|
| status  | integer | Status code (1 for success)  |
| data    | object  | Object containing delete_status |

##### Example Output

```json
{
  "status": 1,
  "data": {
    "delete_status": true
  }
}
```
