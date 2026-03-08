# Design Document: Chat Service Guide Display

## Overview

This design addresses the frontend rendering gap where service guide information returned by the backend is ignored. The solution involves extending the frontend TypeScript interfaces to match the backend schema, modifying the message rendering logic to detect service guides, and creating a new ServiceGuideDisplay component that presents the structured information in an accessible, mobile-friendly format.

The implementation will be minimal and focused: we'll add TypeScript types, update the API response handling to preserve the service_guide field, and create a single new component that renders all service guide information. The design maintains the existing chat UI patterns while introducing a visually distinct presentation for structured service information.

## Architecture

### Component Structure

```
index.tsx (Chat Page)
├── Message Rendering Logic (modified)
│   ├── Regular message display (existing)
│   └── ServiceGuideDisplay (new component)
│       ├── GuideHeader
│       ├── StepsList
│       ├── ProcessingTimeInfo
│       ├── OfficialPortalLink
│       └── ContactInfo
```

### Data Flow

1. User sends message → Backend processes → Returns ChatResponse with optional service_guide
2. Frontend receives response → Checks for service_guide field
3. If service_guide exists → Render ServiceGuideDisplay component
4. If service_guide is null → Render regular message only

### Type System

The frontend will define TypeScript interfaces that mirror the backend Pydantic models:

```typescript
interface ServiceStep {
  step_number: number;
  description: string;
  requires_in_person: boolean;
  online_available: boolean;
  estimated_duration: string;
  notes?: string;
}

interface ProcessingTime {
  minimum: string;
  maximum: string;
  typical: string;
  factors: string[];
}

interface ContactInfo {
  phone?: string;
  email?: string;
  address?: string;
  helpline?: string;
}

interface ServiceGuide {
  service_id: string;
  service_name: string;
  category: string;
  description: string;
  steps: ServiceStep[];
  processing_time: ProcessingTime;
  official_portal_url: string;
  contact_info: ContactInfo;
  last_updated: string;
  available_languages: string[];
}

interface ChatResponse {
  message: string;
  language: string;
  session_id: string;
  service_guide?: ServiceGuide;
}
```

## Components and Interfaces

### Modified: Message Interface (index.tsx)

**Current:**
```typescript
interface Message {
  role: 'user' | 'assistant'
  content: string
}
```

**Updated:**
```typescript
interface Message {
  role: 'user' | 'assistant'
  content: string
  serviceGuide?: ServiceGuide
}
```

### Modified: sendMessage Function

The sendMessage function will be updated to preserve the service_guide field from the API response:

```typescript
const sendMessage = async () => {
  // ... existing user message handling ...
  
  const response = await axios.post(`${API_URL}/api/v1/chat/`, {
    message: input,
    language: 'en'
  })

  const assistantMessage: Message = {
    role: 'assistant',
    content: response.data.message,
    serviceGuide: response.data.service_guide  // NEW: preserve service guide
  }
  setMessages(prev => [...prev, assistantMessage])
}
```

### Modified: Message Rendering Logic

The message rendering loop will check for the serviceGuide field and conditionally render the ServiceGuideDisplay component:

```typescript
{messages.map((msg, idx) => (
  <div key={idx} className={`${styles.message} ${msg.role === 'user' ? styles.userMessage : styles.assistantMessage}`}>
    <div className={styles.messageContent}>
      {msg.content}
    </div>
    {msg.serviceGuide && (
      <ServiceGuideDisplay guide={msg.serviceGuide} />
    )}
  </div>
))}
```

### New Component: ServiceGuideDisplay

**Props Interface:**
```typescript
interface ServiceGuideDisplayProps {
  guide: ServiceGuide;
}
```

**Component Structure:**

The ServiceGuideDisplay component will be a single functional component that renders all sections of the service guide. It will use semantic HTML and follow the existing styling patterns from Home.module.css.

**Rendering Logic:**

1. **Header Section**: Display service_name as h3, description as paragraph
2. **Steps Section**: Map over steps array, render each step with:
   - Step number badge
   - Description text
   - Duration estimate
   - Availability indicators (online/in-person icons or text)
   - Optional notes
3. **Processing Time Section**: Display typical time prominently, show range, list factors
4. **Official Portal Section**: Render official_portal_url as external link with icon
5. **Contact Info Section**: Display available contact methods (phone, email, helpline, address)

### Styling Approach

Create a new CSS module: `ServiceGuide.module.css`

**Key styling requirements:**
- Distinct background color (light blue/purple tint to match #667eea theme)
- Border or shadow to separate from regular messages
- Responsive grid/flexbox layout for mobile
- Icon support for step indicators and contact methods
- Sufficient padding and spacing for readability
- Color contrast meeting WCAG AA standards

**Mobile Responsiveness:**
- Stack sections vertically on small screens
- Ensure touch targets are at least 44x44px
- Use responsive font sizes
- Prevent horizontal overflow

## Data Models

### Frontend Type Definitions

All TypeScript interfaces are defined to match the backend Pydantic schemas exactly. The key difference is naming convention: backend uses snake_case (Python), frontend uses camelCase (TypeScript/JavaScript).

**Field Mapping:**
- `service_guide` (backend) → `serviceGuide` (frontend)
- `step_number` (backend) → `step_number` (frontend - keep snake_case in data)
- `official_portal_url` (backend) → `official_portal_url` (frontend - keep snake_case in data)

Note: We'll keep the data fields in snake_case to match the API response exactly, avoiding unnecessary transformation. Only component props and local variables will use camelCase.

### Data Validation

TypeScript will provide compile-time type checking. At runtime, we'll use optional chaining and nullish coalescing to handle missing fields gracefully:

```typescript
{guide.contact_info?.phone && (
  <div>Phone: {guide.contact_info.phone}</div>
)}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Service Guide Detection

*For any* ChatResponse object, if the service_guide field is non-null, then the frontend should detect its presence and render the ServiceGuideDisplay component; if the service_guide field is null, then only the message text should be rendered.

**Validates: Requirements 1.1, 1.2, 1.3**

### Property 2: Complete Field Rendering

*For any* ServiceGuide object, all non-null fields (service_name, description, steps, processing_time, official_portal_url, contact_info) should appear in the rendered HTML output with their corresponding values.

**Validates: Requirements 2.1, 2.2, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 6.1, 6.2, 6.3, 6.4, 6.5**

### Property 3: Step Sequential Ordering

*For any* ServiceGuide with a steps array, the rendered output should display all steps in ascending order by step_number without skipping any steps.

**Validates: Requirements 3.1**

### Property 4: Conditional Availability Indicators

*For any* ServiceStep, if online_available is true, then the rendered output should contain an online indicator; if requires_in_person is true, then the rendered output should contain an in-person indicator; if notes is non-null, then the notes text should appear in the rendered output.

**Validates: Requirements 3.5, 3.6, 3.7**

### Property 5: Official Portal Link Rendering

*For any* ServiceGuide with an official_portal_url, the rendered output should contain an anchor element with href matching the URL, target="_blank" attribute, and descriptive label text.

**Validates: Requirements 5.1, 5.2, 5.3**

### Property 6: Semantic HTML Structure

*For any* ServiceGuide rendered, the HTML output should use semantic elements (headings for titles, lists for steps, anchor tags for links) and all interactive elements should be keyboard-accessible native HTML elements.

**Validates: Requirements 9.1, 9.3**

### Property 7: ARIA Label Presence

*For any* ServiceGuide rendered, the HTML output should include appropriate ARIA attributes (aria-label, aria-labelledby, or role) for major sections to support screen reader navigation.

**Validates: Requirements 9.2**

## Error Handling

### Missing or Malformed Data

The component will use defensive programming to handle incomplete or malformed service guide data:

1. **Null/Undefined Checks**: Use optional chaining (`?.`) for all nested field access
2. **Empty Arrays**: Check array length before mapping (e.g., `steps.length > 0`)
3. **Fallback Values**: Provide sensible defaults for missing optional fields
4. **Type Guards**: Use TypeScript type guards to ensure data shape before rendering

**Example Error Handling:**

```typescript
// Safe access to optional fields
{guide.contact_info?.phone && (
  <div>Phone: {guide.contact_info.phone}</div>
)}

// Safe array mapping
{guide.steps && guide.steps.length > 0 && (
  <ol>
    {guide.steps.map(step => (
      <li key={step.step_number}>{step.description}</li>
    ))}
  </ol>
)}

// Fallback for missing processing time
<div>
  Processing Time: {guide.processing_time?.typical || 'Not specified'}
</div>
```

### API Errors

The existing error handling in the sendMessage function will catch API errors. No changes needed to error handling logic—if the API call fails, the existing error message will be displayed.

### Invalid URLs

For the official_portal_url, we'll render it as-is. The browser will handle invalid URLs naturally (link won't work, but won't crash the app). For production, we could add URL validation, but for this fix, we'll keep it simple.

## Testing Strategy

### Dual Testing Approach

This feature will use both unit tests and property-based tests to ensure comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and component integration
- **Property tests**: Verify universal properties across all possible service guide data

### Unit Testing

**Framework**: Jest + React Testing Library (already used in Next.js projects)

**Test Cases**:

1. **Component Rendering Tests**:
   - ServiceGuideDisplay renders with complete service guide data
   - ServiceGuideDisplay handles missing optional fields gracefully
   - Message component renders regular message without service guide
   - Message component renders both message and service guide when present

2. **Edge Cases**:
   - Empty steps array
   - Missing contact_info fields
   - Missing notes in steps
   - Very long service names or descriptions

3. **Integration Tests**:
   - Full message flow: API response → state update → component render
   - Multiple messages with mixed content (some with guides, some without)

### Property-Based Testing

**Framework**: fast-check (JavaScript/TypeScript property-based testing library)

**Configuration**: Minimum 100 iterations per property test

**Property Tests**:

Each property test will be tagged with a comment referencing the design document property:

```typescript
// Feature: chat-service-guide-display, Property 1: Service Guide Detection
test('service guide detection property', () => {
  fc.assert(
    fc.property(
      arbitraryChatResponse(),
      (response) => {
        // Test that detection works correctly for all responses
      }
    ),
    { numRuns: 100 }
  )
})
```

**Test Properties**:

1. **Property 1 Test**: Generate random ChatResponse objects with and without service_guide, verify detection and rendering logic
2. **Property 2 Test**: Generate random ServiceGuide objects, verify all non-null fields appear in rendered output
3. **Property 3 Test**: Generate random step arrays with varying lengths and orders, verify sequential rendering
4. **Property 4 Test**: Generate random ServiceStep objects with different boolean flag combinations, verify indicators appear correctly
5. **Property 5 Test**: Generate random URLs, verify anchor element attributes
6. **Property 6 Test**: Generate random ServiceGuide objects, verify semantic HTML structure
7. **Property 7 Test**: Generate random ServiceGuide objects, verify ARIA attributes presence

**Generators (Arbitraries)**:

We'll need to create custom generators for:
- ServiceStep (with random booleans, strings, numbers)
- ProcessingTime (with random duration strings)
- ContactInfo (with optional fields randomly present/absent)
- ServiceGuide (combining all sub-generators)
- ChatResponse (with optional service_guide)

### Testing Balance

- Focus unit tests on specific examples and component integration
- Use property tests to verify universal correctness across all possible inputs
- Avoid writing too many unit tests for variations—let property tests handle input coverage
- Unit tests should focus on: specific examples, edge cases, error conditions, integration points
- Property tests should focus on: universal properties, comprehensive input coverage

## Implementation Notes

### File Structure

```
frontend/
├── pages/
│   └── index.tsx (modified)
├── components/
│   └── ServiceGuideDisplay.tsx (new)
├── styles/
│   ├── Home.module.css (existing)
│   └── ServiceGuide.module.css (new)
└── types/
    └── chat.ts (new - TypeScript interfaces)
```

### Minimal Implementation Approach

1. Create types file with all interfaces
2. Update index.tsx to use new types and preserve service_guide
3. Create ServiceGuideDisplay component with all rendering logic
4. Create CSS module for styling
5. Write tests

### Accessibility Considerations

- Use `<h3>` for service name (assuming chat messages are in a section with `<h2>`)
- Use `<ol>` for steps (ordered list is semantically correct)
- Use `<dl>` for contact info (definition list for key-value pairs)
- Add `rel="noopener noreferrer"` to external links for security
- Ensure color contrast ratios meet WCAG AA (4.5:1 for normal text)
- Add aria-label to the guide container: `aria-label="Service Guide"`

### Performance Considerations

This is a simple rendering component with no performance concerns:
- No heavy computations
- No large data sets (service guides are small)
- No animations or complex interactions
- React will efficiently re-render only when message data changes

### Future Enhancements (Out of Scope)

- Collapsible sections for long guides
- Print-friendly formatting
- Share/copy guide functionality
- Multi-language support (backend already has available_languages field)
- Step completion tracking
- Estimated total time calculation
