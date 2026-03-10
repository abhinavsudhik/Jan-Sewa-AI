/**
 * TypeScript interfaces for enhanced government service data.
 * 
 * These interfaces match the Python data models exactly to ensure
 * type safety between frontend and backend.
 */

// Service category enum matching Python ServiceCategory
export enum ServiceCategory {
  AADHAAR = "aadhaar",
  DATA_ACCESS = "data_access",
  RECORD_MODIFICATION = "record_modification",
  STATUS_INQUIRY = "status_inquiry",
  IDENTITY_CARD = "identity_card",
  CERTIFICATE = "certificate"
}

// Geographic coordinates for office locations
export interface Coordinates {
  latitude: number;
  longitude: number;
}

// Physical location where a government service can be accessed
export interface OfficeLocation {
  name: string;
  address: string;
  city: string;
  state: string;
  postal_code: string;
  coordinates?: Coordinates;
  operating_hours?: string;
  contact_phone?: string;
}

// Document required for a government service
export interface RequiredDocument {
  document_name: string;
  description?: string;
  copies_required: number;
  format_requirements?: string;
  is_mandatory: boolean;
  alternatives?: string[];
}

// A step in the office visit sequence
export interface OfficeVisitStep {
  sequence_number: number;
  office_name: string;
  purpose: string;
  estimated_duration: string;
  is_optional: boolean;
  is_conditional: boolean;
  condition?: string;
}

// Official government website link
export interface OfficialWebsiteLink {
  url: string;
  purpose: string;
  description?: string;
}

// Processing timeline for a government service
export interface ProcessingTimeline {
  minimum_days: number;
  maximum_days: number;
  typical_days: number;
  time_unit: string;
  processing_type: string;
  notes?: string;
  factors_affecting_time: string[];
}

// Complete service guide with all required information categories
export interface EnhancedServiceGuide {
  // Basic information
  service_id: string;
  service_name: string;
  category: ServiceCategory;
  description: string;
  
  // Five required information categories
  office_locations: OfficeLocation[];
  required_documents: RequiredDocument[];
  office_visit_sequence: OfficeVisitStep[];
  official_websites: OfficialWebsiteLink[];
  processing_timelines: ProcessingTimeline[];
  
  // Metadata
  last_updated: string; // ISO datetime string
  data_source: string;
  available_languages: string[];
  
  // Legacy compatibility fields (for gradual migration)
  steps?: any[];
  processing_time?: any;
  official_portal_url?: string;
  contact_info?: any;
}

// A section in the formatted response
export interface ResponseSection {
  header: string;
  content: string;
  is_empty: boolean;
}

// Complete formatted service response
export interface FormattedServiceResponse {
  service_name: string;
  description: string;
  sections: ResponseSection[];
  last_updated: string; // ISO datetime string
}

// Enhanced chat response with new service guide field
export interface ChatResponse {
  message: string;
  language: string;
  session_id: string;
  service_guide?: EnhancedServiceGuide;
  enhanced_service_guide?: EnhancedServiceGuide; // New field for enhanced data
  formatted_response?: FormattedServiceResponse; // Formatted response sections
}