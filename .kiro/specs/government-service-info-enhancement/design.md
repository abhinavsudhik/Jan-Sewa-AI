# Design Document: Government Service Information Enhancement

## Overview

This design document specifies the implementation of an enhanced government service information display system. The system will transform the current ad-hoc service response format into a structured, comprehensive format that consistently presents five key information categories: office locations, required documents, office visit sequences, official website links, and processing timelines.

The enhancement addresses the need for citizens to receive complete, well-organized information about government services in a predictable format. This improves user experience by ensuring no critical information is missing and all services follow the same presentation structure.

### Key Design Goals

1. **Consistency**: All service responses follow the same structure and ordering
2. **Completeness**: All five information categories are always present (with appropriate messaging for unavailable data)
3. **Clarity**: Information is presented in a clear, accessible format with proper visual hierarchy
4. **Extensibility**: The design supports adding new information categories in the future
5. **Maintainability**: Clear separation between data models, formatting logic, and presentation

### Scope

This design covers:
- Enhanced data models for the five information categories
- Response formatting service that structures service information
- Query processing enhancements for service identification
- Frontend display components for the structured format
- Data validation and error handling

Out of scope:
- AI/LLM integration for natural language understanding (uses existing keyword matching)
- Database schema changes (uses existing in-memory mock data structure)
- Multi-language support beyond existing infrastructure
- Real-time data synchronization with government databases

## Architecture

### System Components

The enhancement follows a layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ServiceGuideDisplay Component (Enhanced)        │  │
│  │  - Renders structured service information        │  │
│  │  - Displays all five categories                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          │ HTTP/JSON
                          ▼
┌─────────────────────────────────────────────────────────┐
│                     API Layer                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Chat Endpoint (/api/v1/chat)                    │  │
│  │  - Receives user queries                         │  │
│  │  - Returns structured responses                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Business Logic Layer                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │  QueryProcessor                                   │  │
│  │  - Parses user queries                           │  │
│  │  - Identifies requested service                  │  │
│  │  - Handles ambiguity and errors                  │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ResponseFormatter                                │  │
│  │  - Structures service information                │  │
│  │  - Ensures all five categories present          │  │
│  │  - Handles missing data gracefully              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                     Data Layer                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ServiceRepository                                │  │
│  │  - Retrieves service data                        │  │
│  │  - Manages mock data (current implementation)   │  │
│  │  - Future: Database integration                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Component Interactions

1. **User Query Flow**:
   - User submits query via frontend chat interface
   - Frontend sends POST request to `/api/v1/chat/` endpoint
   - QueryProcessor identifies the requested service
   - ServiceRepository retrieves service data
   - ResponseFormatter structures the data into five categories
   - API returns structured response to frontend
   - ServiceGuideDisplay renders the formatted information

2. **Data Flow**:
   - Service data stored in enhanced schema with all five categories
   - ResponseFormatter validates data completeness
   - Missing categories are handled with "Information not available" messaging
   - Formatted response maintains consistent structure across all services

### Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Data Validation**: Pydantic v2
- **Frontend**: Next.js (React), TypeScript
- **Styling**: CSS Modules
- **Testing**: pytest (backend), property-based testing with Hypothesis

## Components and Interfaces

### Enhanced Data Models

#### OfficeLocation

Represents a physical location where a government service can be accessed.

```python
class OfficeLocation(BaseModel):
    """Physical location for government service access"""
    name: str  # Office name (e.g., "District Collectorate")
    address: str  # Complete address
    city: str
    state: str
    postal_code: str
    coordinates: Optional[Coordinates] = None  # Lat/long if available
    operating_hours: Optional[str] = None
    contact_phone: Optional[str] = None

class Coordinates(BaseModel):
    """Geographic coordinates"""
    latitude: float
    longitude: float
```

#### RequiredDocument

Represents a document needed to complete a government process.

```python
class RequiredDocument(BaseModel):
    """Document required for a government service"""
    document_name: str  # e.g., "Aadhaar Card"
    description: Optional[str] = None  # Additional details
    copies_required: int = 1
    format_requirements: Optional[str] = None  # e.g., "Original + photocopy"
    is_mandatory: bool = True
    alternatives: Optional[List[str]] = None  # Alternative documents
```

#### OfficeVisitStep

Represents a step in the office visit sequence.

```python
class OfficeVisitStep(BaseModel):
    """A step in the office visit sequence"""
    sequence_number: int
    office_name: str
    purpose: str  # What to do at this office
    estimated_duration: str  # e.g., "30 minutes"
    is_optional: bool = False
    is_conditional: bool = False
    condition: Optional[str] = None  # Condition for conditional steps
```

#### OfficialWebsiteLink

Represents an official government website link.

```python
class OfficialWebsiteLink(BaseModel):
    """Official government website link"""
    url: HttpUrl  # Validated URL
    purpose: str  # e.g., "Application Portal", "Status Tracking"
    description: Optional[str] = None
    
    @field_validator('url')
    @classmethod
    def validate_https(cls, v: HttpUrl) -> HttpUrl:
        """Prefer HTTPS when available"""
        if v.scheme == 'http':
            # Log warning but allow HTTP for government sites
            # that may not have HTTPS
            pass
        return v
```

#### ProcessingTimeline

Represents the time required to complete a service.

```python
class ProcessingTimeline(BaseModel):
    """Processing timeline for a government service"""
    minimum_days: int
    maximum_days: int
    typical_days: int
    time_unit: str = "days"  # days, weeks, months
    processing_type: str = "standard"  # standard, expedited
    notes: Optional[str] = None
    factors_affecting_time: List[str] = []
    
    def as_range_string(self) -> str:
        """Format as human-readable range"""
        return f"{self.minimum_days}-{self.maximum_days} {self.time_unit}"
```

#### EnhancedServiceGuide

The main service information model with all five categories.

```python
class EnhancedServiceGuide(BaseModel):
    """Complete service guide with all required information categories"""
    # Basic information
    service_id: str
    service_name: str
    category: ServiceCategory
    description: str
    
    # Five required information categories
    office_locations: List[OfficeLocation] = []
    required_documents: List[RequiredDocument] = []
    office_visit_sequence: List[OfficeVisitStep] = []
    official_websites: List[OfficialWebsiteLink] = []
    processing_timelines: List[ProcessingTimeline] = []
    
    # Metadata
    last_updated: datetime
    data_source: str  # For verification
    available_languages: List[str] = ["en"]
    
    # Legacy compatibility (for gradual migration)
    steps: Optional[List[ServiceStep]] = None
    processing_time: Optional[ProcessingTime] = None
    official_portal_url: Optional[str] = None
    contact_info: Optional[ContactInfo] = None
```

### ResponseFormatter Service

The ResponseFormatter is responsible for structuring service information into the standardized format.

```python
class ResponseFormatter:
    """Formats service information into structured responses"""
    
    CATEGORY_ORDER = [
        "office_locations",
        "required_documents",
        "office_visit_sequence",
        "official_websites",
        "processing_timelines"
    ]
    
    CATEGORY_HEADERS = {
        "office_locations": "📍 Office Locations",
        "required_documents": "📄 Required Documents",
        "office_visit_sequence": "🏢 Office Visit Sequence",
        "official_websites": "🔗 Official Websites",
        "processing_timelines": "⏱️ Processing Timeline"
    }
    
    def format_service_response(
        self, 
        service: EnhancedServiceGuide
    ) -> FormattedServiceResponse:
        """
        Format service information into structured response.
        
        Ensures:
        - All five categories are present
        - Categories appear in consistent order
        - Missing data is handled gracefully
        - Consistent formatting and spacing
        """
        sections = []
        
        for category in self.CATEGORY_ORDER:
            section = self._format_category(service, category)
            sections.append(section)
        
        return FormattedServiceResponse(
            service_name=service.service_name,
            description=service.description,
            sections=sections,
            last_updated=service.last_updated
        )
    
    def _format_category(
        self, 
        service: EnhancedServiceGuide, 
        category: str
    ) -> ResponseSection:
        """Format a single information category"""
        header = self.CATEGORY_HEADERS[category]
        data = getattr(service, category)
        
        if not data or len(data) == 0:
            return ResponseSection(
                header=header,
                content="Information not available",
                is_empty=True
            )
        
        # Format based on category type
        if category == "office_locations":
            content = self._format_office_locations(data)
        elif category == "required_documents":
            content = self._format_required_documents(data)
        elif category == "office_visit_sequence":
            content = self._format_office_sequence(data)
        elif category == "official_websites":
            content = self._format_official_websites(data)
        elif category == "processing_timelines":
            content = self._format_processing_timelines(data)
        
        return ResponseSection(
            header=header,
            content=content,
            is_empty=False
        )
    
    def _format_office_locations(
        self, 
        locations: List[OfficeLocation]
    ) -> str:
        """Format office locations as structured text"""
        formatted = []
        for loc in locations:
            parts = [
                f"• {loc.name}",
                f"  {loc.address}, {loc.city}, {loc.state} {loc.postal_code}"
            ]
            if loc.coordinates:
                parts.append(
                    f"  Coordinates: {loc.coordinates.latitude}, "
                    f"{loc.coordinates.longitude}"
                )
            if loc.operating_hours:
                parts.append(f"  Hours: {loc.operating_hours}")
            if loc.contact_phone:
                parts.append(f"  Phone: {loc.contact_phone}")
            formatted.append("\n".join(parts))
        return "\n\n".join(formatted)
    
    def _format_required_documents(
        self, 
        documents: List[RequiredDocument]
    ) -> str:
        """Format required documents as bulleted list"""
        formatted = []
        for doc in documents:
            parts = [f"• {doc.document_name}"]
            if doc.description:
                parts.append(f"  {doc.description}")
            if doc.copies_required > 1:
                parts.append(f"  Copies required: {doc.copies_required}")
            if doc.format_requirements:
                parts.append(f"  Format: {doc.format_requirements}")
            if not doc.is_mandatory:
                parts.append("  (Optional)")
            if doc.alternatives:
                parts.append(f"  Alternatives: {', '.join(doc.alternatives)}")
            formatted.append("\n".join(parts))
        return "\n\n".join(formatted)
    
    def _format_office_sequence(
        self, 
        sequence: List[OfficeVisitStep]
    ) -> str:
        """Format office visit sequence with numbering"""
        if len(sequence) == 1:
            # Single office - no numbering
            step = sequence[0]
            return f"• {step.office_name}\n  {step.purpose}\n  Duration: {step.estimated_duration}"
        
        # Multiple offices - numbered sequence
        formatted = []
        for step in sorted(sequence, key=lambda x: x.sequence_number):
            parts = [f"{step.sequence_number}. {step.office_name}"]
            parts.append(f"   {step.purpose}")
            parts.append(f"   Duration: {step.estimated_duration}")
            if step.is_optional:
                parts.append("   (Optional)")
            if step.is_conditional and step.condition:
                parts.append(f"   Condition: {step.condition}")
            formatted.append("\n".join(parts))
        return "\n\n".join(formatted)
    
    def _format_official_websites(
        self, 
        websites: List[OfficialWebsiteLink]
    ) -> str:
        """Format official website links"""
        formatted = []
        for site in websites:
            parts = [f"• {site.purpose}: {site.url}"]
            if site.description:
                parts.append(f"  {site.description}")
            formatted.append("\n".join(parts))
        return "\n\n".join(formatted)
    
    def _format_processing_timelines(
        self, 
        timelines: List[ProcessingTimeline]
    ) -> str:
        """Format processing timeline information"""
        formatted = []
        for timeline in timelines:
            parts = [f"• {timeline.processing_type.title()} Processing"]
            parts.append(f"  Typical: {timeline.typical_days} {timeline.time_unit}")
            parts.append(f"  Range: {timeline.as_range_string()}")
            if timeline.notes:
                parts.append(f"  Note: {timeline.notes}")
            if timeline.factors_affecting_time:
                parts.append("  Factors affecting time:")
                for factor in timeline.factors_affecting_time:
                    parts.append(f"    - {factor}")
            formatted.append("\n".join(parts))
        return "\n\n".join(formatted)


class ResponseSection(BaseModel):
    """A section in the formatted response"""
    header: str
    content: str
    is_empty: bool


class FormattedServiceResponse(BaseModel):
    """Complete formatted service response"""
    service_name: str
    description: str
    sections: List[ResponseSection]
    last_updated: datetime
```

### QueryProcessor Service

Handles query parsing and service identification.

```python
class QueryProcessor:
    """Processes user queries and identifies requested services"""
    
    def __init__(self, service_repository: ServiceRepository):
        self.service_repository = service_repository
        self.keyword_map = self._build_keyword_map()
    
    def process_query(self, query: str) -> QueryResult:
        """
        Process user query and identify requested service.
        
        Returns:
        - QueryResult with identified service(s)
        - Handles ambiguity and unknown services
        """
        normalized_query = query.lower().strip()
        
        # Find matching services
        matches = self._find_matching_services(normalized_query)
        
        if len(matches) == 0:
            # No matches - suggest similar services
            suggestions = self._find_similar_services(normalized_query)
            return QueryResult(
                status="no_match",
                message="I couldn't find information about that service.",
                suggestions=suggestions
            )
        elif len(matches) == 1:
            # Single match - return service
            service = self.service_repository.get_service(matches[0])
            return QueryResult(
                status="success",
                service=service
            )
        else:
            # Multiple matches - request clarification
            return QueryResult(
                status="ambiguous",
                message="I found multiple services matching your query. "
                        "Which one do you need?",
                matches=matches
            )
    
    def _find_matching_services(self, query: str) -> List[str]:
        """Find services matching the query"""
        matches = []
        for service_id, keywords in self.keyword_map.items():
            if all(keyword in query for keyword in keywords):
                matches.append(service_id)
        return matches
    
    def _find_similar_services(self, query: str) -> List[str]:
        """Find services with partial keyword matches"""
        # Simple implementation - can be enhanced with fuzzy matching
        similar = []
        query_words = set(query.split())
        for service_id, keywords in self.keyword_map.items():
            keyword_set = set(keywords)
            if len(query_words & keyword_set) > 0:
                similar.append(service_id)
        return similar[:3]  # Return top 3 suggestions
    
    def _build_keyword_map(self) -> Dict[str, List[str]]:
        """Build keyword mapping for service identification"""
        # This would be loaded from configuration or database
        return {
            "aadhaar_name_change": ["aadhaar", "name"],
            "data_access_request": ["data", "access"],
            "service_status_tracking": ["status", "tracking"],
            "driving_license": ["driving", "license"],
        }


class QueryResult(BaseModel):
    """Result of query processing"""
    status: str  # success, no_match, ambiguous
    message: Optional[str] = None
    service: Optional[EnhancedServiceGuide] = None
    matches: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
```

### ServiceRepository

Manages service data retrieval.

```python
class ServiceRepository:
    """Repository for service data access"""
    
    def __init__(self):
        self.services: Dict[str, EnhancedServiceGuide] = {}
        self._load_services()
    
    def get_service(self, service_id: str) -> Optional[EnhancedServiceGuide]:
        """Retrieve service by ID"""
        return self.services.get(service_id)
    
    def get_all_services(self) -> List[EnhancedServiceGuide]:
        """Retrieve all services"""
        return list(self.services.values())
    
    def update_service(self, service: EnhancedServiceGuide) -> None:
        """Update service data"""
        self.services[service.service_id] = service
    
    def _load_services(self) -> None:
        """Load services from data source"""
        # Current implementation: load from mock data
        # Future: load from database
        self.services = self._load_mock_services()
    
    def _load_mock_services(self) -> Dict[str, EnhancedServiceGuide]:
        """Load mock service data"""
        # This will be populated with enhanced mock data
        # including all five information categories
        return {}
```

### Frontend Components

#### Enhanced ServiceGuideDisplay

```typescript
interface EnhancedServiceGuideProps {
  guide: EnhancedServiceGuide;
}

interface ResponseSection {
  header: string;
  content: string;
  isEmpty: boolean;
}

export function EnhancedServiceGuideDisplay({ guide }: EnhancedServiceGuideProps) {
  return (
    <div className={styles.guideContainer} role="article" aria-label="Service Guide">
      <header className={styles.header}>
        <h3 className={styles.serviceName}>{guide.service_name}</h3>
        <p className={styles.description}>{guide.description}</p>
        {guide.last_updated && (
          <p className={styles.lastUpdated}>
            Last updated: {formatDate(guide.last_updated)}
          </p>
        )}
      </header>

      <div className={styles.sectionsContainer}>
        {guide.sections.map((section, index) => (
          <section 
            key={index} 
            className={styles.section}
            aria-labelledby={`section-${index}`}
          >
            <h4 id={`section-${index}`} className={styles.sectionHeader}>
              {section.header}
            </h4>
            <div className={styles.sectionContent}>
              {section.isEmpty ? (
                <p className={styles.notAvailable}>{section.content}</p>
              ) : (
                <div className={styles.content}>
                  {renderSectionContent(section)}
                </div>
              )}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}

function renderSectionContent(section: ResponseSection): JSX.Element {
  // Parse and render formatted content
  // Handles lists, links, and structured text
  const lines = section.content.split('\n');
  // ... rendering logic
}
```

## Data Models

### Complete Schema Hierarchy

```
EnhancedServiceGuide
├── service_id: string
├── service_name: string
├── category: ServiceCategory
├── description: string
├── office_locations: List[OfficeLocation]
│   ├── name: string
│   ├── address: string
│   ├── city: string
│   ├── state: string
│   ├── postal_code: string
│   ├── coordinates: Optional[Coordinates]
│   │   ├── latitude: float
│   │   └── longitude: float
│   ├── operating_hours: Optional[string]
│   └── contact_phone: Optional[string]
├── required_documents: List[RequiredDocument]
│   ├── document_name: string
│   ├── description: Optional[string]
│   ├── copies_required: int
│   ├── format_requirements: Optional[string]
│   ├── is_mandatory: bool
│   └── alternatives: Optional[List[string]]
├── office_visit_sequence: List[OfficeVisitStep]
│   ├── sequence_number: int
│   ├── office_name: string
│   ├── purpose: string
│   ├── estimated_duration: string
│   ├── is_optional: bool
│   ├── is_conditional: bool
│   └── condition: Optional[string]
├── official_websites: List[OfficialWebsiteLink]
│   ├── url: HttpUrl
│   ├── purpose: string
│   └── description: Optional[string]
├── processing_timelines: List[ProcessingTimeline]
│   ├── minimum_days: int
│   ├── maximum_days: int
│   ├── typical_days: int
│   ├── time_unit: string
│   ├── processing_type: string
│   ├── notes: Optional[string]
│   └── factors_affecting_time: List[string]
├── last_updated: datetime
├── data_source: string
└── available_languages: List[string]
```

### Data Validation Rules

1. **OfficeLocation**:
   - Address fields are required
   - Coordinates must be valid lat/long if provided
   - Phone numbers should match standard format

2. **RequiredDocument**:
   - Document name is required
   - Copies required must be >= 1
   - Alternatives must be non-empty if provided

3. **OfficeVisitStep**:
   - Sequence numbers must be unique and sequential
   - Conditional steps must have a condition specified
   - Duration should be in standard format

4. **OfficialWebsiteLink**:
   - URL must be valid and accessible
   - HTTPS preferred over HTTP
   - Purpose is required for labeling

5. **ProcessingTimeline**:
   - Minimum <= Typical <= Maximum
   - Time unit must be valid (days, weeks, months)
   - Processing type must be recognized

### Migration Strategy

To support gradual migration from the current schema:

1. **Dual Schema Support**: EnhancedServiceGuide includes optional legacy fields
2. **Adapter Pattern**: Convert legacy ServiceGuide to EnhancedServiceGuide
3. **Backward Compatibility**: API can return both formats during transition
4. **Deprecation Path**: Legacy fields marked as deprecated with timeline

```python
class SchemaAdapter:
    """Adapts between legacy and enhanced schemas"""
    
    @staticmethod
    def legacy_to_enhanced(
        legacy: ServiceGuide
    ) -> EnhancedServiceGuide:
        """Convert legacy ServiceGuide to EnhancedServiceGuide"""
        # Extract office locations from contact_info
        office_locations = []
        if legacy.contact_info and legacy.contact_info.address:
            office_locations.append(
                OfficeLocation(
                    name="Main Office",
                    address=legacy.contact_info.address,
                    city="Unknown",
                    state="Unknown",
                    postal_code="000000"
                )
            )
        
        # Convert steps to office visit sequence
        office_sequence = [
            OfficeVisitStep(
                sequence_number=step.step_number,
                office_name="Service Office",
                purpose=step.description,
                estimated_duration=step.estimated_duration
            )
            for step in legacy.steps
        ]
        
        # Convert processing time to timeline
        timelines = []
        if legacy.processing_time:
            timelines.append(
                ProcessingTimeline(
                    minimum_days=self._parse_days(legacy.processing_time.minimum),
                    maximum_days=self._parse_days(legacy.processing_time.maximum),
                    typical_days=self._parse_days(legacy.processing_time.typical),
                    factors_affecting_time=legacy.processing_time.factors
                )
            )
        
        # Convert portal URL to website link
        websites = []
        if legacy.official_portal_url:
            websites.append(
                OfficialWebsiteLink(
                    url=legacy.official_portal_url,
                    purpose="Official Portal"
                )
            )
        
        return EnhancedServiceGuide(
            service_id=legacy.service_id,
            service_name=legacy.service_name,
            category=legacy.category,
            description=legacy.description,
            office_locations=office_locations,
            required_documents=[],  # Not in legacy schema
            office_visit_sequence=office_sequence,
            official_websites=websites,
            processing_timelines=timelines,
            last_updated=legacy.last_updated,
            data_source="legacy_migration",
            available_languages=legacy.available_languages
        )
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified several redundancies:

**Redundancies Identified:**
1. Properties 1.4 and 8.4 both test consistent section ordering - can be combined
2. Properties 2.1 and 2.2 both test that all office locations are displayed - 2.2 is redundant
3. Properties 3.1 and 3.2 both test document list completeness - can be combined
4. Properties 3.2 and 3.4 both test list formatting - 3.4 is redundant
5. Properties 1.3 and 8.2 both test missing data handling - can be combined
6. Properties 8.1 and 8.3 test format consistency - can be combined into one comprehensive property

**Properties to Combine:**
- Combine 1.4 and 8.4 into a single "Section Order Consistency" property
- Combine 2.1 and 2.2 into a single "Office Location Completeness" property
- Combine 3.1, 3.2, and 3.4 into a single "Document List Completeness" property
- Combine 1.3 and 8.2 into a single "Missing Data Handling" property
- Combine 8.1 and 8.3 into a single "Format Consistency" property

This reduces the total properties from 44 to approximately 30 unique properties.

### Properties

#### Property 1: All Five Categories Present

*For any* service query that is successfully processed, the formatted response must contain all five information categories (office locations, required documents, office visit sequence, official websites, processing timeline) with appropriate headers, regardless of whether data is available for each category.

**Validates: Requirements 1.1, 8.1**

#### Property 2: Section Order Consistency

*For any* two service responses, the five information categories must appear in the same order: office locations, required documents, office visit sequence, official websites, processing timeline.

**Validates: Requirements 1.4, 8.4**

#### Property 3: Section Headers Present

*For any* formatted service response, each of the five information categories must have a clearly labeled section header.

**Validates: Requirements 1.2, 10.1**

#### Property 4: Missing Data Handling

*For any* service with missing data in one or more categories, the formatted response must display the category header with "Information not available" message for each missing category.

**Validates: Requirements 1.3, 8.2**

#### Property 5: Office Location Completeness

*For any* service with N office locations in the data model, the formatted response must display all N office locations with complete address details.

**Validates: Requirements 2.1, 2.2**

#### Property 6: Coordinates Inclusion

*For any* office location with geographic coordinates in the data model, the formatted response must include those coordinates in the office location information.

**Validates: Requirements 2.3**

#### Property 7: Office Location List Format

*For any* service with multiple office locations, each location must appear on separate lines in a list format.

**Validates: Requirements 2.4**

#### Property 8: Document List Completeness

*For any* service with N required documents in the data model, the formatted response must display all N documents as separate items in a list format.

**Validates: Requirements 3.1, 3.2, 3.4**

#### Property 9: Document Specifications Inclusion

*For any* required document with specifications (copies required, format requirements) in the data model, the formatted response must include these specifications with that document.

**Validates: Requirements 3.3**

#### Property 10: Office Sequence Order Preservation

*For any* service with a multi-step office visit sequence, the formatted response must display the offices in the correct sequence order as specified in the data model.

**Validates: Requirements 4.1**

#### Property 11: Office Sequence Numbering

*For any* service requiring multiple office visits, each office in the formatted response must be numbered to indicate the visit order.

**Validates: Requirements 4.2**

#### Property 12: Optional Visit Indication

*For any* office visit step marked as optional or conditional in the data model, the formatted response must clearly indicate this status.

**Validates: Requirements 4.3**

#### Property 13: Single Office No Numbering

*For any* service requiring exactly one office visit, the formatted response must display that office without sequence numbering.

**Validates: Requirements 4.4 (edge case)**

#### Property 14: Website Links Completeness

*For any* service with N official website links in the data model, the formatted response must display all N links.

**Validates: Requirements 5.1**

#### Property 15: Website URL Format

*For any* official website link, the formatted response must present it as a properly formatted, clickable URL.

**Validates: Requirements 5.2**

#### Property 16: Website Link Labeling

*For any* service with multiple official websites, each link in the formatted response must be labeled with its purpose.

**Validates: Requirements 5.3**

#### Property 17: HTTPS Validation

*For any* official website link using HTTP protocol, the system should log a warning (but still accept the link for government sites that may not have HTTPS).

**Validates: Requirements 5.4**

#### Property 18: Timeline Units Inclusion

*For any* service with processing timeline data, the formatted response must display the timeline with specific time units (days, weeks, or months).

**Validates: Requirements 6.1**

#### Property 19: Timeline Range Format

*For any* processing timeline with varying duration, the formatted response must display the timeline as a range from minimum to maximum duration.

**Validates: Requirements 6.2**

#### Property 20: Timeline Type Distinction

*For any* service with both processing time and total completion time, the formatted response must clearly distinguish between these two timeline types.

**Validates: Requirements 6.3**

#### Property 21: Expedited Timeline Inclusion

*For any* service with expedited processing available, the formatted response must include both standard and expedited timeline options.

**Validates: Requirements 6.4**

#### Property 22: Service Identification

*For any* valid service query containing the correct keywords, the query processor must identify the specific government service being requested.

**Validates: Requirements 7.1**

#### Property 23: Data Retrieval Completeness

*For any* identified service, the system must retrieve all available information fields for that service from the knowledge base.

**Validates: Requirements 7.2**

#### Property 24: Ambiguous Query Handling

*For any* query that matches multiple services, the system must request clarification from the user and present the matching options.

**Validates: Requirements 7.3**

#### Property 25: Unknown Service Handling

*For any* query that cannot be matched to any known service, the system must inform the user and suggest similar services based on partial keyword matches.

**Validates: Requirements 7.4**

#### Property 26: Format Consistency

*For any* two service responses, the spacing, indentation, and visual hierarchy must be consistent across all sections.

**Validates: Requirements 8.1, 8.3**

#### Property 27: Latest Data Usage

*For any* service with multiple versions in the data source, the system must retrieve and use the most recently updated version based on the last_updated timestamp.

**Validates: Requirements 9.1**

#### Property 28: Timestamp Display

*For any* service information with a last_updated timestamp, the formatted response must display this timestamp.

**Validates: Requirements 9.2**

#### Property 29: Update Propagation

*For any* service data that is updated in the knowledge base, all subsequent queries for that service must return the updated information.

**Validates: Requirements 9.3**

#### Property 30: Data Source Tracking

*For any* piece of service information, the system must maintain metadata tracking the data source to enable verification.

**Validates: Requirements 9.4**

#### Property 31: Visual Separators

*For any* formatted service response with multiple sections, appropriate visual separators (spacing, lines, or formatting) must be present between sections.

**Validates: Requirements 10.3**

#### Property 32: Accessibility Compliance

*For any* formatted service response rendered in HTML, the output must include proper semantic HTML elements and ARIA labels for screen reader compatibility.

**Validates: Requirements 10.4**

## Error Handling

### Error Categories

The system must handle the following error scenarios:

#### 1. Query Processing Errors

**Invalid Query Format**:
- Error: Query is empty or contains only whitespace
- Handling: Return friendly message asking user to provide a query
- User Message: "Please enter a question about a government service."

**Ambiguous Query**:
- Error: Query matches multiple services
- Handling: Present list of matching services and ask for clarification
- User Message: "I found multiple services matching your query: [list]. Which one do you need?"

**Unknown Service**:
- Error: Query doesn't match any known service
- Handling: Suggest similar services based on partial matches
- User Message: "I couldn't find information about that service. Did you mean: [suggestions]?"

#### 2. Data Retrieval Errors

**Service Not Found**:
- Error: Service ID exists in keyword map but not in repository
- Handling: Log error, return "coming soon" message to user
- User Message: "This service guide is coming soon. Please contact the relevant government department."

**Incomplete Service Data**:
- Error: Service exists but has missing required fields
- Handling: Display available data, show "Information not available" for missing categories
- Logging: Log warning with service ID and missing fields

**Data Source Unavailable**:
- Error: Cannot access service repository
- Handling: Return error message, suggest trying again later
- User Message: "I'm having trouble accessing service information. Please try again in a moment."

#### 3. Data Validation Errors

**Invalid Office Location**:
- Error: Office location missing required address fields
- Handling: Skip invalid location, log error, continue with valid locations
- Logging: "Invalid office location for service {service_id}: missing {field}"

**Invalid Document Specification**:
- Error: Required document has invalid copies_required (< 1)
- Handling: Default to 1 copy, log warning
- Logging: "Invalid copies_required for document {doc_name}: {value}, defaulting to 1"

**Invalid URL**:
- Error: Official website URL is malformed
- Handling: Skip invalid URL, log error, continue with valid URLs
- Logging: "Invalid URL for service {service_id}: {url}"

**Invalid Timeline**:
- Error: Processing timeline has minimum > maximum
- Handling: Swap values, log warning
- Logging: "Invalid timeline range for service {service_id}: min={min} > max={max}, swapping"

#### 4. Formatting Errors

**Rendering Failure**:
- Error: Exception during response formatting
- Handling: Log full error, return unformatted data with error notice
- User Message: "I found the information but had trouble formatting it. Here's what I know: [raw data]"

**Missing Template**:
- Error: Category formatter not found
- Handling: Display raw data for that category, log error
- Logging: "No formatter found for category {category}"

### Error Response Structure

```python
class ErrorResponse(BaseModel):
    """Structured error response"""
    error_type: str  # query_error, data_error, validation_error, system_error
    error_code: str  # Specific error code for client handling
    user_message: str  # User-friendly error message
    suggestions: Optional[List[str]] = None  # Suggested actions
    technical_details: Optional[str] = None  # For logging/debugging
    timestamp: datetime
```

### Error Logging Strategy

1. **User-Facing Errors**: Log at INFO level (expected errors like unknown service)
2. **Data Issues**: Log at WARNING level (missing data, validation failures)
3. **System Errors**: Log at ERROR level (exceptions, service unavailable)
4. **Critical Failures**: Log at CRITICAL level (data corruption, security issues)

All logs include:
- Timestamp
- Service ID (if applicable)
- User session ID
- Error details
- Stack trace (for exceptions)

### Graceful Degradation

The system follows these principles for graceful degradation:

1. **Partial Data Display**: If some categories have data and others don't, display what's available
2. **Continue on Error**: Single category formatting error doesn't prevent displaying other categories
3. **Fallback Formatting**: If enhanced formatting fails, fall back to simple text display
4. **User Notification**: Always inform user when information is incomplete or unavailable

## Testing Strategy

### Dual Testing Approach

This feature requires both unit testing and property-based testing for comprehensive coverage:

**Unit Tests**: Focus on specific examples, edge cases, and integration points
- Specific service data examples
- Error condition handling
- API endpoint integration
- Frontend component rendering
- Edge cases (empty data, single items, special characters)

**Property Tests**: Verify universal properties across all inputs
- Response structure consistency
- Data completeness guarantees
- Format consistency across services
- Validation rules
- Round-trip conversions (legacy to enhanced schema)

### Property-Based Testing Configuration

**Framework**: Hypothesis (Python) for backend, fast-check (TypeScript) for frontend

**Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with feature name and property number
- Tag format: `# Feature: government-service-info-enhancement, Property {N}: {property_text}`

**Example Property Test**:

```python
from hypothesis import given, strategies as st
import pytest

# Feature: government-service-info-enhancement, Property 1: All Five Categories Present
@given(service=st.builds(EnhancedServiceGuide, ...))
def test_all_categories_present(service):
    """Property 1: All five categories must be present in formatted response"""
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Verify all five categories are present
    category_headers = [section.header for section in response.sections]
    expected_headers = [
        "📍 Office Locations",
        "📄 Required Documents",
        "🏢 Office Visit Sequence",
        "🔗 Official Websites",
        "⏱️ Processing Timeline"
    ]
    
    assert category_headers == expected_headers, \
        f"Expected all five categories, got: {category_headers}"
```

### Test Coverage Requirements

**Backend**:
- Data models: 100% coverage (all fields, validators)
- ResponseFormatter: 95% coverage (all formatting methods)
- QueryProcessor: 90% coverage (all query paths)
- ServiceRepository: 85% coverage (CRUD operations)
- Error handling: 100% coverage (all error paths)

**Frontend**:
- ServiceGuideDisplay component: 90% coverage
- Response rendering: 85% coverage
- Accessibility features: 100% coverage

### Unit Test Categories

#### 1. Data Model Tests

```python
def test_office_location_validation():
    """Test OfficeLocation model validation"""
    # Valid location
    loc = OfficeLocation(
        name="District Office",
        address="123 Main St",
        city="Mumbai",
        state="Maharashtra",
        postal_code="400001"
    )
    assert loc.name == "District Office"
    
    # Invalid location - missing required field
    with pytest.raises(ValidationError):
        OfficeLocation(
            name="Office",
            address="123 Main St"
            # Missing city, state, postal_code
        )

def test_processing_timeline_range():
    """Test ProcessingTimeline validates min <= max"""
    timeline = ProcessingTimeline(
        minimum_days=7,
        maximum_days=30,
        typical_days=14
    )
    assert timeline.minimum_days <= timeline.typical_days <= timeline.maximum_days
```

#### 2. ResponseFormatter Tests

```python
def test_format_empty_category():
    """Test formatting when category has no data"""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test",
        office_locations=[],  # Empty
        required_documents=[],
        office_visit_sequence=[],
        official_websites=[],
        processing_timelines=[],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # All sections should be present
    assert len(response.sections) == 5
    
    # All should show "Information not available"
    for section in response.sections:
        assert section.is_empty
        assert section.content == "Information not available"

def test_format_single_office_no_numbering():
    """Test single office visit doesn't get numbered"""
    service = create_test_service(
        office_visit_sequence=[
            OfficeVisitStep(
                sequence_number=1,
                office_name="Main Office",
                purpose="Submit application",
                estimated_duration="30 minutes"
            )
        ]
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    sequence_section = response.sections[2]  # Office sequence is 3rd
    # Should not contain "1." numbering
    assert not sequence_section.content.startswith("1.")
    assert "Main Office" in sequence_section.content

def test_format_multiple_offices_with_numbering():
    """Test multiple offices get numbered"""
    service = create_test_service(
        office_visit_sequence=[
            OfficeVisitStep(
                sequence_number=1,
                office_name="Office A",
                purpose="Step 1",
                estimated_duration="30 min"
            ),
            OfficeVisitStep(
                sequence_number=2,
                office_name="Office B",
                purpose="Step 2",
                estimated_duration="45 min"
            )
        ]
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    sequence_section = response.sections[2]
    # Should contain numbered sequence
    assert "1. Office A" in sequence_section.content
    assert "2. Office B" in sequence_section.content
```

#### 3. QueryProcessor Tests

```python
def test_query_single_match():
    """Test query matching single service"""
    repo = ServiceRepository()
    processor = QueryProcessor(repo)
    
    result = processor.process_query("aadhaar name change")
    
    assert result.status == "success"
    assert result.service is not None
    assert result.service.service_id == "aadhaar_name_change"

def test_query_no_match():
    """Test query with no matching service"""
    repo = ServiceRepository()
    processor = QueryProcessor(repo)
    
    result = processor.process_query("flying car license")
    
    assert result.status == "no_match"
    assert result.suggestions is not None
    assert len(result.suggestions) >= 0

def test_query_ambiguous():
    """Test ambiguous query matching multiple services"""
    repo = ServiceRepository()
    processor = QueryProcessor(repo)
    
    # Assuming "status" matches multiple services
    result = processor.process_query("status")
    
    if len(result.matches) > 1:
        assert result.status == "ambiguous"
        assert result.matches is not None
```

#### 4. Integration Tests

```python
@pytest.mark.asyncio
async def test_chat_endpoint_full_flow():
    """Test complete flow from query to formatted response"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    response = client.post(
        "/api/v1/chat/",
        json={
            "message": "aadhaar name change",
            "language": "en"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert "service_guide" in data
    assert data["service_guide"] is not None
    
    # Verify enhanced structure
    guide = data["service_guide"]
    assert "office_locations" in guide
    assert "required_documents" in guide
    assert "office_visit_sequence" in guide
    assert "official_websites" in guide
    assert "processing_timelines" in guide
```

#### 5. Frontend Component Tests

```typescript
import { render, screen } from '@testing-library/react';
import { EnhancedServiceGuideDisplay } from './EnhancedServiceGuideDisplay';

describe('EnhancedServiceGuideDisplay', () => {
  test('renders all five category sections', () => {
    const mockGuide = createMockGuide();
    render(<EnhancedServiceGuideDisplay guide={mockGuide} />);
    
    expect(screen.getByText(/Office Locations/i)).toBeInTheDocument();
    expect(screen.getByText(/Required Documents/i)).toBeInTheDocument();
    expect(screen.getByText(/Office Visit Sequence/i)).toBeInTheDocument();
    expect(screen.getByText(/Official Websites/i)).toBeInTheDocument();
    expect(screen.getByText(/Processing Timeline/i)).toBeInTheDocument();
  });
  
  test('displays "Information not available" for empty categories', () => {
    const mockGuide = createMockGuideWithEmptyCategories();
    render(<EnhancedServiceGuideDisplay guide={mockGuide} />);
    
    const notAvailableMessages = screen.getAllByText(/Information not available/i);
    expect(notAvailableMessages.length).toBeGreaterThan(0);
  });
  
  test('has proper ARIA labels for accessibility', () => {
    const mockGuide = createMockGuide();
    render(<EnhancedServiceGuideDisplay guide={mockGuide} />);
    
    const article = screen.getByRole('article');
    expect(article).toHaveAttribute('aria-label', 'Service Guide');
  });
});
```

### Property-Based Test Examples

```python
from hypothesis import given, strategies as st
from hypothesis.strategies import builds, lists, integers, text

# Strategy for generating test data
@st.composite
def enhanced_service_guide(draw):
    """Generate random EnhancedServiceGuide for testing"""
    return EnhancedServiceGuide(
        service_id=draw(text(min_size=1)),
        service_name=draw(text(min_size=1)),
        category=draw(st.sampled_from(ServiceCategory)),
        description=draw(text(min_size=1)),
        office_locations=draw(lists(builds(OfficeLocation, ...), max_size=5)),
        required_documents=draw(lists(builds(RequiredDocument, ...), max_size=10)),
        office_visit_sequence=draw(lists(builds(OfficeVisitStep, ...), max_size=5)),
        official_websites=draw(lists(builds(OfficialWebsiteLink, ...), max_size=5)),
        processing_timelines=draw(lists(builds(ProcessingTimeline, ...), max_size=3)),
        last_updated=datetime.now(),
        data_source="test",
        available_languages=["en"]
    )

# Feature: government-service-info-enhancement, Property 2: Section Order Consistency
@given(service1=enhanced_service_guide(), service2=enhanced_service_guide())
def test_section_order_consistency(service1, service2):
    """Property 2: Section order must be consistent across all services"""
    formatter = ResponseFormatter()
    
    response1 = formatter.format_service_response(service1)
    response2 = formatter.format_service_response(service2)
    
    headers1 = [s.header for s in response1.sections]
    headers2 = [s.header for s in response2.sections]
    
    assert headers1 == headers2, "Section order must be consistent"

# Feature: government-service-info-enhancement, Property 5: Office Location Completeness
@given(service=enhanced_service_guide())
def test_office_location_completeness(service):
    """Property 5: All office locations must appear in formatted response"""
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Find office locations section
    locations_section = response.sections[0]
    
    if len(service.office_locations) == 0:
        assert locations_section.is_empty
    else:
        # All location names should appear in the formatted content
        for location in service.office_locations:
            assert location.name in locations_section.content, \
                f"Location {location.name} missing from formatted response"

# Feature: government-service-info-enhancement, Property 10: Office Sequence Order Preservation
@given(service=enhanced_service_guide())
def test_office_sequence_order_preservation(service):
    """Property 10: Office sequence order must be preserved"""
    if len(service.office_visit_sequence) < 2:
        return  # Skip if less than 2 steps
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    sequence_section = response.sections[2]  # Office sequence is 3rd section
    
    # Extract office names in order from formatted content
    # Verify they appear in the same order as the data model
    sorted_steps = sorted(service.office_visit_sequence, 
                         key=lambda x: x.sequence_number)
    
    last_pos = -1
    for step in sorted_steps:
        pos = sequence_section.content.find(step.office_name)
        assert pos > last_pos, \
            f"Office {step.office_name} appears out of order"
        last_pos = pos
```

### Test Execution

**Local Development**:
```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app --cov-report=html

# Property-based tests with more iterations
pytest tests/property_tests/ -v --hypothesis-show-statistics

# Frontend tests
cd frontend
npm test -- --coverage
```

**CI/CD Pipeline**:
- Run all tests on every pull request
- Require 85% overall coverage
- Property tests run with 100 iterations minimum
- Integration tests run against test environment
- Accessibility tests run with axe-core

### Test Data Management

**Mock Data**:
- Comprehensive mock services covering all scenarios
- Edge cases: empty categories, single items, maximum items
- Special characters in text fields
- Various URL formats
- Different timeline configurations

**Test Fixtures**:
```python
@pytest.fixture
def sample_service_full():
    """Service with all categories populated"""
    return EnhancedServiceGuide(...)

@pytest.fixture
def sample_service_minimal():
    """Service with minimal data"""
    return EnhancedServiceGuide(...)

@pytest.fixture
def sample_service_empty_categories():
    """Service with some empty categories"""
    return EnhancedServiceGuide(...)
```

