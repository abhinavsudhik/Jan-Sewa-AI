# Chat Query Response Bug - Bugfix Design

## Overview

The chat system has a hardcoded keyword matching approach that only recognizes "aadhaar" + "name" queries, causing it to fail for all other service queries. The system advertises services like "data access requests" and "service status tracking" in the welcome message but has no logic to handle these queries. The fix will implement a more flexible keyword matching system that can recognize queries for any service in MOCK_SERVICES and provide appropriate responses for services that don't yet have guides.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when users query about advertised services other than "aadhaar name change"
- **Property (P)**: The desired behavior when valid service queries are made - return relevant service guide or helpful "coming soon" message
- **Preservation**: Existing "aadhaar name change" query handling, session ID generation, and language handling that must remain unchanged
- **process_chat**: The function in `backend/app/api/v1/chat.py` that handles incoming chat messages and returns responses
- **MOCK_SERVICES**: The dictionary in `backend/app/api/v1/services.py` containing available service guides
- **keyword matching**: The current approach of checking if specific words appear in the user's query

## Bug Details

### Bug Condition

The bug manifests when a user sends a query about services other than "aadhaar name change". The `process_chat` function only has hardcoded logic for the specific keyword combination "aadhaar" AND "name", causing all other service queries to fall through to the generic welcome message.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type ChatMessage
  OUTPUT: boolean
  
  user_message := input.message.toLowerCase()
  
  RETURN (containsServiceKeywords(user_message, ["data", "access"]) OR
          containsServiceKeywords(user_message, ["status", "tracking"]) OR
          containsServiceKeywords(user_message, ["service"]))
         AND NOT (user_message.contains("aadhaar") AND user_message.contains("name"))
END FUNCTION
```

### Examples

- Query: "How do I request data access?" → Returns: Generic welcome message (WRONG) → Should return: Service guide or "coming soon" message
- Query: "I need help with service status tracking" → Returns: Generic welcome message (WRONG) → Should return: Service guide or "coming soon" message
- Query: "data access request" → Returns: Generic welcome message (WRONG) → Should return: Service guide or "coming soon" message
- Query: "tell me about services" → Returns: Generic welcome message (CORRECT - this is appropriately vague)

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Queries containing "aadhaar" and "name" keywords must continue to return the Aadhaar name change service guide
- Generic greetings or unclear queries must continue to return the welcome message with available service options
- Session ID generation must continue to work (generate new UUID if not provided, use provided session_id if given)
- Language field must continue to be preserved in responses

**Scope:**
All inputs that do NOT involve queries about advertised services (other than "aadhaar name change") should be completely unaffected by this fix. This includes:
- Generic greetings ("hello", "hi")
- Unclear or vague queries
- Queries about "aadhaar name change"
- Session ID handling logic
- Language handling logic

## Hypothesized Root Cause

Based on the code analysis, the root cause is clear:

1. **Hardcoded Single-Service Logic**: The `process_chat` function only has one `if` statement checking for "aadhaar" AND "name" keywords, with no logic for other services

2. **No Service Discovery Mechanism**: The function doesn't check MOCK_SERVICES to see what services are available or attempt to match user queries to available services

3. **Missing Keyword Mapping**: There's no mapping between service keywords (like "data access", "status tracking") and service IDs in MOCK_SERVICES

4. **No Fallback for Unimplemented Services**: The system advertises services in the welcome message but has no logic to handle queries about services that don't yet have guides in MOCK_SERVICES

## Correctness Properties

Property 1: Bug Condition - Service Query Recognition

_For any_ chat message where the user queries about advertised services (containing keywords like "data access", "status tracking", or other service-related terms), the fixed process_chat function SHALL either return the corresponding service guide from MOCK_SERVICES if available, or return a helpful "coming soon" message indicating the service is being developed.

**Validates: Requirements 2.1, 2.2, 2.3**

Property 2: Preservation - Existing Aadhaar, Session, and Language Handling

_For any_ chat message that does NOT query about new services (including "aadhaar name change" queries, generic greetings, and unclear queries), the fixed process_chat function SHALL produce exactly the same response as the original function, preserving the Aadhaar name change service guide response, welcome message behavior, session ID generation, and language handling.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

## Fix Implementation

### Changes Required

**File**: `backend/app/api/v1/chat.py`

**Function**: `process_chat`

**Specific Changes**:
1. **Add Service Keyword Mapping**: Create a dictionary mapping service keywords to service IDs in MOCK_SERVICES
   - Map ["data", "access"] → check for "data_access_request" in MOCK_SERVICES
   - Map ["status", "tracking"] → check for "service_status_tracking" in MOCK_SERVICES
   - Keep ["aadhaar", "name"] → "aadhaar_name_change"

2. **Implement Flexible Keyword Matching**: Replace the single hardcoded `if` statement with a loop that checks all service keyword patterns
   - For each service keyword pattern, check if all keywords appear in the user message
   - Return the first matching service guide if found in MOCK_SERVICES

3. **Add "Coming Soon" Response**: When a query matches service keywords but the service doesn't exist in MOCK_SERVICES
   - Return a helpful message: "I understand you're asking about [service]. This service guide is coming soon. For now, please contact..."
   - Include session_id and language in the response

4. **Preserve Existing Logic**: Ensure the changes don't affect:
   - Session ID generation (use provided or generate new UUID)
   - Language field preservation
   - Welcome message for unclear queries
   - Aadhaar name change response

5. **Maintain Fallback Behavior**: Keep the generic welcome message as the final fallback for truly unclear queries

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm that queries for advertised services (other than "aadhaar name change") fail to return service guides.

**Test Plan**: Write tests that send queries about "data access" and "status tracking" to the unfixed endpoint. Run these tests on the UNFIXED code to observe that they return only the generic welcome message instead of service-specific responses.

**Test Cases**:
1. **Data Access Query Test**: Send "How do I request data access?" (will fail on unfixed code - returns welcome message)
2. **Status Tracking Query Test**: Send "I need help with service status tracking" (will fail on unfixed code - returns welcome message)
3. **Service Keyword Query Test**: Send "data access request" (will fail on unfixed code - returns welcome message)
4. **Multiple Service Keywords Test**: Send queries with various keyword combinations (will fail on unfixed code)

**Expected Counterexamples**:
- All queries about non-aadhaar services return the generic welcome message
- No service_guide field is populated in the response
- The system advertises services it cannot help with

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  result := process_chat_fixed(input)
  ASSERT (result.service_guide IS NOT None) OR 
         (result.message.contains("coming soon"))
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT process_chat_original(input) = process_chat_fixed(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for "aadhaar name change" queries, generic greetings, and session/language handling, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Aadhaar Name Change Preservation**: Observe that "aadhaar name change" queries return the service guide on unfixed code, then verify this continues after fix
2. **Welcome Message Preservation**: Observe that generic greetings return the welcome message on unfixed code, then verify this continues after fix
3. **Session ID Preservation**: Observe that session IDs are generated or preserved correctly on unfixed code, then verify this continues after fix
4. **Language Preservation**: Observe that language fields are preserved in responses on unfixed code, then verify this continues after fix

### Unit Tests

- Test specific service keyword queries ("data access", "status tracking")
- Test edge cases (queries with partial keywords, mixed case, extra whitespace)
- Test that "aadhaar name change" continues to work
- Test that generic greetings return welcome message
- Test session ID generation and preservation
- Test language field preservation

### Property-Based Tests

- Generate random service queries and verify they either return a service guide or "coming soon" message
- Generate random non-service queries and verify preservation of welcome message behavior
- Generate random session IDs and verify they are preserved or generated correctly
- Test across many language values to ensure preservation

### Integration Tests

- Test full chat flow with multiple service queries in sequence
- Test switching between different service queries
- Test that session context is maintained across multiple queries
- Test that language preferences are respected throughout conversation
