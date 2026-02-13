# Product Specification: Gaming Events Assistant

## Product Pitch

An AI assistant that reads the room and helps turn casual chat into real game nights. You and a friend are talking about how you've been wanting to play Catan for a while—the assistant picks up on the vibe and chimes in: "Want to lock in a time?" It's ready to help when the moment feels right, not pushy or annoying. Users interact primarily through reactive bots in chat apps (Discord, Slack, Telegram, etc.) and secondarily through a standalone web UI. They use natural language to create gaming events, coordinate with participants, and manage event planning. The assistant handles the complexity of event planning, invitations, and coordination, allowing users to focus on playing games together.

## Interaction Channels

**Primary:** Reactive bots in chat applications. The assistant lives where users already convene—chat apps. It reads the conversation, reacts to the current vibe (e.g. when people mention wanting to play a game or suggest a game night), and offers to help when it feels natural. The system is built generic so it can plug into Discord, Slack, Telegram, and others. Discord is the first integration; new channels can be added without changing core logic.

**Secondary:** A standalone web UI remains available for users who prefer a dedicated interface. It provides a chat-only interface and is not the primary path.

**Architecture (unchanged):** REST APIs, database, and event-user-member flow stay as-is. Chat bots and the standalone UI both consume the same backend.

---

## User-Visible Capabilities

### User Account Management
- **View user information**: Retrieve details for any user by ID or browse all users
- **Update user profiles**: Modify username for existing users
- **Delete user accounts**: Permanently remove users from the system
- **Search users**: Find users by partial matches on username or email address
- **User registration**: Create accounts via signup (auth flow); the agent does not create users

### Event Management
- **Create events**: Create new gaming events with a game name and event name (event creator automatically becomes a host)
- **View event information**: Retrieve details for events the user is a member of
- **Update event plans**: Modify event date/time, location, and name (hosts only)
- **Confirm events**: Mark events as confirmed (hosts only)
- **Cancel events**: Mark events as cancelled (hosts only)
- **Delete events**: Permanently remove events (hosts only)
- **List events**: Browse events the user is a member of, with optional filtering by status, including or excluding cancelled events

### Event Participation & Invitations
- **Invite users to events**: Invite other users (by user ID) to events with roles (host or attendee)
- **Accept event invitations**: Accept pending invitations to events
- **Decline event invitations**: Decline pending invitations
- **Leave events**: Remove yourself from events you're participating in
- **View event membership**: See who is participating in events, their roles, and invitation status

---

## Use Cases & System Guarantees

### Use Case 1: User Registration
**User says**: (via signup flow) "Register with username Alice and email alice@example.com"

**System guarantees**:
- A new user account is created with the provided username and email
- The username and email must be unique (system prevents duplicates)
- The user receives a unique ID that can be used for future operations
- If username or email already exists, the system reports an error
- User creation happens via the auth signup flow; the agent does not create users

### Use Case 2: Event Creation
**User says**: "Create an event for Settlers of Catan called Game Night"

**System guarantees**:
- A new event is created with the specified game name and event name
- The event creator automatically becomes a host with accepted membership
- The event is assigned a unique ID
- The event starts in "planning" status
- Event plan details (date, time, location) can be added or updated later by hosts

### Use Case 3: Event Planning
**User says**: "Set the event date to January 15th at 7pm and location to Community Center for event ID 2"

**System guarantees**:
- Only hosts can update event plan details
- If the user is not a host, the system reports an error

### Use Case 4: Event Invitations
**User says**: "Invite user ID 7 to event ID 2 as an attendee"

**System guarantees**:
- Only accepted event members can send invitations
- Users can be invited with roles: host or attendee
- Only existing hosts can invite other hosts
- Invited users receive a pending invitation
- Users cannot be invited twice to the same event
- Invitations cannot be sent to cancelled events
- If the user or event doesn't exist, the system reports an error

### Use Case 5: Accepting Invitations
**User says**: "Accept the invitation to event ID 5"

**System guarantees**:
- Users can accept pending invitations to events
- Once accepted, the user becomes an active participant
- Invitations cannot be accepted for cancelled events
- If no pending invitation exists, the system reports an error

### Use Case 6: Event Status Management
**User says**: "Confirm event ID 3" or "Cancel event ID 4"

**System guarantees**:
- Only hosts can change event status (confirm or cancel)
- Confirmed events are marked as ready to proceed
- Cancelled events cannot have new invitations
- If the user is not a host, the system reports an error

### Use Case 7: Event Visibility
**User says**: "Show me all my events"

**System guarantees**:
- Users can see events where they are members (pending or accepted)
- Events can be filtered by status (planning, confirmed, cancelled)
- Cancelled events are hidden by default but can be included
- The system shows membership details including role and status

### Use Case 8: Leaving Events
**User says**: "Remove me from event ID 5"

**System guarantees**:
- Users can leave events they're participating in
- If a host leaves, at least one other accepted host must remain
- If the last host tries to leave, the system prevents this and reports an error
- Once left, the user can no longer see or interact with the event

### Use Case 9: Natural Language Interaction
**User says**: "I want to organize a game night for Settlers of Catan next Friday at 7pm"

**System guarantees**:
- The assistant understands the intent and identifies required information
- The assistant asks for missing required information (game name, event name, exact date/time format)
- Once all required information is provided, the event is created
- The assistant provides clear, concise responses in conversational language
- The assistant does not proceed with incomplete or invalid information

### Use Case 10: Vibe-Reactive Assistance (Chat Context)
**Context**: In a group chat, two friends are discussing how they've been wanting to play Catan for a while. The assistant reads the conversation.

**System guarantees**:
- The assistant picks up on the vibe—people talking about wanting to play a game
- When it feels natural, the assistant offers to help (e.g. "Want to lock in a time?")
- The assistant is not pushy; it only chimes in when it clearly adds value
- If the conversation is off-topic or no one is suggesting an event, the assistant stays quiet or keeps it brief

---

## Next Steps

1. **Short chat summaries:** Store text summaries per event in the DB. These summaries capture what happened in the conversation so the agent can reference prior context without re-reading full message history.

2. **Truncated history:** Maintain a sliding window of recent messages per event. The window size depends on context (e.g., event size, channel limits). The agent uses this history so it's not blind to what just happened.

---

## Important Constraints & Non-Goals

### Constraints

1. **Data Integrity Requirements**:
   - Usernames and emails must be unique across all users
   - Users cannot be invited to the same event twice
   - Only hosts can update event plans, change event status, or delete events
   - At least one accepted host must remain in an event (hosts cannot all leave)

2. **Required Information**:
   - User creation (via signup) requires both username and email
   - Event creation requires a game name and event name
   - The system will not proceed with placeholder or empty values

3. **Access Control & Visibility**:
   - Users can only see events where they are members
   - Only hosts can modify event plans and status

4. **Event Lifecycle**:
   - Events start in "planning" status
   - Events can be moved to "confirmed" or "cancelled" status
   - Cancelled events cannot accept new invitations

5. **Conversational Limits**:
   - The assistant operates within the domain of users, events, invitations, event participation, and event planning
   - Responses are concise and formatted for chat interfaces
   - The assistant asks one clear question at a time when information is missing

6. **Deletion Behavior**:
   - User deletion is permanent and cannot be undone
   - Event deletion is permanent (hosts only)
   - Leaving an event removes membership permanently
   - The system does not automatically cascade deletions

### Non-Goals

1. **No Authentication or Authorization Details**: The system manages user accounts but does not specify how users log in or authenticate. All operations assume an authenticated user context. (The implementation uses JWT auth for the web UI.)

2. **No Notifications or Reminders**: The system does not send notifications, reminders, or alerts about upcoming events or plan changes.

3. **No Calendar Integration**: The system does not integrate with external calendar systems or provide calendar views.

4. **No Payment or Billing**: The system does not handle payments, fees, or financial transactions related to events.

5. **No Advanced Social Features**: The system does not provide direct messaging between users, user profiles beyond basic info, ratings, reviews, friend connections, or social networking features beyond event participation.

6. **No Game Library Integration**: The system does not fetch game information from external databases or provide game descriptions, images, or metadata. Events use free-form game names.

7. **No Event Discovery or Recommendations**: The system does not suggest events to users or provide discovery features beyond explicit search and member-based visibility.

8. **No Multi-tenancy or Organizations**: The system does not support multiple organizations, groups, or isolated communities within a single instance.

9. **No File Attachments or Media**: The system does not store or manage images, documents, or other media files in profiles.

10. **No Analytics or Reporting**: The system does not provide analytics, statistics, or reporting features beyond basic data retrieval.

11. **No Event Templates or Recurring Events**: The system does not support event templates or automatically recurring events.

---

This specification describes the product from a user perspective, independent of any implementation details, UI design, or technical architecture.
