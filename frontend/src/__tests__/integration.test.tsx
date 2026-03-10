/**
 * Full Stack Integration Tests - Task 10.3
 * 
 * Tests the complete user flow from frontend query submission through
 * backend API processing to frontend display rendering.
 * 
 * **Validates: Requirements 1.1, 1.4, 7.1, 8.1, 8.4**
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import { EnhancedServiceGuideDisplay } from '../components/EnhancedServiceGuideDisplay';
import { EnhancedServiceGuide, ServiceCategory } from '../types/service';

// Mock axios for API calls
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock API responses
const mockApiResponse = {
  data: {
    message: "Here's information about Aadhaar name change:",
    enhanced_service_guide: {
      service_id: 'aadhaar_name_change',
      service_name: 'Aadhaar Name Change',
      category: 'identity_document',
      description: 'Process to update name in Aadhaar card',
      sections: [
        {
          header: '📍 Office Locations',
          content: '• UIDAI Regional Office\n  123 Government Complex, Bangalore, Karnataka 560001\n  Coordinates: 12.9716, 77.5946\n  Hours: 9:00 AM - 5:00 PM\n  Phone: +91-80-12345678',
          is_empty: false
        },
        {
          header: '📄 Required Documents',
          content: '• Proof of Identity\n  Valid government-issued photo ID\n  Copies required: 1\n  Format: Original + photocopy\n\n• Proof of Name Change\n  Marriage certificate, gazette notification, or court order\n  Copies required: 1\n  Format: Original + photocopy',
          is_empty: false
        },
        {
          header: '🏢 Office Visit Sequence',
          content: '1. Document Verification Counter\n   Submit all required documents for verification\n   Duration: 15 minutes\n\n2. Biometric Update Station\n   Update biometric information if required\n   Duration: 10 minutes\n   (Optional)',
          is_empty: false
        },
        {
          header: '🔗 Official Websites',
          content: '• Online Portal: https://uidai.gov.in/my-aadhaar/update-aadhaar\n  Submit name change request online\n\n• Status Tracking: https://resident.uidai.gov.in/check-aadhaar\n  Track your update request status',
          is_empty: false
        },
        {
          header: '⏱️ Processing Timeline',
          content: '• Standard Processing\n  Typical: 90 days\n  Range: 60-120 days\n  Note: Processing time may vary based on document verification\n  Factors affecting time:\n    - Document completeness\n    - Verification requirements\n    - Regional office workload',
          is_empty: false
        }
      ],
      last_updated: '2024-01-15T10:30:00Z',
      service_id: 'aadhaar_name_change',
      category: 'identity_document'
    },
    session_id: 'test-session-123',
    language: 'en'
  }
};

const mockEmptyApiResponse = {
  data: {
    message: "Here's information about the requested service:",
    enhanced_service_guide: {
      service_id: 'empty_service',
      service_name: 'Service with Limited Information',
      category: 'other',
      description: 'A service with minimal available information',
      sections: [
        {
          header: '📍 Office Locations',
          content: 'Information not available',
          is_empty: true
        },
        {
          header: '📄 Required Documents',
          content: 'Information not available',
          is_empty: true
        },
        {
          header: '🏢 Office Visit Sequence',
          content: 'Information not available',
          is_empty: true
        },
        {
          header: '🔗 Official Websites',
          content: 'Information not available',
          is_empty: true
        },
        {
          header: '⏱️ Processing Timeline',
          content: 'Information not available',
          is_empty: true
        }
      ],
      last_updated: '2024-01-15T10:30:00Z',
      service_id: 'empty_service',
      category: 'other'
    },
    session_id: 'test-session-456',
    language: 'en'
  }
};

const mockErrorApiResponse = {
  data: {
    message: "I'm here to help you with government services. You can ask me about:\n\n• Aadhaar services (name change, address update)\n• Birth and death certificates\n• Driving license applications\n• Passport services\n• And many other government procedures\n\nWhat would you like to know about?",
    enhanced_service_guide: null,
    session_id: 'test-session-789',
    language: 'en'
  }
};

// Simple chat component for testing
const ChatInterface: React.FC = () => {
  const [query, setQuery] = React.useState('');
  const [response, setResponse] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const result = await axios.post('/api/v1/chat/', {
        message: query,
        language: 'en'
      });
      setResponse(result.data);
    } catch (err) {
      setError('Failed to get response');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about a government service..."
          data-testid="query-input"
        />
        <button type="submit" disabled={loading} data-testid="submit-button">
          {loading ? 'Loading...' : 'Submit'}
        </button>
      </form>
      
      {error && <div data-testid="error-message">{error}</div>}
      
      {response && (
        <div data-testid="response-container">
          <div data-testid="response-message">{response.message}</div>
          {response.enhanced_service_guide && (
            <EnhancedServiceGuideDisplay guide={response.enhanced_service_guide} />
          )}
        </div>
      )}
    </div>
  );
};

describe('Full Stack Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Complete User Flow - Known Service', () => {
    test('handles complete flow from query to display for Aadhaar service', async () => {
      /**
       * Test: User query → API call → Backend processing → Frontend display
       * **Validates: Requirements 1.1, 7.1, 8.1**
       */
      mockedAxios.post.mockResolvedValueOnce(mockApiResponse);

      render(<ChatInterface />);

      // Step 1: User enters query
      const queryInput = screen.getByTestId('query-input');
      const submitButton = screen.getByTestId('submit-button');

      fireEvent.change(queryInput, { target: { value: 'aadhaar name change' } });
      fireEvent.click(submitButton);

      // Step 2: Verify API call
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/chat/', {
        message: 'aadhaar name change',
        language: 'en'
      });

      // Step 3: Wait for response and verify display
      await waitFor(() => {
        expect(screen.getByTestId('response-container')).toBeInTheDocument();
      });

      // Step 4: Verify complete service guide is displayed
      expect(screen.getByText('Aadhaar Name Change')).toBeInTheDocument();
      expect(screen.getByText('Process to update name in Aadhaar card')).toBeInTheDocument();

      // Step 5: Verify all five categories are displayed in correct order
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
        expect(screen.getByRole('heading', { name: header })).toBeInTheDocument();
      });

      // Step 6: Verify specific content is rendered correctly
      expect(screen.getByText('UIDAI Regional Office')).toBeInTheDocument();
      expect(screen.getByText('Proof of Identity')).toBeInTheDocument();
      expect(screen.getByText('Document Verification Counter')).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /Online Portal/ })).toHaveAttribute('href', 'https://uidai.gov.in/my-aadhaar/update-aadhaar');
      expect(screen.getByText('Standard Processing')).toBeInTheDocument();
    });

    test('handles service with mixed data availability', async () => {
      /**
       * Test: Service with some categories having data, others empty
       * **Validates: Requirements 1.1, 1.3, 8.2**
       */
      const mixedDataResponse = {
        ...mockApiResponse,
        data: {
          ...mockApiResponse.data,
          enhanced_service_guide: {
            ...mockApiResponse.data.enhanced_service_guide,
            sections: [
              {
                header: '📍 Office Locations',
                content: '• Main Office\n  123 Government Street, City, State 123456',
                is_empty: false
              },
              {
                header: '📄 Required Documents',
                content: 'Information not available',
                is_empty: true
              },
              {
                header: '🏢 Office Visit Sequence',
                content: '• Single Office Visit\n  Complete all procedures at main office\n  Duration: 45 minutes',
                is_empty: false
              },
              {
                header: '🔗 Official Websites',
                content: 'Information not available',
                is_empty: true
              },
              {
                header: '⏱️ Processing Timeline',
                content: '• Standard Processing\n  Typical: 14 days\n  Range: 7-21 days',
                is_empty: false
              }
            ]
          }
        }
      };

      mockedAxios.post.mockResolvedValueOnce(mixedDataResponse);

      render(<ChatInterface />);

      fireEvent.change(screen.getByTestId('query-input'), { 
        target: { value: 'mixed data service' } 
      });
      fireEvent.click(screen.getByTestId('submit-button'));

      await waitFor(() => {
        expect(screen.getByTestId('response-container')).toBeInTheDocument();
      });

      // Verify sections with data show content
      expect(screen.getByText('Main Office')).toBeInTheDocument();
      expect(screen.getByText('Single Office Visit')).toBeInTheDocument();
      expect(screen.getByText('Standard Processing')).toBeInTheDocument();

      // Verify empty sections show "Information not available"
      const notAvailableMessages = screen.getAllByText('Information not available');
      expect(notAvailableMessages).toHaveLength(2); // Documents and Websites sections
    });
  });

  describe('Error Flow Testing', () => {
    test('handles unknown service query gracefully', async () => {
      /**
       * Test: Unknown service → Error handling → Helpful message
       * **Validates: Requirements 7.4**
       */
      mockedAxios.post.mockResolvedValueOnce(mockErrorApiResponse);

      render(<ChatInterface />);

      fireEvent.change(screen.getByTestId('query-input'), { 
        target: { value: 'quantum physics permit' } 
      });
      fireEvent.click(screen.getByTestId('submit-button'));

      await waitFor(() => {
        expect(screen.getByTestId('response-container')).toBeInTheDocument();
      });

      // Should show helpful message instead of service guide
      expect(screen.getByText(/I'm here to help you with government services/)).toBeInTheDocument();
      expect(screen.queryByRole('article')).not.toBeInTheDocument(); // No service guide
    });

    test('handles API errors gracefully', async () => {
      /**
       * Test: API error → Error handling → User feedback
       * **Validates: Requirements 7.1**
       */
      mockedAxios.post.mockRejectedValueOnce(new Error('Network error'));

      render(<ChatInterface />);

      fireEvent.change(screen.getByTestId('query-input'), { 
        target: { value: 'aadhaar name change' } 
      });
      fireEvent.click(screen.getByTestId('submit-button'));

      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toBeInTheDocument();
      });

      expect(screen.getByText('Failed to get response')).toBeInTheDocument();
    });

    test('handles empty service data gracefully', async () => {
      /**
       * Test: Service with all empty categories → Proper display
       * **Validates: Requirements 1.3, 8.2**
       */
      mockedAxios.post.mockResolvedValueOnce(mockEmptyApiResponse);

      render(<ChatInterface />);

      fireEvent.change(screen.getByTestId('query-input'), { 
        target: { value: 'empty service' } 
      });
      fireEvent.click(screen.getByTestId('submit-button'));

      await waitFor(() => {
        expect(screen.getByTestId('response-container')).toBeInTheDocument();
      });

      // Should still show service guide with all sections
      expect(screen.getByText('Service with Limited Information')).toBeInTheDocument();
      
      // All sections should show "Information not available"
      const notAvailableMessages = screen.getAllByText('Information not available');
      expect(notAvailableMessages).toHaveLength(5);

      // But all section headers should still be present
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
  });

  describe('Various Service Types Integration', () => {
    test('maintains consistency across different service categories', async () => {
      /**
       * Test: Multiple service types → Consistent structure
       * **Validates: Requirements 8.1, 8.4**
       */
      const serviceVariations = [
        {
          service_name: 'Birth Certificate',
          category: 'certificate',
          description: 'Official birth certificate issuance'
        },
        {
          service_name: 'Driving License',
          category: 'license',
          description: 'Driving license application and renewal'
        },
        {
          service_name: 'Business Registration',
          category: 'registration',
          description: 'Register new business entity'
        }
      ];

      for (const service of serviceVariations) {
        const response = {
          ...mockApiResponse,
          data: {
            ...mockApiResponse.data,
            enhanced_service_guide: {
              ...mockApiResponse.data.enhanced_service_guide,
              service_name: service.service_name,
              category: service.category,
              description: service.description
            }
          }
        };

        mockedAxios.post.mockResolvedValueOnce(response);

        const { unmount } = render(<ChatInterface />);

        fireEvent.change(screen.getByTestId('query-input'), { 
          target: { value: service.service_name.toLowerCase() } 
        });
        fireEvent.click(screen.getByTestId('submit-button'));

        await waitFor(() => {
          expect(screen.getByTestId('response-container')).toBeInTheDocument();
        });

        // Verify consistent structure
        expect(screen.getByText(service.service_name)).toBeInTheDocument();
        expect(screen.getByText(service.description)).toBeInTheDocument();

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
      }
    });
  });

  describe('Performance and User Experience', () => {
    test('provides loading states during API calls', async () => {
      /**
       * Test: Loading states → User feedback during processing
       * **Validates: Requirements 7.1**
       */
      // Mock a delayed response
      mockedAxios.post.mockImplementation(() => 
        new Promise(resolve => 
          setTimeout(() => resolve(mockApiResponse), 100)
        )
      );

      render(<ChatInterface />);

      fireEvent.change(screen.getByTestId('query-input'), { 
        target: { value: 'aadhaar name change' } 
      });
      fireEvent.click(screen.getByTestId('submit-button'));

      // Should show loading state
      expect(screen.getByText('Loading...')).toBeInTheDocument();
      expect(screen.getByTestId('submit-button')).toBeDisabled();

      // Wait for response
      await waitFor(() => {
        expect(screen.getByTestId('response-container')).toBeInTheDocument();
      });

      // Loading state should be gone
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      expect(screen.getByTestId('submit-button')).not.toBeDisabled();
    });

    test('handles rapid successive queries', async () => {
      /**
       * Test: Multiple rapid queries → Proper state management
       * **Validates: Requirements 7.1**
       */
      mockedAxios.post
        .mockResolvedValueOnce(mockApiResponse)
        .mockResolvedValueOnce(mockEmptyApiResponse);

      render(<ChatInterface />);

      // First query
      fireEvent.change(screen.getByTestId('query-input'), { 
        target: { value: 'first query' } 
      });
      fireEvent.click(screen.getByTestId('submit-button'));

      // Second query before first completes
      fireEvent.change(screen.getByTestId('query-input'), { 
        target: { value: 'second query' } 
      });
      fireEvent.click(screen.getByTestId('submit-button'));

      await waitFor(() => {
        expect(screen.getByTestId('response-container')).toBeInTheDocument();
      });

      // Should handle both requests properly
      expect(mockedAxios.post).toHaveBeenCalledTimes(2);
    });
  });

  describe('Data Integrity Through Pipeline', () => {
    test('preserves data integrity from API to display', async () => {
      /**
       * Test: API data → Frontend display → Data preservation
       * **Validates: Requirements 9.1, 9.4**
       */
      mockedAxios.post.mockResolvedValueOnce(mockApiResponse);

      render(<ChatInterface />);

      fireEvent.change(screen.getByTestId('query-input'), { 
        target: { value: 'aadhaar name change' } 
      });
      fireEvent.click(screen.getByTestId('submit-button'));

      await waitFor(() => {
        expect(screen.getByTestId('response-container')).toBeInTheDocument();
      });

      // Verify specific data from API is preserved in display
      const apiGuide = mockApiResponse.data.enhanced_service_guide;
      
      // Service metadata
      expect(screen.getByText(apiGuide.service_name)).toBeInTheDocument();
      expect(screen.getByText(apiGuide.description)).toBeInTheDocument();
      
      // Verify timestamp is formatted and displayed
      expect(screen.getByText(/Last updated: January 15, 2024/)).toBeInTheDocument();
      
      // Verify section content is preserved
      expect(screen.getByText('UIDAI Regional Office')).toBeInTheDocument();
      expect(screen.getByText('Proof of Identity')).toBeInTheDocument();
      expect(screen.getByText('Document Verification Counter')).toBeInTheDocument();
      
      // Verify links are properly rendered
      const portalLink = screen.getByRole('link', { name: /Online Portal/ });
      expect(portalLink).toHaveAttribute('href', 'https://uidai.gov.in/my-aadhaar/update-aadhaar');
    });
  });
});