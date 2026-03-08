# Requirements Document

## Introduction

The Jan Seva AI chat application currently fails to display service guide information when responding to user queries. When users ask about government services (e.g., "how to change the Aadhaar name"), the backend correctly returns a ChatResponse containing both a message string and a detailed ServiceGuide object. However, the frontend only renders the message field and completely ignores the service_guide data, resulting in an incomplete user experience where users see "Here's the complete guide:" but no actual guide content is displayed.

This feature will fix the frontend to properly detect and render service guide information in a structured, accessible format that presents all the detailed steps, processing times, contact information, and official portal links that the backend is already providing.

## Glossary

- **Chat_Frontend**: The Next.js React application that renders the chat interface (frontend/pages/index.tsx)
- **Chat_Response**: The API response object containing both a message string and an optional ServiceGuide object
- **Service_Guide**: A structured object containing comprehensive information about a government service, including steps, processing times, contact info, and official portal URLs
- **Service_Step**: An individual step within a service guide, containing step number, description, duration estimate, and availability flags
- **Message_Renderer**: The component responsible for displaying chat messages in the UI
- **Guide_Display**: The visual presentation of service guide information in a structured format

## Requirements

### Requirement 1: Service Guide Detection

**User Story:** As a user, I want the chat interface to automatically detect when a response includes service guide information, so that I can see the complete guide without any additional action.

#### Acceptance Criteria

1. WHEN THE Chat_Response contains a non-null service_guide field, THEN THE Chat_Frontend SHALL detect its presence
2. WHEN THE Chat_Response contains a null service_guide field, THEN THE Chat_Frontend SHALL render only the message text
3. WHEN THE service_guide field is detected, THEN THE Chat_Frontend SHALL pass the service guide data to the Guide_Display component

### Requirement 2: Service Guide Header Display

**User Story:** As a user, I want to see the service name and description prominently displayed, so that I can quickly understand what service the guide covers.

#### Acceptance Criteria

1. WHEN THE Service_Guide is rendered, THEN THE Guide_Display SHALL display the service_name as a heading
2. WHEN THE Service_Guide is rendered, THEN THE Guide_Display SHALL display the description text below the service name
3. WHEN THE Service_Guide is rendered, THEN THE Guide_Display SHALL visually distinguish the guide header from regular message text

### Requirement 3: Step-by-Step Instructions Display

**User Story:** As a user, I want to see each step of the service process clearly numbered and described, so that I can follow the instructions in the correct order.

#### Acceptance Criteria

1. WHEN THE Service_Guide contains steps, THEN THE Guide_Display SHALL render each Service_Step in sequential order
2. FOR EACH Service_Step, THE Guide_Display SHALL display the step_number prominently
3. FOR EACH Service_Step, THE Guide_Display SHALL display the description text
4. FOR EACH Service_Step, THE Guide_Display SHALL display the estimated_duration
5. WHEN a Service_Step has online_available set to true, THEN THE Guide_Display SHALL indicate that the step can be completed online
6. WHEN a Service_Step has requires_in_person set to true, THEN THE Guide_Display SHALL indicate that in-person visit is required
7. WHEN a Service_Step contains notes, THEN THE Guide_Display SHALL display the notes text

### Requirement 4: Processing Time Information Display

**User Story:** As a user, I want to see how long the service will take to process, so that I can set appropriate expectations.

#### Acceptance Criteria

1. WHEN THE Service_Guide contains processing_time, THEN THE Guide_Display SHALL display the typical processing duration
2. WHEN THE Service_Guide contains processing_time, THEN THE Guide_Display SHALL display the minimum and maximum duration range
3. WHEN THE processing_time contains factors, THEN THE Guide_Display SHALL list all factors that affect processing time

### Requirement 5: Official Portal Link Display

**User Story:** As a user, I want to see a link to the official government portal, so that I can access the authoritative source for the service.

#### Acceptance Criteria

1. WHEN THE Service_Guide contains official_portal_url, THEN THE Guide_Display SHALL render it as a clickable hyperlink
2. WHEN THE official_portal_url link is clicked, THEN THE Chat_Frontend SHALL open the URL in a new browser tab
3. THE Guide_Display SHALL clearly label the link as the official portal

### Requirement 6: Contact Information Display

**User Story:** As a user, I want to see contact information for the service, so that I can get help if I encounter issues.

#### Acceptance Criteria

1. WHEN THE Service_Guide contains contact_info with a phone number, THEN THE Guide_Display SHALL display the phone number
2. WHEN THE Service_Guide contains contact_info with an email address, THEN THE Guide_Display SHALL display the email address
3. WHEN THE Service_Guide contains contact_info with a helpline number, THEN THE Guide_Display SHALL display the helpline number
4. WHEN THE Service_Guide contains contact_info with an address, THEN THE Guide_Display SHALL display the address
5. THE Guide_Display SHALL clearly label each type of contact information

### Requirement 7: Visual Distinction

**User Story:** As a user, I want service guides to look visually different from regular chat messages, so that I can easily identify structured guidance information.

#### Acceptance Criteria

1. WHEN THE Service_Guide is rendered, THEN THE Guide_Display SHALL use a distinct background color or border to separate it from regular messages
2. WHEN THE Service_Guide is rendered, THEN THE Guide_Display SHALL use appropriate spacing and typography to enhance readability
3. THE Guide_Display SHALL maintain visual consistency with the overall chat interface design

### Requirement 8: Mobile Responsiveness

**User Story:** As a mobile user, I want service guides to display properly on my phone screen, so that I can access government service information on the go.

#### Acceptance Criteria

1. WHEN THE Service_Guide is rendered on a mobile device, THEN THE Guide_Display SHALL adapt its layout to fit the screen width
2. WHEN THE Service_Guide is rendered on a mobile device, THEN THE Guide_Display SHALL maintain readability without requiring horizontal scrolling
3. WHEN THE Service_Guide is rendered on a mobile device, THEN THE Guide_Display SHALL ensure all interactive elements (links) are easily tappable

### Requirement 9: Accessibility Compliance

**User Story:** As a user with accessibility needs, I want service guides to be accessible with screen readers and keyboard navigation, so that I can access government service information independently.

#### Acceptance Criteria

1. WHEN THE Service_Guide is rendered, THEN THE Guide_Display SHALL use semantic HTML elements for proper structure
2. WHEN THE Service_Guide is rendered, THEN THE Guide_Display SHALL provide appropriate ARIA labels for screen readers
3. WHEN THE Service_Guide contains links, THEN THE Guide_Display SHALL ensure all links are keyboard accessible
4. THE Guide_Display SHALL maintain sufficient color contrast ratios for text readability

### Requirement 10: TypeScript Type Safety

**User Story:** As a developer, I want proper TypeScript interfaces for service guide data, so that I can catch type errors at compile time and maintain code quality.

#### Acceptance Criteria

1. THE Chat_Frontend SHALL define TypeScript interfaces matching the backend ServiceGuide schema
2. THE Chat_Frontend SHALL define TypeScript interfaces for ServiceStep, ProcessingTime, and ContactInfo
3. WHEN THE Chat_Response is received, THE Chat_Frontend SHALL type-check the service_guide field against the ServiceGuide interface
4. THE Guide_Display component SHALL use typed props for all service guide data
