# Design Document: Frontend Theme Redesign

## Overview

This design document outlines the technical approach for converting the Government Services Assistant frontend from a purple gradient theme to a simple, sleek black and white theme. The redesign focuses on CSS modifications while preserving all existing functionality and component structure.

The current implementation uses Next.js with TypeScript, CSS Modules for component styling, and a global CSS file for base styles. The purple gradient theme (#667eea, #764ba2) is applied through multiple CSS files that need systematic conversion to a black and white color palette.

## Architecture

### Design Approach

The redesign follows a **CSS-only modification strategy** that:
- Maintains the existing React component structure
- Preserves all TypeScript interfaces and logic
- Updates only CSS files (globals.css, Home.module.css, ServiceGuide.module.css)
- Uses a systematic color replacement approach

### Color Palette Definition

The new black and white theme uses a carefully selected grayscale palette:

```
Primary Colors:
- Pure Black: #000000 (primary text, buttons, emphasis)
- Pure White: #FFFFFF (primary backgrounds, button text)

Grayscale Spectrum:
- Dark Gray: #333333 (secondary text, dark elements)
- Medium Gray: #666666 (tertiary text, borders)
- Light Gray: #999999 (disabled states, subtle borders)
- Very Light Gray: #CCCCCC (hover states, light borders)
- Off White: #F5F5F5 (subtle backgrounds, input fields)
- Near White: #FAFAFA (container backgrounds)

Shadows and Overlays:
- rgba(0, 0, 0, 0.1) - Light shadows
- rgba(0, 0, 0, 0.2) - Medium shadows
- rgba(0, 0, 0, 0.05) - Subtle overlays
```

### File Structure

```
frontend/
├── styles/
│   ├── globals.css           # Global styles, body background
│   ├── Home.module.css       # Main page and chat interface
│   └── ServiceGuide.module.css # Service guide component
├── pages/
│   └── index.tsx             # No changes required
└── components/
    └── ServiceGuideDisplay.tsx # No changes required
```

## Components and Interfaces

### 1. Global Styles (globals.css)

**Current State:**
- Purple gradient background: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`

**New Design:**
- Solid white background: `#FFFFFF`
- Clean, minimal base styling

**Key Changes:**
```css
body {
  background: #FFFFFF;
  min-height: 100vh;
}
```

### 2. Header Component

**Current State:**
- White background with purple title (#667eea)
- Gray subtitle (#666)

**New Design:**
- White background maintained
- Black title text (#000000)
- Dark gray subtitle (#666666)
- Subtle bottom border for separation

**Styling Approach:**
```css
.header {
  background: #FFFFFF;
  border-bottom: 1px solid #E0E0E0;
}

.header h1 {
  color: #000000;
  font-weight: 700;
}

.header p {
  color: #666666;
}
```

### 3. Chat Container

**Current State:**
- White background with shadow
- Rounded corners

**New Design:**
- Maintain white background
- Enhanced shadow for depth: `0 4px 20px rgba(0, 0, 0, 0.1)`
- Subtle border: `1px solid #E0E0E0`

### 4. Message Bubbles

**Current State:**
- User messages: Purple background (#667eea), white text
- Assistant messages: Light gray background (#f0f0f0), dark text

**New Design:**
- User messages: Black background (#000000), white text (#FFFFFF)
- Assistant messages: Off-white background (#F5F5F5), black text (#000000)
- Maintain rounded corners and spacing

**Styling Approach:**
```css
.userMessage .messageContent {
  background: #000000;
  color: #FFFFFF;
  border-bottom-right-radius: 4px;
}

.assistantMessage .messageContent {
  background: #F5F5F5;
  color: #000000;
  border-bottom-left-radius: 4px;
}
```

### 5. Input Controls

**Current State:**
- Input field: Light gray border, purple focus border
- Send button: Purple background, white text

**New Design:**
- Input field: Medium gray border (#CCCCCC), black focus border (#000000)
- Send button: Black background (#000000), white text (#FFFFFF)
- Hover state: Slightly lighter black (#333333)
- Disabled state: Light gray (#CCCCCC)

**Styling Approach:**
```css
.input {
  border: 2px solid #CCCCCC;
  background: #FFFFFF;
}

.input:focus {
  border-color: #000000;
}

.sendButton {
  background: #000000;
  color: #FFFFFF;
}

.sendButton:hover:not(:disabled) {
  background: #333333;
}

.sendButton:disabled {
  background: #CCCCCC;
}
```

### 6. Welcome Message

**Current State:**
- Purple heading (#667eea)
- Gray text (#666)
- Light gray list items (#f5f5f5)

**New Design:**
- Black heading (#000000)
- Dark gray text (#666666)
- Off-white list items (#F5F5F5) with subtle border

**Styling Approach:**
```css
.welcomeMessage h2 {
  color: #000000;
}

.welcomeMessage li {
  background: #F5F5F5;
  border: 1px solid #E0E0E0;
}
```

### 7. Footer

**Current State:**
- White background with transparency
- Gray text

**New Design:**
- Solid white background (#FFFFFF)
- Black text (#000000) for emphasis
- Top border for separation

**Styling Approach:**
```css
.footer {
  background: #FFFFFF;
  border-top: 1px solid #E0E0E0;
  color: #000000;
}
```

### 8. Service Guide Display

**Current State:**
- Purple gradient background with transparency
- Purple borders and accents
- Purple step numbers and links

**New Design:**
- White background with subtle gray border
- Black text for headings
- Black step numbers with white text
- Gray badges and metadata
- Black links with hover effects

**Key Sections:**

**Guide Container:**
```css
.guideContainer {
  background: #FFFFFF;
  border: 1px solid #E0E0E0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
```

**Service Name and Header:**
```css
.serviceName {
  color: #000000;
  font-weight: 600;
}

.header {
  border-bottom: 2px solid #E0E0E0;
}
```

**Steps:**
```css
.step {
  background: #FAFAFA;
  border-left: 4px solid #000000;
}

.stepNumber {
  background: #000000;
  color: #FFFFFF;
}
```

**Badges and Metadata:**
```css
.badge {
  background: #F5F5F5;
  color: #333333;
  border: 1px solid #E0E0E0;
}
```

**Portal Link:**
```css
.portalLink {
  background: #000000;
  color: #FFFFFF;
}

.portalLink:hover {
  background: #333333;
}
```

## Data Models

No data model changes are required. All TypeScript interfaces remain unchanged:

- `Message` interface (role, content, serviceGuide)
- `ServiceGuide` interface and nested types
- Component props interfaces

## Correctness Properties


*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Color Palette Compliance

*For all* CSS files in the theme system (globals.css, Home.module.css, ServiceGuide.module.css), every color value (hex, rgb, rgba) should be from the approved black and white palette: #000000, #FFFFFF, #333333, #666666, #999999, #CCCCCC, #E0E0E0, #F5F5F5, #FAFAFA, or rgba values using only (0,0,0) or (255,255,255) with varying alpha.

**Validates: Requirements 1.1, 1.2, 1.5, 6.1, 10.1, 12.2**

### Property 2: Purple Color Removal

*For all* CSS files in the theme system, the specific purple color values #667eea and #764ba2 should not appear anywhere in the code.

**Validates: Requirements 1.2**

### Property 3: Gradient Elimination

*For all* CSS files in the theme system, no linear-gradient or radial-gradient values should be present, ensuring depth is created through borders and shadows instead.

**Validates: Requirements 2.1, 2.2, 6.2**

### Property 4: Contrast Ratio Compliance

*For all* text elements and their backgrounds defined in the CSS, the contrast ratio should be at least 4.5:1 for normal text and at least 3:1 for interactive elements against adjacent colors.

**Validates: Requirements 4.5, 8.1, 8.2, 7.1**

### Property 5: Layout Structure Preservation

*For all* CSS rules that define layout properties (display, flex-direction, grid-template-columns, position, flex, align-items, justify-content), the values should remain unchanged from the original CSS files.

**Validates: Requirements 2.3, 7.5, 10.5**

### Property 6: Interactive State Definitions

*For all* interactive elements (buttons, inputs, links), the CSS should define :hover, :focus, :active, and :disabled pseudo-class styles with appropriate visual feedback properties (background, border, opacity, or box-shadow changes).

**Validates: Requirements 9.1, 9.2, 9.3, 9.4, 8.4**

### Property 7: Typography Hierarchy Preservation

*For all* CSS rules that define font-size and font-weight properties, the values should remain unchanged from the original CSS files, ensuring hierarchy is maintained through typography rather than color.

**Validates: Requirements 3.4, 8.3, 11.2, 11.4**

### Property 8: Border Radius Consistency

*For all* CSS rules that define border-radius, the values should be from a consistent set: 4px, 8px, 12px, 16px, 18px, 20px, or 25px.

**Validates: Requirements 2.5**

### Property 9: Visual Separation Through Borders

*For all* section containers and major UI divisions (header, footer, guide sections), the CSS should define either a border or box-shadow property to create visual separation.

**Validates: Requirements 6.2, 6.3, 7.2**

### Property 10: Smooth Transitions

*For all* interactive elements that have state changes, the CSS should define transition properties with duration values between 0.2s and 0.3s.

**Validates: Requirements 9.5**

### Property 11: Responsive Color Consistency

*For all* media query blocks in the CSS files, any color values defined should also be from the approved black and white palette.

**Validates: Requirements 10.1**

### Property 12: Touch Target Sizing

*For all* interactive elements within mobile breakpoints (max-width: 768px), the minimum height and width should be at least 44px to ensure tappability.

**Validates: Requirements 10.4**

### Property 13: Focus Indicator Visibility

*For all* :focus pseudo-class definitions, the styling should include either a visible border change, box-shadow, or outline property to ensure keyboard navigation visibility.

**Validates: Requirements 8.4, 9.2**

### Property 14: Disabled State Styling

*For all* :disabled pseudo-class definitions, the background or border color should use gray values (#CCCCCC, #999999, #F5F5F5) and cursor should be set to "not-allowed".

**Validates: Requirements 9.4**

## Error Handling

Since this is a CSS-only redesign with no logic changes, error handling remains unchanged. The existing React error boundaries and API error handling continue to function as designed.

### CSS Validation

During development, CSS should be validated to ensure:
- No syntax errors in CSS files
- All color values are valid hex or rgba formats
- All property values are valid CSS values
- No undefined CSS variables or references

### Browser Compatibility

The black and white theme uses standard CSS properties that are widely supported:
- Flexbox (supported in all modern browsers)
- CSS Grid (supported in all modern browsers)
- Border-radius (supported in all modern browsers)
- Box-shadow (supported in all modern browsers)
- RGBA colors (supported in all modern browsers)

No fallbacks are needed for the target browser support (modern evergreen browsers).

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests** focus on:
- Specific CSS rule verification for key components
- Example-based validation of color usage
- Visual regression testing for specific UI states

**Property Tests** focus on:
- Universal color palette compliance across all CSS files
- Contrast ratio validation for all text/background combinations
- Layout preservation verification
- Interactive state completeness

### Property-Based Testing

For this CSS redesign, property-based testing will use a CSS parser to validate properties across all style files. The recommended approach:

**Testing Library:** PostCSS with custom validators (JavaScript/Node.js)

**Test Configuration:**
- Parse all CSS files into AST (Abstract Syntax Tree)
- Extract all color values, layout properties, and interactive states
- Run validation properties against extracted values
- Minimum 100 iterations per property test (testing different CSS rules)

**Property Test Structure:**
Each property test should:
1. Parse the CSS file(s)
2. Extract relevant CSS rules and values
3. Validate against the property specification
4. Report any violations with file name, line number, and rule

**Test Tagging:**
Each property test must include a comment tag:
```javascript
// Feature: frontend-theme-redesign, Property 1: Color Palette Compliance
```

### Unit Testing

Unit tests should verify specific examples:
- Header uses black text on white background
- User messages use black background with white text
- Assistant messages use light gray background with black text
- Send button uses black background with white text
- Input field has black border on focus
- Footer has appropriate contrast

### Visual Regression Testing

Consider using visual regression testing tools (e.g., Percy, Chromatic) to:
- Capture screenshots of all UI states
- Compare against baseline images
- Detect unintended visual changes
- Verify responsive behavior across breakpoints

### Manual Testing Checklist

After implementation, manually verify:
- [ ] All purple colors are removed
- [ ] Text is readable in all contexts
- [ ] Interactive elements provide clear feedback
- [ ] Focus indicators are visible for keyboard navigation
- [ ] Design looks professional and modern
- [ ] Responsive design works on mobile devices
- [ ] Warning footer is prominent and clear

## Implementation Notes

### CSS Modification Strategy

1. **Create a color mapping table** from old to new colors
2. **Use find-and-replace** systematically for each color value
3. **Test incrementally** after each file modification
4. **Verify in browser** with dev tools to inspect computed styles
5. **Check responsive breakpoints** at various screen sizes

### Color Mapping Reference

```
Old Color → New Color
#667eea (purple) → #000000 (black)
#764ba2 (purple) → #000000 (black)
#5568d3 (dark purple) → #333333 (dark gray)
linear-gradient(...) → solid color or remove
rgba(102, 126, 234, ...) → rgba(0, 0, 0, ...)
```

### Development Workflow

1. Backup original CSS files
2. Modify globals.css first (body background)
3. Modify Home.module.css (main interface)
4. Modify ServiceGuide.module.css (service guide component)
5. Test in browser after each file
6. Run property tests to validate compliance
7. Perform visual regression testing
8. Manual testing across devices

### Accessibility Considerations

The black and white theme actually improves accessibility by:
- Providing higher contrast ratios
- Removing reliance on color for information
- Using clear visual hierarchy through typography
- Maintaining focus indicators for keyboard navigation

Ensure WCAG 2.1 Level AA compliance is maintained throughout the redesign.
