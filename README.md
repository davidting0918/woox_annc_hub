# Table of Contents
1. [API Documentation](#api-documentation)
2. [Bot Process](#bot-process)

##  API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication Header (Required for all endpoints):
```
X-API-KEY: your-api-key
X-API-SECRET: your-api-secret
```

### API Structure
1. [Users API](#users-api)
   1. [Get User Information](#1-get-user-information)
   2. [Check Whitelist Status](#2-check-whitelist-status)
   3. [Check Admin Status](#3-check-admin-status)
   4. [Update User Dashboard](#4-update-user-dashboard)
   5. [Create User](#5-create-user)
   6. [Delete User](#6-delete-user)
   7. [Update User](#7-update-user)
2. [Chats API](#chats-api)
   1. [Get Chat Information](#1-get-chat-information)
   2. [Update Chat Dashboard](#2-update-chat-dashboard)
   3. [Create Chat](#3-create-chat)
   4. [Update Chat](#4-update-chat)
   5. [Delete Chat](#5-delete-chat)
3. [Tickets API](#tickets-api)
   1. [Get Ticket Information](#1-get-ticket-information)
   2. [Update Ticket Dashboard](#2-update-ticket-dashboard)
   3. [Create Ticket](#3-create-ticket)
   4. [Approve Ticket](#4-approve-ticket)
   5. [Reject Ticket](#5-reject-ticket)
   6. [Delete Ticket](#6-delete-ticket)
   7. [Update Ticket](#7-update-ticket)

### 1. Get User Information
```http
GET /users/info
```

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | No | Filter by specific user ID |
| name | string | No | Filter by user name |
| admin | boolean | No | Filter by admin status |
| whitelist | boolean | No | Filter by whitelist status |
| num | integer | No | Number of results (default: 100) |

#### Example Response
```json
{
  "status": 1,
  "data": [
    {
      "user_id": "12345",
      "name": "John Doe",
      "admin": true,
      "whitelist": true,
      "created_timestamp": 1634567890000,
      "updated_timestamp": 1634567890000
    }
  ]
}
```

### 2. Check Whitelist Status
```http
GET /users/in_whitelist
```

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User ID to check whitelist status |

#### Example Response
```json
{
  "status": 1,
  "data": true
}
```

### 3. Check Admin Status
```http
GET /users/is_admin
```

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User ID to check admin status |

#### Example Response
```json
{
  "status": 1,
  "data": true
}
```

### 4. Update User Dashboard
```http
GET /users/update_dashboard
```

#### Example Response
```json
{
  "status": 1,
  "data": [
    {
      "User Id": "12345",
      "Name": "John Doe",
      "Admin": "V",
      "Whitelist": "V",
      "Created Timestamp": "2023-10-20 10:30:00",
      "Updated Timestamp": "2023-10-20 10:30:00"
    }
  ]
}
```

### 5. Create User
```http
POST /users/create
```

#### Request Body Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | Unique identifier for the user |
| name | string | Yes | User's name |
| admin | boolean | No | Admin status (default: false) |
| whitelist | boolean | No | Whitelist status (default: true) |

#### Example Request
```json
{
  "user_id": "12345",
  "name": "John Doe",
  "admin": true,
  "whitelist": true
}
```

### 6. Delete User
```http
POST /users/delete
```

#### Request Body Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | ID of user to delete |

#### Example Response
```json
{
  "status": 1,
  "data": {
    "delete_status": true
  }
}
```

### 7. Update User
```http
POST /users/update
```

#### Request Body Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User ID to update |
| name | string | No | New name |
| admin | boolean | No | New admin status |
| whitelist | boolean | No | New whitelist status |

## Chats API
Base path: `/chats`

### 1. Get Chat Information
```http
GET /chats/info
```

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chat_id | string/List[string] | No | Filter by chat ID(s) |
| name | string/List[string] | No | Filter by chat name(s) |
| chat_type | string | No | Type of chat (group/channel/supergroup) |
| language | List[string] | No | Filter by language(s) |
| category | List[string] | No | Filter by category(ies) |
| label | List[string] | No | Filter by label(s) |
| active | boolean | No | Filter by active status (default: true) |
| num | integer | No | Number of results (default: 1000) |

### 2. Update Chat Dashboard
```http
GET /chats/update_dashboard
```

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| direction | string | Yes | "pull" or "push" |

#### Example Response
```json
{
  "status": 1,
  "data": {
    "post_tickets": [...],
    "edit_tickets": [...],
    "delete_tickets": [...]
  }
}
```

### 3. Create Chat
```http
POST /chats/create
```

#### Request Body Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chat_id | string | Yes | Unique chat identifier |
| name | string | Yes | Chat name |
| chat_type | string | Yes | Type (group/channel/supergroup) |
| language | List[string] | No | List of languages |
| category | List[string] | No | List of categories |
| label | List[string] | No | List of labels |
| active | boolean | No | Active status (default: true) |
| description | string | No | Chat description |

### 4. Update Chat
```http
POST /chats/update
```

#### Request Body Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chat_id | string | Yes | Chat ID to update |
| name | string | No | New chat name |
| chat_type | string | No | New chat type |
| language | List[string] | No | New language list |
| category | List[string] | No | New category list |
| label | List[string] | No | New label list |
| active | boolean | No | New active status |
| description | string | No | New description |

### 5. Delete Chat
```http
POST /chats/delete
```

#### Request Body Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chat_id | string | Yes | Chat ID to delete |

## Tickets API
Base path: `/tickets`

### 1. Get Ticket Information
```http
GET /tickets/info
```

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ticket_id | string | No | Filter by ticket ID |
| creator_id | string | No | Filter by creator ID |
| start_created_timestamp | integer | No | Filter by creation time start |
| end_created_timestamp | integer | No | Filter by creation time end |
| start_status_changed_timestamp | integer | No | Filter by status change time start |
| end_status_changed_timestamp | integer | No | Filter by status change time end |
| status | string | No | Filter by status (pending/approved/rejected) |
| num | integer | No | Number of results (default: 100) |

### 2. Update Ticket Dashboard
```http
GET /tickets/update_dashboard
```

#### Example Response
```json
{
  "status": 1,
  "data": {
    "post_tickets": [...],
    "edit_tickets": [...],
    "delete_tickets": [...]
  }
}
```

### 3. Create Ticket
```http
POST /tickets/create
```

#### Request Body Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action | string | Yes | Ticket action (`post_annc`/`edit_annc`/`delete_annc`) |
| ticket | object | Yes | Ticket details object |

#### Post Announcement Ticket Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| content_text | string | Yes | Plain text content |
| content_html | string | Yes | HTML formatted content |
| content_md | string | Yes | Markdown content |
| annc_type | string | Yes | Type (text/image/video/file) |
| category | string | No | Announcement category |
| language | string | No | Announcement language |
| label | List[string] | No | Announcement labels |
| file_path | string | No | Media file path |

#### Edit Announcement Ticket Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| old_ticket_id | string | Yes | Original ticket ID |
| new_content_text | string | Yes | New plain text content |
| new_content_html | string | Yes | New HTML content |
| new_content_md | string | Yes | New markdown content |

#### Delete Announcement Ticket Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| old_ticket_id | string | Yes | Ticket ID to delete |

### 4. Approve Ticket
```http
POST /tickets/approve
```

#### Request Body Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ticket_id | string | Yes | Ticket ID to approve |
| user_id | string | Yes | Approving user's ID |

### 5. Reject Ticket
```http
POST /tickets/reject
```

#### Request Body Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ticket_id | string | Yes | Ticket ID to reject |
| user_id | string | Yes | Rejecting user's ID |

### 6. Delete Ticket
```http
POST /tickets/delete
```

#### Request Body Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ticket_id | string | Yes | Ticket ID to delete |


### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Bot Process
### Introduction
This project run with 2 bots (`command_bot` and `event_bot`).
1. `command_bot` is the main bot that handle all requests from team members. This bot will accept command include `/post`, `/edit`, `/delete`, `/change_permission`, `/check_permission`, `/cancel` and `/help`
2. `event_bot` is the bot that handle all events from the chat and sending the announcement to the clients' group.

### Function Pipeline ([Dashboard](https://docs.google.com/spreadsheets/d/1k2P8Ok0O6d9J3_WWDiEbmKpIkKrWYG96gB52zrEGOf0/edit?gid=0#gid=0))
- `/post`
  1. Use `/post` command to post an announcement.
  2. Choose a category from the category button.
  3. If the category is `others`, then input label or chat name. If the category is not `others`, then choose the language.
  4. Input the content of the announcement, including text, image, video, document.
  5. The ticket will be sent to admin group for approval.
  6. Admin click `Approve` or `Reject` button to approve or reject the ticket.
- `/edit`
  1. Input the post ticket id want to edit (need to start with `POST-`)
  2. Input the new content of the announcement, then the ticket will be sent to admin group for approval.
  3. Admin click `Approve` or `Reject` button to approve or reject the ticket.
- `/delete`
  1. Input the post ticket id want to delete (need to start with `POST-`)
  2. The ticket will be sent to admin group for approval.
  3. Admin click `Approve` or `Reject` button to approve or reject the ticket.
- `/change_permission`
  1. Choose the `Add` or `Remove` button to adjust the permission.
  2. Choose from `Admin` or `Whitelist` or `Both` button to adjust the permission.
  3. Then refer a message from the user to adjust the permission.

> [!TIP]
> You can use `/cancel` command to cancel the process at any time.


