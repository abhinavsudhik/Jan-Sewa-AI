/**
 * Example usage of EnhancedServiceGuideDisplay component
 * 
 * This file demonstrates how to use the EnhancedServiceGuideDisplay component
 * with sample data that includes all five required information categories.
 */

import React from 'react';
import { EnhancedServiceGuideDisplay } from './EnhancedServiceGuideDisplay';
import { EnhancedServiceGuide, ServiceCategory } from '../types/service';

// Example service guide with all categories populated
const exampleServiceGuide: EnhancedServiceGuide = {
  service_id: 'aadhaar_name_change',
  service_name: 'Aadhaar Name Change',
  category: ServiceCategory.AADHAAR,
  description: 'Process to update or correct your name in the Aadhaar database. This service allows you to modify your name details in your Aadhaar card to match your official documents.',
  
  // Office Locations - Multiple locations with complete details
  office_locations: [
    {
      name: 'District Collectorate - Mumbai',
      address: '123 Government Complex, Fort',
      city: 'Mumbai',
      state: 'Maharashtra',
      postal_code: '400001',
      coordinates: {
        latitude: 18.9220,
        longitude: 72.8347
      },
      operating_hours: '9:00 AM - 5:00 PM (Monday to Friday)',
      contact_phone: '+91-22-2266-7788'
    },
    {
      name: 'Aadhaar Seva Kendra - Andheri',
      address: '456 Service Center Road, Andheri East',
      city: 'Mumbai',
      state: 'Maharashtra',
      postal_code: '400069',
      operating_hours: '10:00 AM - 6:00 PM (Monday to Saturday)',
      contact_phone: '+91-22-2834-5566'
    }
  ],
  
  // Required Documents - Comprehensive list with specifications
  required_documents: [
    {
      document_name: 'Aadhaar Card',
      description: 'Original Aadhaar card or e-Aadhaar printout',
      copies_required: 2,
      format_requirements: 'Original + 1 photocopy',
      is_mandatory: true
    },
    {
      document_name: 'Proof of Identity',
      description: 'Government-issued photo ID with correct name',
      copies_required: 1,
      format_requirements: 'Original + photocopy',
      is_mandatory: true,
      alternatives: ['Passport', 'Driving License', 'Voter ID Card', 'PAN Card']
    },
    {
      document_name: 'Proof of Name Change',
      description: 'Document showing the name change (if applicable)',
      copies_required: 1,
      format_requirements: 'Original + photocopy',
      is_mandatory: false,
      alternatives: ['Marriage Certificate', 'Gazette Notification', 'Court Order']
    }
  ],
  
  // Office Visit Sequence - Multi-step process
  office_visit_sequence: [
    {
      sequence_number: 1,
      office_name: 'Document Verification Counter',
      purpose: 'Submit required documents and fill out the name change application form',
      estimated_duration: '30-45 minutes',
      is_optional: false,
      is_conditional: false
    },
    {
      sequence_number: 2,
      office_name: 'Biometric Verification Center',
      purpose: 'Provide fingerprints and iris scan for identity verification',
      estimated_duration: '15-20 minutes',
      is_optional: false,
      is_conditional: false
    },
    {
      sequence_number: 3,
      office_name: 'Payment Counter',
      purpose: 'Pay the processing fee and collect receipt',
      estimated_duration: '10-15 minutes',
      is_optional: false,
      is_conditional: false
    },
    {
      sequence_number: 4,
      office_name: 'Acknowledgment Counter',
      purpose: 'Collect acknowledgment receipt with URN (Update Request Number)',
      estimated_duration: '5-10 minutes',
      is_optional: true,
      is_conditional: true,
      condition: 'Only if you want physical acknowledgment receipt'
    }
  ],
  
  // Official Websites - Multiple relevant links
  official_websites: [
    {
      url: 'https://uidai.gov.in',
      purpose: 'UIDAI Official Website',
      description: 'Main website for all Aadhaar-related services and information'
    },
    {
      url: 'https://resident.uidai.gov.in/update-aadhaar',
      purpose: 'Online Update Portal',
      description: 'Submit name change request online and track status'
    },
    {
      url: 'https://appointments.uidai.gov.in',
      purpose: 'Appointment Booking',
      description: 'Book appointment at Aadhaar Seva Kendra'
    },
    {
      url: 'https://resident.uidai.gov.in/check-status',
      purpose: 'Status Tracking',
      description: 'Check the status of your name change request'
    }
  ],
  
  // Processing Timelines - Standard and expedited options
  processing_timelines: [
    {
      minimum_days: 15,
      maximum_days: 30,
      typical_days: 21,
      time_unit: 'days',
      processing_type: 'standard',
      notes: 'Processing time starts from the date of successful biometric verification',
      factors_affecting_time: [
        'Document verification complexity',
        'Regional office workload',
        'Accuracy of submitted information',
        'Peak season applications'
      ]
    },
    {
      minimum_days: 7,
      maximum_days: 15,
      typical_days: 10,
      time_unit: 'days',
      processing_type: 'expedited',
      notes: 'Available for urgent cases with additional fee. Requires valid justification.',
      factors_affecting_time: [
        'Justification approval',
        'Document completeness',
        'Biometric match quality'
      ]
    }
  ],
  
  // Metadata
  last_updated: '2024-01-15T10:30:00Z',
  data_source: 'UIDAI Official Guidelines',
  available_languages: ['en', 'hi', 'mr']
};

// Example with empty categories to show "Information not available" handling
const exampleServiceGuideWithEmptyCategories: EnhancedServiceGuide = {
  service_id: 'new_service',
  service_name: 'New Government Service',
  category: ServiceCategory.CERTIFICATE,
  description: 'This is a new service with limited information available.',
  
  // Empty arrays to demonstrate "Information not available" display
  office_locations: [],
  required_documents: [],
  office_visit_sequence: [],
  official_websites: [],
  processing_timelines: [],
  
  last_updated: '2024-01-15T10:30:00Z',
  data_source: 'test',
  available_languages: ['en']
};

// Example component usage
export function EnhancedServiceGuideExample() {
  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>Enhanced Service Guide Display - Complete Example</h2>
      <EnhancedServiceGuideDisplay guide={exampleServiceGuide} />
      
      <h2 style={{ marginTop: '40px' }}>Enhanced Service Guide Display - Empty Categories Example</h2>
      <EnhancedServiceGuideDisplay guide={exampleServiceGuideWithEmptyCategories} />
    </div>
  );
}

export default EnhancedServiceGuideExample;