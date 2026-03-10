/**
 * End-to-End Frontend Integration Tests - Task 10.3
 * 
 * Tests the EnhancedServiceGuideDisplay component with various service types
 * and data completeness levels to ensure consistent rendering and accessibility.
 * 
 * **Validates: Requirements 1.1, 1.4, 8.1, 8.4, 10.1, 10.3**
 */

import React from 'react';
import { render, screen, within } from '@testing-library/react';
import { EnhancedServiceGuideDisplay } from '../EnhancedServiceGuideDisplay';
import { EnhancedServiceGuide, ServiceCategory } from '../../types/service';

// Mock data generators for testing
const createMockServiceGuide = (overrides: Partial<EnhancedServiceGuide> = {}): EnhancedServiceGuide => ({
  service_id: 'test_service',
  service_name: 'Test Government Service',
  category: ServiceCategory.CERTIFICATE,
  description: 'A test government service for validation',
  office_locations: [
    {
      name: 'Main District Office',
      address: '123 Government Street',
      city: 'Test City',
      state: 'Test State',
      postal_code: '123456',
      coordinates: {
        latitude: 12.9716,
        longitude: 77.5946
      },
      operating_hours: '9:00 AM - 5:00 PM',
      contact_phone: '+91-80-12345678'
    }
  ],
  required_documents: [
    {
      document_name: 'Identity Proof',
      description: 'Valid government-issued photo ID',
      copies_required: 2,
      format_requirements: 'Original + photocopy',
      is_mandatory: true,
      alternatives: ['Aadhaar Card', 'Passport', 'Driving License']
    },
    {
      document_name: 'Address Proof',
      description: 'Proof of current residential address',
      copies_required: 1,
      format_requirements: 'Original document',
      is_mandatory: false,
      alternatives: ['Utility Bill', 'Bank Statement']
    }
  ],
  office_visit_sequence: [
    {
      sequence_number: 1,
      office_name: 'Document Verification Office',
      purpose: 'Submit and verify all required documents',
      estimated_duration: '30 minutes',
      is_optional: false,
      is_conditional: false,
      condition: null
    },
    {
      sequence_number: 2,
      office_name: 'Processing Office',
      purpose: 'Application processing and approval',
      estimated_duration: '15 minutes',
      is_optional: false,
      is_conditional: true,
      condition: 'If additional verification required'
    }
  ],
  official_websites: [
    {
      url: 'https://services.gov.in/test-service',
      purpose: 'Online Application Portal',
      description: 'Submit applications and track status online'
    },
    {
      url: 'https://status.gov.in/track',
      purpose: 'Status Tracking',
      description: 'Track your application status'
    }
  ],
  processing_timelines: [
    {
      minimum_days: 7,
      maximum_days: 21,
      typical_days: 14,
      time_unit: 'days',
      processing_type: 'standard',
      notes: 'Processing time may vary during peak seasons',
      factors_affecting_time: [
        'Document completeness',
        'Verification requirements',
        'Peak season volume'
      ]
    }
  ],
  last_updated: '2024-01-15T10:30:00Z',
  data_source: 'test_data',
  available_languages: ['en', 'hi']
});

const createEmptyServiceGuide = (): EnhancedServiceGuide => ({
  service_id: 'empty_service',
  service_name: 'Empty Test Service',
  category: ServiceCategory.PERMIT,
  description: 'A service with no additional information',
  office_locations: [],
  required_documents: [],
  office_visit_sequence: [],
  official_websites: [],
  processing_timelines: [],
  last_updated: '2024-01-15T10:30:00Z',
  data_source: 'test_data',
  available_languages: ['en']
});

describe('EnhancedServiceGuideDisplay - End-to-End Integration', () => {
  
  describe('Complete Service Display Flow', () => {
    test('renders complete service with all five categories in correct order', () => {
      /**
       * Test complete user flow: API response → component rendering → display
       * **Validates: Requirements 1.1, 1.4, 8.4**
       */
      const mockGuide = createMockServiceGuide();
      render(<EnhancedServiceGuideDisplay guide={mockGuide} />);

      // Verify service header information
      expect(screen.getByText('Test Government Service')).toBeInTheDocument();
      expect(screen.getByText('A test government service for validation')).toBeInTheDocument();
      expect(screen.getByText(/Last updated: January 15, 2024/)).toBeInTheDocument();

      // Verify all five categories are present in correct order
      const sections = screen.getAllByRole('region');
      expect(sections).toHaveLength(5);

      const expectedHeaders = [
        '📍 Office Locations',
        '📄 Required Documents',
        '🏢 Office Visit Sequence',
        '🔗 Official Websites',
        '⏱️ Processing Timeline'
      ];

      expectedHeaders.forEach((header, index) => {
        const section = sections[index];
        expect(within(section).getByRole('heading', { level: 4 })).toHaveTextContent(header);
      });
    });

    test('displays office locations with complete information', () => {
      /**
       * Test office location rendering with all details
       * **Validates: Requirements 2.1, 2.2, 2.3**
       */
      const mockGuide = createMockServiceGuide();
      render(<EnhancedServiceGuideDisplay guide={mockGuide} />);

      // Find office locations section
      const officeSection = screen.getByLabelText(/office-locations-heading/);
      
      // Verify office details are displayed
      expect(within(officeSection).getByText('Main District Office')).toBeInTheDocument();
      expect(within(officeSection).getByText(/123 Government Street, Test City, Test State 123456/)).toBeInTheDocument();
      expect(within(officeSection).getByText(/Coordinates: 12.9716, 77.5946/)).toBeInTheDocument();
      expect(within(officeSection).getByText(/Hours: 9:00 AM - 5:00 PM/)).toBeInTheDocument();
      expect(within(officeSection).getByText(/Phone: \+91-80-12345678/)).toBeInTheDocument();
    });

    test('displays required documents with specifications', () => {
      /**
       * Test document list rendering with all specifications
       * **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
       */
      const mockGuide = createMockServiceGuide();
      render(<EnhancedServiceGuideDisplay guide={mockGuide} />);

      // Find required documents section
      const documentsSection = screen.getByLabelText(/required-documents-heading/);
      
      // Verify document details
      expect(within(documentsSection).getByText('Identity Proof')).toBeInTheDocument();
      expect(within(documentsSection).getByText('Valid government-issued photo ID')).toBeInTheDocument();
      expect(within(documentsSection).getByText('Copies required: 2')).toBeInTheDocument();
      expect(within(documentsSection).getByText('Format: Original + photocopy')).toBeInTheDocument();
      expect(within(documentsSection).getByText(/Alternatives: Aadhaar Card, Passport, Driving License/)).toBeInTheDocument();

      // Verify optional document marking
      expect(within(documentsSection).getByText('Address Proof')).toBeInTheDocument();
      expect(within(documentsSection).getByText('Optional')).toBeInTheDocument();
    });

    test('displays office visit sequence with proper numbering', () => {
      /**
       * Test office sequence rendering with correct order and numbering
       * **Validates: Requirements 4.1, 4.2, 4.3**
       */
      const mockGuide = createMockServiceGuide();
      render(<EnhancedServiceGuideDisplay guide={mockGuide} />);

      // Find office sequence section
      const sequenceSection = screen.getByLabelText(/office-sequence-heading/);
      
      // Verify sequence numbering and details
      expect(within(sequenceSection).getByText('1')).toBeInTheDocument();
      expect(within(sequenceSection).getByText('Document Verification Office')).toBeInTheDocument();
      expect(within(sequenceSection).getByText('Submit and verify all required documents')).toBeInTheDocument();
      expect(within(sequenceSection).getByText('Duration: 30 minutes')).toBeInTheDocument();

      expect(within(sequenceSection).getByText('2')).toBeInTheDocument();
      expect(within(sequenceSection).getByText('Processing Office')).toBeInTheDocument();
      expect(within(sequenceSection).getByText('Condition: If additional verification required')).toBeInTheDocument();
    });

    test('displays official websites as clickable links', () => {
      /**
       * Test website links rendering with proper formatting
       * **Validates: Requirements 5.1, 5.2, 5.3**
       */
      const mockGuide = createMockServiceGuide();
      render(<EnhancedServiceGuideDisplay guide={mockGuide} />);

      // Find official websites section
      const websitesSection = screen.getByLabelText(/official-websites-heading/);
      
      // Verify website links
      const portalLink = within(websitesSection).getByRole('link', { name: /Online Application Portal/ });
      expect(portalLink).toHaveAttribute('href', 'https://services.gov.in/test-service');
      expect(portalLink).toHaveAttribute('target', '_blank');
      expect(portalLink).toHaveAttribute('rel', 'noopener noreferrer');

      const statusLink = within(websitesSection).getByRole('link', { name: /Status Tracking/ });
      expect(statusLink).toHaveAttribute('href', 'https://status.gov.in/track');

      // Verify descriptions
      expect(within(websitesSection).getByText('Submit applications and track status online')).toBeInTheDocument();
      expect(within(websitesSection).getByText('Track your application status')).toBeInTheDocument();
    });

    test('displays processing timeline with all details', () => {
      /**
       * Test timeline rendering with complete information
       * **Validates: Requirements 6.1, 6.2, 6.3**
       */
      const mockGuide = createMockServiceGuide();
      render(<EnhancedServiceGuideDisplay guide={mockGuide} />);

      // Find processing timeline section
      const timelineSection = screen.getByLabelText(/processing-timeline-heading/);
      
      // Verify timeline details
      expect(within(timelineSection).getByText('Standard Processing')).toBeInTheDocument();
      expect(within(timelineSection).getByText('Typical: 14 days')).toBeInTheDocument();
      expect(within(timelineSection).getByText('Range: 7-21 days')).toBeInTheDocument();
      expect(within(timelineSection).getByText('Processing time may vary during peak seasons')).toBeInTheDocument();
      
      // Verify factors affecting time
      expect(within(timelineSection).getByText('Factors affecting time:')).toBeInTheDocument();
      expect(within(timelineSection).getByText('Document completeness')).toBeInTheDocument();
      expect(within(timelineSection).getByText('Verification requirements')).toBeInTheDocument();
      expect(within(timelineSection).getByText('Peak season volume')).toBe
InTheDocument();
    });
  });

  describe('Data Completeness Level Testing', () => {
    test('handles empty categories gracefully', () => {
      /**
       * Test rendering when service has no data in categories
       * **Validates: Requirements 1.3, 8.2**
       */
      const emptyGuide = createEmptyServiceGuide();
      render(<EnhancedServiceGuideDisplay guide={emptyGuide} />);

      // Verify all sections are still present
      const sections = screen.getAllByRole('region');
      expect(sections).toHaveLength(5);

      // Verify "Information not available" messages
      const notAvailableMessages = screen.getAllByText('Information not available');
      expect(notAvailableMessages).toHaveLength(5);

      // Verify section headers are still displayed
      const expectedHeaders = [
        '📍 Office Locations',
        '📄 Required Documents',
        '🏢 Office Visit Sequence',
        '🔗 Official Websites',
        '⏱️ Processing Timeline'
      ];

      expectedHeaders.forEach(header => {
        expect(screen.getByRole('heading', { name: header })).toBeInTheDocument();
      });
    });

    test('handles single office visit without numbering', () => {
      /**
       * Test single office visit rendering (no sequence numbers)
       * **Validates: Requirements 4.4**
       */
      const singleOfficeGuide = createMockServiceGuide({
        office_visit_sequence: [
          {
            sequence_number: 1,
            office_name: 'Single Office',
            purpose: 'Complete all procedures',
            estimated_duration: '45 minutes',
            is_optional: false,
            is_conditional: false,
            condition: null
          }
        ]
      });

      render(<EnhancedServiceGuideDisplay guide={singleOfficeGuide} />);

      const sequenceSection = screen.getByLabelText(/office-sequence-heading/);
      
      // Should not display sequence number for single office
      expect(within(sequenceSection).queryByText('1')).not.toBeInTheDocument();
      expect(within(sequenceSection).getByText('Single Office')).toBeInTheDocument();
      expect(within(sequenceSection).getByText('Complete all procedures')).toBeInTheDocument();
    });

    test('handles mixed data availability', () => {
      /**
       * Test service with some categories having data and others empty
       * **Validates: Requirements 1.1, 1.3**
       */
      const mixedGuide = createMockServiceGuide({
        office_locations: [], // Empty
        required_documents: [
          {
            document_name: 'Test Document',
            description: 'A test document',
            copies_required: 1,
            format_requirements: null,
            is_mandatory: true,
            alternatives: null
          }
        ],
        office_visit_sequence: [], // Empty
        official_websites: [
          {
            url: 'https://test.gov.in',
            purpose: 'Test Portal',
            description: null
          }
        ],
        processing_timelines: [] // Empty
      });

      render(<EnhancedServiceGuideDisplay guide={mixedGuide} />);

      // Verify empty sections show "Information not available"
      const officeSection = screen.getByLabelText(/office-locations-heading/);
      expect(within(officeSection).getByText('Information not available')).toBeInTheDocument();

      // Verify sections with data show content
      const documentsSection = screen.getByLabelText(/required-documents-heading/);
      expect(within(documentsSection).getByText('Test Document')).toBeInTheDocument();
      expect(within(documentsSection).queryByText('Information not available')).not.toBeInTheDocument();

      const websitesSection = screen.getByLabelText(/official-websites-heading/);
      expect(within(websitesSection).getByRole('link')).toHaveAttribute('href', 'https://test.gov.in');
    });
  });

  describe('Various Service Types Consistency', () => {
    test('maintains consistent structure across different service categories', () => {
      /**
       * Test consistency across different service types
       * **Validates: Requirements 8.1, 8.4**
       */
      const serviceTypes = [
        { category: ServiceCategory.CERTIFICATE, name: 'Birth Certificate Service' },
        { category: ServiceCategory.LICENSE, name: 'Driving License Service' },
        { category: ServiceCategory.PERMIT, name: 'Construction Permit Service' },
        { category: ServiceCategory.REGISTRATION, name: 'Vehicle Registration Service' }
      ];

      serviceTypes.forEach(serviceType => {
        const guide = createMockServiceGuide({
          category: serviceType.category,
          service_name: serviceType.name
        });

        const { unmount } = render(<EnhancedServiceGuideDisplay guide={guide} />);

        // Verify consistent structure
        const sections = screen.getAllByRole('region');
        expect(sections).toHaveLength(5);

        // Verify consistent headers
        const expectedHeaders = [
          '📍 Office Locations',
          '📄 Required Documents',
          '🏢 Office Visit Sequence',
          '🔗 Official Websites',
          '⏱️ Processing Timeline'
        ];

        expectedHeaders.forEach(header => {
          expect(screen.getByRole('heading', { name: header })).toBeInTheDocument();
        });

        unmount();
      });
    });

    test('handles different timeline configurations', () => {
      /**
       * Test various timeline configurations
       * **Validates: Requirements 6.1, 6.2, 6.4**
       */
      const timelineVariations = [
        {
          minimum_days: 1,
          maximum_days: 3,
          typical_days: 2,
          time_unit: 'days',
          processing_type: 'expedited'
        },
        {
          minimum_days: 2,
          maximum_days: 8,
          typical_days: 4,
          time_unit: 'weeks',
          processing_type: 'standard'
        },
        {
          minimum_days: 1,
          maximum_days: 6,
          typical_days: 3,
          time_unit: 'months',
          processing_type: 'priority'
        }
      ];

      timelineVariations.forEach((timeline, index) => {
        const guide = createMockServiceGuide({
          processing_timelines: [timeline]
        });

        const { unmount } = render(<EnhancedServiceGuideDisplay guide={guide} />);

        const timelineSection = screen.getByLabelText(/processing-timeline-heading/);
        
        // Verify timeline details are displayed
        expect(within(timelineSection).getByText(`${timeline.processing_type.charAt(0).toUpperCase() + timeline.processing_type.slice(1)} Processing`)).toBeInTheDocument();
        expect(within(timelineSection).getByText(`Typical: ${timeline.typical_days} ${timeline.time_unit}`)).toBeInTheDocument();
        expect(within(timelineSection).getByText(`Range: ${timeline.minimum_days}-${timeline.maximum_days} ${timeline.time_unit}`)).toBeInTheDocument();

        unmount();
      });
    });
  });

  describe('Accessibility and User Experience', () => {
    test('provides proper ARIA labels and semantic structure', () => {
      /**
       * Test accessibility features for screen readers
       * **Validates: Requirements 10.1, 10.4**
       */
      const mockGuide = createMockServiceGuide();
      render(<EnhancedServiceGuideDisplay guide={mockGuide} />);

      // Verify main article has proper ARIA label
      const article = screen.getByRole('article');
      expect(article).toHaveAttribute('aria-label', 'Service Guide');

      // Verify all sections have proper headings
      const sections = screen.getAllByRole('region');
      sections.forEach((section, index) => {
        const heading = within(section).getByRole('heading', { level: 4 });
        expect(heading).toHaveAttribute('id');
        expect(section).toHaveAttribute('aria-labelledby', heading.id);
      });

      // Verify heading hierarchy
      expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent('Test Government Service');
      const level4Headings = screen.getAllByRole('heading', { level: 4 });
      expect(level4Headings).toHaveLength(5);
    });

    test('handles long content gracefully', () => {
      /**
       * Test rendering with very long content
       * **Validates: Requirements 10.3**
       */
      const longContentGuide = createMockServiceGuide({
        service_name: 'Very Long Government Service Name That Might Wrap Multiple Lines',
        description: 'This is a very long description that contains multiple sentences and detailed information about the government service. It should wrap properly and maintain readability across different screen sizes and devices.',
        office_locations: [
          {
            name: 'Very Long Office Name That Might Cause Layout Issues',
            address: 'A very long address with multiple components including building number, street name, area, landmark, and additional location details',
            city: 'Very Long City Name',
            state: 'Very Long State Name',
            postal_code: '123456',
            coordinates: null,
            operating_hours: 'Monday to Friday: 9:00 AM to 5:00 PM, Saturday: 9:00 AM to 1:00 PM, Sunday: Closed',
            contact_phone: '+91-80-12345678'
          }
        ]
      });

      render(<EnhancedServiceGuideDisplay guide={longContentGuide} />);

      // Verify long content is displayed
      expect(screen.getByText(/Very Long Government Service Name/)).toBeInTheDocument();
      expect(screen.getByText(/This is a very long description/)).toBeInTheDocument();
      expect(screen.getByText(/Very Long Office Name/)).toBeInTheDocument();
    });

    test('handles special characters and unicode', () => {
      /**
       * Test rendering with special characters and unicode
       * **Validates: Requirements 10.1**
       */
      const unicodeGuide = createMockServiceGuide({
        service_name: 'Service with Special Characters & Unicode: आधार',
        description: 'Description with émojis 🏛️ and spëcial çharacters',
        office_locations: [
          {
            name: 'Office with Unicode: सरकारी कार्यालय',
            address: '123 Street with Special Chars & Symbols',
            city: 'City with Àccents',
            state: 'State with Ümlauts',
            postal_code: '123456',
            coordinates: null,
            operating_hours: null,
            contact_phone: null
          }
        ]
      });

      render(<EnhancedServiceGuideDisplay guide={unicodeGuide} />);

      // Verify unicode and special characters are displayed correctly
      expect(screen.getByText(/Service with Special Characters & Unicode: आधार/)).toBeInTheDocument();
      expect(screen.getByText(/Description with émojis 🏛️/)).toBeInTheDocument();
      expect(screen.getByText(/Office with Unicode: सरकारी कार्यालय/)).toBeInTheDocument();
    });
  });

  describe('Error Handling and Edge Cases', () => {
    test('handles missing optional fields gracefully', () => {
      /**
       * Test rendering when optional fields are missing
       * **Validates: Requirements 1.3**
       */
      const minimalGuide = createMockServiceGuide({
        office_locations: [
          {
            name: 'Basic Office',
            address: 'Basic Address',
            city: 'City',
            state: 'State',
            postal_code: '123456',
            coordinates: undefined, // Optional field missing
            operating_hours: undefined, // Optional field missing
            contact_phone: undefined // Optional field missing
          }
        ],
        required_documents: [
          {
            document_name: 'Basic Document',
            description: undefined, // Optional field missing
            copies_required: 1,
            format_requirements: undefined, // Optional field missing
            is_mandatory: true,
            alternatives: undefined // Optional field missing
          }
        ]
      });

      render(<EnhancedServiceGuideDisplay guide={minimalGuide} />);

      // Verify basic information is displayed
      expect(screen.getByText('Basic Office')).toBeInTheDocument();
      expect(screen.getByText('Basic Document')).toBeInTheDocument();

      // Verify optional fields don't cause errors
      const officeSection = screen.getByLabelText(/office-locations-heading/);
      expect(within(officeSection).queryByText('Coordinates:')).not.toBeInTheDocument();
      expect(within(officeSection).queryByText('Hours:')).not.toBeInTheDocument();
      expect(within(officeSection).queryByText('Phone:')).not.toBeInTheDocument();
    });

    test('handles invalid date formats gracefully', () => {
      /**
       * Test date formatting with invalid dates
       * **Validates: Requirements 9.2**
       */
      const invalidDateGuide = createMockServiceGuide({
        last_updated: 'invalid-date-format'
      });

      render(<EnhancedServiceGuideDisplay guide={invalidDateGuide} />);

      // Should display the raw string if date parsing fails
      expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
      expect(screen.getByText(/invalid-date-format/)).toBeInTheDocument();
    });

    test('handles empty arrays and null values', () => {
      /**
       * Test rendering with various empty/null scenarios
       * **Validates: Requirements 1.3**
       */
      const edgeCaseGuide: EnhancedServiceGuide = {
        service_id: 'edge_case',
        service_name: 'Edge Case Service',
        category: ServiceCategory.OTHER,
        description: 'Testing edge cases',
        office_locations: [],
        required_documents: [],
        office_visit_sequence: [],
        official_websites: [],
        processing_timelines: [],
        last_updated: '',
        data_source: 'test',
        available_languages: []
      };

      render(<EnhancedServiceGuideDisplay guide={edgeCaseGuide} />);

      // Verify component renders without crashing
      expect(screen.getByText('Edge Case Service')).toBeInTheDocument();
      
      // All sections should show "Information not available"
      const notAvailableMessages = screen.getAllByText('Information not available');
      expect(notAvailableMessages).toHaveLength(5);
    });
  });

  describe('Performance and Rendering', () => {
    test('renders large datasets efficiently', () => {
      /**
       * Test rendering performance with large amounts of data
       * **Validates: Requirements 8.1**
       */
      const largeDataGuide = createMockServiceGuide({
        office_locations: Array.from({ length: 10 }, (_, i) => ({
          name: `Office ${i + 1}`,
          address: `Address ${i + 1}`,
          city: `City ${i + 1}`,
          state: `State ${i + 1}`,
          postal_code: `12345${i}`,
          coordinates: undefined,
          operating_hours: undefined,
          contact_phone: undefined
        })),
        required_documents: Array.from({ length: 15 }, (_, i) => ({
          document_name: `Document ${i + 1}`,
          description: `Description for document ${i + 1}`,
          copies_required: 1,
          format_requirements: undefined,
          is_mandatory: i % 2 === 0,
          alternatives: undefined
        })),
        office_visit_sequence: Array.from({ length: 8 }, (_, i) => ({
          sequence_number: i + 1,
          office_name: `Office Step ${i + 1}`,
          purpose: `Purpose ${i + 1}`,
          estimated_duration: '30 minutes',
          is_optional: false,
          is_conditional: false,
          condition: undefined
        }))
      });

      const startTime = performance.now();
      render(<EnhancedServiceGuideDisplay guide={largeDataGuide} />);
      const endTime = performance.now();

      // Rendering should complete quickly (under 100ms)
      expect(endTime - startTime).toBeLessThan(100);

      // Verify some data is rendered (not all to avoid test complexity)
      expect(screen.getByText('Office 1')).toBeInTheDocument();
      expect(screen.getByText('Document 1')).toBeInTheDocument();
      expect(screen.getByText('Office Step 1')).toBeInTheDocument();
    });

    test('maintains consistent styling across all sections', () => {
      /**
       * Test CSS class application and styling consistency
       * **Validates: Requirements 8.3, 10.3**
       */
      const mockGuide = createMockServiceGuide();
      const { container } = render(<EnhancedServiceGuideDisplay guide={mockGuide} />);

      // Verify main container has proper CSS class
      const guideContainer = container.querySelector('[class*="guideContainer"]');
      expect(guideContainer).toBeInTheDocument();

      // Verify all sections have consistent CSS classes (use more specific selector)
      const sections = container.querySelectorAll('section[class*="section"]');
      expect(sections).toHaveLength(5);

      sections.forEach(section => {
        expect(section).toHaveClass(expect.stringMatching(/section/));
        
        // Each section should have header and content
        const header = section.querySelector('[class*="sectionHeader"]');
        const content = section.querySelector('[class*="sectionContent"]');
        expect(header).toBeInTheDocument();
        expect(content).toBeInTheDocument();
      });
    });
  });
});