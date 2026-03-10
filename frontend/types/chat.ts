export interface ServiceStep {
  step_number: number;
  description: string;
  requires_in_person: boolean;
  online_available: boolean;
  estimated_duration: string;
  notes?: string;
}

export interface ProcessingTime {
  minimum: string;
  maximum: string;
  typical: string;
  factors: string[];
}

export interface ContactInfo {
  phone?: string;
  email?: string;
  address?: string;
  helpline?: string;
}

export interface ServiceGuide {
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

import { EnhancedServiceGuide } from '../src/types/service';

export interface ChatResponse {
  message: string;
  language: string;
  session_id: string;
  service_guide?: ServiceGuide;
  enhanced_service_guide?: EnhancedServiceGuide; // Enhanced service data with raw structure
}
