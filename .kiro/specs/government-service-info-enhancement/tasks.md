# Implementation Plan: Government Service Information Enhancement

## Overview

This implementation plan breaks down the enhanced government service information display system into discrete coding tasks. The system will transform the current ad-hoc service response format into a structured format with five key information categories: office locations, required documents, office visit sequences, official website links, and processing timelines.

The implementation follows a layered architecture approach, building from data models up through business logic to API and frontend components. Each task builds incrementally on previous work, with checkpoints to ensure quality and completeness.

## Tasks

- [x] 1. Set up enhanced data models and validation
  - [x] 1.1 Create core data model classes in backend
    - Create `backend/app/models/enhanced_service.py` with all five category models (OfficeLocation, RequiredDocument, OfficeVisitStep, OfficialWebsiteLink, ProcessingTimeline)
    - Create EnhancedServiceGuide model with all required fields
    - Add Pydantic validators for data integrity (coordinates, URL validation, timeline ranges)
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1_

  - [x] 1.2 Write property test for data model validation
    - **Property 30: Data Source Tracking** - Verify all service data maintains source metadata
    - **Validates: Requirements 9.4**

  - [x] 1.3 Create schema adapter for legacy compatibility
    - Create `backend/app/services/schema_adapter.py` with SchemaAdapter class
    - Implement `legacy_to_enhanced()` method to convert existing ServiceGuide to EnhancedServiceGuide
    - Handle missing fields gracefully with appropriate defaults
    - _Requirements: 1.1, 8.2_

  - [x] 1.4 Write unit tests for schema adapter
    - Test conversion of legacy data to enhanced format
    - Test handling of missing optional fields
    - Test preservation of existing data
    - _Requirements: 1.1_

- [x] 2. Implement ResponseFormatter service
  - [x] 2.1 Create ResponseFormatter class with category formatting methods
    - Create `backend/app/services/response_formatter.py` with ResponseFormatter class
    - Implement `format_service_response()` main method
    - Implement category-specific formatters: `_format_office_locations()`, `_format_required_documents()`, `_format_office_sequence()`, `_format_official_websites()`, `_format_processing_timelines()`
    - Define CATEGORY_ORDER and CATEGORY_HEADERS constants
    - _Requirements: 1.1, 1.2, 1.4, 8.1, 8.4_

  - [x] 2.2 Write property tests for ResponseFormatter
    - **Property 1: All Five Categories Present** - Verify all categories appear in every response
    - **Property 2: Section Order Consistency** - Verify consistent category ordering
    - **Property 3: Section Headers Present** - Verify all headers are labeled
    - **Property 4: Missing Data Handling** - Verify "Information not available" for empty categories
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 8.1, 8.2, 8.4**

  - [x] 2.3 Implement office location formatting logic
    - Complete `_format_office_locations()` with address, coordinates, hours, phone
    - Handle optional fields (coordinates, operating_hours, contact_phone)
    - Format multiple locations as separate list items
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 2.4 Write property tests for office location formatting
    - **Property 5: Office Location Completeness** - Verify all N locations displayed
    - **Property 6: Coordinates Inclusion** - Verify coordinates included when available
    - **Property 7: Office Location List Format** - Verify list formatting for multiple locations
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

  - [x] 2.5 Implement document list formatting logic
    - Complete `_format_required_documents()` with document details
    - Include specifications (copies, format requirements, alternatives)
    - Mark optional documents appropriately
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 2.6 Write property tests for document formatting
    - **Property 8: Document List Completeness** - Verify all N documents displayed
    - **Property 9: Document Specifications Inclusion** - Verify specs included
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

  - [x] 2.7 Implement office visit sequence formatting logic
    - Complete `_format_office_sequence()` with sequence numbering
    - Handle single office (no numbering) vs multiple offices (numbered)
    - Mark optional and conditional steps
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 2.8 Write property tests for office sequence formatting
    - **Property 10: Office Sequence Order Preservation** - Verify correct ordering
    - **Property 11: Office Sequence Numbering** - Verify numbering for multiple offices
    - **Property 12: Optional Visit Indication** - Verify optional/conditional marking
    - **Property 13: Single Office No Numbering** - Verify no numbering for single office
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

  - [x] 2.9 Implement website links and timeline formatting logic
    - Complete `_format_official_websites()` with URL formatting and labeling
    - Complete `_format_processing_timelines()` with range and type display
    - Handle multiple timelines (standard vs expedited)
    - _Requirements: 5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 6.4_

  - [ ] 2.10 Write property tests for websites and timelines
    - **Property 14: Website Links Completeness** - Verify all N links displayed
    - **Property 15: Website URL Format** - Verify proper URL formatting
    - **Property 16: Website Link Labeling** - Verify purpose labels
    - **Property 17: HTTPS Validation** - Verify HTTP warning logging
    - **Property 18: Timeline Units Inclusion** - Verify time units displayed
    - **Property 19: Timeline Range Format** - Verify range formatting
    - **Property 20: Timeline Type Distinction** - Verify type distinction
    - **Property 21: Expedited Timeline Inclusion** - Verify expedited options
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3, 6.4**

  - [ ] 2.11 Write property test for format consistency
    - **Property 26: Format Consistency** - Verify consistent spacing and hierarchy
    - **Validates: Requirements 8.1, 8.3**

- [x] 3. Checkpoint - Verify data models and formatting
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement QueryProcessor service enhancements
  - [x] 4.1 Create or enhance QueryProcessor class
    - Create/update `backend/app/services/query_processor.py` with QueryProcessor class
    - Implement `process_query()` method for service identification
    - Implement `_find_matching_services()` for keyword matching
    - Implement `_find_similar_services()` for suggestions
    - Build keyword map for service identification
    - _Requirements: 7.1, 7.3, 7.4_

  - [ ] 4.2 Write property tests for QueryProcessor
    - **Property 22: Service Identification** - Verify correct service identification
    - **Property 24: Ambiguous Query Handling** - Verify clarification requests
    - **Property 25: Unknown Service Handling** - Verify suggestions for unknown services
    - **Validates: Requirements 7.1, 7.3, 7.4**

  - [ ] 4.3 Write unit tests for query processing
    - Test single match scenarios
    - Test no match scenarios with suggestions
    - Test ambiguous query handling
    - Test empty/invalid query handling
    - _Requirements: 7.1, 7.3, 7.4_

- [x] 5. Implement ServiceRepository with enhanced data
  - [x] 5.1 Create or enhance ServiceRepository class
    - Create/update `backend/app/repositories/service_repository.py` with ServiceRepository class
    - Implement CRUD methods: `get_service()`, `get_all_services()`, `update_service()`
    - Implement `_load_services()` and `_load_mock_services()` for data loading
    - Add timestamp-based version selection for latest data
    - _Requirements: 7.2, 9.1, 9.3_

  - [ ] 5.2 Write property tests for ServiceRepository
    - **Property 23: Data Retrieval Completeness** - Verify all fields retrieved
    - **Property 27: Latest Data Usage** - Verify most recent version used
    - **Property 29: Update Propagation** - Verify updates reflected in queries
    - **Validates: Requirements 7.2, 9.1, 9.3**

  - [x] 5.3 Create enhanced mock service data
    - Create `backend/app/data/enhanced_mock_services.py` with comprehensive mock data
    - Include at least 3 services with all five categories populated
    - Include edge cases: empty categories, single items, multiple items
    - Add last_updated timestamps and data_source metadata
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 9.2, 9.4_

  - [ ] 5.4 Write unit tests for mock data
    - Test data validation for all mock services
    - Test edge cases (empty categories, single items)
    - Verify all required fields present
    - _Requirements: 1.1_

- [x] 6. Checkpoint - Verify business logic layer
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Integrate enhanced services into API layer
  - [x] 7.1 Update chat endpoint to use enhanced services
    - Update `backend/app/api/v1/endpoints/chat.py` to use QueryProcessor and ResponseFormatter
    - Wire ServiceRepository, QueryProcessor, and ResponseFormatter together
    - Update response models to include EnhancedServiceGuide structure
    - Handle error responses (no match, ambiguous, system errors)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 8.1_

  - [x] 7.2 Write integration tests for chat endpoint
    - Test full flow from query to formatted response
    - Test error scenarios (unknown service, ambiguous query)
    - Test response structure validation
    - Verify all five categories in API response
    - _Requirements: 1.1, 7.1, 7.2, 7.3, 7.4_

  - [ ] 7.3 Implement error handling and logging
    - Add error response models (ErrorResponse class)
    - Implement error handlers for all error categories
    - Add structured logging for errors and warnings
    - Implement graceful degradation for partial data
    - _Requirements: 8.2, 9.4_

  - [ ] 7.4 Write unit tests for error handling
    - Test all error response types
    - Test logging for different error levels
    - Test graceful degradation scenarios
    - _Requirements: 8.2_

- [ ] 8. Update frontend components for enhanced display
  - [x] 8.1 Create or update TypeScript interfaces for enhanced data
    - Create/update `frontend/src/types/service.ts` with EnhancedServiceGuide interface
    - Add interfaces for all five category types
    - Add ResponseSection and FormattedServiceResponse interfaces
    - _Requirements: 1.1, 1.2_

  - [x] 8.2 Create EnhancedServiceGuideDisplay component
    - Create `frontend/src/components/EnhancedServiceGuideDisplay.tsx` component
    - Implement section rendering for all five categories
    - Add proper semantic HTML structure (article, section, headers)
    - Handle empty categories with "Information not available" display
    - Add last_updated timestamp display
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 9.2, 10.1, 10.3_

  - [ ] 8.3 Write property test for frontend display
    - **Property 28: Timestamp Display** - Verify last_updated displayed
    - **Property 31: Visual Separators** - Verify section separators present
    - **Property 32: Accessibility Compliance** - Verify ARIA labels and semantic HTML
    - **Validates: Requirements 9.2, 10.3, 10.4**

  - [ ] 8.3 Add accessibility features
    - Add ARIA labels for all sections and interactive elements
    - Ensure proper heading hierarchy (h3 for service name, h4 for sections)
    - Add role="article" to main container
    - Test with screen reader compatibility
    - _Requirements: 10.1, 10.4_

  - [x] 8.4 Create CSS styling for enhanced display
    - Create `frontend/src/components/EnhancedServiceGuideDisplay.module.css`
    - Style section headers with consistent spacing
    - Add visual separators between sections
    - Ensure responsive design for mobile devices
    - Add styles for empty state ("Information not available")
    - _Requirements: 10.1, 10.3_

  - [ ] 8.5 Write unit tests for frontend component
    - Test rendering of all five category sections
    - Test display of "Information not available" for empty categories
    - Test ARIA labels and accessibility features
    - Test responsive behavior
    - _Requirements: 1.1, 1.2, 1.3, 10.4_

- [ ] 9. Checkpoint - Verify frontend integration
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Wire everything together and test end-to-end
  - [x] 10.1 Update chat interface to use EnhancedServiceGuideDisplay
    - Update main chat component to render EnhancedServiceGuideDisplay
    - Handle API response with enhanced structure
    - Update error message display for new error types
    - _Requirements: 1.1, 7.3, 7.4_

  - [ ] 10.2 Add response consistency validation
    - Add validation middleware to ensure all responses have five categories
    - Log warnings for any inconsistencies
    - _Requirements: 8.1, 8.2_

  - [x] 10.3 Write end-to-end integration tests
    - Test complete user flow: query → API → formatted response → display
    - Test with various service types and data completeness levels
    - Test error flows (unknown service, ambiguous query)
    - Verify consistent structure across all services
    - _Requirements: 1.1, 1.4, 7.1, 8.1, 8.4_

  - [ ] 10.4 Create test data for manual verification
    - Add diverse test services covering all scenarios
    - Document test cases for manual QA
    - _Requirements: 1.1, 9.1_

- [x] 11. Final checkpoint - Complete system verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The implementation builds incrementally: data models → business logic → API → frontend
- All code should follow existing project structure and conventions (FastAPI backend, Next.js frontend)
- Mock data is used initially; database integration can be added later
- Legacy schema support ensures backward compatibility during migration
