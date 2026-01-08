# Product Specification: Gaming Events Assistant

## Product Pitch

A conversational AI assistant that helps users organize and participate in gaming events. Users interact with the system through natural language to manage their game collection, create gaming events, coordinate with friends, and communicate about upcoming games. The assistant handles all the complexity of event planning, invitations, and coordination, allowing users to focus on playing games together.

---

## User-Visible Capabilities

### User Account Management
- **Create user accounts**: Register new users with a unique username and email address
- **View user information**: Retrieve details for any user by ID or browse all users
- **Update user profiles**: Modify username or email address for existing users
- **Delete user accounts**: Permanently remove users from the system
- **Search users**: Find users by partial matches on username or email address

### Friend Connections
- **Send friend requests**: Request to connect with another user
- **Accept friend requests**: Accept incoming friend requests from other users
- **List friends**: View all accepted friend connections
- **View friend requests**: See both incoming and outgoing pending friend requests

### Game Collection Management
- **Add games to collection**: Register games with name, optional description, and optional player count
- **View game information**: Retrieve details for any game by ID or browse all games in the collection
- **Search games**: Find games by partial matches on name

### Event Management
- **Create events**: Create new gaming events by selecting a game (event creator automatically becomes a host)
- **View event information**: Retrieve details for events the user can see (events they're part of or where friends are participating)
- **Update event plans**: Modify event date/time and location (hosts only)
- **Confirm events**: Mark events as confirmed (hosts only)
- **Cancel events**: Mark events as cancelled (hosts only)
- **Delete events**: Permanently remove events (hosts only)
- **List events**: Browse events with optional filtering by status, including or excluding cancelled events

### Event Participation & Invitations
- **Invite users to events**: Invite other users to events with roles (host or attendee)
- **Accept event invitations**: Accept pending invitations to events
- **Decline event invitations**: Decline pending invitations
- **Leave events**: Remove yourself from events you're participating in
- **View event membership**: See who is participating in events, their roles, and invitation status

### Event Planning & Coordination
- **Confirm plan versions**: Confirm that you're aware of the current event plan details
- **Track plan changes**: System tracks when event plans are updated and maintains version numbers
- **View plan status**: See whether you've confirmed the current plan version

### Event Communication
- **Post messages to events**: Send messages to event participants
- **View event messages**: Read messages posted to events you're participating in

---

## Use Cases & System Guarantees

### Use Case 1: User Registration
**User says**: "Create a new user named Alice with email alice@example.com"

**System guarantees**:
- A new user account is created with the provided username and email
- The username and email must be unique (system prevents duplicates)
- The user receives a unique ID that can be used for future operations
- If username or email already exists, the system reports an error

### Use Case 2: Building Friendships
**User says**: "Send a friend request to user ID 5" or "Accept the friend request from Alice"

**System guarantees**:
- Friend requests can be sent to any user (except yourself)
- Users cannot send duplicate friend requests
- Users can accept or decline incoming friend requests
- Once accepted, both users can see each other in their friends list
- The system prevents duplicate friendships

### Use Case 3: Game Collection Building
**User says**: "Add a game called Settlers of Catan that supports up to 4 players"

**System guarantees**:
- A new game entry is created with the specified details
- The game receives a unique ID for future reference
- Games can be searched by name
- Game information can be updated or viewed at any time

### Use Case 4: Event Creation
**User says**: "Create an event for game ID 10"

**System guarantees**:
- A new event is created and associated with the specified game
- The event creator automatically becomes a host with accepted membership
- The event is assigned a unique ID
- The event starts in "planning" status
- The game must exist (system validates this)
- Event plan details (date, time, location) can be added or updated later by hosts

### Use Case 5: Event Planning
**User says**: "Set the event date to January 15th at 7pm and location to Community Center for event ID 2"

**System guarantees**:
- Only hosts can update event plan details
- When plan details change, the system increments the plan version number
- All participants need to confirm they've seen the new plan version
- The system tracks when plans were last updated
- If the user is not a host, the system reports an error

### Use Case 6: Event Invitations
**User says**: "Invite user ID 7 to event ID 2 as an attendee"

**System guarantees**:
- Only accepted event members can send invitations
- Users can be invited with roles: host or attendee
- Only existing hosts can invite other hosts
- Invited users receive a pending invitation
- Users cannot be invited twice to the same event
- Invitations cannot be sent to cancelled events
- If the user or event doesn't exist, the system reports an error

### Use Case 7: Accepting Invitations
**User says**: "Accept the invitation to event ID 5"

**System guarantees**:
- Users can accept pending invitations to events
- Once accepted, the user becomes an active participant
- Invitations cannot be accepted for cancelled events
- If no pending invitation exists, the system reports an error

### Use Case 8: Event Status Management
**User says**: "Confirm event ID 3" or "Cancel event ID 4"

**System guarantees**:
- Only hosts can change event status (confirm or cancel)
- Confirmed events are marked as ready to proceed
- Cancelled events cannot have new invitations or messages
- If the user is not a host, the system reports an error

### Use Case 9: Plan Confirmation
**User says**: "I've seen the updated plan for event ID 2"

**System guarantees**:
- Accepted event members can confirm they've seen the current plan version
- The system tracks which plan version each member has confirmed
- This helps coordinate when plans change
- Only accepted members can confirm plans

### Use Case 10: Event Visibility
**User says**: "Show me all my events" or "What events are my friends going to?"

**System guarantees**:
- Users can see events where they are members (pending or accepted)
- Users can see events where their accepted friends are accepted members
- Events can be filtered by status (planning, confirmed, cancelled)
- Cancelled events are hidden by default but can be included
- The system shows membership details including role and confirmation status

### Use Case 11: Event Communication
**User says**: "Post a message to event ID 2 saying 'Bring snacks!'"

**System guarantees**:
- Only accepted event members can post messages
- Messages are associated with the event and the posting user
- All accepted members can read messages for events they're in
- Messages cannot be posted to cancelled events
- If the user is not an accepted member, the system reports an error

### Use Case 12: Leaving Events
**User says**: "Remove me from event ID 5"

**System guarantees**:
- Users can leave events they're participating in
- If a host leaves, at least one other accepted host must remain
- If the last host tries to leave, the system prevents this and reports an error
- Once left, the user can no longer see or interact with the event

### Use Case 13: Natural Language Interaction
**User says**: "I want to organize a game night for Settlers of Catan next Friday at 7pm"

**System guarantees**:
- The assistant understands the intent and identifies required information
- The assistant asks for missing required information (game must exist, exact date/time format)
- Once all required information is provided, the event is created
- The assistant provides clear, concise responses in conversational language
- The assistant does not proceed with incomplete or invalid information

---

## Important Constraints & Non-Goals

### Constraints

1. **Data Integrity Requirements**:
   - Usernames and emails must be unique across all users
   - Users cannot send friend requests to themselves
   - Users cannot be invited to the same event twice
   - Events must be associated with an existing game
   - Only hosts can update event plans, change event status, or delete events
   - Only accepted members can post messages to events
   - At least one accepted host must remain in an event (hosts cannot all leave)

2. **Required Information**:
   - User creation requires both username and email
   - Game creation requires at least a name
   - Event creation requires an existing game ID
   - The system will not proceed with placeholder or empty values

3. **Access Control & Visibility**:
   - Users can only see events where they are members or where accepted friends are accepted members
   - Only hosts can modify event plans and status
   - Only accepted members can post messages
   - Only accepted members can confirm plan versions
   - Friend connections must be mutual (both users must accept)

4. **Event Lifecycle**:
   - Events start in "planning" status
   - Events can be moved to "confirmed" or "cancelled" status
   - Cancelled events cannot accept new invitations or messages
   - Plan changes increment version numbers automatically
   - Members must confirm new plan versions to acknowledge changes

5. **Conversational Limits**:
   - The assistant operates within the domain of users, games, events, friendships, and event communication
   - Responses are concise and formatted for chat interfaces
   - The assistant asks one clear question at a time when information is missing

6. **Deletion Behavior**:
   - User deletion is permanent and cannot be undone
   - Game deletion is permanent
   - Event deletion is permanent (hosts only)
   - Leaving an event removes membership permanently
   - The system does not automatically cascade deletions

### Non-Goals

1. **No Authentication or Authorization Details**: The system manages user accounts but does not specify how users log in or authenticate. All operations assume an authenticated user context.

2. **No Notifications or Reminders**: The system does not send notifications, reminders, or alerts about upcoming events, friend requests, or plan changes.

3. **No Calendar Integration**: The system does not integrate with external calendar systems or provide calendar views.

4. **No Payment or Billing**: The system does not handle payments, fees, or financial transactions related to events.

5. **No Advanced Social Features**: The system does not provide direct messaging between users, user profiles beyond basic info, ratings, reviews, or social networking features beyond friend connections.

6. **No Game Library Integration**: The system does not fetch game information from external databases or provide game descriptions, images, or metadata beyond what users provide.

7. **No Event Discovery or Recommendations**: The system does not suggest events to users or provide discovery features beyond explicit search and friend-based visibility.

8. **No Multi-tenancy or Organizations**: The system does not support multiple organizations, groups, or isolated communities within a single instance.

9. **No File Attachments or Media**: The system does not store or manage images, documents, or other media files in event messages or profiles.

10. **No Analytics or Reporting**: The system does not provide analytics, statistics, or reporting features beyond basic data retrieval.

11. **No Message History Management**: The system does not provide message editing, deletion, or advanced message threading beyond basic posting and viewing.

12. **No Event Templates or Recurring Events**: The system does not support event templates or automatically recurring events.

---

This specification describes the product from a user perspective, independent of any implementation details, UI design, or technical architecture.
