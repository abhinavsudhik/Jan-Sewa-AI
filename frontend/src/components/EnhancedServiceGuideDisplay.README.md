# EnhancedServiceGuideDisplay Component

## Overview

The `EnhancedServiceGuideDisplay` component is a React component that displays government service information in a structured, accessible format. It renders all five required information categories with proper semantic HTML structure and handles empty categories gracefully.

## Features

### ✅ Requirements Validation

This component validates the following requirements:

- **Requirement 1.1**: Structured Service Response Format with all five information categories
- **Requirement 1.2**: Organize information into clearly labeled sections with consistent formatting
- **Requirement 1.3**: Indicate "Information not available" for unavailable categories
- **Requirement 1.4**: Maintain same section order for all government service queries
- **Requirement 9.2**: Display last_updated timestamp in Service_Response
- **Requirement 10.1**: Use clear section headings for each information category
- **Requirement 10.3**: Use appropriate visual separators between sections

### 🏗️ Structure

The component displays information in the following order:

1. **📍 Office Locations** - Physical locations where services can be accessed
2. **📄 Required Documents** - Documents needed to complete the process
3. **🏢 Office Visit Sequence** - Step-by-step office visit process
4. **🔗 Official Websites** - Relevant government website links
5. **⏱️ Processing Timeline** - Expected processing times and factors

### 🎨 Design Features

- **Semantic HTML**: Uses `<article>`, `<section>`, and proper heading hierarchy
- **Accessibility**: ARIA labels, proper heading structure, keyboard navigation
- **Responsive Design**: Mobile-friendly layout with responsive breakpoints
- **Visual Hierarchy**: Clear section separation with icons and consistent styling
- **Empty State Handling**: Shows "Information not available" for missing data

## Usage

### Basic Usage

```tsx
import { EnhancedServiceGuideDisplay } from './EnhancedServiceGuideDisplay';
import { EnhancedServiceGuide } from '../types/service';

const serviceGuide: EnhancedServiceGuide = {
  // ... service data
};

function MyComponent() {
  return <EnhancedServiceGuideDisplay guide={serviceGuide} />;
}
```

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `guide` | `EnhancedServiceGuide` | Yes | The service guide data to display |

### Data Structure

The component expects an `EnhancedServiceGuide` object with the following structure:

```typescript
interface EnhancedServiceGuide {
  service_id: string;
  service_name: string;
  category: ServiceCategory;
  description: string;
  office_locations: OfficeLocation[];
  required_documents: RequiredDocument[];
  office_visit_sequence: OfficeVisitStep[];
  official_websites: OfficialWebsiteLink[];
  processing_timelines: ProcessingTimeline[];
  last_updated: string; // ISO datetime string
  data_source: string;
  available_languages: string[];
}
```

## Component Behavior

### Office Locations
- Displays complete address information
- Shows coordinates if available
- Includes operating hours and contact information
- Multiple locations are listed separately

### Required Documents
- Lists all required documents with details
- Shows copy requirements and format specifications
- Indicates optional documents with badges
- Displays alternative document options

### Office Visit Sequence
- **Single Office**: Displays without sequence numbering
- **Multiple Offices**: Shows numbered sequence (1, 2, 3...)
- Indicates optional and conditional steps
- Shows estimated duration for each step

### Official Websites
- Renders as clickable links with `target="_blank"`
- Labels each link with its purpose
- Includes security attributes (`rel="noopener noreferrer"`)
- Shows descriptions when available

### Processing Timeline
- Displays typical processing time prominently
- Shows range (minimum to maximum days)
- Includes processing type (standard, expedited)
- Lists factors that may affect processing time
- Shows additional notes when available

### Empty Categories
- Shows "Information not available" message
- Maintains consistent layout structure
- Uses subtle styling to indicate missing data

## Styling

The component uses CSS Modules for styling (`EnhancedServiceGuideDisplay.module.css`):

- **Responsive Design**: Adapts to mobile and desktop screens
- **Accessibility**: High contrast mode support, reduced motion support
- **Print Styles**: Optimized for printing with URL display
- **Visual Hierarchy**: Clear section separation and typography

### CSS Classes

Key CSS classes available for customization:

- `.guideContainer` - Main container
- `.section` - Individual category sections
- `.sectionHeader` - Category headers with icons
- `.notAvailable` - Empty state styling
- `.locationItem`, `.documentItem`, etc. - Individual item styling

## Accessibility Features

- **Semantic HTML**: Proper use of `<article>`, `<section>`, `<h3>`, `<h4>`, `<h5>`
- **ARIA Labels**: `aria-label` and `aria-labelledby` attributes
- **Keyboard Navigation**: All interactive elements are keyboard accessible
- **Screen Reader Support**: Proper heading hierarchy and descriptive text
- **High Contrast**: Supports high contrast mode
- **Reduced Motion**: Respects user's motion preferences

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Supports CSS Grid and Flexbox
- Graceful degradation for older browsers

## Performance

- **Lightweight**: Minimal JavaScript, CSS-only animations
- **Efficient Rendering**: Uses React best practices
- **Optimized Images**: No external image dependencies
- **Fast Loading**: Minimal external dependencies

## Examples

See `EnhancedServiceGuideDisplay.example.tsx` for complete usage examples including:

- Service with all categories populated
- Service with empty categories
- Different data scenarios (single vs. multiple items)

## Testing

The component is designed to be easily testable:

- Pure component with no side effects
- Predictable rendering based on props
- Accessible elements for test queries
- Clear data-testid attributes (can be added if needed)

## Migration from Legacy Component

If migrating from the existing `ServiceGuideDisplay` component:

1. Update import path
2. Ensure data structure matches `EnhancedServiceGuide` interface
3. Update any custom styling to use new CSS classes
4. Test accessibility features
5. Verify all five categories are properly displayed

## Future Enhancements

Potential future improvements:

- Interactive maps for office locations
- Document upload integration
- Real-time status tracking
- Multi-language support
- Dark mode theme
- Advanced filtering and search