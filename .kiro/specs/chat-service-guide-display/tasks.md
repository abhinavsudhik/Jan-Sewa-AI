# Implementation Plan: Chat Service Guide Display

## Overview

This implementation plan breaks down the service guide display fix into discrete coding tasks. The approach is incremental: first establish TypeScript types, then update the message handling to preserve service guide data, then create the display component, add styling, and finally implement tests. Each task builds on the previous ones, ensuring no orphaned code.

## Tasks

- [x] 1. Create TypeScript type definitions
  - Create `frontend/types/chat.ts` file
  - Define ServiceStep, ProcessingTime, ContactInfo, ServiceGuide, and ChatResponse interfaces matching the backend schema
  - Export all interfaces for use in components
  - _Requirements: 10.1, 10.2_

- [ ] 2. Update message handling to preserve service guide data
  - [x] 2.1 Modify Message interface in index.tsx to include optional serviceGuide field
    - Update the Message interface to add `serviceGuide?: ServiceGuide`
    - Import ServiceGuide type from types/chat.ts
    - _Requirements: 1.1, 1.2_
  
  - [x] 2.2 Update sendMessage function to preserve service_guide from API response
    - Modify the assistantMessage object creation to include `serviceGuide: response.data.service_guide`
    - Ensure the field is preserved even when null/undefined
    - _Requirements: 1.1, 1.3_
  
  - [ ]* 2.3 Write property test for service guide detection
    - **Property 1: Service Guide Detection**
    - **Validates: Requirements 1.1, 1.2, 1.3**

- [ ] 3. Create ServiceGuideDisplay component
  - [x] 3.1 Create component file and basic structure
    - Create `frontend/components/ServiceGuideDisplay.tsx`
    - Define ServiceGuideDisplayProps interface
    - Create functional component with props destructuring
    - Add semantic HTML container with aria-label
    - _Requirements: 2.1, 2.2, 9.1, 9.2_
  
  - [x] 3.2 Implement guide header section
    - Render service_name as h3 heading
    - Render description as paragraph
    - Use semantic HTML elements
    - _Requirements: 2.1, 2.2_
  
  - [x] 3.3 Implement steps list section
    - Map over steps array to render ordered list
    - Display step_number, description, and estimated_duration for each step
    - Add conditional rendering for online_available and requires_in_person indicators
    - Add conditional rendering for optional notes field
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  
  - [x] 3.4 Implement processing time section
    - Display typical processing time prominently
    - Display minimum and maximum range
    - Map over factors array to display all factors
    - Use safe optional chaining for nested fields
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 3.5 Implement official portal link section
    - Render official_portal_url as anchor element
    - Add target="_blank" and rel="noopener noreferrer" attributes
    - Add descriptive label text
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [x] 3.6 Implement contact information section
    - Use definition list (dl) for semantic structure
    - Conditionally render phone, email, helpline, and address fields
    - Add clear labels for each contact type
    - Use optional chaining to handle missing fields
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ]* 3.7 Write property test for complete field rendering
    - **Property 2: Complete Field Rendering**
    - **Validates: Requirements 2.1, 2.2, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 6.1, 6.2, 6.3, 6.4, 6.5**
  
  - [ ]* 3.8 Write property test for step sequential ordering
    - **Property 3: Step Sequential Ordering**
    - **Validates: Requirements 3.1**
  
  - [ ]* 3.9 Write property test for conditional availability indicators
    - **Property 4: Conditional Availability Indicators**
    - **Validates: Requirements 3.5, 3.6, 3.7**

- [ ] 4. Integrate ServiceGuideDisplay into chat interface
  - [x] 4.1 Update message rendering logic in index.tsx
    - Import ServiceGuideDisplay component
    - Add conditional rendering: if msg.serviceGuide exists, render ServiceGuideDisplay
    - Pass msg.serviceGuide as guide prop
    - Ensure regular message content still displays
    - _Requirements: 1.3, 2.1, 2.2_
  
  - [ ]* 4.2 Write unit tests for message rendering integration
    - Test message with service guide renders both content and guide
    - Test message without service guide renders only content
    - Test multiple messages with mixed content
    - _Requirements: 1.1, 1.2, 1.3_

- [ ] 5. Create styling for ServiceGuideDisplay
  - [x] 5.1 Create ServiceGuide.module.css file
    - Define styles for guide container with distinct background color (light tint matching #667eea theme)
    - Add border or shadow for visual separation
    - Define styles for header section (service name and description)
    - Define styles for steps list with step number badges
    - Define styles for processing time section
    - Define styles for official portal link with icon/styling
    - Define styles for contact info section using definition list styling
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [x] 5.2 Add responsive styles for mobile devices
    - Add media query for screens below 768px
    - Stack sections vertically on small screens
    - Ensure touch targets are at least 44x44px
    - Use responsive font sizes
    - Prevent horizontal overflow
    - _Requirements: 8.1, 8.2, 8.3_
  
  - [x] 5.3 Import and apply CSS module classes in ServiceGuideDisplay component
    - Import styles from ServiceGuide.module.css
    - Apply className to all elements
    - Ensure visual consistency with existing chat interface
    - _Requirements: 7.1, 7.3_

- [ ] 6. Checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify the chat interface displays service guides correctly
  - Test with the existing "how to change Aadhaar name" query
  - Ask the user if questions arise

- [ ] 7. Add property tests for accessibility and link rendering
  - [ ]* 7.1 Write property test for official portal link rendering
    - **Property 5: Official Portal Link Rendering**
    - **Validates: Requirements 5.1, 5.2, 5.3**
  
  - [ ]* 7.2 Write property test for semantic HTML structure
    - **Property 6: Semantic HTML Structure**
    - **Validates: Requirements 9.1, 9.3**
  
  - [ ]* 7.3 Write property test for ARIA label presence
    - **Property 7: ARIA Label Presence**
    - **Validates: Requirements 9.2**

- [ ] 8. Add unit tests for edge cases
  - [ ]* 8.1 Write unit test for empty steps array
    - Test that component handles empty steps gracefully
    - _Requirements: 3.1_
  
  - [ ]* 8.2 Write unit test for missing optional contact fields
    - Test that component handles missing phone, email, address, helpline
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [ ]* 8.3 Write unit test for missing notes in steps
    - Test that steps without notes render correctly
    - _Requirements: 3.7_
  
  - [ ]* 8.4 Write unit test for very long text content
    - Test that long service names and descriptions don't break layout
    - _Requirements: 7.2, 8.1_

- [ ] 9. Final checkpoint - Ensure all tests pass
  - Run complete test suite (unit + property tests)
  - Manually test the chat interface with various queries
  - Verify mobile responsiveness using browser dev tools
  - Verify accessibility with keyboard navigation
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties across all possible inputs
- Unit tests validate specific examples, edge cases, and integration points
- The implementation uses TypeScript for type safety throughout
