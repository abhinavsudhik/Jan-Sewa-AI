# Implementation Plan: Frontend Theme Redesign

## Overview

This implementation plan converts the Government Services Assistant frontend from a purple gradient theme to a simple, sleek black and white theme. The approach is CSS-only, modifying three CSS files while preserving all React components and functionality.

## Tasks

- [x] 1. Set up testing infrastructure
  - Install PostCSS and CSS parsing dependencies for property-based testing
  - Create test utilities for CSS validation
  - Set up test directory structure
  - _Requirements: 8.1, 8.2, 1.1_

- [ ] 2. Update global styles (globals.css)
  - [x] 2.1 Replace purple gradient background with solid white
    - Change body background from `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` to `#FFFFFF`
    - _Requirements: 1.2, 2.1_
  
  - [ ]* 2.2 Write property test for color palette compliance
    - **Property 1: Color Palette Compliance**
    - **Validates: Requirements 1.1, 1.2, 1.5, 6.1, 10.1, 12.2**
  
  - [ ]* 2.3 Write property test for purple color removal
    - **Property 2: Purple Color Removal**
    - **Validates: Requirements 1.2**

- [ ] 3. Update Home.module.css - Header section
  - [x] 3.1 Convert header styling to black and white
    - Change `.header h1` color from `#667eea` to `#000000`
    - Keep `.header p` color as `#666666`
    - Add bottom border: `border-bottom: 1px solid #E0E0E0`
    - _Requirements: 3.1, 3.5, 1.3_
  
  - [ ]* 3.2 Write unit test for header styling
    - Verify header uses black text on white background
    - Verify header has border for separation
    - _Requirements: 3.1, 3.5_

- [ ] 4. Update Home.module.css - Chat container and messages
  - [x] 4.1 Update chat container styling
    - Add border: `border: 1px solid #E0E0E0`
    - Update box-shadow to `0 4px 20px rgba(0, 0, 0, 0.1)`
    - _Requirements: 2.2, 2.3_
  
  - [x] 4.2 Convert message bubble colors
    - Change `.userMessage .messageContent` background from `#667eea` to `#000000`
    - Change `.assistantMessage .messageContent` background from `#f0f0f0` to `#F5F5F5`
    - Ensure `.assistantMessage .messageContent` color is `#000000`
    - _Requirements: 4.1, 4.2, 1.3, 1.4_
  
  - [ ]* 4.3 Write property test for contrast ratio compliance
    - **Property 4: Contrast Ratio Compliance**
    - **Validates: Requirements 4.5, 8.1, 8.2, 7.1**
  
  - [ ]* 4.4 Write unit tests for message styling
    - Verify user messages use black background with white text
    - Verify assistant messages use light gray background with black text
    - _Requirements: 4.1, 4.2_

- [ ] 5. Update Home.module.css - Welcome message
  - [x] 5.1 Convert welcome message styling
    - Change `.welcomeMessage h2` color from `#667eea` to `#000000`
    - Update `.welcomeMessage li` background to `#F5F5F5`
    - Add border to list items: `border: 1px solid #E0E0E0`
    - _Requirements: 11.1, 11.3_
  
  - [ ]* 5.2 Write unit test for welcome message styling
    - Verify welcome message uses black text
    - Verify list items have gray background with border
    - _Requirements: 11.1, 11.3_

- [ ] 6. Update Home.module.css - Input controls
  - [x] 6.1 Convert input field styling
    - Change `.input` border color to `#CCCCCC`
    - Change `.input:focus` border-color from `#667eea` to `#000000`
    - Keep `.input:disabled` background as `#f5f5f5`
    - _Requirements: 5.1, 5.2_
  
  - [x] 6.2 Convert send button styling
    - Change `.sendButton` background from `#667eea` to `#000000`
    - Change `.sendButton:hover` background from `#5568d3` to `#333333`
    - Keep `.sendButton:disabled` background as `#ccc`
    - _Requirements: 5.3, 5.4, 5.5_
  
  - [ ]* 6.3 Write property test for interactive state definitions
    - **Property 6: Interactive State Definitions**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 8.4**
  
  - [ ]* 6.4 Write unit tests for input control styling
    - Verify input field has black border on focus
    - Verify send button uses black background
    - Verify hover and disabled states
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 7. Update Home.module.css - Footer
  - [x] 7.1 Convert footer styling
    - Change `.footer` background to solid `#FFFFFF`
    - Change `.footer` color to `#000000` for emphasis
    - Add top border: `border-top: 1px solid #E0E0E0`
    - _Requirements: 7.3, 7.1_
  
  - [ ]* 7.2 Write unit test for footer styling
    - Verify footer uses black text on white background
    - Verify footer has high contrast
    - _Requirements: 7.3, 7.1_

- [ ] 8. Checkpoint - Verify Home.module.css changes
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Update ServiceGuide.module.css - Container and header
  - [x] 9.1 Convert guide container styling
    - Change `.guideContainer` background from gradient to `#FFFFFF`
    - Change border to `1px solid #E0E0E0`
    - Update box-shadow to `0 2px 8px rgba(0, 0, 0, 0.08)`
    - _Requirements: 6.1, 6.2, 2.2_
  
  - [x] 9.2 Convert header and service name styling
    - Change `.serviceName` color from `#667eea` to `#000000`
    - Change `.header` border-bottom to `2px solid #E0E0E0`
    - _Requirements: 6.1, 6.3_
  
  - [ ]* 9.3 Write property test for gradient elimination
    - **Property 3: Gradient Elimination**
    - **Validates: Requirements 2.1, 2.2, 6.2**

- [ ] 10. Update ServiceGuide.module.css - Steps section
  - [x] 10.1 Convert step styling
    - Change `.step` background to `#FAFAFA`
    - Change `.step` border-left color from `#667eea` to `#000000`
    - Change `.stepNumber` background from `#667eea` to `#000000`
    - Update `.badge` background to `#F5F5F5` with `border: 1px solid #E0E0E0`
    - Update `.badge` color to `#333333`
    - _Requirements: 6.4, 6.3_
  
  - [ ]* 10.2 Write unit test for step styling
    - Verify step numbers use black background with white text
    - Verify badges use gray styling
    - _Requirements: 6.4_

- [ ] 11. Update ServiceGuide.module.css - Portal link and sections
  - [x] 11.1 Convert portal link styling
    - Change `.portalLink` background from `#667eea` to `#000000`
    - Change `.portalLink:hover` background from `#5568d3` to `#333333`
    - _Requirements: 6.5_
  
  - [x] 11.2 Update section backgrounds
    - Ensure `.processingSection`, `.portalSection`, `.contactSection` use `#FFFFFF` background
    - _Requirements: 6.1_
  
  - [ ]* 11.3 Write property test for visual separation through borders
    - **Property 9: Visual Separation Through Borders**
    - **Validates: Requirements 6.2, 6.3, 7.2**

- [ ] 12. Update responsive styles in all CSS files
  - [x] 12.1 Verify media query color consistency
    - Check all `@media` blocks in Home.module.css
    - Check all `@media` blocks in ServiceGuide.module.css
    - Ensure no purple colors remain in responsive styles
    - _Requirements: 10.1, 10.5_
  
  - [ ]* 12.2 Write property test for responsive color consistency
    - **Property 11: Responsive Color Consistency**
    - **Validates: Requirements 10.1**
  
  - [ ]* 12.3 Write property test for touch target sizing
    - **Property 12: Touch Target Sizing**
    - **Validates: Requirements 10.4**

- [ ] 13. Comprehensive property tests
  - [ ]* 13.1 Write property test for layout structure preservation
    - **Property 5: Layout Structure Preservation**
    - **Validates: Requirements 2.3, 7.5, 10.5**
  
  - [ ]* 13.2 Write property test for typography hierarchy preservation
    - **Property 7: Typography Hierarchy Preservation**
    - **Validates: Requirements 3.4, 8.3, 11.2, 11.4**
  
  - [ ]* 13.3 Write property test for border radius consistency
    - **Property 8: Border Radius Consistency**
    - **Validates: Requirements 2.5**
  
  - [ ]* 13.4 Write property test for smooth transitions
    - **Property 10: Smooth Transitions**
    - **Validates: Requirements 9.5**
  
  - [ ]* 13.5 Write property test for focus indicator visibility
    - **Property 13: Focus Indicator Visibility**
    - **Validates: Requirements 8.4, 9.2**
  
  - [ ]* 13.6 Write property test for disabled state styling
    - **Property 14: Disabled State Styling**
    - **Validates: Requirements 9.4**

- [ ] 14. Visual verification and manual testing
  - [x] 14.1 Test in browser across different screen sizes
    - Verify desktop layout (1920x1080, 1366x768)
    - Verify tablet layout (768x1024)
    - Verify mobile layout (375x667, 414x896)
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [x] 14.2 Test interactive states
    - Verify hover states on all interactive elements
    - Verify focus states for keyboard navigation
    - Verify disabled states
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [x] 14.3 Verify accessibility
    - Check contrast ratios with browser dev tools
    - Test keyboard navigation
    - Verify focus indicators are visible
    - _Requirements: 8.1, 8.2, 8.4_

- [ ] 15. Final checkpoint - Complete verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based tests that can be skipped for faster implementation
- Each CSS modification task references specific requirements for traceability
- Property tests validate universal correctness properties across all CSS files
- Unit tests validate specific examples and edge cases
- Manual testing ensures the design meets quality standards
- All React components and TypeScript code remain unchanged
- Focus on systematic color replacement using the defined color palette
